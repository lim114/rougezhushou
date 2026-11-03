from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return sha256(raw).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='c2b78e4aa4136fe739067b5ccf9d13b595142320'
path=ROOT/'verification/sections/303-preparation/backend-promotion.json';record=json.loads(path.read_bytes())
assert record['section']==303 and record['native_canonical_promoted'] is False
for group in ('promoted','existing_production_changes','historical_test_maintenance'):
    for name,value in record[group].items():assert sha((ROOT/name).read_bytes())==value,name
ready_path=ROOT/'.cache/p3-303-native-window/READY.json';raw=ready_path.read_bytes()
assert sha(raw)=='5f7efd45d47bea9d8fba086a38d7377b0869fbfd665b4f2761898b231bd2a049'
ready=json.loads(raw);canonical=ready['canonical']
assert canonical=='scripts/verify_direct_map_window_303.py' and not (ROOT/canonical).exists()
source=ROOT/'.cache/p3-303-native-window'/Path(canonical).name;body=source.read_bytes();pin=ready['pins'][source.name]
assert sha(body)==pin['sha256']=='06a2856aec1bc7e6d927b8a480022620749e0d0983862780c1220c752e5d8d63' and len(body)==pin['bytes'];ast.parse(body)
expected={**record['promoted'],**record['existing_production_changes'],canonical:sha(body)}
assert expected=={name:pin['sha256'] for name,pin in ready['functional_promotion_source_files'].items()}
record['promoted'][canonical]=sha(body)
record.update(kind='root_reviewed_final_functional_and_exact_test_maintenance_promotion_before_formal_verification',
    at_utc=datetime.now(timezone.utc).isoformat(),native_canonical_promoted=True,
    native_ready='.cache/p3-303-native-window/READY.json',native_ready_sha256=sha(raw),
    historical_test_maintenance_proofs={})
for stem in ('historical294','historical048'):
    source=ROOT/f'.cache/p3-303-parent/{stem}-candidate.json';proof=source.read_bytes()
    dest=ROOT/f'verification/sections/303-preparation/historical-tests/{stem}-candidate.json';assert not dest.exists();dest.write_bytes(proof)
    record['historical_test_maintenance_proofs'][dest.relative_to(ROOT).as_posix()]=sha(proof)
assert len(record['promoted'])==16 and len(record['existing_production_changes'])==1 and len(record['historical_test_maintenance'])==2
final=ROOT/'verification/sections/303-preparation/promotion.json';assert not final.exists()
with (ROOT/canonical).open('xb') as stream:stream.write(body)
final.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'functional_sources':17,'new_paths':16,'existing_production_changes':1,'historical_test_maintenance':2,'validated_source_scope':19,'formal_verification_claimed':False}))
