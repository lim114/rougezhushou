"""Host provision -> actual Windows/Wine product -> independent host check."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
folder=Path(tempfile.mkdtemp(prefix='public-host-link-check-',dir=ROOT))
rows=[]
for implementation in ('base','candidate'):
 original_links={}
 for kind in ('run','cache'):
  path=folder/f'{implementation}-{kind}.json'
  path.symlink_to(folder/f'{implementation}-{kind}-missing.json')
  original_links[kind]=os.readlink(path)
 win_folder='Z:'+str(folder).replace('/','\\')
 command=['bash',str(REPO/'scripts/wine_python.sh'),str(ROOT/'probe_host_public_preservation.py'),implementation,win_folder]
 completed=subprocess.run(command,cwd=REPO,capture_output=True,text=True,check=True)
 result=json.loads((ROOT/('host-public-'+implementation+'.json')).read_text(encoding='utf-8'))
 for row in result['rows']:
  kind=row['kind'];path=folder/f'{implementation}-{kind}.json'
  after_link=os.readlink(path) if path.is_symlink() else None
  retained=after_link==original_links[kind]
  target_absent=not (folder/f'{implementation}-{kind}-missing.json').exists()
  if implementation=='candidate':assert retained and target_absent and row['save_result'] is False and row['save_issue']
  else:assert not retained and target_absent and row['save_result'] is True
  rows.append({'implementation':implementation,'kind':kind,'original_link_target':original_links[kind],'host_after_link_target':after_link,'retained_original_link':retained,'target_still_absent':target_absent,'wine_product':row})
receipt={'public_work_fixtures_only':True,'real_Windows_verified':False,'wine10':True,'base_bug_reproduced':True,'candidate_prevents_both_overwrites':True,'cases':rows}
(ROOT/'host-independent-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('Original product overwrote both own host links; candidate preserved both. Independent host checks PASS.')
