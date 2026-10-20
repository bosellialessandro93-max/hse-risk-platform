"""Validate the newly generated Streamlit downloads, independently of WordPress artifacts."""
from pathlib import Path
import json
import zipfile
import fitz
import openpyxl
from PIL import Image

artifacts=Path(__file__).resolve().parents[1]/'artifacts'
files=[p for p in artifacts.glob('streamlit-*') if p.suffix in ('.pdf','.docx','.xlsx','.pptx','.ics')]
saved=json.loads((artifacts/'streamlit-risk-saved.json').read_text())
counts={};photo_images=0
for path in files:
    suffix=path.suffix;counts[suffix]=counts.get(suffix,0)+1
    if suffix=='.pdf':
        with fitz.open(path) as doc:
            assert len(doc)>0
            assert any(page.get_text().strip() for page in doc) or (path.name.startswith('streamlit-map-') and any(page.get_images() for page in doc)),path
            if path.name.startswith(('streamlit-photos-','streamlit-meeting-')):
                images=sum(len(page.get_images()) for page in doc)
                assert images>=1,path
                photo_images+=images
    elif suffix=='.xlsx':
        wb=openpyxl.load_workbook(path,data_only=True)
        numbers=[cell.value for sheet in wb for row in sheet for cell in row if isinstance(cell.value,(float,int))]
        assert any(abs(x-saved['result']['base'])<1e-8 for x in numbers),'Risk value missing from Excel'
    elif suffix in ('.docx','.pptx'):
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            names=z.namelist()
            if suffix=='.pptx':assert any(n.startswith('ppt/charts/chart') for n in names),'Native chart missing'
            if path.name.startswith(('streamlit-photos-','streamlit-meeting-')):assert any(n.startswith('word/media/') for n in names),'Photo missing from Word'
    else:assert 'BEGIN:VEVENT' in path.read_text() and 'END:VCALENDAR' in path.read_text()
for suffix in ['.pdf','.docx','.xlsx','.pptx','.ics']:assert counts.get(suffix),suffix
for path in artifacts.glob('streamlit-map-*.png'):
    with Image.open(path) as im:im.verify()
exported=[p for p in artifacts.glob('streamlit-risk-*.json') if p.name!='streamlit-risk-saved.json']
assert exported
for path in exported:
    data=json.loads(path.read_text());record=data.get('record',data)
    # Generator JSON wraps a source record plus site and metadata.
    if 'result' not in record and 'data' in record:record=record['data']
    assert record['result']['base']==saved['result']['base']
report={'files_checked':len(files),'formats':counts,'pdf_evidence_images':photo_images,'risk_excel_reconciled':True,'json_reconciled':True,'native_pptx_chart':True}
(artifacts/'streamlit-export-validation.json').write_text(json.dumps(report,indent=2))
print('PASS Streamlit exported files:',counts,'PDF/Word photos, native PPTX chart, Excel/JSON risk and ICS')
