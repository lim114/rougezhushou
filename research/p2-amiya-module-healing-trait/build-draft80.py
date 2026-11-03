import hashlib,json,subprocess,shutil
from pathlib import Path

repo=Path('/workspace/rougezhushou')
out=Path('/workspace/.continuation/p2-amiya-trait-scale-080')
out.mkdir(exist_ok=True)
baseline='4b1e4d1f0bd9c60bc87523d6ac05c61f77f2a52b'
files=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline],cwd=repo,text=True).splitlines()
receipt={}
for name in files:
    p=Path(name)
    if p.parts[0] not in ('rouge','tests','scripts') or p.suffix not in ('.py','.json'):
        continue
    data=subprocess.check_output(['git','show',f'{baseline}:{name}'],cwd=repo)
    dest=out/'baseline'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    receipt[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
shutil.copytree(out/'baseline',out/'draft',dirs_exist_ok=True)
(out/'freeze-receipt.json').write_text(json.dumps({'baseline_commit':baseline,'files':receipt,'tracked_edits':False},indent=2)+'\n')
engine=out/'draft/rouge/operator_engine.py'
data=engine.read_bytes()
old=b"        elif op in ('char_002_amiya','char_1001_amiya2','char_1037_amiya3'):\r\n"
new=old+b"            if op=='char_1037_amiya3':\r\n"+b"                # The reviewed INC-X data-only bundle replaces this same trait ratio.\r\n"+b"                healing_scale=next(b['value'] for b in self.p['trait']['candidates'][0]['blackboard'] if b['key']=='scale')\r\n"+b"                if self.s.get('module_id')=='uniequip_002_amiya3':\r\n"+b"                    for part in self.module_parts:\r\n"+b"                        if (part.get('target')=='TRAIT_DATA_ONLY' and not part.get('isToken') and\r\n"+b"                                part.get('validInGameTag') is None and part.get('validInMapTag') is None):\r\n"+b"                            candidate=part['overrideTraitDataBundle']['candidates'][0]\r\n"+b"                            healing_scale=next(b['value'] for b in candidate['blackboard'] if b['key']=='scale')\r\n"
assert data.count(old)==1
data=data.replace(old,new)
old=b"damage_healing('\xe5\x92\x92\xe6\x84\x88\xe5\xb8\x88\xe4\xbc\xa4\xe5\xae\xb3\xe8\xbd\xac\xe6\xb2\xbb\xe7\x96\x97',.5*min(1,healing_targets))"
assert data.count(old)==3
data=data.replace(old,old.replace(b',.5*',b',healing_scale*'))
old=b"'opening_healing_reference':components[0]['total']*.5*min(1,healing_targets),"
assert data.count(old)==1
data=data.replace(old,old.replace(b'*.5*',b'*healing_scale*'))
assert data.count(b'\n')==data.count(b'\r\n')
engine.write_bytes(data)
print(json.dumps({'baseline_commit':baseline,'public_source_files':len(receipt),'draft_engine_sha256':hashlib.sha256(data).hexdigest()}))
