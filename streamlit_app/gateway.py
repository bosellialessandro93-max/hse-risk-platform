"""Trusted session -> isolated PHP domain invocation. No public PHP endpoint."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from streamlit_app.database import validated_config, schema_config

ROOT = Path(__file__).resolve().parents[1]


class RuntimeUnavailable(RuntimeError):
    pass


def read_batch(request):
    """Only read requests may share a runtime; each is dispatched/authorized separately."""
    items = request.get('requests')
    if request.get('method') != 'GET' or not isinstance(items, list) or not 1 <= len(items) <= 16:
        raise ValueError('Gruppo di letture non valido.')
    result = []
    ids = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('Lettura non valida.')
        path, identity = item.get('path'), item.get('id')
        if (not isinstance(path, str) or len(path) > 10000
                or not re.fullmatch(r'[a-z0-9_-]+(?:/[a-zA-Z0-9_-]+){0,3}', path.split('?')[0])
                or not isinstance(identity, str) or len(identity) > 128 or identity in ids
                or item.get('method') != 'GET'
                or any(item.get(key) for key in ('data', 'files', 'form', 'requests'))):
            raise ValueError('Solo letture indipendenti sono ammesse nel gruppo.')
        ids.add(identity)
        result.append({'id': identity, 'path': path, 'method': 'GET'})
    return result


def invoke(config, actor, *, request=None, action=None, model=None):
    config = schema_config(config) if action == 'bootstrap' else validated_config(config)
    command = json.loads(os.environ['HSE_PHP_COMMAND']) if os.environ.get('HSE_PHP_COMMAND') else [shutil.which('php') or 'php']
    path = os.environ.get('HSE_RUNNER_PATH', str(ROOT / 'streamlit_app/runtime/runner.php'))
    payload = {'actor': {'id': int(actor['id']), 'is_admin': bool(actor['is_admin'])}}
    if action:
        if action not in ('bootstrap', 'calculate_model'):
            raise ValueError('Invalid internal action')
        payload.update(action=action, model=model)
    else:
        if not isinstance(request, dict) or not isinstance(request.get('path'), str):
            raise ValueError('Richiesta non valida.')
        route = request['path'].split('?')[0]
        if not re.fullmatch(r'[a-z0-9_-]+(?:/[a-zA-Z0-9_-]+){0,3}', route) or len(request['path']) > 10000:
            raise ValueError('Percorso non valido.')
        if request.get('data') is not None and not isinstance(request['data'], dict):
            raise ValueError('Dati non validi.')
        if route == '__batch':
            payload['requests'] = read_batch(request)
        else:
            payload['request'] = {key: request.get(key) for key in ('path', 'data', 'files', 'form') if request.get(key) is not None}
            payload['request']['method'] = request.get('method', 'GET')
    serialized = json.dumps(payload, ensure_ascii=False)
    if len(serialized.encode()) > 64 * 1024 * 1024:
        raise ValueError('Richiesta oltre 64 MB.')
    env = dict(os.environ, HSE_DATABASE=json.dumps(config))
    try:
        result = subprocess.run(command + ['-d', 'memory_limit=256M', path], input=serialized,
                                capture_output=True, text=True, env=env, timeout=90)
        response = json.loads(result.stdout)
        if result.returncode or not isinstance(response, dict):
            raise ValueError('Runtime failure')
        return response
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        raise RuntimeUnavailable('Runtime PHP non disponibile: verificare packages.txt, estensioni e connessione database.') from error
