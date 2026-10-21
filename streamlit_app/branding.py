"""Display only locally approved references; empty manifest means no placeholder."""
import json
from pathlib import Path
import re
import streamlit as st

ROOT = Path(__file__).resolve().parent / 'ui'


def show_brand(slot):
    entries = json.loads((ROOT / 'brand.json').read_text())
    item = entries.get(slot)
    if not item:
        return
    filename = item.get('file', '')
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]*\.(png|jpe?g|webp|svg)', filename, re.I):
        return
    image = ROOT / 'references' / filename
    if image.is_file():
        st.image(str(image), caption=item.get('alt', ''), width=240)
