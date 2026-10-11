"""Extract original selector fields, checking the existing pinned source hash."""
import hashlib
import argparse
import json
import urllib.request
from pathlib import Path

root=Path(__file__).resolve().parents[2]
data=json.loads((root/'rouge/data/supplemental-skills.json').read_text(encoding='utf-8'))
source=data['source']['files']['character_table']
parser=argparse.ArgumentParser(__doc__)
parser.add_argument('--source',type=Path,help='Existing original JSON; otherwise download pinned URL')
args=parser.parse_args()
raw=args.source.read_bytes() if args.source else urllib.request.urlopen(source['url'],timeout=60).read()
if hashlib.sha256(raw).hexdigest()!=source['sha256']:
    raise ValueError('Pinned character_table SHA256 mismatch')
characters=json.loads(raw)
result={'source':source,'commit':data['source']['commit'],'operators':{
    identity:{'profession':characters[identity]['profession'].lower(),
              'position':characters[identity]['position'].lower(),
              'subprofession_id':characters[identity]['subProfessionId']}
    for identity in data['operators']}}
output=root/'rouge/data/supplemental-run-selectors.json'
with output.open('x',encoding='utf-8',newline='\n') as f:
    f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Verified pinned source; extracted selectors for',len(result['operators']),'operators.')
