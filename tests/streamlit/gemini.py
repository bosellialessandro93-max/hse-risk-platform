"""No provider calls: assert consent, confidentiality, secret routing and safe failures."""
import io
import json
from pathlib import Path
import sys
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from streamlit_app.gemini import AssistanceUnavailable, assist, dispatch, settings, status


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

    def test_streamlit_secret_aliases_and_metadata_redaction(self):
        for name in ('GEMINI_API_KEY', 'GOOGLE_API_KEY', 'Gemini API Key'):
            secrets = {'gemini': {'enabled': True}, name: 'synthetic-secret-value'}
            self.assertEqual(settings(secrets)['api_key'], 'synthetic-secret-value')
            result = dispatch(secrets, {'operation': 'status'})
            self.assertTrue(result['ready'])
            self.assertNotIn('synthetic-secret-value', json.dumps(result))
            self.assertFalse(status({name: 'synthetic-secret-value'})['enabled'])

    @patch('streamlit_app.gemini.request.urlopen')
    def test_status_does_not_send_and_invalid_operations_fail(self, send):
        dispatch(self.secrets, {'operation': 'status'})
        for data in (None, {}, {'operation': 'other'}):
            with self.assertRaises(AssistanceUnavailable):
                dispatch(self.secrets, data)
        send.assert_not_called()

    @patch('streamlit_app.gemini.request.urlopen')
    def test_http_diagnostics_are_actionable_and_never_echo_provider_secrets(self, send):
        cases = [(400,'API_KEY_INVALID','non accetta'), (403,'API_KEY_HTTP_REFERRER_BLOCKED','restrizioni'),
                 (403,'API_KEY_REPORTED_AS_LEAKED','esposta'), (429,'RESOURCE_EXHAUSTED','quota'),
                 (404,'NOT_FOUND','modello'), (400,'INVALID_ARGUMENT','rifiutato'), (503,'UNAVAILABLE','temporaneamente')]
        for code, reason, expected in cases:
            body = {'error': {'message': 'synthetic-test-key private-provider-detail', 'details': [{'reason':reason}]}}
            send.side_effect = HTTPError('https://example.invalid',code,'private-provider-detail',{},io.BytesIO(json.dumps(body).encode()))
            with self.assertRaises(AssistanceUnavailable) as ctx:
                assist(self.secrets, **self.args)
            self.assertIn(expected,str(ctx.exception))
            self.assertNotIn('synthetic-test-key',str(ctx.exception))
            self.assertNotIn('private-provider-detail',str(ctx.exception))
        self.assertEqual(send.call_count,len(cases),'Never retry automatically')

    @patch('streamlit_app.gemini.request.urlopen')
    def test_probe_is_explicit_read_only_and_never_sends_user_text(self, send):
        dispatch(self.secrets, {'operation':'status'})
        send.assert_not_called()
        send.return_value.__enter__.return_value = io.BytesIO(json.dumps({'supportedGenerationMethods':['generateContent']}).encode())
        result = dispatch(self.secrets, {'operation':'check_connection'})
        req = send.call_args.args[0]
        self.assertEqual(req.get_method(),'GET')
        self.assertIsNone(req.data)
        self.assertNotIn('synthetic-test-key', req.full_url)
        self.assertIn('quota',result['message'])

    @patch('streamlit_app.gemini.request.urlopen')
    def test_network_timeout_and_blocked_outputs_are_distinct(self, send):
        for failure, message in [(URLError('private-address'), 'DNS'), (TimeoutError(), '30 secondi')]:
            send.side_effect=failure
            with self.assertRaisesRegex(AssistanceUnavailable,message):
                assist(self.secrets, **self.args)
        send.side_effect=None
        for result, message in [({'promptFeedback':{'blockReason':'SAFETY'}},'bloccato'),
                                ({'candidates':[{'finishReason':'MAX_TOKENS'}]},'limite di output')]:
            send.return_value.__enter__.return_value=io.BytesIO(json.dumps(result).encode())
            with self.assertRaisesRegex(AssistanceUnavailable,message):
                assist(self.secrets, **self.args)


if __name__ == '__main__':
    unittest.main()
