from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from hashlib import sha1,sha256
from urllib.request import Request,urlopen
from PIL import Image
from io import BytesIO
import json,subprocess
R=Path.cwd();repo=R/'.cache/relic-image-review-git';out=R/'.cache/relic-display-image-review';out.mkdir(exist_ok=False)
commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD']).decode().strip()
tree={}
for line in(R/'.cache/relic-image-review-tree.txt').read_text('utf8').splitlines():
    info,path=line.split('\t',1);mode,kind,blob=info.split();tree[Path(path).stem]={'path':path,'blob':blob}
old=json.loads((R/'verification/maintenance/catalog-review-20261031/review-source.json').read_bytes())['unresolved_inventory_images']
targets=[r for r in old if r['icon']in tree]
def fetch(row):
    entry=tree[row['icon']];url='https://raw.githubusercontent.com/fexli/ArknightsResource/'+commit+'/rogueitem/'+entry['path']
    with urlopen(Request(url,headers={'User-Agent':'rouge-display-image-review'}),timeout=25)as response:raw=response.read()
    blob=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==entry['blob']
    assert raw.startswith(b'\x89PNG\r\n\x1a\n')
    with Image.open(BytesIO(raw))as image:dimensions=image.size;mode=image.mode;image.verify()
    file=out/(row['id']+'.png');file.write_bytes(raw)
    return {**row,'repository':'fexli/ArknightsResource','commit':commit,'source_path':'rogueitem/'+entry['path'],'url':url,'git_blob_sha1':blob,'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'dimensions':dimensions,'mode':mode,'downloaded_original_bytes':True}
results=[];failures=[]
with ThreadPoolExecutor(max_workers=3)as pool:
    futures={pool.submit(fetch,row):row for row in targets}
    for future in as_completed(futures):
        row=futures[future]
        try:results.append(future.result())
        except Exception as exc:failures.append({'id':row['id'],'error':str(exc)})
receipt={'repository':'fexli/ArknightsResource','commit':commit,'resource_tree_blob':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD:rogueitem']).decode().strip(),'icons':sorted(results,key=lambda r:r['id']),'failures':failures,'readme_source':'https://github.com/fexli/ArknightsResource/blob/'+commit+'/README_CN.md','copyright':'Hypergryph; artwork not relicensed under project code license. Existing GAME-ICON-NOTICE.md applies; these files are display references only.'}
(out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'downloaded_verified':len(results),'requested':len(targets),'failures':failures},ensure_ascii=False))
raise SystemExit(1 if failures else 0)
