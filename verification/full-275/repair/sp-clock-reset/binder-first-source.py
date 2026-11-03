from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
path=ROOT/'rouge/data/sp-setter-source.json';data=json.loads(path.read_bytes())
old=data['source_artifacts_sha256']['rouge/sp_recovery_clock.py'];assert old=='ba8a086ad81784b5f94fbe16e16472b5d4d3768d24f2e8ccaa75a9868bb7cc5a'
data['source_artifacts_sha256']['rouge/sp_recovery_clock.py']=sha('rouge/sp_recovery_clock.py')
path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
new=sha('rouge/data/sp-setter-source.json');core=ROOT/'rouge/sp_setter_reference.py';raw=core.read_bytes()
assert b"SOURCE_SHA256='ccae8380f1c3eefb3f5997c5d0cb8f6e7a5b860f64aa444b157f50b0871523f3'" in raw
core.write_bytes(raw.replace(b"SOURCE_SHA256='ccae8380f1c3eefb3f5997c5d0cb8f6e7a5b860f64aa444b157f50b0871523f3'",("SOURCE_SHA256='"+new+"'").encode('ascii')))
from rouge.sp_recovery_clock import sp_recovery_clock_reference,source_data
from rouge.sp_setter_reference import source_data as setter_source
assert source_data() and setter_source()
proof=ROOT/'verification/full-275/repair/sp-clock-reset/original-source-bound-counterexamples.json'
record=json.loads(proof.read_bytes())
for row in record['cases']:
 row['after_same_input']=sp_recovery_clock_reference(row['payload'])
 assert row['after_same_input']['final_period_raw_reference']==row['expected_source_P_R']['period_raw']
 assert row['after_same_input']['final_remaining_raw_reference']==row['expected_source_P_R']['remaining_raw']
record.update(root_same_input_repair_verified=True,core_before_sha256=old,
 core_after_sha256=sha('rouge/sp_recovery_clock.py'),setter_manifest_after_sha256=new,
 source_binding='Original274 source-proof already includes25973 Periodic.Reset and220529 TSMath.Max; fresh source-only comparison by the preparation agent, not game execution.',
 keep_past_and_mark_invalid_not_rewritten=True)
out=ROOT/'verification/full-275/repair/sp-clock-reset/same-input-repair.json';out.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'same_original_cases_verified':len(record['cases']),'clock_core_sha256':sha('rouge/sp_recovery_clock.py'),'setter_manifest_sha256':new,'setter_core_sha256':sha('rouge/sp_setter_reference.py')}))
