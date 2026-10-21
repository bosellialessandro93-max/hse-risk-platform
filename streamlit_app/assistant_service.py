"""Lazy boundary: an optional AI module must never prevent platform startup."""
import importlib

SERVICE_VERSION = 3

def dispatch(secrets, data):
    try:
        module = importlib.import_module('streamlit_app.gemini')
        # Streamlit can retain an imported module while app.py is updated in place.
        # Reload only our module when its cached API predates this deployment.
        if getattr(module, 'ASSISTANT_API_VERSION', None) != SERVICE_VERSION or not callable(getattr(module, 'dispatch', None)):
            module = importlib.reload(module)
        handler = getattr(module, 'dispatch', None)
        if getattr(module, 'ASSISTANT_API_VERSION', None) != SERVICE_VERSION or not callable(handler):
            raise ImportError('Assistant API not available')
    except (ImportError, SyntaxError, OSError):
        raise ValueError('Assistenza AI temporaneamente non disponibile. Riavvia l’app Streamlit; le altre funzioni restano disponibili.') from None
    return handler(secrets, data)
