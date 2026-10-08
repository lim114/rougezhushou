from pathlib import Path
import hashlib,json,subprocess

OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
REV='1ce970fd30aa3b42d8ef787cde02513f05682b66'
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',REV,'rouge'],cwd=REPO,text=True).splitlines()
rows=[]
for name in paths:
    if not name.endswith(('.py','.json')):continue
    data=subprocess.check_output(['git','show',REV+':'+name],cwd=REPO)
    for folder in ('baseline','draft'):
        p=OUT/folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    rows.append({'path':name,'bytes':len(data),'sha256':sha(data),'blob':subprocess.check_output(['git','rev-parse',REV+':'+name],cwd=REPO,text=True).strip()})

leaf='''"""Defer text-only condition errors until an isolated core has finished."""
from contextvars import ContextVar
from functools import wraps


_pending = ContextVar('continuous_attacks_text_pending', default=None)


def observe_continuous_attacks(value, *, active=True):
    if isinstance(value, str) and _pending.get() is not None:
        if active() if callable(active) else active:
            _pending.set(True)
    return value


def read_continuous_attacks(scenario, *, active=True):
    return observe_continuous_attacks(scenario.get('continuous_attacks', True), active=active)


def validate_continuous_attacks(compute):
    @wraps(compute)
    def isolated(*args, **kwargs):
        token = _pending.set(False)
        try:
            result = compute(*args, **kwargs)
            if _pending.get():
                raise ValueError('continuous_attacks 不接受文本条件；请使用布尔值。')
            return result
        finally:
            _pending.reset(token)
    return isolated
'''
(OUT/'draft/rouge/condition_inputs.py').write_text(leaf)
changes={}
def change(name, edits):
    data=(OUT/'baseline'/name).read_bytes();original=data
    for before,after,count in edits:
        assert data.count(before)==count,(name,before,data.count(before),count)
        data=data.replace(before,after)
    (OUT/'draft'/name).write_bytes(data)
    restored=data
    for before,after,count in reversed(edits):
        assert restored.count(after)==count,(name,after)
        restored=restored.replace(after,before)
    assert restored==original
    changes[name]={'baseline_sha256':sha(original),'draft_sha256':sha(data),'inverse_sha256':sha(restored),'inverse_exact':True,'replacement_groups':len(edits),'edits':[{'before_hex':a.hex(),'after_hex':b.hex(),'count':c} for a,b,c in edits]}
getself=b"self.s.get('continuous_attacks',True)";readself=b'read_continuous_attacks(self.s)'
getscenario=b"scenario.get('continuous_attacks',True)";readscenario=b'read_continuous_attacks(scenario)'
importread=b'from .condition_inputs import read_continuous_attacks\r\n'
change('rouge/operator_engine.py',[
    (b'import math\r\n',b'import math\r\n'+importread,1),
    (b"elif "+getself+b" and any(r['kind']=='attack_sp' for r in self.s.get('_relic_rules',[])):",b"elif read_continuous_attacks(self.s,active=lambda:any(r['kind']=='attack_sp' for r in self.s.get('_relic_rules',[]))) and any(r['kind']=='attack_sp' for r in self.s.get('_relic_rules',[])):",1),
    (getself,readself,5),
])
change('rouge/estimate.py',[(b'import math\r\n',b'import math\r\n'+importread,1),(getscenario,readscenario,3)])
change('rouge/timing.py',[(b'import math\r\n',b'import math\r\n'+importread,1),
    (getscenario,b"read_continuous_attacks(scenario,active=lambda:increment+sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='attack_sp')>0)",1)])
change('rouge/sp_events.py',[(b'import math\r\n',b'import math\r\nfrom .condition_inputs import read_continuous_attacks, observe_continuous_attacks\r\n',1),
    (b"scenario.get('continuous_attacks', True)",b'read_continuous_attacks(scenario, active=native_attack > 0)',1),
    (b'ready = next((t for t in starts if t >= ready - 1e-9), None) if attacks else None',
     b'ready = next((t for t in starts if t >= ready - 1e-9), None) if observe_continuous_attacks(attacks) else None',1)])
change('rouge/amiya_continuous_reference.py',[(b'from copy import deepcopy\n',b'from copy import deepcopy\nfrom .condition_inputs import read_continuous_attacks\n',1),
    (b"scenario.get('continuous_attacks', True)",b'read_continuous_attacks(scenario)',1)])
change('rouge/damage.py',[(b'import math\r\n',b'import math\r\nfrom .condition_inputs import validate_continuous_attacks\r\n',1),
    (b'def _evaluate_damage_once(prepared,wine_phase=None) -> dict:',b'@validate_continuous_attacks\r\ndef _evaluate_damage_once(prepared,wine_phase=None) -> dict:',1)])
save('fixed-source-index088.json',{'baseline_commit':REV,'scope':'All tracked rouge/*.py and rouge/**/*.json, no research/history/cache copies.','files':rows,'file_count':len(rows),'bytes':sum(r['bytes'] for r in rows)})
save('surgical-byte-inverse088.json',{'status':'PASS_STATIC_BYTE_INVERSE','changes':changes,'source_read_replacements':12,'new_leaf_sha256':sha(leaf.encode()),'new_project_calls':0,'tracked_mutations':0})
print(json.dumps({'status':'BUILT_EXTERNAL_DRAFT_ZERO_PROJECT_CALLS','fixed_files':len(rows),'changed':list(changes),'new_leaf_sha256':sha(leaf.encode())}))
