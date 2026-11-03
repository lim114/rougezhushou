from pathlib import Path
from hashlib import sha256
import sys,json,subprocess,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/node-card-review-20261031'
def pin(p):
 raw=p.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def read(p):return json.loads(p.read_bytes())
summary=read(B/'summary.json')
for k in('source_review','related_receipt','native_receipt','comparison','image_review','runtime','live_public_fetch'):
 d=summary[k];assert pin(R/d['path'])=={x:d[x]for x in('sha256','bytes')},k
for item in read(B/'review-source.json')['changed_source']:assert pin(R/item['path'])=={x:item[x]for x in('sha256','bytes')}
assert summary['implemented_scope_passed']and not summary['application_review_complete']and not summary['video_parity_complete']
cp=read(R/'DEVELOPMENT_CHECKPOINT.json');m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));assert m['validate_delivery'](R,cp)['current_section']==440
assert read(R/'CLOUD_INDEX.json')['requirements']['sha256']==pin(R/'PROJECT_REQUIREMENTS.md')['sha256']
from scripts.verify_full_available import maintained_selectors
old=read(R/'verification/sections/440-source-audit.json')['current_selectors'];sel=maintained_selectors();assert len(sel)==694 and sel[:len(old)]==old
files=[n for n in subprocess.check_output(['git','ls-files','rouge']).decode().splitlines()if Path(n).suffix in('.py','.cjs','.js')]
new=[n for n in subprocess.check_output(['git','ls-files','--others','--exclude-standard','rouge']).decode().splitlines()if Path(n).suffix in('.py','.cjs','.js')]
assert len(files)+len(new)==530,(len(files),len(new))
for n in ('rouge/run_state.py','rouge/node_catalog_view.py','rouge/capture.py','PROJECT_REQUIREMENTS.md'):
 assert subprocess.check_output(['git','show',summary['baseline_commit']+':'+n])==(R/n).read_bytes()
assert all(not any(s in p.parts for s in('.local','private'))for p in B.rglob('*')if p.is_file())
audit={'passed':True,'baseline_commit':summary['baseline_commit'],'source_inventory_count':530,'ordered_selectors':694,'related_unique_available_checks':132,'final_related_subset':17,'final_native_checks':60,'summary':pin(B/'summary.json'),'current_index':pin(R/'CLOUD_INDEX.json'),'requirements':pin(R/'PROJECT_REQUIREMENTS.md'),'requirements_unchanged':True,'private_contents_included':False,'application_review_complete':False,'video_parity_complete':False,'full_validation_rerun':False}
(B/'final-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf8')
(B/'audit-source.py').write_bytes(Path(__file__).read_bytes())
manifest={p.relative_to(R).as_posix():pin(p)for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
(B/'archive-manifest.json').write_text(json.dumps({'kind':'explicit_public_archive','files':manifest},ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'public_archive_files':len(manifest),'public_bytes':sum(v['bytes']for v in manifest.values()),'goal_complete':False}))
