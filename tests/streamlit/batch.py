"""Read batching must retain per-request errors, permissions and write isolation."""
import json
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from streamlit_app.gateway import read_batch, invoke


class ReadBatchTests(unittest.TestCase):
    def test_reject_mutations_nested_batches_and_unbounded_input(self):
        good = {'id': 'read-1', 'path': 'sites', 'method': 'GET'}
        for items in ([], [good] * 17, [good, good],
                      [{**good, 'method': 'POST'}], [{**good, 'data': {'name': 'bad'}}],
                      [{**good, 'files': {'file': 'bad'}}], [{**good, 'path': '../sites'}],
                      [{**good, 'requests': [good]}], [None]):
            with self.assertRaises(ValueError):
                read_batch({'method': 'GET', 'requests': items})
        with self.assertRaises(ValueError):
            read_batch({'method': 'POST', 'requests': [good]})

    def test_normalized_read_only_payload(self):
        read = {'id': 'read-1', 'path': 'sites?per_page=1', 'method': 'GET', 'active_site': 'ignored'}
        self.assertEqual(read_batch({'method': 'GET', 'requests': [read]}),
                         [{'id': 'read-1', 'path': 'sites?per_page=1', 'method': 'GET'}])

    def test_live_role_authorization_and_partial_failure(self):
        root = Path(__file__).resolve().parents[2]
        qa = Path(os.environ.get('HSE_QA_DIR', root / '.local/streamlit-postgres-qa'))
        os.environ.update(json.loads((qa / 'streamlit-test-env.json').read_text()))
        from streamlit_app import database
        config = json.loads(os.environ['HSE_DATABASE'])
        ids = json.loads((qa / 'streamlit-test-ids.json').read_text())
        company = database.get_user(config, ids['role_users']['company'])
        paths = ['sites', 'observations?site_id=' + ids['site_id'], 'assessments/' + ids['assessment_id'], 'nonexistent-resource']
        reads = [{'id': str(i), 'path': path, 'method': 'GET'} for i, path in enumerate(paths)]
        response = invoke(config, company, request={'path': '__batch', 'method': 'GET', 'requests': reads})
        self.assertIn('data', response)
        self.assertEqual(len(response['data']), len(reads))
        # Compare with the original individual authorization boundary, including rejected resources.
        for read, batched in zip(reads, response['data']):
            individual = invoke(config, company, request=read)
            self.assertEqual({k: v for k, v in batched.items() if k != 'id'}, individual)
        self.assertIn('error', response['data'][2])
        self.assertIn('error', response['data'][3])


if __name__ == '__main__':
    unittest.main()
