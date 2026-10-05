"""Reconcile old public examples against the evidence-backed native changes."""
import copy,hashlib,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prior_mechanism_wording(value):
    """Reverse exact display-only changes, without discarding any fields."""
    if isinstance(value,dict):return {k:prior_mechanism_wording(v) for k,v in value.items()}
    if isinstance(value,list):
        values=[prior_mechanism_wording(v) for v in value]
        first='原始模板确认首跳等待1秒，效果在神经爆发结束时清理；本轮逐跳局外参考尚未接入，未生成跳数或完整总量。'
        second='现有六个模板没有元素冷却加速动作；凋亡、灼燃和侵蚀路径仍待接入。'
        for i in range(len(values)-1):
            if values[i:i+2]==[first,second]:
                values[i:i+2]=['持续伤害的首跳、结束边界与冷却加速联动未核验，未生成跳数或完整总量；其他元素路径仍待接入。']
                break
        return values
    if isinstance(value,str):
        for current,prior in (
            ('神经额外持续伤害的逐跳局外参考待接入','神经冷却期额外持续伤害的首跳、结束边界与冷却加速联动待核验'),
            ('凋亡增强及爆条期间减攻的局外参考待接入','global_buff_normal:rogue_6_enemy_ep_break_fix[dark]'),
            ('灼燃增强及爆条期间减法抗的局外参考待接入','global_buff_normal:rogue_6_enemy_ep_break_fix[fire]'),
            ('侵蚀十次物理伤害与独立持续减防的局外参考待接入','global_buff_normal:rogue_6_enemy_ep_break_fix[water]')):
            value=value.replace(current,prior)
    return value


def main():
    start=time.perf_counter()
    baseline=ROOT/'.cache/p1-050/before-default-results.json'
    rows=json.loads(baseline.read_text(encoding='utf-8'))
    assert len(rows)==732
    allowed={'rogue_6_relic_fight_25','rogue_6_relic_legacy_95',
             'rogue_6_relic_legacy_96','rogue_6_relic_legacy_97','rogue_6_start_4'}
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'rouge').glob('*.py')}
    sources.update({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'rouge/data').glob('*.json')})
    changed=[];unexpected=[]
    for row in rows:
        actual=calculate_damage(row['scenario'])
        if actual==row['result']:continue
        entry={'scenario':row['scenario'],
            'changed_top_level_keys':sorted(k for k in set(actual)|set(row['result'])
                                          if actual.get(k)!=row['result'].get(k))}
        changed.append(entry)
        if set(row['scenario'].get('relic_ids',[]))&allowed:
            entry['change_scope']='Native fee/clock correction and its report/evidence.'
            continue
        if ('rogue_6_relic_fight_22' in row['scenario'].get('relic_ids',[])
                and prior_mechanism_wording(actual)==row['result']):
            entry['change_scope']='Exact display-only river mechanism wording; every numeric and other field unchanged.'
            continue
        # Ready attack-triggered skills still wait for their next attack in
        # the continuous reference schedule. Bound this exception to exactly
        # two old cases and two fields; do not waive other numeric changes.
        ready_cases={
            ('char_1042_phatm2',1,'continuous'):1.6,
            ('char_4087_ines',1,'continuous'):1.0}
        scenario=row['scenario']
        expected=ready_cases.get((scenario['operator'],scenario['skill'],scenario['timing_mode']))
        restored=copy.deepcopy(actual)
        if (expected is not None and len(scenario)==3
                and actual['estimate']['skill']['initial_seconds']==expected
                and row['result']['estimate']['skill']['initial_seconds']==0):
            restored['estimate']['skill']['initial_seconds']=0.0
            metrics=restored['report']['sections'][0]['metrics']
            if metrics[0]['key']=='initial' and metrics[0]['value']==expected:
                metrics[0]['value']=0.0
        if restored==row['result']:
            entry['change_scope']='Ready next-attack skill: initial wait and its report value only.'
        else:unexpected.append(entry)
    drift=[n for n,h in sources.items() if sha(ROOT/n)!=h]
    receipt={'version':'0.55.0','passed':not unexpected and not drift,
        'baseline':baseline.relative_to(ROOT).as_posix(),'baseline_sha256':sha(baseline),
        'replays':len(rows),'exact_unchanged':len(rows)-len(changed),'changed_count':len(changed),
        'changed':changed,'unexpected_changed_cases':unexpected,'source_sha256':sources,
        'source_drift_during_replay':drift,'allowed_native_change_relic_ids':sorted(allowed),
        'comparison_scope':'Exact full structured output comparison; native deployment fees and wine clocks intentionally update these cases.',
        'elapsed_seconds':time.perf_counter()-start}
    directory=ROOT/'.cache/core-055';directory.mkdir(exist_ok=True)
    path=directory/(str(time.time_ns())+'-public-replay.json')
    path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','replays','exact_unchanged','changed_count','unexpected_changed_cases','source_drift_during_replay','elapsed_seconds')}))
    print(json.dumps({'receipt':path.relative_to(ROOT).as_posix()}))
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
