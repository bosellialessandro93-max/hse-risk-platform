"""Neon dotenv/Secrets precedence and direct schema routing, without external credentials."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from streamlit_app.configuration import database_configuration
from streamlit_app.database import schema_config

POOLED = 'postgresql://u:p@pooler.example.org/db?sslmode=require'
DIRECT = 'postgresql://u:p@direct.example.org/db?sslmode=require'
OTHER = 'postgresql://u:p@other.example.org/other?sslmode=require'


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.dict(os.environ, {}, clear=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_neon_generated_dotenv(self):
        (self.root/'.env.local').write_text(f'DATABASE_URL="{POOLED}"\nDATABASE_URL_UNPOOLED="{DIRECT}"\n')
        cfg = database_configuration({}, self.root)
        self.assertEqual(cfg['host'], 'pooler.example.org')
        self.assertEqual(schema_config(cfg)['host'], 'direct.example.org')
        self.assertEqual(cfg['host'], 'pooler.example.org')

    def test_local_wins_over_dotenv(self):
        (self.root/'.env.local').write_text(f'DATABASE_URL="{POOLED}"\n')
        (self.root/'.env').write_text(f'DATABASE_URL="{OTHER}"\n')
        self.assertEqual(database_configuration({}, self.root)['host'], 'pooler.example.org')

    def test_process_wins_over_files(self):
        (self.root/'.env.local').write_text(f'DATABASE_URL="{POOLED}"\n')
        os.environ['DATABASE_URL'] = OTHER
        self.assertEqual(database_configuration({}, self.root)['host'], 'other.example.org')

    def test_secrets_not_mixed_with_unrelated_env_direct_url(self):
        os.environ['DATABASE_URL_UNPOOLED'] = OTHER
        cfg = database_configuration({'DATABASE_URL':POOLED}, self.root)
        self.assertNotIn('schema_url', cfg)

    def test_cloud_top_level_secrets_pair(self):
        cfg = database_configuration({'DATABASE_URL':POOLED,'DATABASE_URL_UNPOOLED':DIRECT}, self.root)
        self.assertEqual(schema_config(cfg)['host'], 'direct.example.org')

    def test_explicit_database_and_qa_settings_preserved(self):
        os.environ['DATABASE_URL'] = OTHER
        self.assertEqual(database_configuration({'database':{'url':POOLED}}, self.root)['host'], 'pooler.example.org')
        os.environ['HSE_DATABASE'] = json.dumps({'url':DIRECT})
        self.assertEqual(database_configuration({'database':{'url':POOLED}}, self.root)['host'], 'direct.example.org')

    def test_direct_only_and_dotenv_fallback(self):
        (self.root/'.env').write_text(f'DATABASE_URL_UNPOOLED="{DIRECT}"\n')
        self.assertEqual(database_configuration({}, self.root)['host'], 'direct.example.org')


if __name__ == '__main__':
    unittest.main()
