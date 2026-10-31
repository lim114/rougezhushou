from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy
R=Path.cwd();B=R/'verification/maintenance/grade16-review-20261031'
p=R/'PROJECT_REQUIREMENTS.md';raw=p.read_bytes();old='不再按历史要求后置。识别覆盖、布局和性能优化统一最后做。'.encode();new='不再按历史要求后置。'.encode();assert raw.count(old)==1;p.write_bytes(raw.replace(old,new))
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert idx['validate_delivery'](R,cp)['current_section']==440
p=B/'final-audit.json';v=json.loads(p.read_bytes())
for k,n in(('requirements','PROJECT_REQUIREMENTS.md'),('cloud_index','CLOUD_INDEX.json')):
 raw=(R/n).read_bytes();v[k]={'path':n,'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
v['active_requirements_old_recognition_last_contradiction_removed']=True;v['at_UTC']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
(B/'final-metadata-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
(B/'archive-manifest.json').write_text(json.dumps({'kind':'explicit_public_archive','files':files},ensure_ascii=False,indent=2)+'\n','utf8')
print({'passed':True,'archive_files':len(files)})
