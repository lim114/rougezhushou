"""Acquire one exact known public blob; no search, alias guessing or retries."""
from datetime import datetime,timezone
from hashlib import sha256,sha1
import json
from pathlib import Path
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def read(name):return json.loads((ROOT/name).read_bytes())
receipt=read('rouge/data/relic-icon-receipt.json')
root=read('.cache/relic-resource-root.json');tree=read('.cache/relic-resource-tree.json')
assert root['sha']==receipt['commit']
assert next(e for e in root['tree']if e['path']=='rogueitem')['sha']==tree['sha']
game=read('research/p3-future-region-effects-300/game-topic-complete.json')
item=game['details']['rogue_6']['items']['rogue_6_scrap_G_12']
assert item['name']=='笼控器'and item['iconId']=='rogue_6_scrap_G_12'
entries=[e for e in tree['tree']if e['path']==item['iconId']+'.png']
assert len(entries)==1 and entries[0]['type']=='blob';entry=entries[0]
url='https://raw.githubusercontent.com/'+receipt['repository']+'/'+receipt['commit']+'/rogueitem/'+entry['path']
directory=HERE/'exact-scrap-icon-first';directory.mkdir(exist_ok=False)
report={'kind':'EXACT_PUBLIC_ICON_ACQUISITION_NOT_IMPLEMENTATION_OR_TEST',
 'at_utc':datetime.now(timezone.utc).isoformat(),'requested_url':url,'retries':0,
 'original_item_id':item['id'],'original_icon_id':item['iconId'],'complete_fixed_tree_entry':entry,
 'resource_commit':receipt['commit'],'raw_response_saved':False}
try:
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-source-research/1.0'}),timeout=30)as response:
  raw=response.read();report.update(status=response.status,response_url=response.url,response_headers=dict(response.headers.items()))
 (directory/entry['path']).write_bytes(raw);report['raw_response_saved']=True
 actual_blob=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 report.update(sha256=sha256(raw).hexdigest(),bytes=len(raw),actual_git_blob_sha1=actual_blob,
  git_blob_sha1_matches_exact_tree=actual_blob==entry['sha'],bytes_match_exact_tree=len(raw)==entry['size'],PNG_signature=raw[:8]==b'\x89PNG\r\n\x1a\n')
 assert report['git_blob_sha1_matches_exact_tree']and report['bytes_match_exact_tree']and report['PNG_signature']
 report['exit_code']=0
except BaseException as error:
 report.update(exit_code=1,error={'type':type(error).__name__,'message':str(error)})
(directory/'http-receipt.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(report['exit_code'])
