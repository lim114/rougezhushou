"""Two exact static call targets; candidates require CFG validation."""
from pathlib import Path
reader=Path(__file__).resolve().parent/'read_calls.py'
code=reader.read_text(encoding='utf-8').replace("targets={0x180ac6c40:'UnitDataFlowConfig.Init',0x180ac6990:'UnitDataFlowConfig.GetDelta'}", "targets={0x180e7ae90:'AbstractBasicAttack.ApplyElementDamageScale',0x18102e150:'ApplyElementDamage.set_epDamageScale'}").replace("'dataflow-call-candidates.json'", "'scale-call-candidates.json'")
exec(compile(code,str(reader),'exec'))
