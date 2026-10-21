"""Regression for a cached pre-upgrade Gemini module in a running Streamlit process."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from streamlit_app.assistant_service import dispatch


class AssistantStartupTests(unittest.TestCase):
    def test_importing_service_does_not_import_optional_gemini(self):
        subprocess.run([sys.executable, '-c', "import sys; import streamlit_app.assistant_service; assert 'streamlit_app.gemini' not in sys.modules"], cwd=ROOT, check=True)

    def test_old_cached_module_is_reloaded_before_dispatch(self):
        subprocess.run([sys.executable, '-c', """
import importlib.util, sys, types
from pathlib import Path
path=Path('streamlit_app/gemini.py').resolve()
old=types.ModuleType('streamlit_app.gemini')
old.__file__=str(path)
old.__spec__=importlib.util.spec_from_file_location(old.__name__,path)
sys.modules[old.__name__]=old
from streamlit_app.assistant_service import dispatch
assert dispatch({}, {'operation':'status'}) == {'enabled':False,'key_present':False,'ready':False,'confidential_authorized':False}
assert sys.modules[old.__name__].ASSISTANT_API_VERSION == 2
"""], cwd=ROOT, check=True)

    @patch('streamlit_app.assistant_service.importlib.import_module', side_effect=ImportError('private diagnostic'))
    def test_missing_optional_module_has_safe_actionable_error(self, load):
        with self.assertRaises(ValueError) as exc:
            dispatch({}, {'operation': 'status'})
        self.assertIn('Riavvia', str(exc.exception))
        self.assertNotIn('private diagnostic', str(exc.exception))


if __name__ == '__main__':
    unittest.main()
