"""No provider calls: assert consent, confidentiality, secret routing and safe failures."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from streamlit_app.gemini import AssistanceUnavailable, assist


class GeminiTests(unittest.TestCase):
    def setUp(self):
        self.secrets = {'gemini': {'enabled': True, 'api_key': 'synthetic-test-key'}}
        self.args = dict(task='Analisi NC', text='Testo sintetico', classification='synthetic', consent=True)

    @patch('streamlit_app.gemini.request.urlopen')
    def test_denied_requests_never_reach_provider(self, send):
        cases = [({}, {}), (self.secrets, {'consent': False}),
                 (self.secrets, {'classification': 'confidential'}),
                 (self.secrets, {'text': 'x' * 20001}),
                 (self.secrets, {'classification': 'other'}),
                 ({'gemini': {'enabled': True}}, {})]
        for secrets, overrides in cases:
            with self.assertRaises(AssistanceUnavailable):
                assist(secrets, **{**self.args, **overrides})
        send.assert_not_called()

    @patch('streamlit_app.gemini.request.urlopen')
    def test_explicit_submission_and_header_secret(self, send):
        send.return_value.__enter__.return_value = io.BytesIO(json.dumps({'candidates': [{'content': {'parts': [{'text': 'Da verificare'}]}}]}).encode())
        self.assertEqual(assist(self.secrets, **self.args), 'Da verificare')
        req = send.call_args.args[0]
        self.assertNotIn('synthetic-test-key', req.full_url)
        self.assertEqual(req.get_header('X-goog-api-key'), 'synthetic-test-key')
        self.assertEqual(json.loads(req.data)['contents'][0]['parts'], [{'text': 'Testo sintetico'}])
        self.assertEqual(send.call_args.kwargs['timeout'], 30)

    @patch('streamlit_app.gemini.request.urlopen', side_effect=OSError('synthetic-test-key secret-provider-error'))
    def test_provider_failure_redacted(self, send):
        with self.assertRaises(AssistanceUnavailable) as ctx:
            assist(self.secrets, **self.args)
        self.assertNotIn('synthetic-test-key', str(ctx.exception))
        self.assertNotIn('secret-provider-error', str(ctx.exception))

    @patch('streamlit_app.gemini.request.urlopen')
    def test_confidential_needs_both_explicit_settings(self, send):
        self.secrets['gemini']['allow_confidential_data'] = True
        with self.assertRaises(AssistanceUnavailable):
            assist(self.secrets, **{**self.args, 'classification': 'confidential'})
        send.assert_not_called()

    @patch('streamlit_app.gemini.request.urlopen')
    def test_empty_blocked_and_malformed_answers_are_safe(self, send):
        for value in ([], {}, {'candidates': []}, {'candidates': [None]},
                      {'candidates': [{'content': {'parts': None}}]}):
            send.return_value.__enter__.return_value = io.BytesIO(json.dumps(value).encode())
            with self.assertRaises(AssistanceUnavailable):
                assist(self.secrets, **self.args)


if __name__ == '__main__':
    unittest.main()
