from pathlib import Path
import zipfile,hashlib,re
root=Path(__file__).resolve().parents[1]
p=root/'hse-risk-platform'
version=re.search(r'^\s*\* Version:\s*([0-9.]+)',(p/'hse-risk-platform.php').read_text(),re.M).group(1)
output=root/('dist/hse-risk-platform-'+version+'.zip')
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
sums=root/'dist/SHA256SUMS'
entries={line.split()[1]:line.split()[0] for line in sums.read_text().splitlines()} if sums.exists() else {}
entries[output.name]=hashlib.sha256(output.read_bytes()).hexdigest()
sums.write_text(''.join(entries[name]+'  '+name+'\n' for name in sorted(entries)))
print(output.name,output.stat().st_size,'bytes')
