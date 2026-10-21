"""Resolve existing Secrets and Neon CLI dotenv variables without logging credentials."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from streamlit_app.database import validated_config


def database_configuration(values, root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    # Process variables win; .env.local wins over .env. Never search other projects.
    load_dotenv(root / '.env.local', override=False)
    load_dotenv(root / '.env', override=False)
    if os.environ.get('HSE_DATABASE'):
        config = json.loads(os.environ['HSE_DATABASE'])
    elif values.get('database'):
        config = dict(values['database'])
    else:
        if values.get('DATABASE_URL') or values.get('DATABASE_URL_UNPOOLED'):
            url, direct = values.get('DATABASE_URL'), values.get('DATABASE_URL_UNPOOLED')
        else:
            url, direct = os.environ.get('DATABASE_URL'), os.environ.get('DATABASE_URL_UNPOOLED')
        config = {'url': url or direct or '',
                  'prefix': values.get('HSE_DATABASE_PREFIX') or os.environ.get('HSE_DATABASE_PREFIX', 'st_')}
        if url and direct:
            config['schema_url'] = direct
    return validated_config(config)
