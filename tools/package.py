from pathlib import Path
import zipfile,hashlib
root=Path(__file__).resolve().parents[1]
p=root/'hse-risk-platform'
output=root/'dist/hse-risk-platform-0.2.0.zip'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(p.rglob('*')):
  if f.is_file():
   info=zipfile.ZipInfo(str(f.relative_to(root)));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(info,f.read_bytes())
with zipfile.ZipFile(output) as z:
 assert z.testzip() is None
 assert 'hse-risk-platform/hse-risk-platform.php' in z.namelist()
 assert 'hse-risk-platform/assets/app.bundle.js' in z.namelist()
 assert not any('.local' in x or 'auth.json' in x or 'node_modules' in x for x in z.namelist())
(root/'dist/SHA256SUMS').write_text(hashlib.sha256(output.read_bytes()).hexdigest()+'  '+output.name+'\n')
print(output.name,output.stat().st_size,'bytes')
