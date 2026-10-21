"""Additional PostgreSQL checks; run after backend/auth with HSE_QA_DIR set."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
qa = Path(os.environ.get('HSE_QA_DIR', ROOT / '.local'))
os.environ.update(json.loads((qa / 'streamlit-test-env.json').read_text()))
from streamlit_app import database
from streamlit_app.gateway import invoke

config = json.loads(os.environ['HSE_DATABASE'])
auth = json.loads(os.environ['HSE_AUTH'])
assert config['driver'] == 'postgresql'
parsed = database.validated_config({'url': 'postgresql://name:p%40ss%27word@localhost/hse?sslmode=require&channel_binding=require'})
assert parsed['password'] == "p@ss'word" and parsed['channel_binding'] == 'require'
assert parsed['prefix'] == 'st_' and parsed['port'] == 5432
assert database.validated_config({'url': 'postgres://u:p@localhost/db'})['sslmode'] == 'verify-full'
assert database.validated_config({'host':'localhost','name':'db','user':'u','password':'p'})['driver'] == 'mysql'
for bad in [{'url':'https://secret@example.org/db'}, {'url':'postgresql://u:p@localhost/db','prefix':'x; DROP TABLE users'}, {'url':'postgresql://u:p@localhost/db?sslmode=bad'}]:
    try:
        database.validated_config(bad)
    except ValueError as e:
        assert 'secret' not in str(e)
    else:
        raise AssertionError('Invalid configuration accepted')
# Concurrent first-time bootstrap cannot create two administrators or fail DDL.
bootstrap_config = {**config, 'prefix': 'boot_' + uuid.uuid4().hex[:8] + '_'}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(lambda _: database.initialize(bootstrap_config, auth), range(3)))
with database.connection(bootstrap_config) as db, db.cursor() as cur:
    cur.execute(f'SELECT COUNT(*) AS n FROM {bootstrap_config["prefix"]}users')
    assert cur.fetchone()['n'] == 1
    for suffix in ('login_limits', 'options', 'users'):
        cur.execute(f'DROP TABLE {bootstrap_config["prefix"]}{suffix}')
admin = database.authenticate(config, auth['bootstrap_username'], auth['bootstrap_password'])
assert admin
request = {'path':'sites','method':'POST','data':{'name':'PG concurrent replay '+uuid.uuid4().hex[:6], 'technology':'Wind','request_id':str(uuid.uuid4())}}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    responses = list(pool.map(lambda _: invoke(config, admin, request=request), range(3)))
assert all('data' in r for r in responses), responses
assert len({r['data']['id'] for r in responses}) == 1
php = json.loads(os.environ.get('HSE_PHP_COMMAND', '["php"]'))
subprocess.run(php + [str(ROOT/'tests/streamlit/postgres.php')], check=True)
report = {'url_parsing_and_redaction':True, 'mysql_config_preserved':True,
          'concurrent_bootstrap_one_admin':True, 'concurrent_idempotent_create':True,
          'bytea_all_256_bytes':True, 'unicode_sql_literal_roundtrip':True,
          'options_upsert':True, 'record_revision_request_rollback':True}
(ROOT/'tests/artifacts/streamlit-postgres.json').write_text(json.dumps(report, indent=2))
print('PASS PostgreSQL configuration, concurrent bootstrap/idempotency, binaries and rollback')
