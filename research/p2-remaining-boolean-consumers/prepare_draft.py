"""Freeze current root Git objects and make an external product draft."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path('/workspace/rougezhushou')
OUT=Path(__file__).resolve().parent
BASE='9ef5a469673502754db3be320a8eece9a7fd18d4'


def sha(data):return hashlib.sha256(data).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def replace(path,old,new):
    data=path.read_bytes();old=old.replace('\n','\r\n').encode();new=new.replace('\n','\r\n').encode()
    assert data.count(old)==1,(path,old)
    path.write_bytes(data.replace(old,new))


def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    assert git('branch','--show-current').decode().strip()=='codex/p2-development'
    assert not git('status','--porcelain')
    frozen=[]
    paths=git('ls-tree','-r','--name-only',BASE,'rouge','tests','scripts').decode().splitlines()
    for name in paths:
        if not name.endswith(('.py','.json')):continue
        data=git('show',BASE+':'+name)
        for folder in ('baseline','draft'):
            p=OUT/folder/name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(data)
        frozen.append({'path':name,'git_blob':git('rev-parse',BASE+':'+name).decode().strip(),'sha256':sha(data),'bytes':len(data)})
    assert len(frozen)==723
    save('current-baseline-freeze.json',{'base_commit':BASE,'branch':'codex/p2-development','files':frozen,
         'source_of_bytes':'Git fixed objects, not other agents working tree','old_source_probes_reexecuted':False})
    engine=OUT/'draft/rouge/operator_engine.py'
    replace(engine,'    def calculate(self):\n',
                    '    def calculate(self):\n        self.ranged_attack_condition_consumed=False\n')
    old="""        normal=self.plan(normal=True,window=recharge) if cycle is not None and not (
            sp['sp_type']=='INCREASE_WHEN_ATTACK' and not self.s.get('continuous_attacks',True)) else None
"""
    new=old+"""        if self.s['operator']=='char_4182_oblvns':
            ranged_overridden=self.s.get('module_id') and self.tv.get('颂乐音符',{}).get('max_cnt',10)>10
            self.ranged_attack_condition_consumed=not ranged_overridden or normal is not None
"""
    replace(engine,old,new)
    damage=OUT/'draft/rouge/damage.py'
    replace(damage,'        from .operator_engine import calculate_extended\n        result=calculate_extended(scenario,attributes)\n',
                   '        from .operator_engine import Combat\n        combat=Combat(scenario,attributes)\n        result=combat.calculate()\n')
    old="""            raise ValueError('near_previous_deployment 不接受文本条件；请使用布尔值。')
    return result
"""
    new="""            raise ValueError('near_previous_deployment 不接受文本条件；请使用布尔值。')
    # Keep legacy calculation/finisher/report errors before text-only conditions.
    op=scenario['operator'];number=scenario['skill']
    conditions={
        'char_4228_closur':('reinforcement_blocks_target',),
        'char_206_gnosis':('frozen_at_skill_end',) if number==3 else (),
        'char_4087_ines':('ines_first_deployment',) if number==3 else (),
        'char_1041_angel2':('steal_success',) if number==2 else ('delivery_coordinate',) if number==3 else (),
        'char_1035_wisdel':('overload',) if number==2 else (),
    }.get(op,())
    if op=='char_4182_oblvns':
        conditions=(('ranged_attack',) if combat.ranged_attack_condition_consumed else ())
        if number==2:conditions+=('organ_mode','fever')
    if op in ('char_437_mizuki','char_1048_orchd2'):
        field,talent=('enemy_below_half','反移情') if op=='char_437_mizuki' else ('power_coating','强击瓶专家')
        if isinstance(scenario.get(field),str):
            from .operator_engine import selected_talents
            talents,_=selected_talents(catalog()['operators'][op],scenario)
            if any(t.get('name')==talent for t in talents):conditions+=(field,)
        if op=='char_1048_orchd2' and number==1:conditions+=('double_charge',)
    for field in conditions:
        if isinstance(scenario.get(field),str):
            raise ValueError(field+' 不接受文本条件；请使用布尔值。')
    return result
"""
    replace(damage,old,new)
    changes=[]
    for name in ('rouge/operator_engine.py','rouge/damage.py'):
        data=(OUT/'draft'/name).read_bytes();assert b'\r\n' in data and b'\n' not in data.replace(b'\r\n',b'')
        changes.append({'path':name,'baseline_sha256':sha((OUT/'baseline'/name).read_bytes()),'draft_sha256':sha(data),'CRLF':True})
    save('draft-product-receipt.json',{'passed':True,'base_commit':BASE,'changes':changes,
         'ranged_signal':'per-calculation Combat attribute reset False; same actual skill override or executed normal plan; no scenario or public fields',
         'old_source_36_probe_calls_repeated':0,'source_240_ranks_or_12_module_binding_audit_repeated':False,
         'new_native_mechanism':False,'tracked_edits':0})
    print(json.dumps({'passed':True,'frozen_files':len(frozen),'changed_product_files':len(changes)}))


if __name__=='__main__':main()
