"""Inactive bounded full110 Window Source draft; Root final109 guard binding pending."""
import argparse, functools, hashlib, json, os, sys, threading, time
from pathlib import Path

_parser100 = argparse.ArgumentParser()
_parser100.add_argument('--root', required=True)
_parser100.add_argument('--guard', required=True)
_parser100.add_argument('--out', required=True)
_args100 = _parser100.parse_args()
ROOT = Path(_args100.root).resolve()
OUT = Path(_args100.out).resolve()
if OUT == ROOT or OUT.is_relative_to(ROOT):
    raise ValueError('The fresh evidence directory must be outside the repository')
# Draft deliberately refuses execution before Root final109 Source binding.
_SOURCE110_GUARD_SHA256 = 'ac629aec8d42caefa2ff53497bd34929d45c1fd4d72b75e1c06a5b8ee19a6b4b'
_SOURCE110_MAINTAINED_COUNT = 753
if _SOURCE110_GUARD_SHA256 is None or _SOURCE110_MAINTAINED_COUNT is None:
    raise ValueError('Inactive full110 Source draft: actual completed109/final110 guard not bound')
_guard_bytes100 = Path(_args100.guard).read_bytes()
if hashlib.sha256(_guard_bytes100).hexdigest() != _SOURCE110_GUARD_SHA256:
    raise ValueError('Exact Root final109/final110 public Source guard bytes required')
_guard100 = json.loads(_guard_bytes100)
_expected100 = _guard100['source_sha256']
_additional100 = _guard100['source_additional_sha256']
if not isinstance(_expected100, dict) or len(_expected100)!=_SOURCE110_MAINTAINED_COUNT:
    raise ValueError('Exact actual completed109/final110 maintained Source count is required')
if not isinstance(_additional100, dict) or 'CORE_0.70_VERIFICATION.json' not in _additional100:
    raise ValueError('Completed109/final110 additional Source map must include CORE registration')

def maintained_source100():
    result = {}
    for name in ('rouge', 'tests', 'scripts'):
        folder = ROOT / name
        if not folder.is_dir():
            raise ValueError('Missing maintained Source folder: ' + name)
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(ROOT)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            if path.is_symlink():
                raise ValueError('Source symlink refused: ' + str(relative))
            if path.is_file():
                result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))

def additional_source100():
    result = {}
    for relative in _additional100:
        path = ROOT / relative
        if (not isinstance(relative, str) or Path(relative).is_absolute()
                or '..' in Path(relative).parts or path.is_symlink()
                or not path.resolve().is_relative_to(ROOT)):
            raise ValueError('Invalid supplemental Source path: ' + str(relative))
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))

if maintained_source100() != _expected100:
    raise AssertionError('Completed109/final110 maintained Source drift before project imports')
if additional_source100() != _additional100:
    raise AssertionError('Completed109/final110 supplemental Source drift before project imports')
OUT.mkdir(parents=True, exist_ok=False)
(OUT / 'source100-guard-input.json').write_bytes(_guard_bytes100)
_started100 = time.perf_counter()
_deadline100 = _started100 + 1200
_restorations100 = []
_count_enabled100 = False

def _deadline_check100():
    if time.perf_counter() >= _deadline100:
        raise TimeoutError('Fresh full110 attempt1 deadline of1200 seconds reached')

def _hard_timeout100():
    record = {'passed': False, 'scope': 'actual full110 attempt1 hard deadline', 'after_section': 110,
              'attempt': 1, 'deadline_seconds': 1200, 'elapsed_seconds': time.perf_counter()-_started100,
              'guard_sha256': hashlib.sha256(_guard_bytes100).hexdigest(),
              'full_function_vector_measured': False}
    try:
        (OUT / 'hard-timeout-100.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
        print(json.dumps({'passed': False, 'attempt': 1, 'hard_deadline': 1200}), flush=True)
    finally:
        os._exit(124)

_timer100 = threading.Timer(1200, _hard_timeout100)
_timer100.daemon = True
_timer100.start()

def _write_progress105(count, last_check):
    # Only completed append count and public scalar labels; never dump checks,
    # window, caller, state, function vectors or repeat a full Source hash scan.
    record = {'kind': 'FULL110_ATTEMPT1_APPENDED_CHECK_PROGRESS',
              'after_section': 110, 'attempt': 1, 'passed': False,
              'workflow_complete': False, 'appended_checks': count,
              'last_check': last_check,
              'elapsed_seconds': round(time.perf_counter()-_started100, 3),
              'checkpoint_every_appended_checks': 32,
              'complete_function_vector_measured': False}
    temporary = OUT / 'full110-progress.json.tmp'
    with temporary.open('w', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, OUT / 'full110-progress.json')


class _ProgressChecks105(list):
    def __init__(self):
        super().__init__()
        _write_progress105(0, {})

    def append(self, item):
        # Real list.append first. Its original None return is preserved; an
        # observer IO error propagates to the unchanged outer failure handler.
        super().append(item)
        count = len(self)
        if count % 32 == 0:
            labels = {}
            if type(item) is dict:
                for key in ('scope', 'section', 'operator', 'skill', 'pair_id'):
                    value = item.get(key)
                    if key in item and (value is None or type(value) in (str, int, bool)):
                        labels[key] = value
            _write_progress105(count, labels)


def _replace_binding100(owner, name, replacement):
    original = getattr(owner, name)
    _restorations100.append((owner, name, original))
    setattr(owner, name, replacement)

def _increment100(key):
    _deadline_check100()
    if _count_enabled100:
        entry_counts090[key] = entry_counts090.get(key, 0) + 1

def _install_narrow_observers100():
    # Every wrapper calls its actual original; no return, input, or state substitution.
    import rouge.damage as damage100
    import rouge.estimate as estimate100
    import rouge.reporting as reporting100
    import rouge.run_state as run100
    import rouge.operator_engine as engine100

    def instrument(owner, name, key):
        original = getattr(owner, name)
        @functools.wraps(original)
        def passthrough(*args, **kwargs):
            _increment100(key)
            return original(*args, **kwargs)
        _replace_binding100(owner, name, passthrough)

    instrument(damage100, 'calculate_damage', 'calculate_damage')
    instrument(estimate100, 'format_estimate', 'format_estimate')
    original_report100 = reporting100.format_report
    @functools.wraps(original_report100)
    def report100(result, *, technical=False):
        _increment100('format_report_technical' if technical else 'format_report_default')
        return original_report100(result, technical=technical)
    _replace_binding100(reporting100, 'format_report', report100)
    for name in ('__init__', 'apply', 'load'):
        if hasattr(run100.RunState, name):
            instrument(run100.RunState, name, 'RunState.' + name)

    original_plan100 = engine100.Combat.plan
    @functools.wraps(original_plan100)
    def plan100(self, normal=False, window=None):
        _deadline_check100()
        selected = _count_enabled100 and profile_case090 is not None and normal is True
        if selected:
            profile_trace090.append({'event':'actual_same_call_normal_plan_entry','normal':True})
        returned = original_plan100(self, normal=normal, window=window)
        if selected:
            profile_trace090.append({'event':'actual_same_call_normal_plan_return',
                                     'returned_not_none': returned is not None})
        return returned
    _replace_binding100(engine100.Combat, 'plan', plan100)
    original_calculate100 = engine100.Combat.calculate
    @functools.wraps(original_calculate100)
    def calculate100(self):
        _deadline_check100()
        returned = original_calculate100(self)
        if (_count_enabled100 and profile_case090 is not None
                and self.s['operator']=='char_4182_oblvns'
                and profile_case090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal'):
            actual_plan_returns = [row for row in profile_trace090
                                  if row['event']=='actual_same_call_normal_plan_return']
            profile_trace090.append({'event':'actual_same_call_Combat_calculate_return',
                'normal_plan_return_not_none': len(actual_plan_returns)==1
                    and actual_plan_returns[0]['returned_not_none'] is True,
                'actual_ranged_condition_consumed':self.ranged_attack_condition_consumed,
                'actual_selected_note_max_cnt':self.tv['颂乐音符']['max_cnt']})
        return returned
    _replace_binding100(engine100.Combat, 'calculate', calculate100)

"""Real Windows Qt widgets under Wine; isolated state; no capture/chat operations."""
import hashlib, importlib, importlib.metadata, json, os, platform, subprocess, sys, tempfile, time, traceback
from pathlib import Path
sys.path.insert(0,str(ROOT))
"""Existing public contracts for future Qt checks; no Qt or game inference."""
import json
def require_wisdel(result,args,text,scope):
    ghosts=args['ghost_count'];casts=args['ghost_casts'] if ghosts else 0
    ref=result['wisdel_secondary_reference']
    assert type(ref['ghost_casts_requested']) is int and ref['ghost_casts_requested']==casts
    for field in ('ghost_cast_times_seconds','secondary_hit_times_seconds','explosion_expected_count'):
        assert ref[field] is None,field
    for field in ('ghost_full_cast_attribution_verified','shadow_lifecycle_verified','random_independence_verified','s1_binding_verified'):
        assert ref[field] is False,field
    if casts:
        assert ref['ghost_per_cast_damage_reference'] is not None
        assert abs(ref['ghost_declared_count_damage_reference']-casts*ref['ghost_per_cast_damage_reference'])<1e-7
        ghost=next(c for c in result['components'] if c['name']=='魂灵之影施放')
        assert ghost['hits']==0 and 'times_seconds' not in ghost
        assert '指定魂灵之影施放次数参考' in text
        assert '魂灵之影施放时刻：未知' in text
    else:
        assert ref['ghost_declared_count_damage_reference']==0
        assert '指定魂灵之影施放次数参考' not in text
    assert '好礼与余震 · 次生事件待核验' in text
    if scope in ('zero_window','zero_lifetime'):assert result['total_damage']==0

def require_incoming(result,args,text,scope,qualified=True,immune=False):
    count=args['enemy_attack_count']
    active=bool(count and qualified and not immune and scope!='zero_lifetime')
    if active:
        ref=result['neural_incoming_reference']
        assert type(ref['attacks_requested']) is int and ref['attacks_requested']==count
        assert ref['buildup_per_attack']==70
        assert ref['attack_times_seconds'] is None and ref['events_scheduled'] is False
        assert '堕梦 · 目标攻击时间待确认' in text
        assert '目标首个普通攻击时刻：未知' in text
        if scope=='zero_window':
            assert ref['affected_damage_phases']['cast'] is True
            assert ref['affected_damage_phases']['window'] is False
        else:
            assert result['total_damage'] is None
            assert result['estimate']['skill']['window_dps'] is None
    else:
        assert 'neural_incoming_reference' not in result
        assert '堕梦 · 目标攻击时间待确认' not in text
    if scope in ('zero_window','zero_lifetime'):assert result['total_damage']==0

def require_shu_periodic(result,text):
    ref=result['shu_periodic_sp_reference'];skill=result['estimate']['skill']
    assert ref['interval_seconds_parameter']==4 and ref['sp_per_pulse_parameter']==1
    for field in ('first_tick_seconds','actual_tick_times_seconds','clock_origin','reset_rule','blocked_credit_rule'):
        assert ref[field] is None,field
    for field in ('clock_verified','events_scheduled','native_attachment_verified'):
        assert ref[field] is False,field
    assert skill['sp_recovery_per_second']==1
    for field in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
        assert skill[field] is None,field
    assert '天有四时 · 周期技力待核验' in text

def require_professions(result,args,text,plain,qualified):
    if not qualified:
        assert json.dumps(result,sort_keys=True,allow_nan=False)==json.dumps(plain,sort_keys=True,allow_nan=False)
        assert 'shu_periodic_sp_reference' not in result
        return
    stats=result['estimate']['base_stats'];base=plain['estimate']['base_stats']
    hp_factor=1.12 if args['three_professions'] else 1
    speed_bonus=12 if args['three_same_profession'] else 0
    assert abs(stats['hp']-base['hp']*hp_factor)<1e-7
    assert stats['attack_speed_reference']==base['attack_speed_reference']+speed_bonus
    assert stats['attack']==base['attack']
    if args['four_sui']:require_shu_periodic(result,text)
    else:assert 'shu_periodic_sp_reference' not in result

def require_cooperative(result,args,text,plain,scope):
    names=['本体丹增','协同丹增'] if args['cooperative'] else ['本体丹增']
    assert [c['name'] for c in result['components']]==names
    assert all(c['damage_type']=='physical' for c in result['components'])
    if args['cooperative']:
        assert abs(result['total_damage']-plain['total_damage']*2)<1e-7
        first,second=result['components']
        assert first['hits']==second['hits'] and first['per_hit']==second['per_hit']
        assert first['per_hit']==plain['components'][0]['per_hit']
    if scope in ('zero_window','zero_lifetime'):assert result['total_damage']==0

def require_sown(result,args,text,plain,scope,bb):
    if args['enemy_on_sown_tile']:
        assert result['attack']>plain['attack']
        assert result['attack_speed_reference']==plain['attack_speed_reference']+bb['e_attack_speed']
        assert result['estimate']['base_stats']==plain['estimate']['base_stats']
    if args['four_sui']:require_shu_periodic(result,text)
    else:assert 'shu_periodic_sp_reference' not in result
    if scope=='zero_window':
        assert result['total_damage']==0 and result['total_healing']==0
    elif scope=='zero_lifetime':
        assert result['total_damage']==0 and result['total_healing']>0


"""Shared public-output assertions; API use does not prove actual Qt execution."""
import json

def canonical075(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def require_squad075(result,args,text,record):
    resolution=result['run_resolution']
    assert resolution['squad']['id']==record['id']
    assert resolution['squad']['effect_verified'] is args['run_config']['squad']['effect_verified']
    section_ids=[s['id'] for s in result['report']['sections']]
    if record['bandLevel']!=1:
        assert 'squad_unlock_reference' not in resolution
        assert 'squad_unlock_reference' not in section_ids
        return
    ref=resolution['squad_unlock_reference']
    assert ref['squad_id']==record['id'] and ref['base_squad_id']==record['normalBandId']
    assert ref['variant_level_parameter']==1
    assert ref['unlock_condition_reference']==record['unlockCondDesc']
    assert ref['account_unlocked'] is None and ref['actual_activation'] is None
    assert ref['reference_only'] is True
    assert section_ids.count('squad_unlock_reference')==1
    assert '强化分队 · 条件资料' in text and record['unlockCondDesc'] in text
    assert '账户解锁状态：未知' in text and '解锁条件实际激活：未知' in text
    assert '不据此切换分队版本或追加效果' in text
    assert 'rogue_6_band_' not in text and 'commonDevelopment' not in text
    gates={'rogue_6_band_2':3,'rogue_6_band_5':6,'rogue_6_band_7':9}
    node=ref['technology_node_reference']
    if record['id'] in gates:
        assert node['gate_reference']['enable_grade_parameter']==gates[record['id']]
        assert node['gate_reference']['enable_description_reference'] in text
    elif record['id']=='rogue_6_band_22':
        assert node is None
    else:
        assert node['gate_reference'] is None
    if record['id']=='rogue_6_band_7':
        if args['run_config']['squad']['effect_verified']:
            assert len(resolution['applied'])==3
            assert all(r['value']==.15 for r in resolution['applied'])
        else:
            assert resolution['applied']==[]
            assert any('效果阶段尚未确认' in s for s in resolution['pending'])

def require_headwolf075(result,args,text,plain=None):
    assert args['operator']=='char_1038_whitw2'
    drones=[c for c in result['components'] if c['name']=='浮游单元']
    if args['skill'] in (1,2):
        assert bool(drones) is (args.get('window_seconds')!=0)
        assert all(c['timing_reference']=='owner_attack_clock; independent drone clock unverified' for c in drones)
        if args['elite']==0:
            assert args['skill']==1
            if plain is not None:
                assert canonical075(result)==canonical075(plain)
    if args['skill']==3:
        ref=result['drone_lifecycle_reference']
        for key in ('aura_first_tick_seconds','aura_tick_count','arrival_seconds','same_target_hit_counter'):
            assert ref[key] is None
    assert '独立' in text and ('未核验' in text or '未知' in text)

def require_mei075(result,args,text,qualified,stage):
    section_ids=[s['id'] for s in result['report']['sections']]
    if not qualified:
        assert 'mei_airborne_module_reference' not in result
        assert 'mei_airborne_module' not in section_ids
        return
    ref=result['mei_airborne_module_reference']
    assert ref['module_id']=='uniequip_002_mm' and ref['module_level']==stage
    assert ref['unlock_elite']==2 and ref['unlock_level']==40
    assert ref['attack_scale_parameter']==1.1
    assert ref['actual_target_is_airborne'] is None and ref['actual_conditional_damage'] is None
    assert ref['reference_only'] is True and ref['applied_to_numeric_estimate'] is False
    for key in ('native_attachment_verified','damage_composition_verified','live_state_verified'):
        assert ref[key] is False
    assert section_ids.count('mei_airborne_module')==1
    assert '梅 MAR-X · 空中条件参数参考' in text
    assert '当前目标空中条件：未知' in text and '该特性实际条件伤害：未知' in text
    assert '110%参数未计入当前伤害数值' in text

def require_wisdel_routes075(result,args,text):
    ref=result['wisdel_summon_qualification_reference']
    assert ref['operator_id']=='char_1035_wisdel'
    assert ref['token_id']=='token_10035_wisdel_wward'
    assert ref['current_cultivation']=={k:args[k] for k in ('elite','level','potential')}
    talent=ref['talent_route'];skill=ref['skill_route'];qualified=args['elite']==2
    assert talent['cultivation_qualified'] is qualified and skill['cultivation_qualified'] is qualified
    assert talent['unlock_elite']==skill['unlock_elite']==2
    assert talent['unlock_level']==skill['unlock_level']==1
    assert skill['currently_selected'] is (args['skill']==3)
    if args['skill']==3:
        assert skill['selected_level_source']['rank']==args['skill_rank']
    else:
        assert skill['selected_level_source'] is None
    assert ref['actual_source_provenance'] is None
    for key in ('actual_presence_verified','actual_cast_clock_verified','covers_all_routes','declared_counts_reinterpreted'):
        assert ref[key] is False
    assert '魂灵之影 · 本体召唤途径培养资料' in text
    status='已达原表培养门槛' if qualified else '未达原表培养门槛'
    assert status in text and '未确定其来源归属' in text
    assert '本资料不涵盖模组或藏品' in text
    source=result['wisdel_secondary_reference']
    count=args['ghost_casts'] if args['ghost_count'] else 0
    assert type(source['ghost_casts_requested']) is int and source['ghost_casts_requested']==count
    assert source['ghost_cast_times_seconds'] is None
    assert source['shadow_lifecycle_verified'] is False

def require_movement075(entry,text,technical,stage):
    move=entry['movement_reference']
    assert move['complete_effective_speed_verified'] is False
    assert '预计有效移速：未知' in text
    if stage['id']=='ro6_e_3_6':
        ref=move['stage_move_speed_rune_reference']
        assert ref['parameter']==1.5 and ref['source_selector']=='$.runes[0].blackboard[2]'
        assert ref['source']==stage['level_source']
        assert ref['source']['sha256']=='2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296'
        assert (ref['difficulty_mask_parameter'],ref['profession_mask_parameter'],ref['buildable_mask_parameter'])==('FOUR_STAR',1023,'ALL')
        assert ref['native_target_writer_layer_verified'] is False
        assert ref['combined_with_stage_multiplier_speed'] is None
        assert ref['complete_effective_speed_verified'] is False
        if technical:
            assert '关卡移速符文参数参考：1.5' in text
            assert '基础移速×关卡倍率小计：' in text
            assert '符文与关卡倍率合成的移速：未知' in text
            assert '原生目标、写入及叠加层尚未核验' in text
            assert ref['source']['url'] in text
        else:
            assert '关卡移速符文参数参考' not in text
            assert '基础移速×关卡倍率小计' not in text
    else:
        assert 'stage_move_speed_rune_reference' not in move
        assert '关卡移速符文参数参考' not in text
    if move['base_attribute'] is not None:
        assert move['base_times_stage_speed']==move['base_attribute']*stage['movement_multiplier']

"""Public design cases; list construction performs no API, GUI or state reads."""
def cases075(squads):
    rows=[]
    def add(section,owner,number,elite,level,rank,mode,**extra):
        args={'operator':owner,'skill':number,'elite':elite,'level':level,'skill_rank':rank,
              'potential':1,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':10,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
        args.update(extra);rows.append({'section':section,'input':args})
    modes=('frames','continuous')
    for record in squads.values():
        for mode in modes:
            for flag in (False,True):
                add(71,'silverash',3,2,90,10,mode,run_config={'squad':{
                    'id':record['id'],'name':record['name'],'level':record['bandLevel'],'effect_verified':flag}})
    for sid,gate in (('rogue_6_band_2',3),('rogue_6_band_5',6),('rogue_6_band_7',9)):
        record=squads[sid]
        for grade in (gate-1,gate):
            for mode in modes:
                add(71,'silverash',3,2,90,10,mode,run_config={'squad':{
                    'id':sid,'name':record['name'],'level':1,'effect_verified':True},
                    'difficulty':{'value':grade,'modeDifficulty':'NORMAL'}})
    record=squads['rogue_6_band_22']
    for elite,level,rank in ((0,50,4),(1,80,7),(2,90,10)):
        for mode in modes:
            add(71,'mechanist',1,elite,level,rank,mode,run_config={'squad':{
                'id':record['id'],'name':record['name'],'level':1,'effect_verified':True}})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,90,10,(1,2,3))):
        for potential in (1,6):
            interval={(1,1):30,(1,6):26,(2,1):20,(2,6):16}.get((elite,potential))
            # Existing option QDoubleSpinBox has two decimal places.
            ages=(0,59,60,120,3600) if interval is None else (0,interval-.01,interval,3*interval-.01,3*interval,3600)
            for number in numbers:
                for mode in modes:
                    for warmup in (0,100):
                        for age in ages:
                            add(72,'char_1038_whitw2',number,elite,level,rank,mode,potential=potential,
                                deployment_elapsed_seconds=age,drone_warmup_hits=warmup)
    for elite,level,rank in ((1,60,7),(2,39,7),(2,40,10)):
        for stage in (1,2,3):
            for number in (1,2):
                for mode in modes:
                    for horizon in (0,10):
                        add(73,'char_133_mm',number,elite,level,rank,mode,module_id='uniequip_002_mm',
                            module_level=stage,window_seconds=horizon)
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,1,1,(1,2,3)),(2,90,10,(1,2,3))):
        for stage in ((0,1,2,3) if elite==2 and level==90 else (0,)):
            for number in numbers:
                for mode in modes:
                    for ghosts,casts,horizon in ((0,0,10),(1,2,10),(3,0,0)):
                        add(74,'char_1035_wisdel',number,elite,level,rank,mode,
                            module_id='uniequip_002_wisdel' if stage else None,module_level=stage,
                            ghost_count=ghosts,ghost_casts=casts,window_seconds=horizon)
    return rows

def preview_cases075(stages):
    return [{'section':75,'stage_id':sid,'enemy_id':enemy['id'],'level':enemy['level'],'technical':technical}
        for sid in ('ro6_n_3_6','ro6_e_3_6') for enemy in stages[sid]['enemies'] for technical in (False,True)]


"""Public-output design only; assertions do not provide actual Qt proof."""
from copy import deepcopy
import json

HARUKA_LOCKED_NOTE080='当前培养尚未解锁扶摇花火；浮泡破碎声明保留，但不产生该天赋治疗或二技能中依赖该治疗的派生伤害。'

def canonical080(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def normalized_locked_haruka080(result):
    value=deepcopy(result)
    for ref in (value['external_event_reference'],value['external_event_reference']['window_reference']):
        ref['parameter_rows'][0]=('声明窗口内浮泡破碎次数',0.0,'次')
        ref['notes']=[n for n in ref['notes']if n!=HARUKA_LOCKED_NOTE080]
    for section in value['report']['sections']:
        if section['id']=='external_events':
            section['notes']=[n for n in section['notes']if n!=HARUKA_LOCKED_NOTE080]
            next(m for m in section['metrics']if m['key']=='parameter_0')['value']=0.0
    return value

def require_haruka080(result,args,text,plain):
    count=args['bubble_bursts'];qualified=args['elite']==2
    ref=result['external_event_reference']
    assert ref['kind']=='haruka_bubbles'
    assert ref['parameter_rows'][0]==('声明窗口内浮泡破碎次数',float(count),'次')
    assert ref['actual_event_times_seconds'] is None
    if not qualified:
        assert canonical080(normalized_locked_haruka080(result))==canonical080(plain)
        if count>0:assert HARUKA_LOCKED_NOTE080 in ref['notes'] and HARUKA_LOCKED_NOTE080 in text
        else:assert HARUKA_LOCKED_NOTE080 not in ref['notes']
        for component in result['components']:
            if component['name'] in ('扶摇花火','浮泡治疗衍生伤害'):
                assert component['hits']==0 and component['total']==0
                assert 'actual_total' not in component
    else:
        assert HARUKA_LOCKED_NOTE080 not in ref['notes']
        healing=result['haruka_healing_reference']
        assert healing['native_attachment_verified'] is False
        assert healing['native_composition_verified'] is False
        if count>0 and args['window_seconds']>0:
            assert result['total_healing'] is None
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0
    if args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    assert '独立条件来源 · 事件时钟待核验' in text

def require_aglna080(result,args,text,controls):
    name='飘浮大地之上'
    component=next(c for c in result['components']if c['name']==name)
    if args['elite']==0:
        assert component['hits']==component['per_hit']==component['total']==0
        assert component['times_seconds']==[]
        assert result['estimate']['skill']['hit_counts'][name]==0
        assert canonical080(result)==canonical080(controls['light'])
    else:
        weight=args['enemy_weight']
        if weight<=3:
            assert canonical080(result)==canonical080(controls['light'])
        else:
            assert canonical080(result)==canonical080(controls['heavy'])
            light=next(c for c in controls['light']['components']if c['name']==name)
            hi,lo={(1,1):(.2,.13),(1,3):(.3,.18),(2,1):(.35,.25),(2,3):(.45,.3)}[(args['elite'],args['potential'])]
            assert abs(component['per_hit']*hi-light['per_hit']*lo)<1e-7
    if args['skill']==2:
        ref=result['aglna_liftoff_reference']
        assert ref['actual_takeoff_seconds'] is None and ref['lifecycle_binding_verified'] is False
        assert result['estimate']['skill']['duration_seconds'] is None
        assert result['estimate']['skill']['cycle_seconds'] is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0

def require_aglna_selected080(result,args,text,plain,mass):
    target=args['target_enemy'];enemy=result['run_resolution']['enemy']
    for key in ('stage_id','enemy_id','level'):
        assert enemy[key]==target[key]
    assert enemy['reference_stats']['massLevel']==mass
    assert canonical080(result)==canonical080(plain)
    component=next(c for c in result['components']if c['name']=='飘浮大地之上')
    if args['elite']==0:
        assert component['hits']==component['per_hit']==component['total']==0
        assert component['times_seconds']==[]
        assert result['estimate']['skill']['hit_counts']['飘浮大地之上']==0
    else:
        assert component['hits']>0 and component['per_hit']>0
    assert enemy['name'] in text

def normalized_locked_mantra080(result):
    value=deepcopy(result)
    for ref in (value['external_event_reference'],value['external_event_reference']['window_reference']):
        ref['parameter_rows'][0]=('声明当前目标麻痹触发次数',0.0,'次')
    for section in value['report']['sections']:
        if section['id']=='external_events':
            next(m for m in section['metrics']if m['key']=='parameter_0')['value']=0.0
    return value

def require_mantra080(result,args,text,plain):
    count=args['palsy_triggers'];qualified=args['elite']>=1
    ref=result['external_event_reference'];window=ref['window_reference']
    assert ref['kind']=='mantra_events'
    assert ref['parameter_rows'][0]==('声明当前目标麻痹触发次数',float(count),'次')
    assert window['parameter_rows'][0]==ref['parameter_rows'][0]
    assert ref['actual_event_times_seconds'] is None
    assert ref['collision_clock_verified'] is False and window['collision_clock_verified'] is False
    if not qualified:
        assert canonical080(normalized_locked_mantra080(result))==canonical080(plain)
        component=next(c for c in result['components']if c['name']=='麻痹触发天赋')
        assert component['hits']==component['per_hit']==component['total']==0
        assert 'actual_total'not in component
    elif count>0 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
        assert result['total_damage'] is None
    if args['skill']==3:
        assert ref['parameter_rows'][1]==('声明当前目标溢出跳跃命中次数',float(args['palsy_overflow_hits']),'次')
        if args['palsy_overflow_hits']>0 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
            assert result['total_damage'] is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    assert '独立条件来源 · 事件时钟待核验' in text

def require_medical_amiya080(result,args,text):
    name='诚挚期许本体生命回复'
    component=next(c for c in result['components']if c['name']==name)
    assert component['damage_type']=='regeneration' and component['source_unit']=='operator'
    assert type(component['hits'])is float and type(component['total'])is float
    assert '阿米娅 · 医疗'in text
    if args['elite']==0:
        assert args['skill']==1
        assert component['hits']==component['per_hit']==component['total']==0
        assert type(result['estimate']['skill']['hit_counts'][name])is float
        assert result['estimate']['skill']['hit_counts'][name]==0.0
        assert 'actual_total'not in component
        assert name not in result['timing'].get('unplaced_components',[])
        assert not any('尚未统一排入时间轴' in note and name in note for note in result['estimate']['notes'])
        assert '尚未统一排入时间轴的输出分项：'+name not in text
        assert result['estimate']['skill']['duration_seconds']>0
    else:
        assert component['per_hit']>0
        assert component['hits']==float(args['window_seconds'])
        if args['skill']==1:
            assert 'actual_total'not in component
            assert result['estimate']['skill']['hit_counts'][name]>0
            if args['timing_mode']=='frames' and args['window_seconds']>0:
                assert name in result['timing']['unplaced_components']
        else:
            phase=result['amiya_phase_reference']
            assert phase['actual_strengthening_start_seconds']is None
            assert phase['actual_skill_end_seconds']is None
            assert phase['phase_clock_verified']is False
            assert phase['opening_buff_healing_order_verified']is False
            assert result['estimate']['skill']['duration_seconds']is None
            assert result['estimate']['skill']['cycle_seconds']is None
            assert component['nominal_duration_reference_seconds']==float(args['window_seconds'])
            if args['window_seconds']>0:assert component['actual_total']is None
            else:assert 'actual_total'not in component
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0
    if args['skill']==2 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
        assert result['total_damage']is None
        if args['healing_targets']==0:assert result['total_healing']==0
        else:assert result['total_healing']is None

def require_medical_trait080(result,args,text,ratio):
    require_medical_amiya080(result,args,text)
    heal=next(c for c in result['components']if c['name']=='咒愈师伤害转治疗')
    dependent=heal['damage_healing']
    expected=ratio*min(1,args['healing_targets'])
    assert dependent['ratio']==expected
    assert dependent['sources']==([0]if args['skill']==1 else [0,1])
    healing_factor=1.2 if args['relic_ids']==['rogue_6_relic_legacy_81']else 1.0
    subtotal=sum(result['components'][i]['total']for i in dependent['sources'])
    assert abs(heal['total']-subtotal*expected*healing_factor)<1e-7
    if args['skill']==2:
        phase=result['amiya_phase_reference']
        assert abs(phase['opening_healing_reference']-phase['opening_damage_reference']*expected*healing_factor)<1e-7
        if (args['window_seconds']>0 and args['healing_targets']>0 and
                args.get('timing',{}).get('target_disappears_seconds')!=0):
            assert heal['actual_total']is None
            assert phase['actual_skill_end_seconds']is None
        if args.get('timing',{}).get('target_disappears_seconds')==0:
            assert heal['total']==0 and 'actual_total'not in heal
    elif args['healing_targets']==2:
        direct=next(c for c in result['components']if c['name']=='哀恸共情范围治疗')
        assert direct['hits']>0 and direct['total']>0
        assert dependent['ratio']==ratio


"""Construct public design cases without API calls or private state reads."""
def cases080():
    rows=[]
    def add(elite,level,rank,number,mode,scope,horizon,timing,**extra):
        args={'operator':'char_4202_haruka','elite':elite,'level':level,'skill_rank':rank,
              'skill':number,'timing_mode':mode,'potential':5,'trust':100,
              'module_id':None,'module_level':0,'window_seconds':horizon,'healing_targets':1,
              'enemy_defense':0,'enemy_resistance':0,'cooperative':False,'preexisting_fragile':False,'relic_ids':[]}
        if timing:args['timing']=timing
        args.update(extra);rows.append({'section':76,'context':scope,'input':args})
    scopes=[('positive',10,{}),('zero_window',0,{}),
            ('zero_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_target_windows',10,{'target_windows':[]})]
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,60,10,(1,2,3))):
        for potential in (4,5):
            for number in numbers:
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for repeat in ((False,True)if number==2 else (False,)):
                            for count in (0,1,10000):
                                opts={'bubble_bursts':count,'potential':potential}
                                if number==2:opts['haruka_repeat']=repeat
                                if number==3:opts['levitate_triggers']=0
                                add(elite,level,rank,number,mode,scope,horizon,timing,**opts)
    for stage in (1,2,3):
        for level in (59,60):
            for mode in ('frames','continuous'):
                for count in (0,1):
                    add(2,level,10,2,mode,'module_unlock_boundary',10,{},bubble_bursts=count,
                        module_id='uniequip_002_haruka',module_level=stage,haruka_repeat=True)
    for elite,level,rank,number in ((0,50,4,1),(1,80,7,2)):
        for mode in ('frames','continuous'):
            for count in (0,1):
                opts={'haruka_repeat':False}if number==2 else {}
                add(elite,level,rank,number,mode,'locked_module_does_not_grant_talent',10,{},bubble_bursts=count,
                    module_id='uniequip_002_haruka',module_level=3,**opts)
    for mode in ('frames','continuous'):
        for trigger in (1,1000):
            for count in (0,1):
                add(2,60,10,3,mode,'independent_levitate_declaration',10,{},bubble_bursts=count,levitate_triggers=trigger)
    for elite,rank in ((1,7),(2,10)):
        for mode in ('frames','continuous'):
            for count in (0,1):
                add(elite,60,rank,2,mode,'zero_declared_friendly_targets',10,{},bubble_bursts=count,
                    healing_targets=0,haruka_repeat=False)
    def aglna(elite,level,rank,number,potential,mode,scope,horizon,timing,weight):
        args={'operator':'char_1015_aglna2','elite':elite,'level':level,'skill_rank':rank,'skill':number,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[],
              'enemy_weight':weight}
        if timing:args['timing']=timing
        rows.append({'section':77,'context':scope,'input':args})
    for elite,numbers in ((0,(1,)),(1,(1,2)),(2,(1,2,3))):
        for number in numbers:
            for potential in (1,3):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for weight in (0,3,4,100):
                            aglna(elite,1,1,number,potential,mode,scope,horizon,timing,weight)
    for elite,level,rank,number in ((0,50,4,1),(1,80,7,2),(2,90,10,3)):
        for mode in ('frames','continuous'):
            for weight in (0,3,4,100):
                aglna(elite,level,rank,number,3,mode,'readonly_max_cultivation',10,{},weight)
    # Exact public NORMAL roster identities, massLevel3/4. Selection overrides
    # the separate manual reference; declared weight remains genuine Qt input.
    for elite,number in ((0,1),(2,3)):
        for enemy_id,level,mass in (('enemy_10107_mjcdog_2',0,3),('enemy_2002_bearmi',1,4)):
            for mode in ('frames','continuous'):
                for weight in (0,100):
                    aglna(elite,1,1,number,3,mode,'selected_enemy_overrides_manual_weight',10,{},weight)
                    rows[-1]['input']['target_enemy']={'stage_id':'ro6_n_3_6','enemy_id':enemy_id,'level':level}
                    rows[-1]['expected_reference_mass']=mass
    #78 final source is committed; these designs still need final080 preflight.
    def mantra(elite,level,rank,number,potential,mode,scope,horizon,timing,count,**extra):
        args={'operator':'char_4204_mantra','elite':elite,'level':level,'skill_rank':rank,'skill':number,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[],
              'palsy_triggers':count}
        if number==3:args['palsy_overflow_hits']=0
        if timing:args['timing']=timing
        args.update(extra)
        rows.append({'section':78,'context':scope,'input':args})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,80,7,(1,2)),(2,90,10,(1,2,3))):
        for number in numbers:
            for potential in (4,5):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for count in (0,1,10000):
                            mantra(elite,level,rank,number,potential,mode,scope,horizon,timing,count)
    for mode in ('frames','continuous'):
        for scope,horizon,timing in scopes:
            for overflow in (1,10000):
                for count in (0,1):
                    mantra(2,90,10,3,5,mode,'separate_overflow_'+scope,horizon,timing,count,palsy_overflow_hits=overflow)
    for number in (1,2,3):
        for mode in ('frames','continuous'):
            for count in (0,1):
                mantra(2,90,10,number,5,mode,'elemental_immunity_does_not_bind_clock',10,{},count,
                    enemy_elemental_resistance=100.0)
    for stage in (1,2,3):
        for level in (59,60):
            for mode in ('frames','continuous'):
                for count in (0,1):
                    mantra(2,level,10,2,5,mode,'readonly_module_boundary',10,{},count,
                        module_id='uniequip_002_mantra',module_level=stage)
    for mode in ('frames','continuous'):
        for count in (0,1):
            mantra(0,50,4,1,5,mode,'locked_module_does_not_grant_talent',10,{},count,
                module_id='uniequip_002_mantra',module_level=3)
    #79 medical form only. No assumed account form-unlock or unavailable HP0.
    def medical(elite,level,rank,number,potential,mode,scope,horizon,timing,**extra):
        args={'operator':'char_1037_amiya3','elite':elite,'level':level,'skill_rank':rank,
              'skill':number,'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'enemy_defense':0,'enemy_resistance':0,
              'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
        if number==2:args['amiya_hit_targets']=1
        if timing:args['timing']=timing
        args.update(extra);rows.append({'section':79,'context':scope,'input':args})
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,80,10,(1,2))):
        for number in numbers:
            for potential in (1,6):
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for count in ((1,5,100)if number==2 else (None,)):
                            opts={'amiya_hit_targets':count}if count is not None else {}
                            medical(elite,level,rank,number,potential,mode,scope,horizon,timing,**opts)
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,49,10,(1,2)),(2,50,10,(1,2))):
        for number in numbers:
            for stage in (1,2,3):
                for mode in ('frames','continuous'):
                    medical(elite,level,rank,number,1,mode,'readonly_INC_X_boundary',10,{},
                        module_id='uniequip_002_amiya3',module_level=stage)
    for elite,numbers in ((0,(1,)),(1,(1,2)),(2,(1,2))):
        for number in numbers:
            for mode in ('frames','continuous'):
                for targets in ((0,2)if number==1 else (0,1)):
                    medical(elite,1,1,number,1,mode,'own_regeneration_independent_of_friendly_count',10,{},
                        healing_targets=targets)
        for mode in ('frames','continuous'):
            medical(elite,1,1,1,1,mode,'readonly_talent_minimum_level',10,{})
    #80 confirmed same medical trait replacement. Final patch remains pending.
    def trait_case(elite,level,rank,number,stage,mode,scope,horizon,timing,**extra):
        medical(elite,level,rank,number,1,mode,scope,horizon,timing,
            module_id='uniequip_002_amiya3'if stage else None,module_level=stage,**extra)
        rows[-1]['section']=80
        rows[-1]['expected_trait_ratio']=.6 if elite==2 and level>=50 and stage else .5
    for elite,level,rank,numbers in ((0,50,4,(1,)),(1,70,7,(1,2)),(2,49,10,(1,2)),(2,50,10,(1,2))):
        for number in numbers:
            for stage in (0,1,2,3):
                for mode in ('frames','continuous'):
                    for targets in (0,1):
                        trait_case(elite,level,rank,number,stage,mode,'INC_X_same_trait_ratio_boundary',10,{},
                            healing_targets=targets)
    for stage in (1,2,3):
        for number in (1,2):
            for mode in ('frames','continuous'):
                for scope,horizon,timing in scopes[1:]:
                    trait_case(2,50,10,number,stage,mode,'qualified_trait_'+scope,horizon,timing)
                trait_case(2,50,10,number,stage,mode,'accepted_healing_factor_preserves_trait_ratio',10,{},
                    relic_ids=['rogue_6_relic_legacy_81'])
                trait_case(2,50,10,number,stage,mode,'conversion_uses_dealt_enemy_damage',10,{},
                    enemy_resistance=50)
    for stage in (0,1,2,3):
        for mode in ('frames','continuous'):
            trait_case(2,50,10,1,stage,mode,'trait_one_recipient_and_separate_S1_range_healing',10,{},
                healing_targets=2)
    return rows


"""Current source-backed planned assertions; no actual Qt/Wine certification."""
import json

def canonical085(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def require_warning_order085(result,args,text,technical):
    groups=('heal_scale','received_regeneration')
    selected=args['relic_ids']
    conflicting=len(set(selected)&{'rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'})>=2
    expected=['组合 '+group+' 的叠加规则尚未核验，未套用该组合。'for group in groups]if conflicting else []
    actual=[w for w in result['warnings']if w.startswith('组合 ')]
    assert actual==expected
    records=result['relic_resolution']['records']
    assert [r['id']for r in records]==selected
    if conflicting:
        assert not result['relic_resolution']['complete']
        assert not any(r['kind']in ('healing_factor','regeneration_factor')for r in result['relic_resolution']['rules'])
        for record in records:
            if record['id']in ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):
                assert record['pending']==['组合叠加规则待核验:'+group for group in groups]
                assert record['applied']==[] and record['status']=='incomplete'
        if technical:
            assert text.index(expected[0])<text.index(expected[1])
        else:
            rendered='组合 未核验配置（原文见技术资料） 的叠加规则尚未核验，未套用该组合。'
            assert text.count(rendered)==2
            assert '组合 heal_scale 'not in text and '组合 received_regeneration 'not in text
    if 'rogue_6_relic_legacy_5'in selected:
        other=next(r for r in records if r['id']=='rogue_6_relic_legacy_5')
        assert other['status']=='applied' and other['applied']
    # Unknown stacking is excluded irrespective of zero observation; this
    # never establishes real target/recipient state or a composition formula.
    if args['window_seconds']==0:
        assert result['total_damage']==0
        if args['operator']=='mechanist'and args['skill']==3:
            # Legacy _skill_damage emits a damage-only dictionary; its estimate
            # independently carries zero direct healing without adding a field.
            assert 'total_healing'not in result
            assert result['estimate']['skill']['window_healing']==0
        else:assert result['total_healing']==0

def require_susuro_checkbox085(result,args,text,plain,factor):
    assert type(args['low_cost_healing_target'])is bool
    assert result['total_damage']==0
    assert result['timing']==plain['timing']
    a,b=plain['estimate']['skill'],result['estimate']['skill']
    for key in ('mode','initial_seconds','recharge_seconds','cycle_seconds','duration_seconds',
                'sp_recovery_per_second','hit_counts'):
        assert b[key]==a[key]
    effective=factor if args['low_cost_healing_target']else 1.0
    for key in ('total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps'):
        if a[key]is None:assert b[key]is None
        else:assert abs(b[key]-a[key]*effective)<1e-7
    assert abs(result['total_healing']-plain['total_healing']*effective)<1e-7
    if args['healing_targets']==0 or args['window_seconds']==0:assert result['total_healing']==0
    if args['skill']==2 and args['casts_used']==1:
        assert b['cycle_seconds']is None and b['cycle_healing']is None
    if args.get('timing',{}).get('target_disappears_seconds')==0 or args.get('timing',{}).get('target_windows')==[]:
        assert '真实友方获取时钟未核验'in text

"""Provisional sourced contracts; no API execution or native validation proof."""
def require_neural_checkbox085(result,args,text):
    hidden=args['operator']=='char_4204_mantra'and args['skill']==3
    if hidden:
        assert not {'enemy_is_boss','enemy_in_neural_break','initial_neural_buildup','enemy_buildup_resistance'}&args.keys()
    else:
        assert type(args['enemy_is_boss'])is bool and type(args['enemy_in_neural_break'])is bool
        assert type(args['initial_neural_buildup'])is int
    if 'rogue_6_relic_fight_22'in args['relic_ids']:
        ref=result['neural_relic_reference']
        assert ref['periodic_damage_scheduled']is False
        assert ref['preexisting_break_assumed']is args.get('enemy_in_neural_break',False)
        section=next(s for s in result['report']['sections']if s['id']=='river_neural')
        assert next(m['value']for m in section['metrics']if m['key']=='first_tick')is None
        assert '实际首跳时刻和每跳麻痹条件尚未确认'in text
    else:assert 'neural_relic_reference'not in result
    if args['operator']=='char_1042_phatm2':
        assert 'neural_bait_reference'not in result and 'neural_incoming_reference'not in result
    else:
        ref=result['external_event_reference']
        assert ref['kind']=='mantra_events' and ref['actual_event_times_seconds']is None
    target=args.get('target_enemy')
    if target:
        enemy=result['run_resolution']['enemy']
        # Processed enemy spreads target keys; catalog record uses id separately.
        assert enemy['enemy_id']==target['enemy_id'] and enemy['level']==target['level']
        assert enemy['stage_id']==target['stage_id']
        assert enemy['level_type']=='BOSS'
        assert args['initial_neural_buildup']==1500
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0

def require_repeat_checkbox085(result,args,text,plain,attack_bonus):
    healing=result['haruka_healing_reference']
    for ref in (healing,healing['window_reference']):
        assert ref['actual_target_count']is None and ref['actual_acquisition_times_seconds']is None
        assert ref['native_composition_verified']is False and ref['native_attachment_verified']is False
    events=result['external_event_reference']
    assert events['kind']=='haruka_bubbles' and events['actual_event_times_seconds']is None
    if args['skill']==2:
        assert type(args['haruka_repeat'])is bool
        skill=result['estimate']['skill']
        assert skill['mode']==('infinite'if args['haruka_repeat']else 'timed')
        delta=plain['estimate']['base_stats']['attack']*attack_bonus if args['haruka_repeat']else 0.0
        assert abs(result['attack']-plain['attack']-delta)<1e-7
        assert abs(skill['skill_attack']-plain['estimate']['skill']['skill_attack']-delta)<1e-7
        assert result['estimate']['base_stats']==plain['estimate']['base_stats']
        if args['haruka_repeat']:
            assert skill['duration_seconds']is None and skill['cycle_seconds']is None
            assert skill['cycle_damage']is None and skill['cycle_healing']is None
    else:assert 'haruka_repeat'not in args
    if args['elite']<2:
        for c in result['components']:
            if c['name']in ('扶摇花火','浮泡治疗衍生伤害'):
                assert c['hits']==0 and c['total']==0
    if args['healing_targets']==0 or args['window_seconds']==0:assert result['total_healing']==0
    assert '实际友方获取'in text

def require_nearby_checkbox085(result,args,text,plain,talent_bonus):
    assert type(args['near_previous_deployment'])is bool
    factor=talent_bonus if args['near_previous_deployment']else 0.0
    base=plain['estimate']['base_stats']['attack']
    assert abs(result['estimate']['base_stats']['attack']-base*(1+factor))<1e-7
    assert abs(result['attack']-plain['attack']-base*factor)<1e-7
    assert abs(result['estimate']['skill']['skill_attack']-plain['estimate']['skill']['skill_attack']-base*factor)<1e-7
    if args['elite']==0:
        assert factor==0 and canonical085(result)==canonical085(plain)
    assert result['orchid_redeploy_reference']==plain['orchid_redeploy_reference']
    redeploy=result['orchid_redeploy_reference']
    assert redeploy['events_scheduled']is False and redeploy['native_attachment_verified']is False
    assert redeploy['actual_retreat_seconds']is None and redeploy['actual_next_deployment_seconds']is None
    cast=result['unbound_cast_reference']
    assert cast['kind']=='orchid_arrows' and cast['collision_clock_verified']is False
    assert cast['actual_hit_times_seconds']is None and cast['actual_end_seconds']is None
    assert result['estimate']['skill']['cycle_seconds']is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    else:assert result['total_damage']is None
    assert result['total_healing']==0
    assert '实际撤退、倒下和再次部署的时刻'in text

"""Pure future085 actual-control designs; no calculation or Qt execution."""
def cases085():
    rows=[]
    scopes=(('positive',10,{}),('zero_window',0,{}),
            ('zero_enemy_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_enemy_windows',10,{'target_windows':[]}))
    def add(section,owner,skill,elite,level,rank,potential,mode,scope,horizon,timing,**extra):
        args={'operator':owner,'skill':skill,'elite':elite,'level':level,'skill_rank':rank,
              'potential':potential,'trust':100,'module_id':None,'module_level':0,
              'timing_mode':mode,'window_seconds':horizon,'healing_targets':1,
              'enemy_defense':0,'enemy_resistance':0,'preexisting_fragile':False,
              'cooperative':False,'relic_ids':[]}
        if timing:args['timing']=timing
        if owner=='mechanist' and skill==3:args['charge_count']=0
        args.update(extra);rows.append({'section':section,'context':scope,'input':args})
    # Genuine Qt list preserves its catalog index order, never click order or
    # synthetic reverse/duplicate/unknown relic arrays.
    sets=((),('rogue_6_relic_legacy_81',),
          ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82'),
          ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'))
    for owner,skill in (('char_1037_amiya3',1),('char_1037_amiya3',2),
                        ('mechanist',3),('char_110_deepcl',2)):
        for mode in ('frames','continuous'):
            for technical in (False,True):
                for scope,horizon,timing in scopes[:2]:
                    for ids in sets:
                        add(81,owner,skill,2,60,10,1,mode,scope,horizon,timing,relic_ids=list(ids))
                        rows[-1]['technical']=technical
    for mode in ('frames','continuous'):
        for technical in (False,True):
            for ids in (['rogue_6_relic_legacy_5'],
                        ['rogue_6_relic_legacy_5','rogue_6_relic_legacy_81','rogue_6_relic_legacy_82']):
                add(81,'char_110_deepcl',2,2,60,10,1,mode,'unrelated_attack_rule_keeps_order',10,{},relic_ids=ids)
                rows[-1]['technical']=technical
    #82 source formal root; only genuine bool checkbox and int controls.
    for elite,level,rank,potential,numbers in ((0,1,1,1,(1,)),(1,1,7,1,(1,2)),
            (1,1,7,5,(1,2)),(2,40,10,1,(1,2)),(2,40,10,5,(1,2))):
        for skill in numbers:
            for mode in ('frames','continuous'):
                for scope,horizon,timing in scopes:
                    for flag in (False,True):
                        add(82,'char_298_susuro',skill,elite,level,rank,potential,mode,scope,horizon,timing,
                            low_cost_healing_target=flag,**({'casts_used':0}if skill==2 else {}))
    for level in (39,40):
        for stage in (1,2,3):
            for skill in (1,2):
                for mode in ('frames','continuous'):
                    for flag in (False,True):
                        add(82,'char_298_susuro',skill,2,level,10,1,mode,'readonly_module_qualification',10,{},
                            module_id='uniequip_002_susuro',module_level=stage,low_cost_healing_target=flag,
                            **({'casts_used':0}if skill==2 else {}))
    for elite,rank in ((1,7),(2,10)):
        for mode in ('frames','continuous'):
            for flag in (False,True):
                add(82,'char_298_susuro',2,elite,40,rank,1,mode,'remaining_S2_use_keeps_unknown_cycle',10,{},
                    low_cost_healing_target=flag,casts_used=1)
        for skill in (1,2):
            for mode in ('frames','continuous'):
                for flag in (False,True):
                    add(82,'char_298_susuro',skill,elite,40,rank,1,mode,'zero_friendly_recipients',10,{},
                        low_cost_healing_target=flag,healing_targets=0,
                        **({'casts_used':0}if skill==2 else {}))
    rows.extend(pending_cases083085())
    return rows

"""Provisional genuine-control rows; source final guards remain pending."""
def pending_cases083085():
    rows=[]
    scopes=(('positive',10,{}),('zero_window',0,{}),
            ('zero_enemy_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_enemy_windows',10,{'target_windows':[]}))
    def add(section,owner,skill,elite,level,rank,potential,mode,scope,horizon,timing,**extra):
        args={'operator':owner,'skill':skill,'elite':elite,'level':level,'skill_rank':rank,
            'potential':potential,'trust':100,'module_id':None,'module_level':0,
            'timing_mode':mode,'window_seconds':horizon,'healing_targets':1,
            'enemy_defense':0,'enemy_resistance':0,'preexisting_fragile':False,
            'cooperative':False,'relic_ids':[]}
        if timing:args['timing']=timing
        args.update(extra)
        rows.append({'section':section,'context':scope,'input':args})
    def neural_options(owner,skill,boss=False,breaking=False,initial=0):
        # The hidden S3 widgets are never emitted; its API consumer still exists.
        if owner=='char_4204_mantra'and skill==3:
            return {'enemy_elemental_resistance':0.0,'palsy_triggers':0,'palsy_overflow_hits':0}
        args={'enemy_is_boss':boss,'enemy_in_neural_break':breaking,
            'initial_neural_buildup':initial,'enemy_buildup_resistance':0.0,
            'enemy_elemental_resistance':0.0}
        if owner=='char_1042_phatm2':
            args['enemy_attack_count']=0
            if skill==2:args['bait_triggers']=0
        else:args['palsy_triggers']=0
        return args
    qualifications=((0,1,1,(1,)),(1,1,7,(1,2)),(2,60,10,(1,2,3)))
    for owner in ('char_1042_phatm2','char_4204_mantra'):
        for elite,level,rank,numbers in qualifications:
            for skill in numbers:
                flags=((False,False),)if owner=='char_4204_mantra'and skill==3 else (
                    (False,False),(False,True),(True,False),(True,True))
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for boss,breaking in flags:
                            add(83,owner,skill,elite,level,rank,1,mode,scope,horizon,timing,
                                **neural_options(owner,skill,boss,breaking))
                            if owner=='char_4204_mantra'and skill==3:
                                rows[-1]['hidden_neural_checkbox_state']=True
        for mode in ('frames','continuous'):
            for boss in (False,True):
                for breaking in (False,True):
                    add(83,owner,2,1,1,7,1,mode,'actual_spinbox1500_threshold',10,{},
                        **neural_options(owner,2,boss,breaking,1500))
                    if not boss:rows[-1]['expected_error']='initial_neural_buildup需要范围内的有限非负数。'
        for skill in (1,2,3):
            flags=((False,False),)if owner=='char_4204_mantra'and skill==3 else (
                (False,False),(False,True),(True,False),(True,True))
            for mode in ('frames','continuous'):
                for boss,breaking in flags:
                    add(83,owner,skill,2,60,10,1,mode,'actual_River_selected_reference',10,{},
                        relic_ids=['rogue_6_relic_fight_22'],**neural_options(owner,skill,boss,breaking))
                    if owner=='char_4204_mantra'and skill==3:rows[-1]['hidden_neural_checkbox_state']=True
        targets=(('NORMAL',{'stage_id':'ro6_n_1_1','enemy_id':'enemy_2133_shdopl','level':0}),
                 ('BOSS',{'stage_id':'ro6_n_2_3','enemy_id':'enemy_1501_demonk','level':0}))
        for mode in ('frames','continuous'):
            for level_type,target in targets:
                for boss in (False,True):
                    for breaking in (False,True):
                        add(83,owner,2,1,1,7,1,mode,'actual_fixed_enemy_overrides_manual_threshold',10,{},
                            target_enemy=target,**neural_options(owner,2,boss,breaking,1500))
                        rows[-1]['processed_enemy_level_type']=level_type
                        if level_type!='BOSS':rows[-1]['expected_error']='initial_neural_buildup需要范围内的有限非负数。'
    for elite,level,rank,potential in ((1,1,7,1),(2,60,10,1),(2,60,10,5)):
        for mode in ('frames','continuous'):
            for scope,horizon,timing in scopes:
                for repeat in (False,True):
                    add(84,'char_4202_haruka',2,elite,level,rank,potential,mode,scope,horizon,timing,
                        bubble_bursts=0,haruka_repeat=repeat)
    for level in (59,60):
        for stage in (1,2,3):
            for mode in ('frames','continuous'):
                for repeat in (False,True):
                    add(84,'char_4202_haruka',2,2,level,10,1,mode,'readonly_repeat_module_qualification',10,{},
                        module_id='uniequip_002_haruka',module_level=stage,bubble_bursts=0,haruka_repeat=repeat)
    for elite,skill,rank in ((0,1,1),(1,1,7),(2,1,10),(2,3,10)):
        for mode in ('frames','continuous'):
            add(84,'char_4202_haruka',skill,elite,1 if elite<2 else 60,rank,1,mode,
                'inactive_repeat_checkbox_omitted',10,{},bubble_bursts=0,
                **({'levitate_triggers':0}if skill==3 else {}))
            rows[-1]['hidden_repeat_checkbox_state']=True
    for elite,level,rank in ((1,1,7),(2,60,10)):
        for mode in ('frames','continuous'):
            for repeat in (False,True):
                add(84,'char_4202_haruka',2,elite,level,rank,1,mode,'zero_friendly_recipients',10,{},
                    healing_targets=0,bubble_bursts=0,haruka_repeat=repeat)
    for elite,level,rank,numbers in qualifications:
        for potential in (1,5):
            for skill in numbers:
                for mode in ('frames','continuous'):
                    for scope,horizon,timing in scopes:
                        for nearby in (False,True):
                            add(85,'char_1048_orchd2',skill,elite,level,rank,potential,mode,scope,horizon,timing,
                                power_coating=True,near_previous_deployment=nearby,
                                **({'double_charge':True}if skill==1 else {}),
                                **({'dragon_arrow_hits':1}if skill==3 else {}))
    for level in (59,60):
        for stage in (1,2,3):
            for skill in (1,2,3):
                for mode in ('frames','continuous'):
                    for nearby in (False,True):
                        add(85,'char_1048_orchd2',skill,2,level,10,1,mode,'readonly_nearby_module_qualification',10,{},
                            module_id='uniequip_002_orchd2',module_level=stage,
                            power_coating=True,near_previous_deployment=nearby,
                            **({'double_charge':True}if skill==1 else {}),
                            **({'dragon_arrow_hits':1}if skill==3 else {}))
    return rows


# BEGIN FINAL090 PURE HELPERS
import copy as _copy090
actual_states090=[]
entry_counts090={}
profile_case090=None
profile_trace090=[]

def projection090(result):
    keys=['attack','total_damage','components','attack_speed','base_attack_speed','interval_seconds','timing']
    if 'total_healing' in result:keys.append('total_healing')
    keys.extend(k for k in result if k.endswith('_reference'))
    out={key:result[key] for key in dict.fromkeys(keys)}
    out['estimate']={key:result['estimate'][key] for key in ('training','base_stats','skill')}
    return out

def entries_delta090(before,after):
    return {key:after.get(key,0)-before.get(key,0) for key in sorted(set(before)|set(after))}

def native090(value):
    kind=type(value).__name__
    if value is None or type(value) in (bool,int,str):return {'type':kind,'value':value}
    if type(value) is float:return {'type':'float','hex':value.hex()}
    if type(value) in (list,tuple):return {'type':kind,'items':[native090(v) for v in value]}
    if type(value) is dict:return {'type':'dict','items':[[native090(k),native090(v)] for k,v in value.items()]}
    raise AssertionError(('unhandled native value',kind))
# END FINAL090 PURE HELPERS

def source_hashes():
    return maintained_source100()
checks=_ProgressChecks105();started=time.perf_counter();window=None;app=None;before=source_hashes()
receipt={'scope':'Wine Windows binary compatibility; no native Windows or game integration',
         'after_section':110,'current_maintained_source_count_expected':_SOURCE110_MAINTAINED_COUNT,
         'inherited_full100_runner_sha256':'e7a185ea5eba2d1d4905bbbe8f8cdfff1978c1a25e39b865d5018c00a6ac93f3',
         'legacy_output_names_preserved':True,'specialist101_109_validation_in_this_runner':False,
         'native_windows_verified':False,'game_captures':0,'chat_requests':0,
         'private_state_isolated':True,'platform':platform.platform(),'python':sys.version,
         'checks':checks,'passed':False,'complete_ui_validation':False,'plain_text_normalization':'QPlainTextEdit converts non-breaking spaces to ordinary spaces',
         'source100_guard_sha256':hashlib.sha256(_guard_bytes100).hexdigest(),
         'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'deadline_seconds':1200,'global_profile_or_trace_used':False,
         'full110_attempt':1,'progress_checkpoint_file':'full110-progress.json',
         'progress_every_appended_checks':32,'progress_is_partial_observation_only':True,
         'full105_v1_source_sha256':'98e6cef848ffea73d36f330edb071e28cc884e676838a876a76995d28ea821a5',
         'old095_complete_function_vector_measured':False,
         'old090_frame_local_normal_observed':False,
         'normal_plan_original_return_observed_instead':True,
         'specialist96_100_validation_in_this_runner':False,
         'scope_note100':'Inherited actual successful full105 progressv2 functional suite transported to actual completed109/final110 Source. Separate96-109 specialist receipts required. Legacy projection-only/producer/no-alias limitations remain unchanged. No old095 complete invocation vector, native Windows, capture or chat certification.'}
try:
    for name in ('PySide6.QtWidgets','numpy','cv2','win32gui','win32process','win32api','httpx','rapidocr_onnxruntime','windows_capture'):
        importlib.import_module(name)
        checks.append({'scope':'real_dependency_import','module':name,'passed':True})
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QPushButton
    _install_narrow_observers100()
    import rouge.app as module
    from rouge.reporting import format_report
    diagnosis_path=ROOT/'research/p2-friendly-scope-report/independent-diagnosis.json'
    assert diagnosis_path.is_file(),str(diagnosis_path)
    diagnosis_bytes=diagnosis_path.read_bytes()
    diagnosis=json.loads(diagnosis_bytes)
    from rouge.capture import list_game_windows
    with tempfile.TemporaryDirectory(prefix='rouge-full100-') as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
        backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        # BEGIN FINAL090 STARTUP INSTRUMENTATION
        _count_enabled100=True
        # END FINAL090 STARTUP INSTRUMENTATION
        app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()
        # BEGIN FINAL090 STARTUP SNAPSHOT
        _count_enabled100=False
        receipt['actual_startup_runstate_entries_090']=dict(entry_counts090)
        # END FINAL090 STARTUP SNAPSHOT
        assert window.isVisible()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process and not window.desktop_request_busy
        assert not list_game_windows()
        checks.append({'scope':'actual_main_window_visible','title':window.windowTitle(),
                       'win32_game_enumeration':'no Arknights.exe window present',
                       'auto_sampling':False,'desktop_backend_started':False})
        window.auto_relics.setChecked(False)
        original_select=window.select_operator
        def checked_select(op):
            assert op in module.catalog()['operators'],op
            selected=original_select(op)
            assert window.operator.currentData()==op,(op,window.operator.currentData())
            return selected
        window.select_operator=checked_select
        skills=0
        for op,profile in module.catalog()['operators'].items():
            for skill in range(1,len(profile['skills'])+1):
                window.select_operator(op)
                window.skill.setCurrentIndex(window.skill.findData(skill))
                window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                actual=window.damage_text.toPlainText();expected=format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
                if actual!=expected:
                    (OUT/'wine-ui-report-difference-100.json').write_text(json.dumps({'operator':op,'skill':skill,'actual':actual,'expected':expected},ensure_ascii=False,indent=2),encoding='utf-8')
                    raise AssertionError(f'report text differs for {op} skill {skill}')
                skills+=1
        assert skills==87,skills
        checks.append({'scope':'actual_controls_calculate_all_profiles','skills':skills,'passed':True})
        for guarded_op,reference_key in (('char_437_mizuki','mizuki_s1_reference'),('char_4087_ines','ines_dot_reference')):
            window.select_operator(guarded_op)
            window.skill.setCurrentIndex(window.skill.findData(1));window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            guarded=window.damage_result['result']
            assert reference_key in guarded
            assert guarded['estimate']['skill']['duration_seconds'] is None
            assert guarded['estimate']['skill']['cycle_seconds'] is None
            assert '未知' in window.damage_text.toPlainText()
            checks.append({'scope':'unknown_s1_end_and_cycle_visible','operator':guarded_op,'skill':1,
                           'duration_seconds':None,'cycle_seconds':None,
                           'report_contains_unknown':True,'passed':True})
        window.select_operator('char_1044_hsgma2')
        window.skill.setCurrentIndex(window.skill.findData(3))
        terminal=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_1044_hsgma2' and key=='last_stand_seconds')
        terminal.setValue(5);window.limit_window.setChecked(True);window.window_seconds.setValue(1)
        window.calculate();app.processEvents()
        assert window.damage_result,window.damage_text.toPlainText()
        guarded=window.damage_result['result'];reference=guarded['manual_close_reference']
        assert reference['close_seconds'] is None
        assert guarded['estimate']['skill']['window_seconds']==1
        assert guarded['estimate']['skill']['duration_seconds'] is None
        assert guarded['total_damage'] is None
        assert '未知' in window.damage_text.toPlainText()
        checks.append({'scope':'positive_terminal_duration_preserves_window','operator':'char_1044_hsgma2','skill':3,
                       'last_stand_seconds':5,'requested_window_seconds':1,'reported_window_seconds':1,
                       'close_seconds':None,'complete_total':None,'passed':True})
        window.select_operator('char_1015_aglna2')
        window.skill.setCurrentIndex(window.skill.findData(1))
        weight=next(widget for owner,key,_skills,widget in window.model_option_widgets
                    if owner=='char_1015_aglna2' and key=='enemy_weight')
        window.window_seconds.setValue(3)
        talent=[]
        for mass in (3,4):
            weight.setValue(mass);window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            talent.append(next(c['per_hit'] for c in result['components'] if c['name']=='飘浮大地之上'))
        assert talent[0]>talent[1],talent
        checks.append({'scope':'actual_manual_weight_control_selects_talent','weights':[3,4],'per_hit':talent,'passed':True})
        for op,key in (('char_1015_aglna2','aglna_liftoff_reference'),('char_196_sunbr','next_attack_healing_reference'),('char_2025_shu','next_attack_healing_reference'),('char_1046_sbell2','snow_field_reference')):
            window.select_operator(op)
            window.skill.setCurrentIndex(window.skill.findData(2 if op in ('char_1015_aglna2','char_1046_sbell2') else 1))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert key in result
                assert result['estimate']['skill']['window_seconds']==horizon
                amount=result['total_healing'] if key=='next_attack_healing_reference' else result['total_damage']
                assert amount==0 if horizon==0 else amount is None
                assert result['estimate']['skill']['cycle_seconds'] is None
            checks.append({'scope':'actual_short_window_controls_and_unknowns','operator':op,'zero_window_total':0,'one_second_total':None,'passed':True})
        tech=window.technology_reference
        assert tech.nodes.count()==57
        for index in range(tech.nodes.count()):
            tech.nodes.setCurrentIndex(index);app.processEvents()
            assert '账户解锁状态：未知' in tech.text.toPlainText()
        tech.search.setText('颊囊');app.processEvents();assert tech.nodes.count()==2
        tech.search.setText('不存在的科技xyz');app.processEvents();assert tech.nodes.count()==0
        assert '没有匹配' in tech.text.toPlainText()
        tech.search.clear();tech.nodes.setCurrentIndex(tech.nodes.findData('rogue_6_difficulty_1'));app.processEvents()
        assert '<保密等级3>' in tech.text.toPlainText()
        assert '原件SHA256' not in tech.text.toPlainText()
        tech.technical.setChecked(True);app.processEvents();assert '原件SHA256' in tech.text.toPlainText()
        tech.technical.setChecked(False);app.processEvents()
        checks.append({'scope':'actual_technology_browser','nodes':57,'duplicate_name_results':2,'empty_search':True,'grade_gate':3,'technical_toggle':True,'passed':True})
        for op,skills in (('char_4182_oblvns',(1,)),('char_1044_hsgma2',(2,)),('char_1048_orchd2',(1,2,3))):
            window.select_operator(op)
            for skill in skills:
                window.skill.setCurrentIndex(window.skill.findData(skill))
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                    assert window.damage_result,window.damage_text.toPlainText()
                    result=window.damage_result['result']
                    assert 'unbound_cast_reference' in result
                    assert result['estimate']['skill']['window_seconds']==horizon
                    assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                    if op=='char_1044_hsgma2':
                        assert result['total_healing']==0 if horizon==0 else result['total_healing'] is None
                    assert result['estimate']['skill']['cycle_seconds'] is None
                checks.append({'scope':'actual_unbound_multihit_short_window_controls','operator':op,'skill':skill,'zero_window_total':0,'one_second_total':None,'passed':True})
        for op,skills in (('char_1029_yato2',(2,3)),('char_1050_chen3',(2,3)),('char_4202_haruka',(1,2,3)),('char_2027_wang',(1,2,3)),('char_4204_mantra',(1,2,3))):
            window.select_operator(op)
            for skill in skills:
                window.skill.setCurrentIndex(window.skill.findData(skill))
                if op in ('char_4202_haruka','char_4204_mantra'):
                    keys=('bubble_bursts','levitate_triggers') if op=='char_4202_haruka' else ('palsy_triggers','palsy_overflow_hits')
                    for owner,key,_skills,widget in window.model_option_widgets:
                        if owner==op and key in keys:widget.setValue(1)
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                    assert window.damage_result,window.damage_text.toPlainText()
                    result=window.damage_result['result']
                    assert result['estimate']['skill']['window_seconds']==horizon
                    if horizon==0:
                        assert result['total_damage']==0
                        if op=='char_4202_haruka':assert result['total_healing']==0
                    elif op=='char_4202_haruka' and skill==1:
                        assert result['total_healing'] is None
                    else:assert result['total_damage'] is None
                checks.append({'scope':'actual_section31_35_short_window_and_event_controls','operator':op,'skill':skill,'zero_window_output':0,'positive_unplaced_source_unknown':True,'passed':True})
        for op in ('char_133_mm','char_1046_sbell2'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(1))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['estimate']['skill']['window_seconds']==horizon
                assert result['estimate']['skill']['duration_seconds'] is None
                assert result['estimate']['skill']['cycle_seconds'] is None
                if horizon==0:assert result['total_damage']==0
                assert '未知' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_mei_and_sbell_window_end_controls','operator':op,'zero_window':0,'positive_window_preserved':1,'actual_end_unknown':True,'passed':True})
        window.select_operator('char_1046_sbell2')
        snow_count=next(widget for owner,key,_skills,widget in window.model_option_widgets if owner=='char_1046_sbell2' and key=='snow_entries')
        snow_count.setValue(2)
        for skill in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(skill))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                assert result['estimate']['skill']['window_seconds']==horizon
            checks.append({'scope':'actual_snow_entry_controls','skill':skill,'manual_entries':2,'zero_window':0,'unplaced_positive_total':None,'passed':True})
        snow_count.setValue(0)
        for op in ('char_4087_ines','char_1041_angel2'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(3))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['estimate']['skill']['window_seconds']==horizon
                assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                assert result.get('external_event_reference')
            checks.append({'scope':'actual_independent_deployment_projectile_controls','operator':op,'zero_window':0,'unplaced_positive_total':None,'passed':True})
        window.select_operator('char_298_susuro');window.skill.setCurrentIndex(window.skill.findData(1))
        window.window_seconds.setValue(10)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert result['total_damage']==0 and result['total_healing']>0
            assert '真实友方获取时钟未核验' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_friendly_clock_explanation_probe','passed':True,
                'mode':'frames' if use_frames else 'continuous','scenario':window.damage_result['scenario'],
                'report_contains_friendly_clock_unknown':True,'numerical_damage':result['total_damage'],
                'numerical_healing':result['total_healing']})
        checks.append({'scope':'actual_friendly_healing_survives_empty_enemy','modes':['frames','continuous'],'positive_healing':True,'enemy_damage':0,'passed':True})
        window.select_operator('char_002_amiya');window.skill.setCurrentIndex(window.skill.findData(1))
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        window.limit_window.setChecked(False);window.frame_timing.setChecked(False);window.calculate();app.processEvents()
        assert window.damage_result,window.damage_text.toPlainText()
        result=window.damage_result['result'];skill=result['estimate']['skill']
        assert result['total_damage']==0 and skill['initial_seconds']==7 and skill['recharge_seconds']==30
        checks.append({'scope':'actual_amiya_empty_enemy_natural_recharge','first':7,'recharge':30,'enemy_damage':0,'passed':True})
        window.timing_scenario.clear();window.frame_timing.setChecked(True);window.limit_window.setChecked(True);window.window_seconds.setValue(1)
        window.window_seconds.setValue(10)
        op='char_437_mizuki'
        window.operator_observations[op]={'id':op,'fields':{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_003_mizuki','module_level':2},'skill_ranks':{'1':10,'2':10,'3':10}}
        window.select_operator(op);window.update_operator()
        for skill in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(skill));window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert 'mizuki_amb_y_reference' in result and result['total_damage'] is None
            assert result['total_healing'] is None
            assert '模组实际额外回复：未知' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_mizuki_amb_y_readonly_cultivation_preview','skill':skill,'module_level':2,'level':60,'actual_extra_healing':None,'passed':True})
        def train(op,fields,ranks=None):
            window.operator_observations[op]={'id':op,'fields':fields,'skill_ranks':ranks or {'1':10,'2':10,'3':10}}
            window.select_operator(op);window.update_operator()
        def calculate_result():
            window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            actual=window.damage_text.toPlainText()
            assert actual==format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
            return result
        def relics(ids):
            window.relic_list.blockSignals(True)
            for index in range(window.relic_list.count()):
                item=window.relic_list.item(index)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
        for stage,expected in ((1,30),(2,28),(3,27)):
            train('char_1048_orchd2',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_002_orchd2','module_level':stage})
            window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
            result=calculate_result()
            assert result['estimate']['base_stats']['redeploy_seconds']==expected
            assert result['orchid_redeploy_reference']['actual_next_deployment_seconds'] is None
            checks.append({'scope':'actual_orchid_module_redeploy_reference','module_level':stage,'parameter_seconds':expected,'actual_next_deployment':None,'passed':True})
        train('char_2027_wang',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_002_wang','module_level':2})
        window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
        result=calculate_result()
        token=next(t for t in result['relic_token_stats'] if t['id']=='token_10064_wang_stone1')
        assert token['deployment_cost']==2 and token['module_cost_reference']['cost_add']==-1
        checks.append({'scope':'actual_wang_module_token_cost_reference','cost':2,'module_level':2,'passed':True})
        window.select_operator('char_4202_haruka');window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
        window.window_seconds.setValue(10)
        bubble=next(widget for owner,key,_skills,widget in window.model_option_widgets if owner=='char_4202_haruka' and key=='bubble_bursts')
        bubble.setValue(1);relics([])
        base=calculate_result()['known_healing_subtotals']['window_healing']
        relics(['rogue_6_relic_legacy_81']);result=calculate_result()
        assert abs(result['known_healing_subtotals']['window_healing']-base*1.2)<1e-7
        assert result['total_healing'] is None
        checks.append({'scope':'actual_known_healing_subtotal_factor','base_subtotal':base,'final_subtotal':result['known_healing_subtotals']['window_healing'],'actual_healing':None,'passed':True})
        relics([])
        for op in ('char_1001_amiya2','char_1037_amiya3'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(2))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                window.timing_scenario.clear();window.limit_window.setChecked(True)
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);result=calculate_result()
                    assert result['estimate']['skill']['window_seconds']==horizon
                    assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                    assert result['estimate']['skill']['duration_seconds'] is None
                    if op=='char_1037_amiya3':
                        assert result['total_healing']==0 if horizon==0 else result['total_healing'] is None
                    checks.append({'scope':'actual_amiya_phase_window_controls','operator':op,'mode':'frames' if use_frames else 'continuous','window':horizon,'actual_output':result['total_damage'],'actual_end':None,'passed':True})
        window.frame_timing.setChecked(True);window.window_seconds.setValue(10)
        base=calculate_result()['known_healing_subtotals']['window_healing']
        relics(['rogue_6_relic_legacy_81']);result=calculate_result()
        known=result['known_healing_subtotals']['window_healing']
        assert abs(known-base*1.2)<1e-7
        assert abs(result['amiya_phase_reference']['opening_healing_reference']-known)<1e-7
        assert result['total_healing'] is None
        checks.append({'scope':'actual_medical_amiya_opening_healing_factor','unscaled_opening_reference':base,'scaled_known_reference':known,'actual_healing':None,'passed':True})
        # New section46-50 checks use only actual window controls and read-only cultivation.
        from rouge.operator_engine import selected_talents
        from rouge.gnosis_module_reference import DOT_NAME
        window.timing_scenario.clear();window.limit_window.setChecked(True)
        window.window_seconds.setValue(10);window.healing_targets.setValue(1);relics([])
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_4202_haruka' and key in ('bubble_bursts','levitate_triggers'):widget.setValue(0)
            if owner=='char_4202_haruka' and key=='haruka_repeat':widget.setChecked(False)
        cold=next(widget for owner,key,_skills,widget in window.model_option_widgets
                  if owner=='char_206_gnosis' and key=='cold_state')
        for stage in (1,2,3):
            train('char_206_gnosis',{'elite':2,'level':60,'potential':1,'trust':100,
                                   'module_id':'uniequip_004_gnosis','module_level':stage})
            cold.setValue(1)
            for skill in (1,2,3):
                window.skill.setCurrentIndex(window.skill.findData(skill))
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for horizon in (0,1):
                        window.window_seconds.setValue(horizon);result=calculate_result()
                        ref=result['gnosis_isw_a_reference']
                        assert ref['module_id']=='uniequip_004_gnosis' and ref['module_level']==stage
                        assert ref['original_talent']['blackboard']=={'cold':1,'damage_scale_cold':1.25,'damage_scale_freeze':1.5}
                        assert ref['original_talent']['prefab_key']=='1'
                        assert ref['original_talent']['talent_index']==0
                        assert not ref['original_talent']['module_coexistence_verified']
                        assert ref['dot_parameters']=={'atk_scale':.5,'interval':.5}
                        assert not ref['native_ability_attachment_verified'] and not ref['events_scheduled']
                        for key in ('actual_tick_count','actual_tick_times_seconds','actual_first_tick_seconds'):
                            assert ref[key] is None
                        records={r['prefab_key']:r for r in ref['module_records'] if r['kind']=='talent'}
                        if stage in (2,3):
                            assert set(records)=={'#','1','10_root','11_root'}
                            assert records['#']['blackboard']=={}
                            assert records['10_root']['blackboard']=={'cold':stage+1,'delay':.8}
                            assert records['11_root']['blackboard']=={'cold':1}
                            expected={'damage_scale_cold':1.25,'multi':2,'add':0,'max':1.5} if stage==2 else {'damage_scale_cold':1.3,'multi':2,'add':.05,'max':1.8}
                            assert records['1']['blackboard']==expected
                            assert records['10_root']['hidden'] and records['11_root']['hidden']
                            assert all(not r['attachment_verified'] for r in records.values())
                        else:assert records=={}
                        dot=next(c for c in result['components'] if c['name']==DOT_NAME)
                        assert dot['attack_scale_parameter']==.5 and dot['tick_interval_parameter_seconds']==.5
                        assert 'times_seconds' not in dot and dot['hits']==0
                        assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                        assert ref['actual_dot_damage']==0 if horizon==0 else ref['actual_dot_damage'] is None
                        assert ref['source_possible']['window']==bool(horizon)
                        assert '灵知ISW-A' in window.damage_text.toPlainText()
                        checks.append({'scope':'actual_gnosis_isw_a_module_cultivation_and_unknown_boundaries',
                            'stage':stage,'skill':skill,'mode':'frames' if use_frames else 'continuous',
                            'window':horizon,'actual_damage':result['total_damage'],'dot_parameters':ref['dot_parameters'],
                            'original_talent':ref['original_talent'],'module_records':ref['module_records'],'passed':True})
        # Explicitly reset all Haruka manual sources left by the earlier suite.
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_4202_haruka' and key in ('bubble_bursts','levitate_triggers'):widget.setValue(0)
            if owner=='char_4202_haruka' and key=='haruka_repeat':widget.setChecked(False)
        window.timing_scenario.clear();window.window_seconds.setValue(10)
        for stage in (1,2,3):
            train('char_4202_haruka',{'elite':2,'level':60,'potential':1,'trust':100,
                                    'module_id':'uniequip_002_haruka','module_level':stage})
            for skill in (1,3):
                window.skill.setCurrentIndex(window.skill.findData(skill))
                assert window.healing_targets.maximum()==2
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    window.healing_targets.setValue(1);one=calculate_result()
                    window.healing_targets.setValue(2);two=calculate_result()
                    assert one['total_healing']>0 and abs(two['total_healing']-one['total_healing']*2)<1e-7
                    assert two['haruka_healing_reference']['actual_target_count'] is None
                    assert not two['haruka_healing_reference']['native_attachment_verified']
                    checks.append({'scope':'actual_haruka_module_s1_s3_two_recipient_reference',
                        'stage':stage,'skill':skill,'mode':'frames' if use_frames else 'continuous',
                        'widget_maximum':2,'one_reference':one['total_healing'],'two_reference':two['total_healing'],'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(2))
            assert window.skill_rank_value()==10 and window.healing_targets.maximum()==3
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                window.healing_targets.setValue(3);result=calculate_result()
                assert result['total_healing'] is None and result['total_damage'] is None
                assert result['known_healing_subtotals']['window_healing']>0
                assert result['haruka_healing_reference']['additional_conditional_targets']==1
                assert result['haruka_healing_reference']['skill_target_add_parameter']==1
                checks.append({'scope':'actual_haruka_rank10_s2_extra_conditional_recipient',
                    'stage':stage,'mode':'frames' if use_frames else 'continuous','widget_maximum':3,
                    'actual_healing':None,'known_healing':result['known_healing_subtotals']['window_healing'],'passed':True})
        for module_id,module_level,expected in (('uniequip_002_haruka',1,2),(None,0,1)):
            train('char_4202_haruka',{'elite':2,'level':60,'potential':1,'trust':100,
                'module_id':module_id,'module_level':module_level},ranks={'1':4,'2':4,'3':4})
            window.skill.setCurrentIndex(window.skill.findData(2))
            window.update_skill_options();app.processEvents()
            assert window.skill_rank_value()==4 and window.healing_targets.maximum()==expected
            window.healing_targets.setValue(expected);result=calculate_result()
            assert window.damage_result['scenario']['skill_rank']==4
            assert result['haruka_healing_reference']['skill_target_add_parameter']==0
            assert result['haruka_healing_reference']['conditional_target_limit_reference']==expected
            checks.append({'scope':'actual_haruka_rank4_readonly_training_input_limit',
                'module_id':module_id,'module_level':module_level,'read_skill_rank':4,
                'widget_maximum':expected,'passed':True})
        low_cost=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_298_susuro' and key=='low_cost_healing_target')
        from PySide6.QtWidgets import QCheckBox
        assert isinstance(low_cost,QCheckBox)
        train('char_298_susuro',{'elite':2,'level':60,'potential':1,'trust':100,
                               'module_id':None,'module_level':0})
        window.healing_targets.setValue(1);window.window_seconds.setValue(10)
        window.timing_scenario.clear();relics([])
        for skill in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(skill))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                low_cost.setChecked(False);plain=calculate_result()
                low_cost.setChecked(True);qualified=calculate_result()
                assert window.damage_result['scenario']['low_cost_healing_target'] is True
                talents,_=selected_talents(module.catalog()['operators']['char_298_susuro'],window.damage_result['scenario'])
                factor=next(t['values']['heal_scale'] for t in talents if t['name']=='微创治疗')
                assert abs(qualified['estimate']['skill']['cycle_healing']-plain['estimate']['skill']['cycle_healing']*factor)<1e-7
                for key in ('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second'):
                    assert qualified['estimate']['skill'][key]==plain['estimate']['skill'][key]
                checks.append({'scope':'actual_susuro_low_cost_checkbox_whole_cycle_factor',
                    'skill':skill,'mode':'frames' if use_frames else 'continuous','selected_factor':factor,
                    'plain_cycle_healing':plain['estimate']['skill']['cycle_healing'],
                    'qualified_cycle_healing':qualified['estimate']['skill']['cycle_healing'],
                    'natural_sp_clocks_unchanged':True,'passed':True})
        window.select_operator('char_1037_amiya3');window.skill.setCurrentIndex(window.skill.findData(2))
        opening=next(widget for owner,key,_skills,widget in window.model_option_widgets
                     if owner=='char_1037_amiya3' and key=='amiya_hit_targets')
        assert opening.minimum()==1
        calculate_result()
        assert window.rank.text() and window.skill_rank_value()==window.damage_result['scenario']['skill_rank']
        checks.append({'scope':'actual_medical_amiya_public_minimum_and_readonly_rank','minimum':1,'passed':True})
        # Sections 51–55: actual available widgets; API booleans have no widget input.
        relics([]);window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        train('char_002_amiya',{'elite':2,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(1));window.frame_timing.setChecked(False)
        for timing in ({'target_disappears_seconds':.1},{'target_windows':[[0,1]]},{'target_windows':[]}):
            for horizon in (0,10):
                window.window_seconds.setValue(horizon);window.timing_scenario.setPlainText(json.dumps(timing))
                result=calculate_result();ref=result['amiya_continuous_reference'];skill=result['estimate']['skill']
                assert result['total_damage']==0 if horizon==0 or timing.get('target_windows')==[] else result['total_damage'] is None
                assert skill['recharge_seconds'] is None and skill['cycle_seconds'] is None
                assert result['timing']['phase_clock_unbound'] and not result['timing']['resource_and_damage_shared_clock']
                assert ref['native_clock_binding_verified'] is False
                assert '受限连续时序参考' in window.damage_text.toPlainText()
                assert result['scope']==result['estimate']['scenario_scope']
                checks.append({'scope':'actual_caster_amiya_restricted_continuous_inputs','timing':timing,'window':horizon,
                    'actual_damage':result['total_damage'],'actual_recharge':None,'actual_cycle':None,'passed':True})
        train('mechanist',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(2));window.shield_breaks.setValue(2)
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            for horizon,life in ((0,None),(10,None),(10,0)):
                window.window_seconds.setValue(horizon)
                window.timing_scenario.setPlainText(json.dumps({} if life is None else {'target_disappears_seconds':life}))
                result=calculate_result();ref=result['shield_break_reference'];actual=window.damage_text.toPlainText()
                assert result['total_damage']==0 if horizon==0 or life==0 else result['total_damage'] is None
                assert ref['hits_requested']==2 and ref['declared_count_damage_reference']>0
                assert ref['actual_break_times_seconds'] is None and ref['actual_end_seconds'] is None
                assert '实际破屏/爆炸时刻：未知' in actual and '仅实际屏障破碎' not in actual
                assert result['scope']==result['estimate']['scenario_scope']
                assert type(window.damage_result['scenario']['shield_break_count']) is int
                checks.append({'scope':'actual_mechanist_shield_count_and_window_controls','mode':'frames' if use_frames else 'continuous',
                    'window':horizon,'enemy_lifetime':life,'count':2,'actual_damage':result['total_damage'],'passed':True})
        for op,number,key in (('char_151_myrtle',2,'healing_targets'),('char_1037_amiya3',2,'amiya_hit_targets'),('char_4087_ines',2,'stolen_enemy_count')):
            train(op,{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
            window.skill.setCurrentIndex(window.skill.findData(number));window.timing_scenario.clear();window.window_seconds.setValue(10)
            widget=window.healing_targets if key=='healing_targets' else next(w for owner,k,_skills,w in window.model_option_widgets if owner==op and k==key)
            widget.setValue(1);result=calculate_result();args=window.damage_result['scenario']
            assert type(widget.value()) is int and type(args[key]) is int and args[key]==1
            for field in ('elite','level','potential','module_level'):assert type(args[field]) is int,(field,args[field])
            checks.append({'scope':'actual_supported_count_widgets_supply_integers','operator':op,'key':key,'value':1,'passed':True})
        locked_note='所选模组未满足当前精英阶段或等级门槛，本次未计模组基础属性与能力覆盖。'
        for op,module_id,below,gate,cap in (('mechanist','uniequip_002_mcnist',59,60,90),('char_298_susuro','uniequip_002_susuro',39,40,70)):
            for elite,level,locked in ((1,60,True),(2,below,True),(2,gate,False)):
                fields={'elite':elite,'level':level,'potential':1,'trust':100,'module_id':module_id,'module_level':3}
                train(op,fields,{'1':7,'2':7,'3':7});window.skill.setCurrentIndex(window.skill.findData(1))
                window.timing_scenario.clear();window.frame_timing.setChecked(True);window.window_seconds.setValue(10)
                result=calculate_result();actual=window.damage_text.toPlainText()
                assert (locked_note in actual)==locked
                assert result['estimate']['training']['module_id']==module_id
                assert result['estimate']['training']['module_level']==3
                if locked:
                    assert '当前模组基础属性已参与估算' not in actual and '已计模组基础属性与适用天赋数据覆盖' not in actual
                    plain={**fields,'module_id':None,'module_level':0};stats=result['estimate']['base_stats']
                    train(op,plain,{'1':7,'2':7,'3':7});window.skill.setCurrentIndex(window.skill.findData(1))
                    assert calculate_result()['estimate']['base_stats']==stats
                checks.append({'scope':'actual_readonly_module_request_respects_qualification','operator':op,'elite':elite,'level':level,
                    'module_id':module_id,'module_level':3,'locked':locked,'passed':True})
        receipt['api_boolean_guard_scope']='API rejection is verified by regression; actual Qt numeric controls emit integers and cannot submit booleans.'
        # Sections56-60: actual Qt controls and calculation button; no Wine run
        # has been performed merely by authoring this external draft.
        supplemental_start=len(checks)
        from copy import deepcopy
        from PySide6.QtWidgets import QPlainTextEdit,QSpinBox
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        supplemental_button=next(b for b in window.findChildren(QPushButton)
                                 if b.text()=='计算属性与技能预估')
        assert supplemental_button.isVisible() and supplemental_button.isEnabled()
        def click_result():
            supplemental_button.click();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert window.damage_text.toPlainText()==format_report(
                result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
            return result
        def clock_zero(value):
            payload=json.dumps({'target_disappears_seconds':value},ensure_ascii=False)
            window.timing_scenario.setPlainText(payload)
            result=click_result()
            submitted=window.damage_result['scenario']['timing']['target_disappears_seconds']
            assert type(submitted) is type(value) and submitted==value
            assert window.timing_scenario.toPlainText()==payload
            return result
        assert isinstance(window.timing_scenario,QPlainTextEdit)
        window.damage_technical.setChecked(False);relics([])
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        # The string is entered in an existing JSON text field, never in a
        # numeric spinbox. The API's full87-skill aliases remain regression scope.
        for op,number,level in (('char_002_amiya',1,80),
                                ('char_298_susuro',1,60),('mechanist',2,90)):
            train(op,{'elite':2,'level':level,'potential':1,'trust':100,
                      'module_id':None,'module_level':0})
            window.skill.setCurrentIndex(window.skill.findData(number))
            window.healing_targets.setValue(1);window.shield_breaks.setValue(2)
            window.shield_duration_known.setChecked(False);low_cost.setChecked(False)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                numeric=deepcopy(clock_zero(0))
                assert numeric['total_damage']==0
                if op=='char_298_susuro':assert numeric['total_healing']>0
                if op=='char_002_amiya' and not use_frames:
                    assert numeric['estimate']['skill']['initial_seconds']==7
                    assert numeric['estimate']['skill']['recharge_seconds']==30
                    assert numeric['estimate']['skill']['cycle_seconds']==60
                if op=='mechanist':
                    assert numeric['shield_break_reference']['declared_count_damage_reference']>0
                for alias in ('0','0.0','-0'):
                    aliased=clock_zero(alias)
                    assert aliased==numeric,(op,number,use_frames,alias)
                    checks.append({'scope':'actual_json_text_zero_lifetime_alias',
                        'section':56,'operator':op,'skill':number,
                        'mode':'frames' if use_frames else 'continuous','alias':alias,
                        'input_widget':'QPlainTextEdit JSON, not a numeric spinbox',
                        'complete_result_equal_to_numeric_zero':True,
                        'caller_json_text_and_raw_string_preserved':True,
                        'enemy_damage':0,'friendly_healing':aliased.get('total_healing'),
                        'passed':True})
        receipt['section56_input_scope']='Actual timing_scenario JSON text and calculate button verify three zero strings on three representative skills in both modes; numeric spinboxes do not emit strings. Full87-skill API equivalence is separate regression coverage.'

        # Section57 does not simulate booleans accepted by numeric widgets.
        # Its four declared counts are real QSpinBox values with existing limits.
        window.timing_scenario.clear();relics([])
        for op,number,key,widget,upper in (
                ('mechanist',2,'shield_break_count',window.shield_breaks,100),
                ('mechanist',3,'charge_count',window.charge_count,100),
                ('silverash',2,'activation_count',window.activation_count,100),
                ('silverash',2,'deployment_stacks',window.stacks,2)):
            train(op,{'elite':2,'level':90,'potential':1,'trust':100,
                      'module_id':None,'module_level':0})
            window.skill.setCurrentIndex(window.skill.findData(number))
            window.timing_scenario.clear();window.window_seconds.setValue(10)
            window.activation_count.setValue(1);window.stacks.setValue(0)
            window.shield_breaks.setValue(0);window.charge_count.setValue(0)
            assert isinstance(widget,QSpinBox)
            assert widget.minimum()==0 and widget.maximum()==upper
            assert widget.isVisible() and widget.isEnabled(),key
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for value in (0,1,upper):
                    widget.setValue(value);result=click_result()
                    args=window.damage_result['scenario']
                    assert type(widget.value()) is int and widget.value()==value
                    assert type(args[key]) is int and args[key]==value
                    if key=='shield_break_count':
                        ref=result['shield_break_reference']
                        assert ref['hits_requested']==value
                        assert (ref['declared_count_damage_reference']==0)==(value==0)
                        assert result['total_damage']==0 if value==0 else result['total_damage'] is None
                    if key=='charge_count':
                        if value:
                            ref=result['charge_reference']
                            assert ref['hits_requested']==value
                            assert ref['declared_count_damage']==ref['per_hit_damage']*value
                            assert ref['collision_times_seconds'] is None
                            assert ref['events_scheduled'] is False
                            assert ref['full_cast_count_verified'] is False
                        else:
                            assert 'charge_reference' not in result
                    checks.append({'scope':'actual_declared_count_spinbox_range_and_type',
                        'section':57,'operator':op,'skill':number,'key':key,
                        'mode':'frames' if use_frames else 'continuous',
                        'widget':'QSpinBox','minimum':0,'maximum':upper,
                        'widget_value':value,'serialized_type':'int','passed':True})
            # Verify Qt's configured limits with integers, without claiming an
            # API100 cap or inventing native counts/ammunition-source ownership.
            widget.setValue(-1);assert widget.value()==0
            widget.setValue(upper+1);assert widget.value()==upper
            widget.setValue(0)
        receipt['section57_input_scope']='Four actual QSpinBox controls emit int and retain GUI0..100/stack0..2 limits. Boolean API rejection and accepted API counts above GUI bounds are regression coverage, not fake GUI inputs or native event caps.'

        # Section58: only synthetic public state in the already isolated window.
        # No saved/private run, recognition frame or recruitment event is read.
        assert module.RUN_STATE.parent==isolated and module.OPERATOR_STATE.parent==isolated
        state_snapshot=deepcopy(window.run.state)
        account_snapshot=deepcopy(window.operator_observations)
        run_training_snapshot=window.use_run_training.isChecked()
        emergency_relic='rogue_6_relic_cargo_10';op='silverash'
        fields={'elite':2,'level':90,'potential':1,'trust':100,
                'module_id':None,'module_level':0}
        ranks={'1':10,'2':10,'3':10}
        def inject_origin(kind,scope='run'):
            member={'id':op,'scope':scope,'present':True,'fields':deepcopy(fields),
                    'skill_ranks':dict(ranks),'recruitment_kind':kind,
                    'char_buff_ids':[],'char_buffs_complete':False}
            window.run.state['operators']={op:member} if scope=='run' else {}
            window.operator_observations[op]={**deepcopy(member),'scope':'account'}
            window.select_operator(op);window.update_operator()
            window.skill.setCurrentIndex(window.skill.findData(3))
            window.timing_scenario.clear();window.window_seconds.setValue(3)
        def emergency_record(result):
            return next(record for record in result['relic_resolution']['records']
                        if record['id']==emergency_relic)
        try:
            window.use_run_training.setChecked(True)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                inject_origin(None);relics([]);plain=deepcopy(click_result())
                relics([emergency_relic]);pending_reference=None
                for kind in (None,'unknown','non_emergency','emergency_hire'):
                    inject_origin(kind);result=click_result();record=emergency_record(result)
                    args=window.damage_result['scenario']
                    assert args['recruitment_kind']==kind
                    assert window.current_operator_state()['scope']=='run'
                    if kind in (None,'unknown'):
                        assert record['status']=='incomplete'
                        assert record['missing_conditions']==['emergency_hire']
                        assert record['applied']==[]
                        assert result['relic_resolution']['complete'] is False
                        assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                        actual_human=window.damage_text.toPlainText()
                        assert '同行者：条件缺失或机制未覆盖；缺 应急招募来源' in actual_human
                        assert '同行者：尚未确认条件 应急招募来源，未按0或满层套用。' in actual_human
                        assert 'emergency_hire' not in actual_human
                        if kind is None:pending_reference=deepcopy(result)
                        else:assert result==pending_reference
                    else:
                        assert record['status']=='applied' and not record['missing_conditions']
                        assert result['relic_resolution']['complete'] is True
                        assert len(record['applied'])==3
                        factor=.4 if kind=='emergency_hire' else 0
                        assert {effect['kind'] for effect in record['applied']}=={'attack_pct','hp_pct','defense_pct'}
                        assert all(effect['value']==factor for effect in record['applied'])
                        if kind=='non_emergency':
                            assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                        else:
                            assert abs(result['estimate']['base_stats']['attack']-
                                       plain['estimate']['base_stats']['attack']*1.4)<1e-7
                            assert '应急雇佣' in window.training_status.text()
                    checks.append({'scope':'actual_isolated_run_recruitment_source_condition',
                        'section':58,'mode':'frames' if use_frames else 'continuous',
                        'operator':op,'state_injection':'temporary in-memory public state only',
                        'recruitment_kind':kind,'serialized_kind':args['recruitment_kind'],
                        'missing_conditions':record['missing_conditions'],
                        'applied_effects':record['applied'],
                        'base_attack':result['estimate']['base_stats']['attack'],'passed':True})
                # Account-only source is not a confirmed current-run source.
                inject_origin('emergency_hire',scope='account')
                result=click_result();record=emergency_record(result)
                assert window.damage_result['scenario']['recruitment_kind'] is None
                assert record['missing_conditions']==['emergency_hire'] and not record['applied']
                assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                checks.append({'scope':'actual_account_recruitment_source_not_used_for_run_condition',
                    'section':58,'mode':'frames' if use_frames else 'continuous',
                    'account_kind':'emergency_hire','submitted_kind':None,'passed':True})
                inject_origin('emergency_hire');window.use_run_training.setChecked(False)
                result=click_result();record=emergency_record(result)
                assert window.damage_result['scenario']['recruitment_kind'] is None
                assert record['missing_conditions']==['emergency_hire'] and not record['applied']
                checks.append({'scope':'actual_run_training_toggle_preserves_source_boundary',
                    'section':58,'mode':'frames' if use_frames else 'continuous',
                    'run_training_enabled':False,'submitted_kind':None,'passed':True})
                window.use_run_training.setChecked(True)
        finally:
            window.run.state=state_snapshot
            window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy(account_snapshot));assert window.operator_observations is window.account_cache.records
            window.use_run_training.setChecked(run_training_snapshot)
            window.update_operator();relics([])
        receipt['section58_state_scope']='Recruitment origins are injected only into this temporary MainWindow public in-memory state, then restored. This checks current_operator_state, the real run-training checkbox, scenario serialization, relic pending/known output and report; no actual OCR/recruitment/private-state lifecycle is certified.'

        # Section59: source-specific unknown reports and known magic subtotals.
        # New complete sentences may be refined by root; stable source labels,
        # actual unknown boundaries and the absence of an unselected relic bind.
        from rouge.river_effects import RELIC_ID as river_id
        train('char_1042_phatm2',{'elite':2,'level':60,'potential':1,'trust':100,
                                'module_id':None,'module_level':0})
        window.target_enemy.setCurrentIndex(0)
        assert window.target_enemy.currentData() is None
        window.defense.setValue(0);window.resistance.setValue(0)
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_1042_phatm2':
                default=next(entry[2] for entry in module.OPTIONS[owner] if entry[0]==key)
                widget.setChecked(default) if isinstance(widget,QCheckBox) else widget.setValue(default)
        incoming=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_1042_phatm2' and key=='enemy_attack_count')
        for number,horizon,count,reference_key,label in (
                (1,1,0,'neural_s1_reference','暗夜回声 · 束缚倍率待核验'),
                (2,30,20,'neural_incoming_reference','堕梦 · 目标攻击时间待确认')):
            window.skill.setCurrentIndex(window.skill.findData(number))
            incoming.setValue(count);window.timing_scenario.clear()
            window.limit_window.setChecked(True);window.window_seconds.setValue(horizon);relics([])
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames);result=click_result()
                actual=window.damage_text.toPlainText();skill=result['estimate']['skill']
                subtotal=result['known_damage_subtotals']['window_damage']
                section=next(s for s in result['report']['sections'] if s['id']=='known_damage_subtotals')
                assert result['total_damage'] is None and skill['window_damage'] is None
                assert result['complete'] is False and result['estimate']['complete'] is False
                assert subtotal>0
                assert abs(subtotal-sum(c['total'] for c in result['components']
                                       if c['damage_type']=='magic'))<1e-7
                assert reference_key in result and 'neural_relic_reference' not in result
                assert not any(r['id']==river_id for r in result['relic_resolution']['records'])
                assert window.damage_result['scenario']['relic_ids']==[]
                assert '河谷祭祈' not in actual
                assert label in actual and '观察窗口已计伤害小计' in actual
                assert any('不能当作完整' in note for note in section['notes'])
                source_note=('暗夜回声的束缚倍率首次生效与刷新顺序尚未核验；小计不含受其影响的未知神经爆发。'
                             if number==1 else
                             '堕梦的目标普通攻击次数没有事件时刻；小计不含受其影响的未知神经爆发。')
                assert source_note in section['notes'] and source_note in actual
                assert all('河谷祭祈' not in note for note in section['notes'])
                if number==1:assert 'neural_incoming_reference' not in result
                else:
                    assert 'neural_s1_reference' not in result and 'neural_bait_reference' not in result
                    assert '目标首个普通攻击时刻：未知' in actual and '观察窗口总伤：未知' in actual
                checks.append({'scope':'actual_no_river_damage_subtotal_source',
                    'section':59,'operator':'char_1042_phatm2','skill':number,
                    'mode':'frames' if use_frames else 'continuous',
                    'enemy_attack_count':count,'window_seconds':horizon,
                    'actual_damage':None,'known_magic_window_subtotal':subtotal,
                    'subtotal_notes':section['notes'],'source_label':label,
                    'unselected_river_name_absent':True,'passed':True})
        # A truly selected River still has its named, independently scoped info.
        window.frame_timing.setChecked(True);relics([river_id]);result=click_result()
        assert any(r['id']==river_id for r in result['relic_resolution']['records'])
        assert '河谷祭祈' in window.damage_text.toPlainText()
        assert result['total_damage'] is None and result['estimate']['skill']['window_damage'] is None
        checks.append({'scope':'actual_selected_river_reference_report_preserved',
            'section':59,'operator':'char_1042_phatm2','skill':2,
            'actual_damage':None,'selected_relic':river_id,'passed':True})
        # Held River supplies independent mechanism documentation without
        # attributing an unplaced shield subtotal to an absent neural source.
        train('mechanist',{'elite':2,'level':90,'potential':1,'trust':100,
                          'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(2))
        window.shield_breaks.setValue(2);window.shield_duration_known.setChecked(False)
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        window.timing_scenario.clear();relics([river_id])
        generic_subtotal_note='这些数值只包含已保留的本体来源参考，不含未核验的次生事件，不能当作完整输出。'
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);result=click_result()
            actual=window.damage_text.toPlainText()
            section=next(s for s in result['report']['sections'] if s['id']=='known_damage_subtotals')
            assert result['total_damage'] is None and 'neural_relic_reference' not in result
            assert result['shield_break_reference']['hits_requested']==2
            assert result['shield_break_reference']['actual_break_times_seconds'] is None
            assert any(r['id']==river_id for r in result['relic_resolution']['records'])
            assert section['notes']==[generic_subtotal_note]
            assert generic_subtotal_note in actual
            assert all('河谷祭祈' not in note for note in section['notes'])
            assert any(s['id']=='river_limits' for s in result['report']['sections'])
            assert '河谷祭祈 · 已知边界与待确认' in actual
            assert '实际破屏/爆炸时刻：未知' in actual
            checks.append({'scope':'actual_held_river_reference_does_not_supply_shield_subtotal_source',
                'section':59,'operator':'mechanist','skill':2,
                'mode':'frames' if use_frames else 'continuous','shield_break_count':2,
                'selected_relic':river_id,'actual_damage':None,
                'neural_relic_reference_present':False,'subtotal_notes':section['notes'],
                'river_independent_reference_preserved':True,'passed':True})
        relics([]);window.timing_scenario.clear()
        # Section60 uses finalized source parameters and public API contracts.
        # This real checkbox selects a declared squad condition, not a clock.
        shu_widgets={key:widget for owner,key,_skills,widget in window.model_option_widgets
                     if owner=='char_2025_shu'}
        four_sui=shu_widgets['four_sui']
        assert isinstance(four_sui,QCheckBox)
        for key,widget in shu_widgets.items():widget.setChecked(False)
        train('char_2025_shu',{'elite':2,'level':90,'potential':1,'trust':100,
                             'module_id':None,'module_level':0})
        window.healing_targets.setValue(1);relics([])
        window.target_enemy.setCurrentIndex(0)
        assert window.target_enemy.currentData() is None
        window.defense.setValue(0);window.resistance.setValue(0)
        window.limit_window.setChecked(True);window.timing_scenario.clear()
        def assert_shu_clock(result,plain,number,use_frames,horizon,enemy_lifetime=None):
            args=window.damage_result['scenario'];skill=result['estimate']['skill']
            ref=result['shu_periodic_sp_reference'];actual=window.damage_text.toPlainText()
            assert args['four_sui'] is True and type(four_sui.isChecked()) is bool
            assert abs(result['estimate']['base_stats']['attack']-
                       plain['estimate']['base_stats']['attack']*1.12)<1e-7
            assert ref['interval_seconds_parameter']==4
            assert ref['sp_per_pulse_parameter']==1
            assert ref['attack_bonus_parameter']==.12
            assert skill['sp_recovery_per_second']==1
            for field in ('first_tick_seconds','actual_tick_times_seconds','clock_origin',
                          'reset_rule','blocked_credit_rule'):assert ref[field] is None,field
            for field in ('native_attachment_verified','clock_verified','events_scheduled'):
                assert ref[field] is False,field
            assert ref['independent_sp_clock_reference']['excludes_four_sui_periodic_credit'] is True
            for field in ('initial_seconds','recharge_seconds','cycle_seconds',
                          'cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
                assert skill[field] is None,(number,field,skill[field])
            assert skill['window_seconds']==horizon
            if horizon==0:
                assert result['total_damage']==0 and result['total_healing']==0
            if enemy_lifetime==0:
                assert result['total_damage']==0 and result['total_healing']>0
            assert result['timing']['phase_clock_unbound'] is True
            assert result['timing']['resource_and_damage_shared_clock'] is False
            assert result['complete'] is False and result['estimate']['complete'] is False
            assert result['scope']==result['estimate']['scenario_scope']
            assert any(section['id']=='shu_periodic_sp' for section in result['report']['sections'])
            assert '天有四时 · 周期技力待核验' in actual
            assert '实际周期首跳：未知' in actual and '结束后充能：未知' in actual
            checks.append({'scope':'actual_shu_four_sui_checkbox_periodic_sp_boundary',
                'section':60,'operator':'char_2025_shu','skill':number,
                'mode':'frames' if use_frames else 'continuous','window_seconds':horizon,
                'enemy_lifetime_seconds':enemy_lifetime,'widget':'QCheckBox',
                'four_sui_condition':True,'natural_sp_per_second':skill['sp_recovery_per_second'],
                'attack_bonus_parameter':ref['attack_bonus_parameter'],
                'periodic_interval_parameter':ref['interval_seconds_parameter'],
                'periodic_sp_parameter':ref['sp_per_pulse_parameter'],
                'actual_first_tick':None,'actual_recharge':None,'actual_cycle':None,
                'resource_clock_unbound':True,'passed':True})
        for number in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(number))
            assert four_sui.isVisible() and four_sui.isEnabled()
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for horizon in (0,10):
                    window.window_seconds.setValue(horizon);window.timing_scenario.clear()
                    four_sui.setChecked(False);plain=deepcopy(click_result())
                    assert 'shu_periodic_sp_reference' not in plain
                    four_sui.setChecked(True);result=click_result()
                    assert_shu_clock(result,plain,number,use_frames,horizon)
        # Empty enemy lifetime does not prove a friendly resource source absent.
        window.skill.setCurrentIndex(window.skill.findData(2));window.window_seconds.setValue(10)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            four_sui.setChecked(False);plain=deepcopy(click_result())
            four_sui.setChecked(True);result=click_result()
            assert_shu_clock(result,plain,2,use_frames,10,enemy_lifetime=0)
        # The same real checkbox below the original E2 talent gate adds nothing.
        train('char_2025_shu',{'elite':1,'level':80,'potential':1,'trust':100,
                             'module_id':None,'module_level':0},ranks={'1':7,'2':7})
        window.window_seconds.setValue(10);window.timing_scenario.clear()
        for number in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(number))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                four_sui.setChecked(False);plain=deepcopy(click_result())
                four_sui.setChecked(True);result=click_result()
                assert result==plain and 'shu_periodic_sp_reference' not in result
                checks.append({'scope':'actual_shu_four_sui_checkbox_original_talent_qualification',
                    'section':60,'operator':'char_2025_shu','elite':1,'skill':number,
                    'mode':'frames' if use_frames else 'continuous','skill_rank':7,
                    'four_sui_condition':True,'full_result_equal_to_unselected':True,'passed':True})
        four_sui.setChecked(False);window.timing_scenario.clear();relics([])
        receipt['section60_input_scope']='The actual four_sui QCheckBox declares a squad condition; E2 static attack bonus and original4s/1SP parameters remain, actual pulse/resource clocks remain unknown in empty and positive observation windows, and the E1 talent gate still excludes the effect. No first tick, owner clock, reset, blocked credit or native event was inferred.'

        supplemental_end=len(checks)
        receipt['supplemental_sections']=[56,57,58,59,60]
        receipt['supplemental_checks_56_60']=supplemental_end-supplemental_start
        assert receipt['supplemental_checks_56_60']==79,receipt['supplemental_checks_56_60']
        receipt['section60_final_checks_pending']=False
        assert receipt['section60_final_checks_pending'] is False,'Section60 source review is not finalized; do not treat this candidate as a complete UI runner'
        # Root freezes integrated source after commit; API probing is not GUI proof.

        # Sections61-65: real Qt producers, not invented bool/text spinbox input.
        new_start=len(checks);new_section_counts={}
        def strict_json(value):
            return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)
        from rouge.operator_options import OPTIONS
        option_widgets={(owner,key):widget for owner,key,_skills,widget in window.model_option_widgets}
        def reset_owner_options(owner):
            for key,label,default,maximum,skills in OPTIONS.get(owner,[]):
                widget=option_widgets[(owner,key)]
                widget.setChecked(default) if isinstance(widget,QCheckBox) else widget.setValue(default)
        def report_metrics(result,section_id):
            sections=[section for section in result['report']['sections'] if section['id']==section_id]
            assert len(sections)==1,(section_id,len(sections))
            return {row['key']:row['value'] for row in sections[0]['metrics']}
        window.damage_technical.setChecked(False);window.timing_scenario.clear();relics([])
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        assert window.target_enemy.currentData() is None

        #61: all24 existing owner/key integer controls, covering23 distinct keys.
        # Raw bool rejection is API regression scope; real QSpinBox emits int.
        count_fields={'summon_count','casts_used','slash_kills','amiya_slash_kills',
            'incoming_hits','shield_contact_ticks','cold_state','dash_hits','bubble_bursts',
            'levitate_triggers','snow_entries','drone_warmup_hits','note_count',
            'bait_triggers','enemy_attack_count','palsy_triggers','palsy_overflow_hits',
            'connected_stones','trap_triggers','trap_dot_ticks','dragon_arrow_hits',
            'ghost_count','ghost_casts'}
        integer_controls=[(owner,key,default,maximum,skills)
            for owner,entries in OPTIONS.items() for key,label,default,maximum,skills in entries
            if key in count_fields]
        assert len(integer_controls)==24 and {row[1] for row in integer_controls}==count_fields
        section_start=len(checks)
        for owner,key,default,maximum,skills in integer_controls:
            profile=module.catalog()['operators'][owner]
            train(owner,{'elite':2,'level':profile['phases'][2]['max_level'],'potential':1,
                         'trust':100,'module_id':None,'module_level':0})
            number=skills[0];window.skill.setCurrentIndex(window.skill.findData(number))
            reset_owner_options(owner);window.healing_targets.setValue(1)
            widget=option_widgets[(owner,key)]
            assert isinstance(widget,QSpinBox) and widget.isVisible() and widget.isEnabled()
            assert widget.minimum()==0 and widget.maximum()==(4 if key=='summon_count' else maximum)
            if key=='ghost_casts':option_widgets[(owner,'ghost_count')].setValue(1)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for value in (0,1):
                    widget.setValue(value);result=click_result();args=window.damage_result['scenario']
                    assert type(widget.value()) is int and type(args[key]) is int
                    assert args[key]==value
                    assert args['timing_mode']==('frames' if use_frames else 'continuous')
                    checks.append({'scope':'actual_all_integer_option_spinbox_serializer',
                        'section':61,'operator':owner,'skill':number,'key':key,
                        'mode':args['timing_mode'],'value':value,'widget':'QSpinBox',
                        'submitted_type':'int','gui_minimum':widget.minimum(),
                        'gui_maximum':widget.maximum(),'calculation_returned':True,'passed':True})
            widget.setValue(default)
        new_section_counts[61]=len(checks)-section_start
        assert new_section_counts[61]==len(integer_controls)*2*2
        receipt['section61_input_scope']='All24 real owner/key QSpinBox controls emit integer0/1;23 distinct queried keys are covered. API raw bool errors are separate regression evidence. GUI maximums are control limits, not new native stock/event/deployment caps.'

        #62: true/false are actual checkbox values above and below the E2 gate.
        section_start=len(checks);four_sui=option_widgets[('char_2025_shu','four_sui')]
        for elite,number,rank in ((2,3,10),(1,2,7)):
            train('char_2025_shu',{'elite':elite,'level':90 if elite==2 else 80,
                'potential':1,'trust':100,'module_id':None,'module_level':0},
                ranks={'1':rank,'2':rank,'3':rank})
            reset_owner_options('char_2025_shu');window.skill.setCurrentIndex(window.skill.findData(number))
            window.window_seconds.setValue(10);window.timing_scenario.clear()
            assert isinstance(four_sui,QCheckBox) and four_sui.isVisible() and four_sui.isEnabled()
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames);plain=None
                for flag in (False,True):
                    four_sui.setChecked(flag);result=click_result();args=window.damage_result['scenario']
                    assert type(four_sui.isChecked()) is bool and args['four_sui'] is flag
                    if not flag:
                        plain=deepcopy(result);assert 'shu_periodic_sp_reference' not in result
                    elif elite==1:
                        assert strict_json(result)==strict_json(plain)
                        assert 'shu_periodic_sp_reference' not in result
                    else:
                        ref=result['shu_periodic_sp_reference'];skill=result['estimate']['skill']
                        assert abs(result['estimate']['base_stats']['attack']-
                                   plain['estimate']['base_stats']['attack']*1.12)<1e-7
                        assert ref['interval_seconds_parameter']==4 and ref['sp_per_pulse_parameter']==1
                        assert ref['first_tick_seconds'] is None and ref['clock_verified'] is False
                        assert ref['events_scheduled'] is False
                        assert skill['initial_seconds'] is None and skill['recharge_seconds'] is None
                        assert skill['cycle_seconds'] is None
                        assert '实际周期首跳：未知' in window.damage_text.toPlainText()
                    checks.append({'scope':'actual_four_sui_typed_bool_qualification',
                        'section':62,'operator':'char_2025_shu','elite':elite,'skill':number,
                        'mode':args['timing_mode'],'value':flag,'widget':'QCheckBox',
                        'submitted_type':'bool','talent_qualified':elite==2,
                        'periodic_clock_verified':False,'passed':True})
        four_sui.setChecked(False);new_section_counts[62]=len(checks)-section_start
        assert new_section_counts[62]==8
        receipt['section62_input_scope']='Existing four_sui QCheckBox serializes genuine bool False/True; E1 excludes the talent, E2 preserves static attack and original4s/1SP parameters with actual resource clocks unknown. API text refusal cannot be submitted through this checkbox and is covered by regression.'

        #63: real declared integer count and original cultivation/module caps.
        section_start=len(checks);deepcl='char_110_deepcl';mod='uniequip_002_deepcl'
        count_widget=option_widgets[(deepcl,'summon_count')]
        deepcl_training=[({'elite':0,'level':45,'module_id':None,'module_level':0},4,2),
            ({'elite':1,'level':60,'module_id':None,'module_level':0},7,3),
            ({'elite':2,'level':70,'module_id':None,'module_level':0},10,4),
            ({'elite':2,'level':39,'module_id':mod,'module_level':3},10,4),
            ({'elite':2,'level':40,'module_id':mod,'module_level':1},10,7),
            ({'elite':2,'level':40,'module_id':mod,'module_level':2},10,7),
            ({'elite':2,'level':40,'module_id':mod,'module_level':3},10,7)]
        expected63=0
        for fields,rank,cap in deepcl_training:
            train(deepcl,{**fields,'potential':1,'trust':100},
                  ranks={'1':rank,'2':rank})
            reset_owner_options(deepcl)
            for number in ((1,) if fields['elite']==0 else (1,2)):
                window.skill.setCurrentIndex(window.skill.findData(number))
                assert isinstance(count_widget,QSpinBox) and count_widget.isVisible() and count_widget.isEnabled()
                assert count_widget.minimum()==0 and count_widget.maximum()==cap
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for value in (0,1,cap):
                        count_widget.setValue(value);result=click_result();args=window.damage_result['scenario']
                        assert type(args['summon_count']) is int and args['summon_count']==value
                        rates=report_metrics(result,'summons')
                        assert type(rates['summon_count']) is int and rates['summon_count']==value
                        assert rates['concurrent_limit']==cap
                        if number==1:
                            regeneration=report_metrics(result,'regeneration')
                            bb=module.catalog()['operators'][deepcl]['skills'][0]['levels'][rank-1]['values']
                            assert regeneration['per_token_rate']==bb['hp_recovery_per_sec']
                            assert regeneration['all_tokens_rate']==bb['hp_recovery_per_sec']*value
                        if cap==7:
                            module_metrics=report_metrics(result,'relic_token_token_10001_deepcl_tentac')
                            assert type(module_metrics['model_count']) is int and module_metrics['model_count']==value
                            assert module_metrics['held_limit']==7 and module_metrics['concurrent_limit']==7
                            assert '关卡可用部署位、地块和当前库存约束' in window.damage_text.toPlainText()
                        assert '局外假设' in window.damage_text.toPlainText()
                        checks.append({'scope':'actual_deepcolor_declared_integer_count_report',
                            'section':63,'operator':deepcl,'skill':number,'skill_rank':rank,
                            'elite':fields['elite'],'level':fields['level'],'module_id':fields['module_id'],
                            'module_level':fields['module_level'],'mode':args['timing_mode'],
                            'value':value,'widget':'QSpinBox','submitted_type':'int',
                            'gui_concurrent_cap':cap,'actual_stock_or_deployment_clock_verified':False,'passed':True})
                        expected63+=1
        count_widget.setValue(1);new_section_counts[63]=len(checks)-section_start
        assert new_section_counts[63]==expected63
        receipt['section63_input_scope']='Actual Deepcolor QSpinBox produces declared integer0/1/currentcap with existing E0/E1/E2 and SUM-Y unlock gates, typed report counts and S1 fixed per-token regeneration reference. Legal API numeric strings are verified separately; no actual stock, presence, concurrency, deployment event or recovery tick is inferred.'

        #64: select both real checkbox states; never infer the API flag from GUI default.
        section_start=len(checks)
        train('silverash',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(3));window.window_seconds.setValue(10)
        window.timing_scenario.clear()
        assert isinstance(window.fragile,QCheckBox) and window.fragile.isVisible() and window.fragile.isEnabled()
        assert isinstance(window.cooperative,QCheckBox) and window.cooperative.isVisible()
        for rank in (1,7,10):
            train('silverash',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
                  ranks={'1':rank,'2':rank,'3':rank})
            window.skill.setCurrentIndex(window.skill.findData(3))
            factor=module.catalog()['operators']['silverash']['skills'][2]['levels'][rank-1]['values']['damage_scale']
            assert factor==({1:1.15,7:1.25,10:1.3}[rank])
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for cooperation in (False,True):
                    window.cooperative.setChecked(cooperation);plain=None
                    for flag in (False,True):
                        window.fragile.setChecked(flag);result=click_result();args=window.damage_result['scenario']
                        assert args['preexisting_fragile'] is flag and type(window.fragile.isChecked()) is bool
                        assert args['cooperative'] is cooperation and type(window.cooperative.isChecked()) is bool
                        components=result['components']
                        assert [row['name'] for row in components]==(['本体丹增','协同丹增'] if cooperation else ['本体丹增'])
                        assert all(row['damage_type']=='physical' for row in components)
                        if not flag:plain=deepcopy(result)
                        else:
                            assert abs(result['total_damage']-plain['total_damage']*factor)<1e-7
                            for old,row in zip(plain['components'],components):
                                assert row['hits']==old['hits']
                                assert abs(row['per_hit']-old['per_hit']*factor)<1e-7
                        checks.append({'scope':'actual_fragile_and_cooperative_typed_checkbox_controls',
                            'section':64,'operator':'silverash','skill':3,'skill_rank':rank,
                            'mode':args['timing_mode'],'preexisting_fragile':flag,'cooperative':cooperation,
                            'submitted_types':'bool/bool','selected_skill_factor':factor,
                            'native_attachment_or_overlap_rule_verified':False,'passed':True})
        train('silverash',{'elite':1,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0},
              ranks={'1':7,'2':7})
        assert window.skill.findData(3)==-1
        window.skill.setCurrentIndex(window.skill.findData(2))
        assert not window.fragile.isVisible() and not window.cooperative.isVisible()
        window.cooperative.setChecked(False)
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);plain=None
            for flag in (False,True):
                window.fragile.setChecked(flag);result=click_result();args=window.damage_result['scenario']
                assert args['preexisting_fragile'] is flag
                if not flag:plain=deepcopy(result)
                else:assert strict_json(result)==strict_json(plain)
                checks.append({'scope':'actual_fragile_checkbox_inactive_skill_qualification',
                    'section':64,'operator':'silverash','elite':1,'skill':2,'skill_rank':7,
                    'mode':args['timing_mode'],'preexisting_fragile':flag,
                    's3_unavailable':True,'checkbox_hidden':True,'passed':True})
        window.fragile.setChecked(False);window.cooperative.setChecked(False)
        new_section_counts[64]=len(checks)-section_start
        assert new_section_counts[64]==3*2*2*2+2*2
        receipt['section64_input_scope']='Actual fragile/cooperative QCheckBox states serialize bool, preserve chosen S3 rank1/7/10 factor1.15/1.25/1.3 and physical component arithmetic; E1 excludes S3 and hides these controls for S2. Text rejection is API-only regression. No first-hit attachment, overlapping-source identity, max-source composition or native dynamic coverage is certified.'

        #65: only real integer bait count; original positive/empty boundary remains.
        section_start=len(checks);phatm='char_1042_phatm2'
        train(phatm,{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        reset_owner_options(phatm);window.skill.setCurrentIndex(window.skill.findData(2))
        bait=option_widgets[(phatm,'bait_triggers')]
        assert isinstance(bait,QSpinBox) and bait.isVisible() and bait.isEnabled()
        assert bait.minimum()==0 and bait.maximum()==100
        scopes=[('positive',10,{}),('zero_window',0,{}),
                ('zero_lifetime',10,{'target_disappears_seconds':0}),
                ('empty_target_windows',10,{'target_windows':[]})]
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            for scope_name,horizon,timing in scopes:
                window.window_seconds.setValue(horizon)
                window.timing_scenario.setPlainText(json.dumps(timing) if timing else '')
                for value in (0,1):
                    bait.setValue(value);result=click_result();args=window.damage_result['scenario']
                    assert type(bait.value()) is int and type(args['bait_triggers']) is int
                    assert args['bait_triggers']==value
                    sections=[section['id'] for section in result['report']['sections']]
                    if value==0:
                        assert 'neural_bait_reference' not in result and 'neural_bait' not in sections
                        assert '本能的召唤 · 诱饵持续效果待核验' not in window.damage_text.toPlainText()
                    else:
                        ref=result['neural_bait_reference']
                        assert type(ref['triggers_requested']) is int and ref['triggers_requested']==1
                        assert ref['snapshot_attack'] is None and ref['first_tick_seconds'] is None
                        assert ref['events_scheduled'] is False
                        metrics=report_metrics(result,'neural_bait')
                        assert metrics['trigger_count']==1 and metrics['snapshot_attack'] is None
                        assert metrics['first_tick'] is None
                        assert '本能的召唤 · 诱饵持续效果待核验' in window.damage_text.toPlainText()
                        if scope_name in ('zero_window','zero_lifetime'):
                            assert ref['affected_damage_phases']['window'] is False
                        else:
                            assert result['total_damage'] is None and result['estimate']['skill']['window_dps'] is None
                    if scope_name in ('zero_window','zero_lifetime'):assert result['total_damage']==0
                    checks.append({'scope':'actual_bait_integer_count_and_unknown_event_boundary',
                        'section':65,'operator':phatm,'skill':2,'mode':args['timing_mode'],
                        'scenario_scope':scope_name,'window_seconds':horizon,'value':value,
                        'widget':'QSpinBox','submitted_type':'int','reference_present':value>0,
                        'actual_snapshot_attack':None,'actual_first_tick':None,'events_scheduled':False,
                        'gui_maximum_not_native_cap':100,'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(1));window.window_seconds.setValue(10)
            window.timing_scenario.clear();bait.setValue(1)
            assert not bait.isVisible()
            result=click_result();args=window.damage_result['scenario']
            assert 'bait_triggers' not in args and 'neural_bait_reference' not in result
            checks.append({'scope':'actual_bait_integer_widget_inactive_skill_serializer',
                'section':65,'operator':phatm,'skill':1,'mode':args['timing_mode'],
                'widget_hidden':True,'inactive_key_submitted':False,'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(2))
        bait.setValue(0);window.timing_scenario.clear();relics([])
        new_section_counts[65]=len(checks)-section_start
        assert new_section_counts[65]==len(scopes)*2*2+2
        receipt['section65_input_scope']='Real bait_triggers QSpinBox integer0 has no bait reference; positive1 retains unplaced effect with actual deployment snapshot/firsttick unknown, and zero observation/enemy lifetime preserve original zero-window output. API string aliases use separate regression; no fixed trigger interval, original maxcap, scheduled tick or overlapping effect is inferred.'

        new_end=len(checks)
        receipt['supplemental_sections_61_65']=[61,62,63,64,65]
        receipt['supplemental_checks_by_section_61_65']=new_section_counts
        receipt['supplemental_checks_61_65']=new_end-new_start
        assert sum(new_section_counts.values())==new_end-new_start
        receipt['section65_final_checks_pending']=False
        assert receipt['section65_final_checks_pending'] is False,'Section65 source review is not finalized; do not execute this draft as a complete UI runner'
        # Root replaces the pending marker after final schema/source review,
        # freezes integrated source on a clean commit and alone executes Wine.

        #66-70: actual Qt values and actual visible results. API aliases/text are separate.
        latest_start=len(checks);latest_section_counts={}
        window.damage_technical.setChecked(False);window.timing_scenario.clear();relics([])
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.limit_window.setChecked(True);window.healing_targets.setValue(1)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        scopes070=[('positive',10,{}),('zero_window',0,{}),
            ('zero_lifetime',10,{'target_disappears_seconds':0}),
            ('empty_target_windows',10,{'target_windows':[]})]
        def set_observation070(horizon,timing):
            window.window_seconds.setValue(horizon)
            window.timing_scenario.setPlainText(json.dumps(timing) if timing else '')
        def require_real_int070(widget,args,key,value):
            assert isinstance(widget,QSpinBox) and widget.isVisible() and widget.isEnabled()
            assert type(widget.value()) is int and widget.value()==value
            assert type(args[key]) is int and args[key]==value
        def require_real_bool070(widget,args,key,value):
            assert isinstance(widget,QCheckBox) and widget.isVisible() and widget.isEnabled()
            assert type(widget.isChecked()) is bool and widget.isChecked() is value
            assert args[key] is value

        section_start=len(checks);wisdel='char_1035_wisdel'
        train(wisdel,{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0})
        reset_owner_options(wisdel)
        ghosts_widget=option_widgets[(wisdel,'ghost_count')];casts_widget=option_widgets[(wisdel,'ghost_casts')]
        assert ghosts_widget.minimum()==0 and ghosts_widget.maximum()==3
        assert casts_widget.minimum()==0 and casts_widget.maximum()==1000
        for number in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(number))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for scope_name,horizon,timing in scopes070:
                    set_observation070(horizon,timing)
                    for ghosts,casts in ((0,0),(0,1),(1,0),(1,1),(3,2)):
                        ghosts_widget.setValue(ghosts);casts_widget.setValue(casts)
                        invalid=horizon==0 and ghosts>0 and casts>0
                        if invalid:
                            # A real, numeric combination the original UI can submit.
                            supplemental_button.click();app.processEvents()
                            assert window.damage_result is None
                            assert window.damage_text.toPlainText()=='零长度观察窗口不能声明魂灵施放命中。'
                            assert type(ghosts_widget.value()) is int and ghosts_widget.value()==ghosts
                            assert type(casts_widget.value()) is int and casts_widget.value()==casts
                        else:
                            result=click_result();args=window.damage_result['scenario']
                            require_real_int070(ghosts_widget,args,'ghost_count',ghosts)
                            require_real_int070(casts_widget,args,'ghost_casts',casts)
                            require_wisdel(result,args,window.damage_text.toPlainText(),scope_name)
                        checks.append({'scope':'actual_wisdel_integer_presence_gate_and_declared_cast_reference',
                            'section':66,'operator':wisdel,'skill':number,
                            'mode':'frames' if use_frames else 'continuous','observation_scope':scope_name,
                            'ghost_count':ghosts,'ghost_casts':casts,'submitted_types':'int/int',
                            'expected_numeric_input_error_visible':invalid,
                            'actual_shadow_clock_or_presence_verified':False,'passed':True})
        ghosts_widget.setValue(0);casts_widget.setValue(0)
        latest_section_counts[66]=len(checks)-section_start;assert latest_section_counts[66]==120
        receipt['section66_input_scope']='Real ghost_count/casts QSpinBoxes submit integers. Zero ghosts ignores declared casts; positive casts remain conditional without placement/cast time or full-phase attribution. Twelve genuinely numeric zero-window combinations show the existing exact error and clear the prior result; these are expected error checks, not successful calculations or API text inputs.'

        section_start=len(checks);phatm='char_1042_phatm2'
        train(phatm,{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        reset_owner_options(phatm);incoming_widget=option_widgets[(phatm,'enemy_attack_count')]
        resistance_widget=option_widgets[(phatm,'enemy_buildup_resistance')]
        assert incoming_widget.minimum()==0 and incoming_widget.maximum()==10000
        def incoming_case070(number,use_frames,scope_name,horizon,timing,count,qualified=True,immune=False):
            set_observation070(horizon,timing);incoming_widget.setValue(count)
            result=click_result();args=window.damage_result['scenario']
            require_real_int070(incoming_widget,args,'enemy_attack_count',count)
            require_incoming(result,args,window.damage_text.toPlainText(),scope_name,qualified,immune)
            checks.append({'scope':'actual_enemy_attack_integer_metadata_and_unplaced_clock',
                'section':67,'operator':phatm,'skill':number,
                'mode':'frames' if use_frames else 'continuous','observation_scope':scope_name,
                'enemy_attack_count':count,'submitted_type':'int','talent_qualified':qualified,
                'buildup_immune':immune,'actual_attack_times':None,'events_scheduled':False,'passed':True})
        for number in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(number));resistance_widget.setValue(0)
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for scope_name,horizon,timing in scopes070:
                    for count in (0,1):incoming_case070(number,use_frames,scope_name,horizon,timing,count)
                incoming_case070(number,use_frames,'positive',10,{},20)
                resistance_widget.setValue(100)
                for count in (0,1):incoming_case070(number,use_frames,'positive',10,{},count,immune=True)
                resistance_widget.setValue(0)
        train(phatm,{'elite':1,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0},ranks={'1':7,'2':7})
        assert window.skill.findData(3)==-1
        for number in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(number))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for count in (0,1):incoming_case070(number,use_frames,'positive',10,{},count,qualified=False)
        incoming_widget.setValue(0);latest_section_counts[67]=len(checks)-section_start
        assert latest_section_counts[67]==74
        receipt['section67_input_scope']='Real target-attack QSpinBox integers0/1/20 retain metadata70 per-attack parameter, but no attack timestamps or uniform schedule. Zero observation preserves cast pending/window0; lifetime0, immunity100 and E1 talent gates exclude this source. Empty target windows do not establish event timing and continuous subtotals are not forced to frame-mode zero.'

        section_start=len(checks);shu='char_2025_shu'
        different_widget=option_widgets[(shu,'three_professions')]
        same_widget=option_widgets[(shu,'three_same_profession')];four_widget=option_widgets[(shu,'four_sui')]
        assert different_widget.text()=='三种不同职业在场' and same_widget.text()=='三名相同职业在场'
        for elite,level,rank,numbers,fours in ((2,90,10,(1,2,3),(False,True)),
                (1,80,7,(1,2),(False,)),(0,50,4,(1,),(False,))):
            train(shu,{'elite':elite,'level':level,'potential':1,'trust':100,'module_id':None,'module_level':0},
                  ranks={'1':rank,'2':rank,'3':rank})
            reset_owner_options(shu);set_observation070(10,{})
            for number in numbers:
                window.skill.setCurrentIndex(window.skill.findData(number))
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for four in fours:
                        four_widget.setChecked(four);plain=None
                        for different,same in ((False,False),(True,False),(False,True),(True,True)):
                            different_widget.setChecked(different);same_widget.setChecked(same)
                            result=click_result();args=window.damage_result['scenario']
                            require_real_bool070(different_widget,args,'three_professions',different)
                            require_real_bool070(same_widget,args,'three_same_profession',same)
                            require_real_bool070(four_widget,args,'four_sui',four)
                            if not different and not same:plain=deepcopy(result)
                            require_professions(result,args,window.damage_text.toPlainText(),plain,elite==2)
                            checks.append({'scope':'actual_shu_profession_checkbox_combinations_and_qualification',
                                'section':68,'operator':shu,'elite':elite,'skill':number,'skill_rank':rank,
                                'mode':args['timing_mode'],'three_professions':different,
                                'three_same_profession':same,'four_sui':four,'submitted_types':'bool/bool/bool',
                                'actual_squad_count_or_periodic_clock_verified':False,'passed':True})
        reset_owner_options(shu);latest_section_counts[68]=len(checks)-section_start
        assert latest_section_counts[68]==72
        receipt['section68_input_scope']='Actual different/same-profession QCheckBox combinations are bool; E2 affects only selected Shu HP12% and attack speed12, E0/E1 results remain unchanged. Four-sui coexistence retains unknown periodic clocks. This declares conditions without reading actual squad counts or certifying a team-wide application.'

        section_start=len(checks)
        train('silverash',{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
              ranks={'1':4,'2':4,'3':4})
        window.skill.setCurrentIndex(window.skill.findData(3))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames)
            for scope_name,horizon,timing in scopes070:
                set_observation070(horizon,timing);controls={}
                for cooperation in (False,True):
                    window.cooperative.setChecked(cooperation)
                    for fragile in (False,True):
                        window.fragile.setChecked(fragile);result=click_result();args=window.damage_result['scenario']
                        require_real_bool070(window.cooperative,args,'cooperative',cooperation)
                        require_real_bool070(window.fragile,args,'preexisting_fragile',fragile)
                        if not cooperation:controls[fragile]=deepcopy(result)
                        require_cooperative(result,args,window.damage_text.toPlainText(),controls[fragile],scope_name)
                        checks.append({'scope':'actual_cooperative_checkbox_explicit_coverage_condition',
                            'section':69,'operator':'silverash','skill':3,'skill_rank':4,
                            'mode':args['timing_mode'],'observation_scope':scope_name,
                            'cooperative':cooperation,'preexisting_fragile':fragile,'submitted_types':'bool/bool',
                            'actual_position_or_synchronized_hit_clock_verified':False,'passed':True})
        train('silverash',{'elite':0,'level':50,'potential':1,'trust':100,'module_id':None,'module_level':0},ranks={'1':1})
        assert window.skill.findData(3)==-1;window.skill.setCurrentIndex(window.skill.findData(1))
        assert not window.cooperative.isVisible();window.fragile.setChecked(False);set_observation070(10,{})
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);plain=None
            for cooperation in (False,True):
                window.cooperative.setChecked(cooperation);result=click_result();args=window.damage_result['scenario']
                assert args['cooperative'] is cooperation and type(window.cooperative.isChecked()) is bool
                if not cooperation:plain=deepcopy(result)
                else:assert strict_json(result)==strict_json(plain)
                checks.append({'scope':'actual_cooperative_global_bool_inactive_skill',
                    'section':69,'operator':'silverash','elite':0,'skill':1,
                    'mode':args['timing_mode'],'cooperative':cooperation,'checkbox_hidden':True,'passed':True})
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        latest_section_counts[69]=len(checks)-section_start;assert latest_section_counts[69]==36
        receipt['section69_input_scope']='Explicit cooperative/fragile QCheckBox bool states preserve existing physical component math and rank4 declaration across empty/positive observations. E0 S1 ignores the global cooperative flag and offers no S3. API text rejection, native placement, synchronized events and overlap identity remain separate.'

        section_start=len(checks);tile_widget=option_widgets[(shu,'enemy_on_sown_tile')]
        assert tile_widget.text()=='存在地面敌人处于播种地块'
        for rank in (1,7,10):
            train(shu,{'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
                  ranks={'1':rank,'2':rank,'3':rank})
            reset_owner_options(shu);window.skill.setCurrentIndex(window.skill.findData(3))
            bb=module.catalog()['operators'][shu]['skills'][2]['levels'][rank-1]['values']
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                for four in (False,True):
                    four_widget.setChecked(four)
                    for scope_name,horizon,timing in scopes070[:3]:
                        set_observation070(horizon,timing);plain=None
                        for tile in (False,True):
                            tile_widget.setChecked(tile);result=click_result();args=window.damage_result['scenario']
                            require_real_bool070(tile_widget,args,'enemy_on_sown_tile',tile)
                            require_real_bool070(four_widget,args,'four_sui',four)
                            assert window.target_enemy.currentData() is None and 'target_enemy' not in args
                            if not tile:plain=deepcopy(result)
                            require_sown(result,args,window.damage_text.toPlainText(),plain,scope_name,bb)
                            if rank==10 and use_frames and not four and scope_name=='positive' and tile:
                                assert tile_widget.grab().save(str(OUT/'wine-sown-tile-control-100.png'))
                                receipt['section70_actual_checkbox_screenshot']='wine-sown-tile-control-100.png'
                            checks.append({'scope':'actual_ground_enemy_presence_label_and_sown_checkbox',
                                'section':70,'operator':shu,'skill':3,'skill_rank':rank,
                                'mode':args['timing_mode'],'observation_scope':scope_name,
                                'label':tile_widget.text(),'enemy_on_sown_tile':tile,'four_sui':four,
                                'submitted_types':'bool/bool','current_target_selected':False,
                                'e_atk_parameter':bb['e_atk'],'e_attack_speed_parameter':bb['e_attack_speed'],
                                'actual_ground_presence_or_position_verified':False,'passed':True})
        train(shu,{'elite':1,'level':80,'potential':1,'trust':100,'module_id':None,'module_level':0},ranks={'1':7,'2':7})
        reset_owner_options(shu);assert window.skill.findData(3)==-1;set_observation070(10,{})
        for number in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(number));assert not tile_widget.isVisible()
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames);plain=None
                for tile in (False,True):
                    tile_widget.setChecked(tile);result=click_result();args=window.damage_result['scenario']
                    assert type(tile_widget.isChecked()) is bool and tile_widget.isChecked() is tile
                    assert 'enemy_on_sown_tile' not in args
                    if not tile:plain=deepcopy(result)
                    else:assert strict_json(result)==strict_json(plain)
                    checks.append({'scope':'actual_sown_checkbox_inactive_skill_key_not_submitted',
                        'section':70,'operator':shu,'elite':1,'skill':number,'mode':args['timing_mode'],
                        'hidden_checkbox_state':tile,'inactive_key_submitted':False,'passed':True})
        reset_owner_options(shu);window.timing_scenario.clear();relics([])
        latest_section_counts[70]=len(checks)-section_start;assert latest_section_counts[70]==80
        receipt['section70_input_scope']='Actual checkbox label declares the existence of a ground enemy on a sown tile, not the selected target location. Genuine bool states retain original skill parameters/empty boundaries and four-sui unknown clock. No ground_type filter, position detection, actual coverage, trigger or teleport clock is inferred; S1/S2 omit this inactive key.'
        latest_end=len(checks)
        receipt['supplemental_sections_66_70']=[66,67,68,69,70]
        receipt['supplemental_checks_by_section_66_70']=latest_section_counts
        receipt['supplemental_checks_66_70']=latest_end-latest_start
        assert sum(latest_section_counts.values())==latest_end-latest_start
        receipt['section70_final_checks_pending']=False
        assert receipt['section70_final_checks_pending'] is False

        #71-75 genuine Qt controls and read-only public observation previews.
        from PySide6.QtWidgets import QDoubleSpinBox
        current_start=len(checks);current_section_counts={}
        window.damage_technical.setChecked(False);relics([])
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.limit_window.setChecked(True);window.healing_targets.setValue(1)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        window.deployment_elapsed.setValue(0)
        from rouge.run_config import config_data
        config075=config_data();design075=cases075(config075['squads'])
        state075=deepcopy(window.run.state);account075=deepcopy(window.operator_observations)
        run_training075=window.use_run_training.isChecked()
        difficulty075=window.difficulty.currentIndex();summary075=window.run_summary.text()
        plain_e0_075={}
        try:
            window.run.state['operators']={};window.use_run_training.setChecked(False)
            for case075 in design075:
                section075=case075['section'];requested075=case075['input']
                owner075=requested075['operator'];number075=requested075['skill']
                fields075={k:requested075[k] for k in ('elite','level','potential','trust','module_id','module_level')}
                # These are public synthetic observation records in the same
                #temporary window, not recognition, account files or selectors.
                window.run.state['config']=deepcopy(requested075.get('run_config',{}))
                window.run_summary.setText(window.run.summary());window.sync_run_config()
                train(owner075,fields075,ranks={str(n):requested075['skill_rank'] for n in (1,2,3)})
                reset_owner_options(owner075)
                index075=window.skill.findData(number075);assert index075>=0
                window.skill.setCurrentIndex(index075)
                assert window.elite.text()==f'精英 {fields075["elite"]}'
                assert window.potential.text()==str(fields075['potential'])
                if fields075['module_id']:assert f'阶段 {fields075["module_level"]}' in window.module.text()
                if fields075['elite']==0:assert window.skill.findData(2)==window.skill.findData(3)==-1
                if fields075['elite']==1:assert window.skill.findData(3)==-1
                window.frame_timing.setChecked(requested075['timing_mode']=='frames')
                window.window_seconds.setValue(requested075['window_seconds']);window.timing_scenario.clear()
                for key075 in ('deployment_elapsed_seconds','drone_warmup_hits','ghost_count','ghost_casts'):
                    if key075 in requested075:
                        widget075=option_widgets[(owner075,key075)]
                        widget075.setValue(requested075[key075])
                result075=click_result();args075=window.damage_result['scenario']
                for key075 in ('operator','skill','elite','level','potential','trust','skill_rank',
                        'module_id','module_level','timing_mode','window_seconds'):
                    assert args075[key075]==requested075[key075],(section075,key075,args075[key075],requested075[key075])
                actual075=window.damage_text.toPlainText()
                if section075==71:
                    assert canonical075(args075['run_config'])==canonical075(requested075['run_config'])
                    record075=config075['squads'][args075['run_config']['squad']['id']]
                    assert record075['name'] in window.run_summary.text()
                    assert ('（强化）' if record075['bandLevel']==1 else '（基础）') in window.run_summary.text()
                    grade075=requested075['run_config'].get('difficulty')
                    assert window.difficulty.isEnabled() is (grade075 is None)
                    if grade075:assert window.difficulty.currentData()==grade075['value']
                    require_squad075(result075,args075,actual075,record075)
                elif section075==72:
                    elapsed075=option_widgets[(owner075,'deployment_elapsed_seconds')]
                    assert isinstance(elapsed075,QDoubleSpinBox) and elapsed075.isVisible() and elapsed075.isEnabled()
                    assert elapsed075.minimum()==0 and elapsed075.maximum()==3600 and elapsed075.decimals()==2
                    assert type(elapsed075.value()) is float and type(args075['deployment_elapsed_seconds']) is float
                    assert elapsed075.value()==args075['deployment_elapsed_seconds']==requested075['deployment_elapsed_seconds']
                    require_real_int070(option_widgets[(owner075,'drone_warmup_hits')],args075,
                                        'drone_warmup_hits',requested075['drone_warmup_hits'])
                    baseline_key075=(args075['potential'],args075['timing_mode'],args075['drone_warmup_hits'])
                    if args075['elite']==0 and args075['deployment_elapsed_seconds']==0:
                        plain_e0_075[baseline_key075]=deepcopy(result075)
                    require_headwolf075(result075,args075,actual075,
                        plain_e0_075.get(baseline_key075) if args075['elite']==0 else None)
                elif section075==73:
                    require_mei075(result075,args075,actual075,args075['elite']==2 and args075['level']>=40,args075['module_level'])
                    if args075['window_seconds']==0:assert result075['total_damage']==0
                elif section075==74:
                    for key075 in ('ghost_count','ghost_casts'):
                        require_real_int070(option_widgets[(owner075,key075)],args075,key075,requested075[key075])
                    require_wisdel_routes075(result075,args075,actual075)
                    if args075['window_seconds']==0:assert result075['total_damage']==0
                else:raise AssertionError(('Unsealed section',section075))
                current_section_counts[section075]=current_section_counts.get(section075,0)+1
                checks.append({'scope':'actual_qt_public_config_and_readonly_cultivation_contract' if section075==71 else
                    'actual_qt_owner_controls_and_readonly_cultivation_reference',
                    'section':section075,'operator':owner075,'skill':number075,'mode':args075['timing_mode'],
                    'elite':args075['elite'],'level':args075['level'],'potential':args075['potential'],
                    'module_level':args075['module_level'],'window_seconds':args075['window_seconds'],
                    'input_design':requested075,'state_scope':'temporary public in-memory observation/config only',
                    'actual_account_source_or_clock_verified':False,'passed':True})
        finally:
            window.run.state=state075;window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy(account075));assert window.operator_observations is window.account_cache.records
            window.use_run_training.setChecked(run_training075)
            window.run_summary.setText(summary075);window.sync_run_config()
            if not state075.get('config',{}).get('difficulty'):window.difficulty.setCurrentIndex(difficulty075)
            window.update_operator();relics([]);window.timing_scenario.clear()
        assert current_section_counts=={71:106,72:280,73:72,74:108},current_section_counts

        #75 The battle-preview combos/checkbox produce their real read-only text.
        #This is selected public stage data, not actual movement or game capture.
        from rouge.battle_preview import battle_data,enemy_preview,enemy_text
        preview075=window.battle_preview;stage075=window.target_stage.currentData()
        enemy075=window.target_enemy.currentData();page075=window.centralWidget().currentIndex()
        technical075=preview075.technical.isChecked()
        try:
            window.centralWidget().setCurrentIndex(4);app.processEvents()
            for case075 in preview_cases075(battle_data()['stages']):
                sid075=case075['stage_id'];eid075=case075['enemy_id'];level075=case075['level']
                # BranchChoice reveals the genuine stage/identity combo and emits
                #its normal Qt selection signal; no private _render API is called.
                assert preview075.stage_choices.select_value(sid075)
                app.processEvents()
                assert preview075.stage_combo.currentData()==sid075 and preview075.current_stage==sid075
                assert preview075.stage_combo.isVisible() and preview075.stage_combo.isEnabled()
                assert preview075.enemy_choices.select_value((eid075,level075))
                app.processEvents()
                assert tuple(preview075.enemy_combo.currentData())==(eid075,level075)
                assert preview075.enemy_combo.isVisible() and preview075.enemy_combo.isEnabled()
                preview075.technical.setChecked(case075['technical']);app.processEvents()
                assert isinstance(preview075.technical,QCheckBox) and preview075.technical.isVisible()
                assert preview075.technical.isChecked() is case075['technical']
                entry075=enemy_preview(sid075,eid075,level075,preview075.context)
                actual075=preview075.enemy_detail.toPlainText()
                assert preview075.enemy_detail.isReadOnly() and preview075.enemy_detail.isVisible()
                assert actual075==enemy_text(entry075,technical=case075['technical']).replace(chr(160),' ')
                require_movement075(entry075,actual075,case075['technical'],battle_data()['stages'][sid075])
                current_section_counts[75]=current_section_counts.get(75,0)+1
                checks.append({'scope':'actual_stage_enemy_combo_and_technical_movement_source_reference',
                    **case075,'old_base_times_stage_subtotal':entry075['movement_reference']['base_times_stage_speed'],
                    'effective_movement_known':False,'rune_composition_known':False,'passed':True})
                if sid075=='ro6_e_3_6' and eid075=='enemy_10107_mjcdog_2' and case075['technical']:
                    from PySide6.QtGui import QTextCursor
                    preview075.enemy_detail.moveCursor(QTextCursor.MoveOperation.Start)
                    assert preview075.enemy_detail.find('关卡移速符文参数参考')
                    preview075.enemy_detail.ensureCursorVisible();app.processEvents()
                    assert window.grab().save(str(OUT/'wine-movement-reference-100.png'))
                    receipt['section75_actual_technical_screenshot']='wine-movement-reference-100.png'
        finally:
            preview075.technical.setChecked(technical075)
            assert window.target_stage_choices.select_value(stage075)
            if enemy075 is None:window.target_enemy.setCurrentIndex(0)
            else:assert window.target_enemy_choices.select_value(enemy075)
            window.centralWidget().setCurrentIndex(page075);app.processEvents()
        assert current_section_counts[75]==48
        current_end=len(checks)
        receipt['supplemental_sections_71_75']=[71,72,73,74,75]
        receipt['supplemental_checks_by_section_71_75']=current_section_counts
        receipt['supplemental_checks_71_75']=current_end-current_start
        assert sum(current_section_counts.values())==current_end-current_start
        receipt['section71_input_scope']='No squad selector exists. Synthetic public run config plus real button/read-only summary/difficulty preset; grades and Mechanist cultivation never prove account unlock or actual activation. Entire state/observations/preset are restored.'
        receipt['section72_input_scope']='Owner QDoubleSpinBox elapsed has two decimals; QSpinBox warmup emits int. Cultivation is read-only public observation preview. E0 age does not activate absent Headwolf; original E1/E2 owner-clock reference remains distinct from unknown independent drone arrival/targeting/aura.'
        receipt['section73_input_scope']='Module stage/cultivation are existing QLabel public observation previews, not invented selectors. Exact110% airborne source parameter is unused; actual target, native attachment and composition remain unknown.'
        receipt['section74_input_scope']='Existing ghost count/cast QSpinBoxes retain legal E0/E1 declarations despite both original native body routes requiring E2level1. Qualification does not prove source, presence, cast clock or all module/relic routes.'
        receipt['section75_input_scope']='Actual battle-preview stage/enemy selectors and technical checkbox retain all12 enemy records in each normal/emergency stage. Exact emergency raw rune1.5 remains a source parameter; old base-times-stage subtotal is unchanged, effective speed and native writer/composition remain unknown. No capture, actual route or movement clock is certified.'
        receipt['section75_final_checks_pending']=False
        assert receipt['section75_final_checks_pending'] is False,'Final section75 source/independent review is not yet sealed'

        #76-80 genuine Qt design. API textual/invalid values are separate.
        next_start=len(checks);next_section_counts={};controls080={}
        state080=deepcopy(window.run.state);account080=deepcopy(window.operator_observations)
        run_training080=window.use_run_training.isChecked()
        difficulty080=window.difficulty.currentIndex();summary080=window.run_summary.text()
        target_stage080=window.target_stage.currentData();target_enemy080=deepcopy(window.target_enemy.currentData())
        try:
            window.run.state['operators']={};window.run.state['config']={}
            window.use_run_training.setChecked(False);window.sync_run_config()
            window.damage_technical.setChecked(False);relics([])
            window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
            window.cooperative.setChecked(False);window.fragile.setChecked(False)
            window.limit_window.setChecked(True);window.deployment_elapsed.setValue(0)
            for case080 in cases080():
                requested080=case080['input'];owner080=requested080['operator'];number080=requested080['skill']
                section080=case080['section']
                fields080={k:requested080[k]for k in ('elite','level','potential','trust','module_id','module_level')}
                train(owner080,fields080,ranks={str(n):requested080['skill_rank']for n in (1,2,3)})
                reset_owner_options(owner080)
                index080=window.skill.findData(number080);assert index080>=0
                window.skill.setCurrentIndex(index080)
                assert window.elite.text()==f'精英 {fields080["elite"]}'
                assert window.potential.text()==str(fields080['potential'])
                if fields080['module_id']:assert f'阶段 {fields080["module_level"]}'in window.module.text()
                if fields080['elite']==0:assert window.skill.findData(2)==window.skill.findData(3)==-1
                if fields080['elite']==1:assert window.skill.findData(3)==-1
                window.frame_timing.setChecked(requested080['timing_mode']=='frames')
                window.window_seconds.setValue(requested080['window_seconds'])
                window.healing_targets.setValue(requested080['healing_targets'])
                relics(requested080['relic_ids'])
                window.defense.setValue(requested080['enemy_defense'])
                window.resistance.setValue(requested080['enemy_resistance'])
                window.timing_scenario.setPlainText(json.dumps(requested080['timing'])if requested080.get('timing')else '')
                if requested080.get('target_enemy'):
                    target080=requested080['target_enemy']
                    assert window.target_stage_choices.select_value(target080['stage_id'])
                    assert window.target_enemy_choices.select_value(target080)
                    app.processEvents()
                    assert window.target_enemy.currentData()==target080
                else:
                    window.target_enemy.setCurrentIndex(0)
                if section080==76:
                    bubble080=option_widgets[(owner080,'bubble_bursts')]
                    repeat080=option_widgets[(owner080,'haruka_repeat')]
                    levitate080=option_widgets[(owner080,'levitate_triggers')]
                    assert isinstance(bubble080,QSpinBox) and bubble080.minimum()==0 and bubble080.maximum()==10000
                    bubble080.setValue(requested080['bubble_bursts'])
                    if number080==2:repeat080.setChecked(requested080['haruka_repeat'])
                    if number080==3:levitate080.setValue(requested080['levitate_triggers'])
                elif section080==77:
                    weight080=option_widgets[(owner080,'enemy_weight')]
                    assert isinstance(weight080,QSpinBox) and weight080.minimum()==0 and weight080.maximum()==100
                    weight080.setValue(requested080['enemy_weight'])
                elif section080==78:
                    palsy080=option_widgets[(owner080,'palsy_triggers')]
                    overflow080=option_widgets[(owner080,'palsy_overflow_hits')]
                    assert isinstance(palsy080,QSpinBox) and palsy080.minimum()==0 and palsy080.maximum()==10000
                    palsy080.setValue(requested080['palsy_triggers'])
                    if number080==3:overflow080.setValue(requested080['palsy_overflow_hits'])
                    if 'enemy_elemental_resistance'in requested080:
                        elemental080=option_widgets[(owner080,'enemy_elemental_resistance')]
                        assert isinstance(elemental080,QDoubleSpinBox) and elemental080.minimum()==0 and elemental080.maximum()==100
                        elemental080.setValue(requested080['enemy_elemental_resistance'])
                elif section080 in (79,80):
                    medical_targets080=option_widgets[(owner080,'amiya_hit_targets')]
                    assert isinstance(window.healing_targets,QSpinBox) and window.healing_targets.minimum()==0
                    assert window.healing_targets.maximum()==(100 if number080==1 else 1)
                    if number080==2:
                        assert isinstance(medical_targets080,QSpinBox)
                        assert medical_targets080.minimum()==1 and medical_targets080.maximum()==100
                        medical_targets080.setValue(requested080['amiya_hit_targets'])
                else:raise AssertionError('Unsealed section')
                result080=click_result();args080=window.damage_result['scenario']
                for key080 in ('operator','skill','elite','level','potential','trust','module_id','module_level',
                               'skill_rank','timing_mode','window_seconds','healing_targets','relic_ids',
                               'enemy_defense','enemy_resistance'):
                    assert args080[key080]==requested080[key080],(case080,key080,args080[key080])
                assert args080.get('timing',{})==requested080.get('timing',{})
                if section080==76:
                    require_real_int070(bubble080,args080,'bubble_bursts',requested080['bubble_bursts'])
                    if number080==2:
                        require_real_bool070(repeat080,args080,'haruka_repeat',requested080['haruka_repeat'])
                    else:
                        assert not repeat080.isVisible() and 'haruka_repeat'not in args080
                    if number080==3:
                        assert levitate080.minimum()==0 and levitate080.maximum()==1000
                        require_real_int070(levitate080,args080,'levitate_triggers',requested080['levitate_triggers'])
                    else:
                        assert not levitate080.isVisible() and 'levitate_triggers'not in args080
                    control_key080=canonical080({k:v for k,v in requested080.items()if k!='bubble_bursts'})
                    if requested080['bubble_bursts']==0:controls080[control_key080]=deepcopy(result080)
                    assert control_key080 in controls080
                    require_haruka080(result080,args080,window.damage_text.toPlainText(),controls080[control_key080])
                elif section080==77:
                    require_real_int070(weight080,args080,'enemy_weight',requested080['enemy_weight'])
                    control_key080=canonical080({k:v for k,v in requested080.items()if k!='enemy_weight'})
                    if requested080.get('target_enemy'):
                        assert args080['target_enemy']==requested080['target_enemy']
                        if args080['enemy_weight']==0:controls080[control_key080]=deepcopy(result080)
                        require_aglna_selected080(result080,args080,window.damage_text.toPlainText(),
                            controls080[control_key080],case080['expected_reference_mass'])
                    else:
                        assert window.target_enemy.currentData() is None and 'target_enemy'not in args080
                        control080=controls080.setdefault(control_key080,{})
                        if args080['enemy_weight']==0:control080['light']=deepcopy(result080)
                        if args080['enemy_weight']==4:control080['heavy']=deepcopy(result080)
                        require_aglna080(result080,args080,window.damage_text.toPlainText(),control080)
                elif section080==78:
                    require_real_int070(palsy080,args080,'palsy_triggers',requested080['palsy_triggers'])
                    if number080==3:
                        assert overflow080.minimum()==0 and overflow080.maximum()==10000
                        require_real_int070(overflow080,args080,'palsy_overflow_hits',requested080['palsy_overflow_hits'])
                    else:
                        assert not overflow080.isVisible() and 'palsy_overflow_hits'not in args080
                    if 'enemy_elemental_resistance'in requested080:
                        assert elemental080.isVisible() and elemental080.isEnabled()
                        assert type(args080['enemy_elemental_resistance']) is float
                        assert args080['enemy_elemental_resistance']==elemental080.value()==requested080['enemy_elemental_resistance']
                    control_key080=canonical080({k:v for k,v in requested080.items()if k!='palsy_triggers'})
                    if args080['palsy_triggers']==0:controls080[control_key080]=deepcopy(result080)
                    require_mantra080(result080,args080,window.damage_text.toPlainText(),controls080[control_key080])
                elif section080 in (79,80):
                    if number080==2:
                        require_real_int070(medical_targets080,args080,'amiya_hit_targets',requested080['amiya_hit_targets'])
                    else:
                        assert not medical_targets080.isVisible() and 'amiya_hit_targets'not in args080
                    if section080==79:require_medical_amiya080(result080,args080,window.damage_text.toPlainText())
                    else:require_medical_trait080(result080,args080,window.damage_text.toPlainText(),case080['expected_trait_ratio'])
                    if (section080==80 and case080['context']=='INC_X_same_trait_ratio_boundary' and
                            args080['elite']==2 and args080['level']==50 and args080['module_level']==3 and
                            number080==1 and args080['timing_mode']=='frames' and args080['healing_targets']==1):
                        from PySide6.QtGui import QTextCursor
                        window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
                        assert window.damage_text.find('【治疗输出】')
                        window.damage_text.ensureCursorVisible();app.processEvents()
                        assert window.isVisible() and window.module.isVisible()
                        assert '带有灼痕的裙子'in window.module.text() and '阶段 3'in window.module.text()
                        assert window.grab().save(str(OUT/'wine-medical-trait-100.png'))
                        conversion080=next(c for c in result080['components']if c['name']=='咒愈师伤害转治疗')
                        receipt['section80_actual_trait_screenshot']={'filename':'wine-medical-trait-100.png',
                            'captured_during_existing_case':True,'extra_API_or_Qt_case':False,
                            'readonly_elite_text':window.elite.text(),'readonly_module_text':window.module.text(),
                            'ratio':conversion080['damage_healing']['ratio'],
                            'damage_conversion_hits':conversion080['hits'],
                            'damage_conversion_per_hit':conversion080['per_hit'],
                            'damage_conversion_total':conversion080['total'],
                            'visible_report_scrolled_to_healing_section':True,
                            'native_clock_or_recipient_verified':False}
                next_section_counts[section080]=next_section_counts.get(section080,0)+1
                checks.append({'scope':{76:'actual_bubble_spin_and_readonly_talent_qualification_with_zero_control',
                    77:'actual_manual_weight_spin_and_readonly_locked_talent_event_count',
                    78:'actual_palsy_spin_and_readonly_talent_qualification_with_zero_control',
                    79:'actual_medical_form_readonly_talent_qualification_and_opening_count_spin',
                    80:'actual_medical_INC_X_same_trait_ratio_and_damage_dependent_healing'}[section080],
                    'section':section080,'operator':owner080,'skill':number080,'mode':args080['timing_mode'],
                    'context':case080['context'],'elite':args080['elite'],'potential':args080['potential'],
                    'module_level':args080['module_level'],'bubble_bursts':args080.get('bubble_bursts'),
                    'enemy_weight':args080.get('enemy_weight'),
                    'selected_enemy':args080.get('target_enemy'),'reference_mass':case080.get('expected_reference_mass'),
                    'haruka_repeat':args080.get('haruka_repeat'),'levitate_triggers':args080.get('levitate_triggers'),
                    'palsy_triggers':args080.get('palsy_triggers'),'palsy_overflow_hits':args080.get('palsy_overflow_hits'),
                    'enemy_elemental_resistance':args080.get('enemy_elemental_resistance'),
                    'amiya_hit_targets':args080.get('amiya_hit_targets'),
                    'expected_trait_ratio':case080.get('expected_trait_ratio'),
                    'state_scope':'temporary public readonly cultivation observation; no editable module/elite selector',
                    'native_clock_attachment_or_actual_recipient_verified':False,'passed':True})
        finally:
            window.run.state=state080;window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy(account080));assert window.operator_observations is window.account_cache.records
            window.use_run_training.setChecked(run_training080)
            window.run_summary.setText(summary080);window.sync_run_config()
            if not state080.get('config',{}).get('difficulty'):window.difficulty.setCurrentIndex(difficulty080)
            assert window.target_stage_choices.select_value(target_stage080)
            if target_enemy080 is None:window.target_enemy.setCurrentIndex(0)
            else:assert window.target_enemy_choices.select_value(target_enemy080)
            window.update_operator();relics([]);window.timing_scenario.clear()
        next_end=len(checks)
        assert next_section_counts=={76:432,77:424,78:360,79:212,80:180},next_section_counts
        receipt['supplemental_sections_76_80']=[76,77,78,79,80]
        receipt['supplemental_checks_by_section_76_80']=next_section_counts
        receipt['supplemental_checks_76_80']=next_end-next_start
        receipt['section76_input_scope']='Genuine bubble QSpinBox int0/1/10000 retains declarations at every elite. Read-only public cultivation/module previews do not invent selectors. BeforeE2 only declared-count row and source exclusion note differ from same-window/count0 complete result; original ordinary healing/derived damage and other unknowns stay. E2 event clock, native attachment/composition and recipient/adjacency remain unknown. S2 repeat is real bool, S3 levitate count is separate int; inactive keys are omitted.'
        receipt['section77_input_scope']='Real manual enemy-weight QSpinBox0/3/4/100 and read-only E0/E1/E2/potential1/3 retain source threshold and coefficients. E0 S1 locked extra component has zero hits/timestamps/full-skill count without changing ordinary damage; selected E1/E2 conditional per-hit references remain. Separate genuine stage/enemy selections verify exact fixed roster identity massLevel3/4 overrides raw manual0/100 without claiming actual spawn/live weight/extra attack snapshot/native ordering/takeoff clock.'
        receipt['section78_input_scope']='Genuine palsy QSpinBox0/1/10000 preserves declarations beforeE1; only three declared-count metadata values differ from complete same-condition/count0 output with zero effective locked-talent damage. Qualified positive declarations, elemental immunity and separate S3 overflow hits retain unknown actual times/snapshots. Read-only module/elite observations introduce no selectors or native qualification inference.'
        receipt['section79_input_scope']='Readonly medical Amiya form/cultivation, actual S2 opening-count QSpinBox1/5/100, E0S1 zero effective own-regeneration events without an unplaced-source warning. Qualified S1 retains its existing regeneration reference; qualified S2 retains unknown actual strengthening/end/order/complete output even with zero friendly targets or empty hostile lifetime. INC-X49/50/stages remain genuine readonly previews. No HP0, account form unlock, or real-game recipient/clock proof is invented.'
        receipt['section80_input_scope']='The same medical damage-conversion trait uses its original0.5 below INC-X qualification and explicit same-template0.6 override at E2L50/all3stages. Real readonly cultivation and existing friendly-count controls verify damage-dependent treatment after dealt damage, separate S1 range healing, accepted healing factor and S2 opening subtotal; zero recipient/window/lifetime retain mathematical exclusions. Actual S2 end/order/recipient and complete totals remain unverified; no new selector or trait stacking guess.'
        receipt['sections77_80_final_checks_pending']=False
        assert receipt['sections77_80_final_checks_pending'] is False,'Final77-80 source/schema are pending'

        #81-85 actual-controls design; API strings are separate regressions.
        group085_start=len(checks);group085_counts={};anchors085={};errors085=0
        state085=deepcopy(window.run.state);account085=deepcopy(window.operator_observations)
        run_training085=window.use_run_training.isChecked()
        difficulty085=window.difficulty.currentIndex();summary085=window.run_summary.text()
        stage085=window.target_stage.currentData();enemy085=deepcopy(window.target_enemy.currentData())
        technical085=window.damage_technical.isChecked()
        try:
            window.run.state['operators']={};window.run.state['config']={}
            window.use_run_training.setChecked(False);window.sync_run_config()
            window.target_enemy.setCurrentIndex(0)
            window.cooperative.setChecked(False);window.fragile.setChecked(False)
            window.limit_window.setChecked(True);window.deployment_elapsed.setValue(0)
            for case085 in cases085():
                requested085=case085['input'];owner085=requested085['operator'];number085=requested085['skill']
                section085=case085['section']
                fields085={k:requested085[k]for k in ('elite','level','potential','trust','module_id','module_level')}
                train(owner085,fields085,ranks={str(n):requested085['skill_rank']for n in (1,2,3)})
                reset_owner_options(owner085)
                index085=window.skill.findData(number085);assert index085>=0
                window.skill.setCurrentIndex(index085)
                assert window.elite.text()==f'精英 {fields085["elite"]}'
                assert window.potential.text()==str(fields085['potential'])
                if fields085['module_id']:assert f'阶段 {fields085["module_level"]}'in window.module.text()
                if fields085['elite']==0:assert window.skill.findData(2)==window.skill.findData(3)==-1
                if fields085['elite']==1:assert window.skill.findData(3)==-1
                window.frame_timing.setChecked(requested085['timing_mode']=='frames')
                window.window_seconds.setValue(requested085['window_seconds'])
                window.healing_targets.setValue(requested085['healing_targets'])
                window.defense.setValue(requested085['enemy_defense']);window.resistance.setValue(requested085['enemy_resistance'])
                relics(requested085['relic_ids'])
                window.damage_technical.setChecked(case085.get('technical',False))
                window.timing_scenario.setPlainText(json.dumps(requested085['timing'])if requested085.get('timing')else '')
                if requested085.get('target_enemy'):
                    target085=requested085['target_enemy']
                    assert window.target_stage_choices.select_value(target085['stage_id'])
                    assert window.target_enemy_choices.select_value(target085)
                    app.processEvents()
                    assert window.target_enemy.currentData()==target085
                else:window.target_enemy.setCurrentIndex(0)
                if owner085=='mechanist' and number085==3:
                    assert isinstance(window.charge_count,QSpinBox) and window.charge_count.minimum()==0 and window.charge_count.maximum()==100
                    window.charge_count.setValue(requested085['charge_count'])
                if section085==82:
                    checkbox085=option_widgets[(owner085,'low_cost_healing_target')]
                    casts085=option_widgets[(owner085,'casts_used')]
                    assert isinstance(checkbox085,QCheckBox)
                    checkbox085.setChecked(requested085['low_cost_healing_target'])
                    if number085==2:
                        assert isinstance(casts085,QSpinBox) and casts085.minimum()==0 and casts085.maximum()==2
                        casts085.setValue(requested085['casts_used'])
                if section085 in (83,84,85):
                    for key085,_label085,default085,maximum085,numbers085 in OPTIONS[owner085]:
                        widget085=option_widgets[(owner085,key085)]
                        if key085 not in requested085:continue
                        assert number085 in numbers085 and widget085.isVisible() and widget085.isEnabled()
                        if type(default085)is bool:
                            assert isinstance(widget085,QCheckBox)
                            widget085.setChecked(requested085[key085]);assert widget085.isChecked()is requested085[key085]
                        elif type(default085)is int:
                            assert isinstance(widget085,QSpinBox) and widget085.minimum()==0 and widget085.maximum()==maximum085
                            widget085.setValue(requested085[key085]);assert type(widget085.value())is int and widget085.value()==requested085[key085]
                        else:
                            assert type(default085)is float and isinstance(widget085,QDoubleSpinBox)
                            assert widget085.minimum()==0 and widget085.maximum()==maximum085
                            widget085.setValue(requested085[key085]);assert type(widget085.value())is float and widget085.value()==requested085[key085]
                    if case085.get('hidden_neural_checkbox_state'):
                        for key085 in ('enemy_is_boss','enemy_in_neural_break'):
                            hidden085=option_widgets[(owner085,key085)]
                            assert isinstance(hidden085,QCheckBox) and not hidden085.isVisible() and key085 not in requested085
                            hidden085.setChecked(True)
                    if case085.get('hidden_repeat_checkbox_state'):
                        hidden085=option_widgets[(owner085,'haruka_repeat')]
                        assert isinstance(hidden085,QCheckBox) and not hidden085.isVisible() and 'haruka_repeat'not in requested085
                        hidden085.setChecked(True)
                if case085.get('expected_error'):
                    supplemental_button.click();app.processEvents()
                    assert window.damage_result is None and window.damage_text.toPlainText()==case085['expected_error']
                    assert option_widgets[(owner085,'initial_neural_buildup')].value()==1500
                    assert window.target_enemy.currentData()==requested085.get('target_enemy')
                    if requested085.get('target_enemy'):
                        assert case085['processed_enemy_level_type']=='NORMAL'
                    else:assert requested085['enemy_is_boss']is False
                    errors085+=1;group085_counts[section085]=group085_counts.get(section085,0)+1
                    checks.append({'scope':'actual_neural_spinbox_preserves_existing_threshold_error',
                        'section':section085,'operator':owner085,'skill':number085,'context':case085['context'],
                        'mode':requested085['timing_mode'],'initial_neural_buildup':1500,
                        'manual_enemy_is_boss':option_widgets[(owner085,'enemy_is_boss')].isChecked(),
                        'manual_enemy_in_neural_break':option_widgets[(owner085,'enemy_in_neural_break')].isChecked(),
                        'actual_selected_target':window.target_enemy.currentData(),
                        'expected_existing_error':case085['expected_error'],'new_text_error_emitted_by_checkbox':False,
                        'native_identity_or_clock_verified':False,'passed':True})
                    continue
                result085=click_result();args085=window.damage_result['scenario']
                for key085 in ('operator','skill','elite','level','potential','trust','module_id','module_level',
                               'skill_rank','timing_mode','window_seconds','healing_targets','relic_ids',
                               'enemy_defense','enemy_resistance'):
                    assert args085[key085]==requested085[key085],(case085,key085,args085[key085])
                assert args085.get('timing',{})==requested085.get('timing',{})
                if requested085.get('target_enemy'):
                    assert window.target_enemy.currentData()==requested085['target_enemy']==args085['target_enemy']
                else:assert window.target_enemy.currentData()is None and 'target_enemy'not in args085
                if section085 in (83,84,85):
                    for key085,_label085,default085,_maximum085,numbers085 in OPTIONS[owner085]:
                        widget085=option_widgets[(owner085,key085)]
                        if number085 not in numbers085:
                            assert not widget085.isVisible() and key085 not in args085
                            continue
                        if key085 not in requested085:continue
                        if type(default085)is bool:require_real_bool070(widget085,args085,key085,requested085[key085])
                        elif type(default085)is int:require_real_int070(widget085,args085,key085,requested085[key085])
                        else:assert type(widget085.value())is float and type(args085[key085])is float and args085[key085]==requested085[key085]
                if owner085=='mechanist' and number085==3:
                    require_real_int070(window.charge_count,args085,'charge_count',requested085['charge_count'])
                if section085==81:
                    assert isinstance(window.damage_technical,QCheckBox)
                    assert window.damage_technical.isChecked()is case085['technical']
                    actual_ids085=[window.relic_list.item(i).data(Qt.ItemDataRole.UserRole)
                        for i in range(window.relic_list.count())
                        if window.relic_list.item(i).checkState()==Qt.CheckState.Checked]
                    assert args085['relic_ids']==actual_ids085==requested085['relic_ids']
                    require_warning_order085(result085,args085,window.damage_text.toPlainText(),case085['technical'])
                elif section085==82:
                    require_real_bool070(checkbox085,args085,'low_cost_healing_target',requested085['low_cost_healing_target'])
                    if number085==2:require_real_int070(casts085,args085,'casts_used',requested085['casts_used'])
                    else:assert not casts085.isVisible()and 'casts_used'not in args085
                    anchor085=canonical085({k:v for k,v in requested085.items()if k!='low_cost_healing_target'})
                    if not requested085['low_cost_healing_target']:anchors085[anchor085]=deepcopy(result085)
                    talents085,_=selected_talents(module.catalog()['operators'][owner085],args085)
                    factor085=next((t['values']['heal_scale']for t in talents085 if t['name']=='微创治疗'),1.0)
                    require_susuro_checkbox085(result085,args085,window.damage_text.toPlainText(),anchors085[anchor085],factor085)
                elif section085==83:
                    require_neural_checkbox085(result085,args085,window.damage_text.toPlainText())
                elif section085==84:
                    bonus085=module.catalog()['operators'][owner085]['skills'][number085-1]['levels'][args085['skill_rank']-1]['values'].get('atk',0.0)
                    if number085==2:
                        anchor085=canonical085({k:v for k,v in requested085.items()if k!='haruka_repeat'})
                        if not requested085['haruka_repeat']:anchors085[anchor085]=deepcopy(result085)
                        plain085=anchors085[anchor085]
                    else:plain085=result085
                    require_repeat_checkbox085(result085,args085,window.damage_text.toPlainText(),plain085,bonus085)
                elif section085==85:
                    anchor085=canonical085({k:v for k,v in requested085.items()if k!='near_previous_deployment'})
                    if not requested085['near_previous_deployment']:anchors085[anchor085]=deepcopy(result085)
                    talents085,_=selected_talents(module.catalog()['operators'][owner085],args085)
                    bonus085=next((t['values']['atk']for t in talents085 if t['name']=='翔虫机动'),0.0)
                    require_nearby_checkbox085(result085,args085,window.damage_text.toPlainText(),anchors085[anchor085],bonus085)
                else:raise AssertionError('085 section source not sealed')
                group085_counts[section085]=group085_counts.get(section085,0)+1
                checks.append({'scope':{81:'actual_relic_list_and_technical_checkbox_stable_unknown_warning_order',
                    82:'actual_low_cost_checkbox_and_readonly_susuro_talent_reference',
                    83:'actual_neural_checkboxes_spinbox_and_fixed_enemy_source_boundaries',
                    84:'actual_S2_repeat_checkbox_and_readonly_Haruka_source_boundaries',
                    85:'actual_nearby_checkbox_and_readonly_Orchid_talent_source_boundaries'}[section085],
                    'section':section085,'operator':owner085,'skill':number085,'context':case085['context'],
                    'mode':args085['timing_mode'],'elite':args085['elite'],'potential':args085['potential'],
                    'module_level':args085['module_level'],'relic_ids':args085['relic_ids'],
                    'technical':window.damage_technical.isChecked(),'low_cost_healing_target':args085.get('low_cost_healing_target'),
                    'casts_used':args085.get('casts_used'),'enemy_is_boss':args085.get('enemy_is_boss'),
                    'enemy_in_neural_break':args085.get('enemy_in_neural_break'),'initial_neural_buildup':args085.get('initial_neural_buildup'),
                    'actual_selected_target':args085.get('target_enemy'),'haruka_repeat':args085.get('haruka_repeat'),
                    'near_previous_deployment':args085.get('near_previous_deployment'),
                    'native_stack_or_recipient_clock_verified':False,'passed':True})
        finally:
            window.run.state=state085;window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy(account085));assert window.operator_observations is window.account_cache.records
            window.use_run_training.setChecked(run_training085);window.run_summary.setText(summary085);window.sync_run_config()
            if not state085.get('config',{}).get('difficulty'):window.difficulty.setCurrentIndex(difficulty085)
            assert window.target_stage_choices.select_value(stage085)
            if enemy085 is None:window.target_enemy.setCurrentIndex(0)
            else:assert window.target_enemy_choices.select_value(enemy085)
            window.update_operator();relics([]);window.timing_scenario.clear();window.damage_technical.setChecked(technical085)
        group085_end=len(checks)
        assert group085_counts=={81:136,82:216,83:450,84:88,85:264},group085_counts
        assert errors085==24,errors085
        receipt['supplemental_sections_81_85']=[81,82,83,84,85]
        receipt['supplemental_checks_by_section_81_85']=group085_counts
        receipt['supplemental_checks_81_85']=group085_end-group085_start
        receipt['section81_input_scope']='Genuine Qt relic list emits selected IDs in its original catalog index order; no reverse/duplicate/unknown ID controls invented. Existing unknown-composition warnings and each source pending order stay stable; technical checkbox preserves raw group names, default text retains both opaque warnings. No unknown numeric stack is applied.'
        receipt['section82_input_scope']='Genuine bool recipient checkbox and int prior-S2-use controls, with public readonly cultivation/module previews. Text validation is separate API coverage and cannot be emitted by this checkbox. Existing source-selected whole-cycle factor, missing-talent exclusions, zero-recipient arithmetic and friendly-clock unknown remain; no account ownership/actual recipient or native acquisition timing is invented.'
        receipt['section83_input_scope']='Only existing neural True/False checkboxes, numeric buildup spinboxes and genuine fixed-enemy choices. Mantra S3 hides and omits these keys while its actual default API neural consumer remains; no synthetic S3 flag control. Public threshold1500 error remains for manual normal or identity-derived NORMAL targets; selected BOSS overrides raw manual bool. River periodic scheduling, S1 attachment and S3/incoming/bait clocks remain unknown.'
        receipt['section83_expected_existing_threshold_errors']=errors085
        receipt['section84_input_scope']='Genuine S2 repeat checkbox works at E1 without requiring E2 flower talent; inactive S1/S3 values are omitted. Source skill attack parameter and infinite-mode/cycle exclusions preserve their existing meaning. Readonly module eligibility, absent flower source and actual friendly/activation clocks remain distinct.'
        receipt['section85_input_scope']='Genuine nearby checkbox across available Orchid skills and readonly E0/E1/E2 cultivation/module previews; absent E0 翔虫机动 is ignored, actual E1/E2 same-identity selected talent coefficients apply. Redeploy values and conditional arrow references do not establish actual movement, 30-second phase overlap, collision, retreat or redeployment events.'
        receipt['sections83_85_final_checks_pending']=False
        assert receipt['sections83_85_final_checks_pending']is False,'Final83-85 source/schema are pending'


        # BEGIN FINAL090 ACTUAL SOURCE-BOUND ADDITIONS
        group090_start=len(checks)
        state090=_copy090.deepcopy(window.run.state)
        account090=_copy090.deepcopy(window.operator_observations)
        use090=window.use_run_training.isChecked()
        summary090=window.run_summary.text()
        animation090=_copy090.deepcopy(window.animation_previews)
        animation_key090=window.animation_preview_key
        technical090=window.damage_technical.isChecked()
        continuous090=window.continuous_attacks.isChecked()
        source090_before=source_hashes()
        entries090_before=dict(entry_counts090)
        previous090=_count_enabled100
        _count_enabled100=True
        new_counts090={86:0,87:0,88:0,89:0}
        try:
            rows090=[{'section': 86, 'pair_id': 'active:char_4228_closur:reinforcement_blocks_target', 'kind': 'active', 'field': 'reinforcement_blocks_target', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_4228_closur', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'reinforcement_blocks_target': False}, 'context': 'active:char_4228_closur:reinforcement_blocks_target checked=False', 'expected_public_projection': {'attack': 993.6, 'total_damage': 28814.4, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 29, 'per_hit': 993.6, 'total': 28814.4, 'source_unit': 'operator', 'times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4228_closur', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840], 'release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0], 'emitted_impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'emitted_times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0], 'emitted_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'hit_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'interval_frames_by_attack': [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_4228_closur', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140], 'release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0], 'emitted_impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'emitted_times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0], 'emitted_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'hit_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'interval_frames_by_attack': [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 6.0, 'cycle_seconds': 70.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1762, 'attack': 561.6, 'defense': 151, 'resistance': 0.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '模型扩展', 'initial_seconds': 6.0, 'recharge_seconds': 40.0, 'cycle_seconds': 70.0, 'duration_seconds': 30.0, 'total_damage': 28814.4, 'total_healing': 0, 'phase_damage': 28814.4, 'phase_healing': 0, 'cycle_dps': 724.5257142857143, 'cycle_hps': 0.0, 'cycle_damage': 50716.8, 'cycle_healing': 0, 'skill_attack': 993.6, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'技能攻击': 29}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 960.48, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'd3ab5e0de916514f45d7bfd9cca440cbd81992046c76d82a0416950741d627cb'}, {'section': 86, 'pair_id': 'active:char_4228_closur:reinforcement_blocks_target', 'kind': 'active', 'field': 'reinforcement_blocks_target', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_4228_closur', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'reinforcement_blocks_target': True}, 'context': 'active:char_4228_closur:reinforcement_blocks_target checked=True', 'expected_public_projection': {'attack': 1490.4, 'total_damage': 43221.600000000006, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 29, 'per_hit': 1490.4, 'total': 43221.600000000006, 'source_unit': 'operator', 'times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4228_closur', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840], 'release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0], 'emitted_impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'emitted_times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0], 'emitted_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'hit_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870], 'interval_frames_by_attack': [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_4228_closur', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140], 'release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0], 'emitted_impact_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'emitted_times_seconds': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0], 'emitted_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'hit_release_frames': [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170], 'interval_frames_by_attack': [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 6.0, 'cycle_seconds': 70.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1762, 'attack': 561.6, 'defense': 151, 'resistance': 0.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '模型扩展', 'initial_seconds': 6.0, 'recharge_seconds': 40.0, 'cycle_seconds': 70.0, 'duration_seconds': 30.0, 'total_damage': 43221.600000000006, 'total_healing': 0, 'phase_damage': 43221.600000000006, 'phase_healing': 0, 'cycle_dps': 1086.7885714285717, 'cycle_hps': 0.0, 'cycle_damage': 76075.20000000001, 'cycle_healing': 0, 'skill_attack': 1490.4, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'技能攻击': 29}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 1440.7200000000003, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'f86a66368883218b39b50fa512a1ed03147ae99be38298d29c58b2461ffe3a7d'}, {'section': 86, 'pair_id': 'active:char_437_mizuki:enemy_below_half', 'kind': 'active', 'field': 'enemy_below_half', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_437_mizuki', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'enemy_below_half': False}, 'context': 'active:char_437_mizuki:enemy_below_half checked=False', 'expected_public_projection': {'attack': 1267.5, 'total_damage': 20913.75, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 11, 'per_hit': 1267.5, 'total': 13942.5, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335]}, {'name': '创伤性癔症', 'damage_type': 'magic', 'hits': 11, 'per_hit': 633.75, 'total': 6971.25, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 60, 'interval_seconds': 2.0, 'start_frames': [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600], 'release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'emitted_times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'hit_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'interval_frames_by_attack': [60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 60, 'interval_seconds': 2.0, 'start_frames': [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600], 'release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'emitted_times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'hit_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'interval_frames_by_attack': [60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [30, 135, 240, 345], 'release_frames': [46, 151, 256, 361], 'impact_frames': [46, 151, 256, 361], 'times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_impact_frames': [46, 151, 256, 361], 'emitted_times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_release_frames': [46, 151, 256, 361], 'hit_release_frames': [46, 151, 256, 361], 'interval_frames_by_attack': [105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [30, 135, 240, 345], 'release_frames': [46, 151, 256, 361], 'impact_frames': [46, 151, 256, 361], 'times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_impact_frames': [46, 151, 256, 361], 'emitted_times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_release_frames': [46, 151, 256, 361], 'hit_release_frames': [46, 151, 256, 361], 'interval_frames_by_attack': [105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.0, 'cycle_seconds': 36.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1758, 'attack': 975.0, 'defense': 356, 'resistance': 30.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 0.0}, 'skill': {'name': '囚徒困境', 'initial_seconds': 5.0, 'recharge_seconds': 15.0, 'cycle_seconds': 36.0, 'duration_seconds': 21.0, 'total_damage': 20913.75, 'total_healing': 0, 'phase_damage': 20913.75, 'phase_healing': 0, 'cycle_dps': 743.4375, 'cycle_hps': 0.0, 'cycle_damage': 26763.75, 'cycle_healing': 0, 'skill_attack': 1267.5, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'创伤性癔症': 11, '技能攻击': 11}, 'window_seconds': 21.0, 'window_healing': 0, 'window_dps': 995.8928571428571, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '5aa26f74657d125387239ddf75774fd0e4385c75d5a84c043f49f93023fe7989'}, {'section': 86, 'pair_id': 'active:char_437_mizuki:enemy_below_half', 'kind': 'active', 'field': 'enemy_below_half', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_437_mizuki', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'enemy_below_half': True}, 'context': 'active:char_437_mizuki:enemy_below_half checked=True', 'expected_public_projection': {'attack': 1365.0000000000002, 'total_damage': 22522.500000000004, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 11, 'per_hit': 1365.0000000000002, 'total': 15015.000000000002, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335]}, {'name': '创伤性癔症', 'damage_type': 'magic', 'hits': 11, 'per_hit': 682.5000000000001, 'total': 7507.500000000001, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 60, 'interval_seconds': 2.0, 'start_frames': [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600], 'release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'emitted_times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'hit_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'interval_frames_by_attack': [60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 60, 'interval_seconds': 2.0, 'start_frames': [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600], 'release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_impact_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'emitted_times_seconds': [0.5333333333333333, 2.533333333333333, 4.533333333333333, 6.533333333333333, 8.533333333333333, 10.533333333333333, 12.533333333333333, 14.533333333333333, 16.533333333333335, 18.533333333333335, 20.533333333333335], 'emitted_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'hit_release_frames': [16, 76, 136, 196, 256, 316, 376, 436, 496, 556, 616], 'interval_frames_by_attack': [60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [30, 135, 240, 345], 'release_frames': [46, 151, 256, 361], 'impact_frames': [46, 151, 256, 361], 'times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_impact_frames': [46, 151, 256, 361], 'emitted_times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_release_frames': [46, 151, 256, 361], 'hit_release_frames': [46, 151, 256, 361], 'interval_frames_by_attack': [105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [30, 135, 240, 345], 'release_frames': [46, 151, 256, 361], 'impact_frames': [46, 151, 256, 361], 'times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_impact_frames': [46, 151, 256, 361], 'emitted_times_seconds': [1.5333333333333334, 5.033333333333333, 8.533333333333333, 12.033333333333333], 'emitted_release_frames': [46, 151, 256, 361], 'hit_release_frames': [46, 151, 256, 361], 'interval_frames_by_attack': [105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.0, 'cycle_seconds': 36.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1758, 'attack': 1072.5, 'defense': 356, 'resistance': 30.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 0.0}, 'skill': {'name': '囚徒困境', 'initial_seconds': 5.0, 'recharge_seconds': 15.0, 'cycle_seconds': 36.0, 'duration_seconds': 21.0, 'total_damage': 22522.500000000004, 'total_healing': 0, 'phase_damage': 22522.500000000004, 'phase_healing': 0, 'cycle_dps': 804.3750000000001, 'cycle_hps': 0.0, 'cycle_damage': 28957.500000000004, 'cycle_healing': 0, 'skill_attack': 1365.0000000000002, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'创伤性癔症': 11, '技能攻击': 11}, 'window_seconds': 21.0, 'window_healing': 0, 'window_dps': 1072.5000000000002, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'd05e4943396775be1829a07b60efcccc1d4dd2ef45c247b232cfb7b18db163fe'}, {'section': 86, 'pair_id': 'active:char_206_gnosis:frozen_at_skill_end', 'kind': 'active', 'field': 'frozen_at_skill_end', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_206_gnosis', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'cold_state': 0, 'frozen_at_skill_end': False}, 'context': 'active:char_206_gnosis:frozen_at_skill_end checked=False', 'expected_public_projection': {'attack': 535.0, 'total_damage': 10165.0, 'components': [{'name': '失温症攻击', 'damage_type': 'magic', 'hits': 19, 'per_hit': 535.0, 'total': 10165.0, 'times_seconds': [0.26666666666666666, 0.9666666666666667, 1.6666666666666667, 2.3666666666666667, 3.066666666666667, 3.7666666666666666, 4.466666666666667, 5.166666666666667, 5.866666666666666, 6.566666666666666, 7.266666666666667, 7.966666666666667, 8.666666666666666, 9.366666666666667, 10.066666666666666, 10.766666666666667, 11.466666666666667, 12.166666666666666, 12.866666666666667]}], 'attack_speed': 230.0, 'base_attack_speed': 100.0, 'interval_seconds': 0.6956521739130435, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_206_gnosis', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 8, 'recovery_frames': 13, 'interval_frames': 21, 'interval_seconds': 0.7, 'start_frames': [0, 21, 42, 63, 84, 105, 126, 147, 168, 189, 210, 231, 252, 273, 294, 315, 336, 357, 378], 'release_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'impact_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'times_seconds': [0.26666666666666666, 0.9666666666666667, 1.6666666666666667, 2.3666666666666667, 3.066666666666667, 3.7666666666666666, 4.466666666666667, 5.166666666666667, 5.866666666666666, 6.566666666666666, 7.266666666666667, 7.966666666666667, 8.666666666666666, 9.366666666666667, 10.066666666666666, 10.766666666666667, 11.466666666666667, 12.166666666666666, 12.866666666666667], 'emitted_impact_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'emitted_times_seconds': [0.26666666666666666, 0.9666666666666667, 1.6666666666666667, 2.3666666666666667, 3.066666666666667, 3.7666666666666666, 4.466666666666667, 5.166666666666667, 5.866666666666666, 6.566666666666666, 7.266666666666667, 7.966666666666667, 8.666666666666666, 9.366666666666667, 10.066666666666666, 10.766666666666667, 11.466666666666667, 12.166666666666666, 12.866666666666667], 'emitted_release_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'hit_release_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'interval_frames_by_attack': [21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 9, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_206_gnosis', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 24, 'interval_frames': 48, 'interval_seconds': 1.6, 'start_frames': [9, 57, 105, 153, 201, 249, 297, 345, 393, 441, 489, 537, 585, 633, 681, 729, 777, 825, 873, 921, 969, 1017, 1065, 1113, 1161], 'release_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'impact_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'times_seconds': [0.7666666666666667, 2.3666666666666667, 3.966666666666667, 5.566666666666666, 7.166666666666667, 8.766666666666667, 10.366666666666667, 11.966666666666667, 13.566666666666666, 15.166666666666666, 16.766666666666666, 18.366666666666667, 19.966666666666665, 21.566666666666666, 23.166666666666668, 24.766666666666666, 26.366666666666667, 27.966666666666665, 29.566666666666666, 31.166666666666668, 32.766666666666666, 34.36666666666667, 35.96666666666667, 37.56666666666667, 39.166666666666664], 'emitted_impact_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'emitted_times_seconds': [0.7666666666666667, 2.3666666666666667, 3.966666666666667, 5.566666666666666, 7.166666666666667, 8.766666666666667, 10.366666666666667, 11.966666666666667, 13.566666666666666, 15.166666666666666, 16.766666666666666, 18.366666666666667, 19.966666666666665, 21.566666666666666, 23.166666666666668, 24.766666666666666, 26.366666666666667, 27.966666666666665, 29.566666666666666, 31.166666666666668, 32.766666666666666, 34.36666666666667, 35.96666666666667, 37.56666666666667, 39.166666666666664], 'emitted_release_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'hit_release_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'interval_frames_by_attack': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 9, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 15.0, 'cycle_seconds': 53.0}, 'total_healing': 0, 'attack_speed_reference': 230.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2035, 'attack': 535.0, 'defense': 132, 'resistance': 25.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '失温症', 'initial_seconds': 15.0, 'recharge_seconds': 40.0, 'cycle_seconds': 53.0, 'duration_seconds': 13.0, 'total_damage': 10165.0, 'total_healing': 0, 'phase_damage': 10165.0, 'phase_healing': 0, 'cycle_dps': 444.1509433962264, 'cycle_hps': 0.0, 'cycle_damage': 23540.0, 'cycle_healing': 0, 'skill_attack': 535.0, 'skill_attack_speed': 230.0, 'skill_attack_speed_reference': 230.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'失温症攻击': 19}, 'window_seconds': 13.0, 'window_healing': 0, 'window_dps': 781.9230769230769, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'ef707ce250952502577b39500f09d881bfefbe95627aa55524e91670d730a542'}, {'section': 86, 'pair_id': 'active:char_206_gnosis:frozen_at_skill_end', 'kind': 'active', 'field': 'frozen_at_skill_end', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_206_gnosis', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'cold_state': 0, 'frozen_at_skill_end': True}, 'context': 'active:char_206_gnosis:frozen_at_skill_end checked=True', 'expected_public_projection': {'attack': 535.0, 'total_damage': 13375.0, 'components': [{'name': '失温症攻击', 'damage_type': 'magic', 'hits': 19, 'per_hit': 535.0, 'total': 10165.0, 'times_seconds': [0.26666666666666666, 0.9666666666666667, 1.6666666666666667, 2.3666666666666667, 3.066666666666667, 3.7666666666666666, 4.466666666666667, 5.166666666666667, 5.866666666666666, 6.566666666666666, 7.266666666666667, 7.966666666666667, 8.666666666666666, 9.366666666666667, 10.066666666666666, 10.766666666666667, 11.466666666666667, 12.166666666666666, 12.866666666666667]}, {'name': '失温症终结', 'damage_type': 'magic', 'hits': 1, 'per_hit': 3210.0, 'total': 3210.0, 'terminal_clock_verified': False, 'nominal_terminal_seconds': 13.0}], 'attack_speed': 230.0, 'base_attack_speed': 100.0, 'interval_seconds': 0.6956521739130435, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_206_gnosis', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 8, 'recovery_frames': 13, 'interval_frames': 21, 'interval_seconds': 0.7, 'start_frames': [0, 21, 42, 63, 84, 105, 126, 147, 168, 189, 210, 231, 252, 273, 294, 315, 336, 357, 378], 'release_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'impact_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'times_seconds': [0.26666666666666666, 0.9666666666666667, 1.6666666666666667, 2.3666666666666667, 3.066666666666667, 3.7666666666666666, 4.466666666666667, 5.166666666666667, 5.866666666666666, 6.566666666666666, 7.266666666666667, 7.966666666666667, 8.666666666666666, 9.366666666666667, 10.066666666666666, 10.766666666666667, 11.466666666666667, 12.166666666666666, 12.866666666666667], 'emitted_impact_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'emitted_times_seconds': [0.26666666666666666, 0.9666666666666667, 1.6666666666666667, 2.3666666666666667, 3.066666666666667, 3.7666666666666666, 4.466666666666667, 5.166666666666667, 5.866666666666666, 6.566666666666666, 7.266666666666667, 7.966666666666667, 8.666666666666666, 9.366666666666667, 10.066666666666666, 10.766666666666667, 11.466666666666667, 12.166666666666666, 12.866666666666667], 'emitted_release_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'hit_release_frames': [8, 29, 50, 71, 92, 113, 134, 155, 176, 197, 218, 239, 260, 281, 302, 323, 344, 365, 386], 'interval_frames_by_attack': [21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 9, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_206_gnosis', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 24, 'interval_frames': 48, 'interval_seconds': 1.6, 'start_frames': [9, 57, 105, 153, 201, 249, 297, 345, 393, 441, 489, 537, 585, 633, 681, 729, 777, 825, 873, 921, 969, 1017, 1065, 1113, 1161], 'release_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'impact_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'times_seconds': [0.7666666666666667, 2.3666666666666667, 3.966666666666667, 5.566666666666666, 7.166666666666667, 8.766666666666667, 10.366666666666667, 11.966666666666667, 13.566666666666666, 15.166666666666666, 16.766666666666666, 18.366666666666667, 19.966666666666665, 21.566666666666666, 23.166666666666668, 24.766666666666666, 26.366666666666667, 27.966666666666665, 29.566666666666666, 31.166666666666668, 32.766666666666666, 34.36666666666667, 35.96666666666667, 37.56666666666667, 39.166666666666664], 'emitted_impact_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'emitted_times_seconds': [0.7666666666666667, 2.3666666666666667, 3.966666666666667, 5.566666666666666, 7.166666666666667, 8.766666666666667, 10.366666666666667, 11.966666666666667, 13.566666666666666, 15.166666666666666, 16.766666666666666, 18.366666666666667, 19.966666666666665, 21.566666666666666, 23.166666666666668, 24.766666666666666, 26.366666666666667, 27.966666666666665, 29.566666666666666, 31.166666666666668, 32.766666666666666, 34.36666666666667, 35.96666666666667, 37.56666666666667, 39.166666666666664], 'emitted_release_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'hit_release_frames': [23, 71, 119, 167, 215, 263, 311, 359, 407, 455, 503, 551, 599, 647, 695, 743, 791, 839, 887, 935, 983, 1031, 1079, 1127, 1175], 'interval_frames_by_attack': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 9, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['失温症终结'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 15.0, 'cycle_seconds': 53.0}, 'total_healing': 0, 'attack_speed_reference': 230.0, 'base_attack_speed_reference': 100.0, 'gnosis_terminal_reference': {'nominal_skill_end_seconds': 13.0, 'terminal_clock_verified': False, 'freeze_removal_order_verified': False, 'conditional_terminal_damage': 3210.0, 'source_possible': {'cast': True, 'window': True}, 'same_frame_disappearance_unresolved': False}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2035, 'attack': 535.0, 'defense': 132, 'resistance': 25.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '失温症', 'initial_seconds': 15.0, 'recharge_seconds': 40.0, 'cycle_seconds': 53.0, 'duration_seconds': 13.0, 'total_damage': 13375.0, 'total_healing': 0, 'phase_damage': 13375.0, 'phase_healing': 0, 'cycle_dps': 504.7169811320755, 'cycle_hps': 0.0, 'cycle_damage': 26750.0, 'cycle_healing': 0, 'skill_attack': 535.0, 'skill_attack_speed': 230.0, 'skill_attack_speed_reference': 230.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'失温症攻击': 19, '失温症终结': 1}, 'window_seconds': 13.0, 'window_healing': 0, 'window_dps': 1028.8461538461538, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'd74cf41ac163272015aa1d8b11e8135a8670f196e27233819cbfc33a32c8a4cd'}, {'section': 86, 'pair_id': 'active:char_4087_ines:ines_first_deployment', 'kind': 'active', 'field': 'ines_first_deployment', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_4087_ines', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'stolen_enemy_count': 1, 'ines_first_deployment': False}, 'context': 'active:char_4087_ines:ines_first_deployment checked=False', 'expected_public_projection': {'attack': 1751.4, 'total_damage': None, 'components': [{'name': '收回影哨', 'damage_type': 'physical', 'hits': 1, 'per_hit': 3502.8, 'total': 3502.8, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '技能攻击', 'damage_type': 'physical', 'hits': 16, 'per_hit': 1751.4, 'total': 28022.4, 'source_unit': 'operator', 'times_seconds': [0.4666666666666667, 1.4666666666666666, 2.466666666666667, 3.466666666666667, 4.466666666666667, 5.466666666666667, 6.466666666666667, 7.466666666666667, 8.466666666666667, 9.466666666666667, 10.466666666666667, 11.466666666666667, 12.466666666666667, 13.466666666666667, 14.466666666666667, 15.466666666666667]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4087_ines', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 16, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450], 'release_frames': [14, 44, 74, 104, 134, 164, 194, 224, 254, 284, 314, 344, 374, 404, 434, 464], 'impact_frames': [14, 44, 74, 104, 134, 164, 194, 224, 254, 284, 314, 344, 374, 404, 434, 464], 'times_seconds': [0.4666666666666667, 1.4666666666666666, 2.466666666666667, 3.466666666666667, 4.466666666666667, 5.466666666666667, 6.466666666666667, 7.466666666666667, 8.466666666666667, 9.466666666666667, 10.466666666666667, 11.466666666666667, 12.466666666666667, 13.466666666666667, 14.466666666666667, 15.466666666666667], 'emitted_impact_frames': [14, 44, 74, 104, 134, 164, 194, 224, 254, 284, 314, 344, 374, 404, 434, 464], 'emitted_times_seconds': [0.4666666666666667, 1.4666666666666666, 2.466666666666667, 3.466666666666667, 4.466666666666667, 5.466666666666667, 6.466666666666667, 7.466666666666667, 8.466666666666667, 9.466666666666667, 10.466666666666667, 11.466666666666667, 12.466666666666667, 13.466666666666667, 14.466666666666667, 15.466666666666667], 'emitted_release_frames': [14, 44, 74, 104, 134, 164, 194, 224, 254, 284, 314, 344, 374, 404, 434, 464], 'hit_release_frames': [14, 44, 74, 104, 134, 164, 194, 224, 254, 284, 314, 344, 374, 404, 434, 464], 'interval_frames_by_attack': [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': ['收回影哨'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'external_event_reference': {'conditional_components': [{'name': '收回影哨', 'damage_type': 'physical', 'per_hit': 3502.8, 'hits': 1, 'total': 3502.8}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'kind': 'ines_shadow_return', 'parameter_rows': [['穿过敌人数上限参数', 6.0, '名']], 'notes': ['收回影哨列单个穿过目标的条件伤害；立刻收回不证明路径碰撞发生在开启当帧。', '本体供靶/打断窗口不代表影哨路径覆盖；实际路径、碰撞及施放归属未核验，未叠加到完整输出。'], 'window_reference': {'conditional_components': [{'name': '收回影哨', 'damage_type': 'physical', 'per_hit': 3502.8, 'hits': 1, 'total': 3502.8}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False, 'kind': 'ines_shadow_return', 'parameter_rows': [['穿过敌人数上限参数', 6.0, '名']], 'notes': ['收回影哨列单个穿过目标的条件伤害；立刻收回不证明路径碰撞发生在开启当帧。', '本体供靶/打断窗口不代表影哨路径覆盖；实际路径、碰撞及施放归属未核验，未叠加到完整输出。']}, 'actual_event_times_seconds': None}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2121, 'attack': 729.0, 'defense': 311, 'resistance': 0.0, 'redeploy_seconds': 35.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '独影归途', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 16.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1751.4, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': None, 'mode': 'deployment', 'hit_counts': {'技能攻击': 16, '收回影哨': None}, 'window_seconds': 16.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '44293cf1c9ee94df9bdbf106b3091c0bbd549c9598787780986ddf80a79fe1f3'}, {'section': 86, 'pair_id': 'active:char_4087_ines:ines_first_deployment', 'kind': 'active', 'field': 'ines_first_deployment', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_4087_ines', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'stolen_enemy_count': 1, 'ines_first_deployment': True}, 'context': 'active:char_4087_ines:ines_first_deployment checked=True', 'expected_public_projection': {'attack': 1751.4, 'total_damage': 0, 'components': [], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2121, 'attack': 729.0, 'defense': 311, 'resistance': 0.0, 'redeploy_seconds': 35.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '独影归途', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 0.0, 'total_damage': 0, 'total_healing': 0, 'phase_damage': 0, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1751.4, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': None, 'mode': 'deployment', 'hit_counts': {}, 'window_seconds': 0, 'window_healing': 0, 'window_dps': None, 'window_hps': None}}}, 'saved_result_full_json_sha256': '3de5f3ef373b3c28d247d554e0df2c86d6edfba2fe8c73c8a30bd3f12f75e697'}, {'section': 86, 'pair_id': 'active:char_4182_oblvns:ranged_attack', 'kind': 'active', 'field': 'ranged_attack', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': False, 'organ_mode': False, 'fever': False}, 'context': 'active:char_4182_oblvns:ranged_attack checked=False', 'expected_public_projection': {'attack': 1648.5, 'total_damage': 41212.5, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 25, 'per_hit': 1648.5, 'total': 41212.5, 'source_unit': 'operator', 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668]}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 35, 'interval_seconds': 1.1666666666666667, 'start_frames': [0, 35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840], 'release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'emitted_times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'hit_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'interval_frames_by_attack': [35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.866666666666666, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '满月的舞会', 'initial_seconds': 5.866666666666666, 'recharge_seconds': 5.866666666666666, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': None, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1648.5, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'switch', 'hit_counts': {'技能攻击': 25}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 1373.75, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '56209bdc4a24f10efadc400c2579a9d998715978cbc7dbf453706a3df1315964'}, {'section': 86, 'pair_id': 'active:char_4182_oblvns:ranged_attack', 'kind': 'active', 'field': 'ranged_attack', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True, 'organ_mode': False, 'fever': False}, 'context': 'active:char_4182_oblvns:ranged_attack checked=True', 'expected_public_projection': {'attack': 1648.5, 'total_damage': 32970.00000000001, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 25, 'per_hit': 1318.8000000000002, 'total': 32970.00000000001, 'source_unit': 'operator', 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668]}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 35, 'interval_seconds': 1.1666666666666667, 'start_frames': [0, 35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840], 'release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'emitted_times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'hit_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'interval_frames_by_attack': [35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.866666666666666, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '满月的舞会', 'initial_seconds': 5.866666666666666, 'recharge_seconds': 5.866666666666666, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': None, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1648.5, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'switch', 'hit_counts': {'技能攻击': 25}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 1099.0000000000002, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3549f7ae0b6ae04f2193b1dba864c2503780e225ad68102c952ca2f382c3627f'}, {'section': 86, 'pair_id': 'active:char_4182_oblvns:organ_mode', 'kind': 'active', 'field': 'organ_mode', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True, 'organ_mode': False, 'fever': False}, 'context': 'active:char_4182_oblvns:organ_mode checked=False', 'expected_public_projection': {'attack': 1648.5, 'total_damage': 32970.00000000001, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 25, 'per_hit': 1318.8000000000002, 'total': 32970.00000000001, 'source_unit': 'operator', 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668]}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 35, 'interval_seconds': 1.1666666666666667, 'start_frames': [0, 35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840], 'release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'emitted_times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'hit_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'interval_frames_by_attack': [35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.866666666666666, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '满月的舞会', 'initial_seconds': 5.866666666666666, 'recharge_seconds': 5.866666666666666, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': None, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1648.5, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'switch', 'hit_counts': {'技能攻击': 25}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 1099.0000000000002, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3549f7ae0b6ae04f2193b1dba864c2503780e225ad68102c952ca2f382c3627f'}, {'section': 86, 'pair_id': 'active:char_4182_oblvns:organ_mode', 'kind': 'active', 'field': 'organ_mode', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True, 'organ_mode': True, 'fever': False}, 'context': 'active:char_4182_oblvns:organ_mode checked=True', 'expected_public_projection': {'attack': 785.0, 'total_damage': 37052.0, 'components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 59, 'per_hit': 628.0, 'total': 37052.0, 'source_unit': 'operator', 'times_seconds': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5]}], 'attack_speed': 252.0, 'base_attack_speed': 112.0, 'interval_seconds': 0.5158730158730159, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 15, 'interval_seconds': 0.5, 'start_frames': [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870], 'release_frames': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885], 'impact_frames': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885], 'times_seconds': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5], 'emitted_impact_frames': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885], 'emitted_times_seconds': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5], 'emitted_release_frames': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885], 'hit_release_frames': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885], 'interval_frames_by_attack': [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.866666666666666, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 252.0, 'base_attack_speed_reference': 112.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '满月的舞会', 'initial_seconds': 5.866666666666666, 'recharge_seconds': 5.866666666666666, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': None, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 785.0, 'skill_attack_speed': 252.0, 'skill_attack_speed_reference': 252.0, 'sp_recovery_per_second': None, 'mode': 'switch', 'hit_counts': {'技能攻击': 59}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 1235.0666666666666, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'd34f953f2a3cc9306e1ead016fd8222e1585ba0ee135c69fd3e6ae8784b3b20d'}, {'section': 86, 'pair_id': 'active:char_4182_oblvns:fever', 'kind': 'active', 'field': 'fever', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True, 'organ_mode': False, 'fever': False}, 'context': 'active:char_4182_oblvns:fever checked=False', 'expected_public_projection': {'attack': 1648.5, 'total_damage': 32970.00000000001, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 25, 'per_hit': 1318.8000000000002, 'total': 32970.00000000001, 'source_unit': 'operator', 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668]}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 35, 'interval_seconds': 1.1666666666666667, 'start_frames': [0, 35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840], 'release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'emitted_times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'hit_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'interval_frames_by_attack': [35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.866666666666666, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '满月的舞会', 'initial_seconds': 5.866666666666666, 'recharge_seconds': 5.866666666666666, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': None, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1648.5, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'switch', 'hit_counts': {'技能攻击': 25}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 1099.0000000000002, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3549f7ae0b6ae04f2193b1dba864c2503780e225ad68102c952ca2f382c3627f'}, {'section': 86, 'pair_id': 'active:char_4182_oblvns:fever', 'kind': 'active', 'field': 'fever', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True, 'organ_mode': False, 'fever': True}, 'context': 'active:char_4182_oblvns:fever checked=True', 'expected_public_projection': {'attack': 1648.5, 'total_damage': 65940.00000000001, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 50, 'per_hit': 1318.8000000000002, 'total': 65940.00000000001, 'source_unit': 'operator', 'times_seconds': [1.1666666666666667, 1.1666666666666667, 2.3333333333333335, 2.3333333333333335, 3.5, 3.5, 4.666666666666667, 4.666666666666667, 5.833333333333333, 5.833333333333333, 7.0, 7.0, 8.166666666666666, 8.166666666666666, 9.333333333333334, 9.333333333333334, 10.5, 10.5, 11.666666666666666, 11.666666666666666, 12.833333333333334, 12.833333333333334, 14.0, 14.0, 15.166666666666666, 15.166666666666666, 16.333333333333332, 16.333333333333332, 17.5, 17.5, 18.666666666666668, 18.666666666666668, 19.833333333333332, 19.833333333333332, 21.0, 21.0, 22.166666666666668, 22.166666666666668, 23.333333333333332, 23.333333333333332, 24.5, 24.5, 25.666666666666668, 25.666666666666668, 26.833333333333332, 26.833333333333332, 28.0, 28.0, 29.166666666666668, 29.166666666666668]}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 35, 'interval_seconds': 1.1666666666666667, 'start_frames': [0, 35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840], 'release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_impact_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'emitted_times_seconds': [1.1666666666666667, 2.3333333333333335, 3.5, 4.666666666666667, 5.833333333333333, 7.0, 8.166666666666666, 9.333333333333334, 10.5, 11.666666666666666, 12.833333333333334, 14.0, 15.166666666666666, 16.333333333333332, 17.5, 18.666666666666668, 19.833333333333332, 21.0, 22.166666666666668, 23.333333333333332, 24.5, 25.666666666666668, 26.833333333333332, 28.0, 29.166666666666668], 'emitted_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'hit_release_frames': [35, 70, 105, 140, 175, 210, 245, 280, 315, 350, 385, 420, 455, 490, 525, 560, 595, 630, 665, 700, 735, 770, 805, 840, 875], 'interval_frames_by_attack': [35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.866666666666666, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '满月的舞会', 'initial_seconds': 5.866666666666666, 'recharge_seconds': 5.866666666666666, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': None, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 1648.5, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'switch', 'hit_counts': {'技能攻击': 50}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': 2198.0000000000005, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'fdb01ab08f646bb4bdda9c61424e0f579c50ed563bac23f8226dee86b5536356'}, {'section': 86, 'pair_id': 'active:char_1048_orchd2:power_coating', 'kind': 'active', 'field': 'power_coating', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_1048_orchd2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'power_coating': False, 'near_previous_deployment': False, 'double_charge': True}, 'context': 'active:char_1048_orchd2:power_coating checked=False', 'expected_public_projection': {'attack': 942.0, 'total_damage': None, 'components': [{'name': '刚射', 'damage_type': 'physical', 'hits': 4, 'per_hit': 1507.2, 'total': 6028.8, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '刚连射', 'damage_type': 'physical', 'hits': 5, 'per_hit': 1884.0, 'total': 9420.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['刚射', '刚连射'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'unbound_cast_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 5, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1507.2, 'hits': 4, 'total': 6028.8}, {'name': '刚连射', 'damage_type': 'physical', 'per_hit': 1884.0, 'hits': 5, 'total': 9420.0}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 5, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1507.2, 'hits': 4, 'total': 6028.8}, {'name': '刚连射', 'damage_type': 'physical', 'per_hit': 1884.0, 'hits': 5, 'total': 9420.0}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'orchid_redeploy_reference': {'scope': 'cultivated attribute and same-identity talent parameter reference', 'operator_id': 'char_1048_orchd2', 'module_id': None, 'module_level': 0, 'module_unlocked': False, 'module_attribute_delta_seconds_parameter': 0, 'after_attribute_sources_seconds_reference': 70.0, 'talent_delta_seconds_parameter': -15, 'parameter_seconds': 55.0, 'original_talent_identity': {'talent_index': 3, 'prefab_key': '3'}, 'actual_retreat_seconds': None, 'actual_defeat_seconds': None, 'actual_next_deployment_seconds': None, 'events_scheduled': False, 'native_attachment_verified': False, 'live_state_verified': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime', 'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers', 'character_table.char_1048_orchd2.talents[1].candidates', 'character_table.char_1048_orchd2.talents[3].candidates', 'uniequip_table.equipDict.uniequip_002_orchd2', 'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard', 'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1788, 'attack': 942.0, 'defense': 231, 'resistance': 0.0, 'redeploy_seconds': 55.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '刚射', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 942.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'instant', 'hit_counts': {'刚射': None, '刚连射': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '79626c0fad5cdfb9a8751d9243564c5785b4d2a3b0d27bc729cd634440eb6ad9'}, {'section': 86, 'pair_id': 'active:char_1048_orchd2:power_coating', 'kind': 'active', 'field': 'power_coating', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_1048_orchd2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'power_coating': True, 'near_previous_deployment': False, 'double_charge': True}, 'context': 'active:char_1048_orchd2:power_coating checked=True', 'expected_public_projection': {'attack': 942.0, 'total_damage': None, 'components': [{'name': '刚射', 'damage_type': 'physical', 'hits': 4, 'per_hit': 1733.28, 'total': 6933.12, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '刚连射', 'damage_type': 'physical', 'hits': 5, 'per_hit': 2166.6, 'total': 10833.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['刚射', '刚连射'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'unbound_cast_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 5, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1733.28, 'hits': 4, 'total': 6933.12}, {'name': '刚连射', 'damage_type': 'physical', 'per_hit': 2166.6, 'hits': 5, 'total': 10833.0}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 5, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1733.28, 'hits': 4, 'total': 6933.12}, {'name': '刚连射', 'damage_type': 'physical', 'per_hit': 2166.6, 'hits': 5, 'total': 10833.0}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'orchid_redeploy_reference': {'scope': 'cultivated attribute and same-identity talent parameter reference', 'operator_id': 'char_1048_orchd2', 'module_id': None, 'module_level': 0, 'module_unlocked': False, 'module_attribute_delta_seconds_parameter': 0, 'after_attribute_sources_seconds_reference': 70.0, 'talent_delta_seconds_parameter': -15, 'parameter_seconds': 55.0, 'original_talent_identity': {'talent_index': 3, 'prefab_key': '3'}, 'actual_retreat_seconds': None, 'actual_defeat_seconds': None, 'actual_next_deployment_seconds': None, 'events_scheduled': False, 'native_attachment_verified': False, 'live_state_verified': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime', 'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers', 'character_table.char_1048_orchd2.talents[1].candidates', 'character_table.char_1048_orchd2.talents[3].candidates', 'uniequip_table.equipDict.uniequip_002_orchd2', 'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard', 'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1788, 'attack': 942.0, 'defense': 231, 'resistance': 0.0, 'redeploy_seconds': 55.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '刚射', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 942.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'instant', 'hit_counts': {'刚射': None, '刚连射': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '26425a27648665576865f1b2ada8de5eaa7b67754704327f64f6b4e7c78313f7'}, {'section': 86, 'pair_id': 'active:char_1048_orchd2:double_charge', 'kind': 'active', 'field': 'double_charge', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_1048_orchd2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'power_coating': True, 'near_previous_deployment': False, 'double_charge': False}, 'context': 'active:char_1048_orchd2:double_charge checked=False', 'expected_public_projection': {'attack': 942.0, 'total_damage': None, 'components': [{'name': '刚射', 'damage_type': 'physical', 'hits': 4, 'per_hit': 1733.28, 'total': 6933.12, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['刚射'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'unbound_cast_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 0, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1733.28, 'hits': 4, 'total': 6933.12}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 0, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1733.28, 'hits': 4, 'total': 6933.12}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'orchid_redeploy_reference': {'scope': 'cultivated attribute and same-identity talent parameter reference', 'operator_id': 'char_1048_orchd2', 'module_id': None, 'module_level': 0, 'module_unlocked': False, 'module_attribute_delta_seconds_parameter': 0, 'after_attribute_sources_seconds_reference': 70.0, 'talent_delta_seconds_parameter': -15, 'parameter_seconds': 55.0, 'original_talent_identity': {'talent_index': 3, 'prefab_key': '3'}, 'actual_retreat_seconds': None, 'actual_defeat_seconds': None, 'actual_next_deployment_seconds': None, 'events_scheduled': False, 'native_attachment_verified': False, 'live_state_verified': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime', 'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers', 'character_table.char_1048_orchd2.talents[1].candidates', 'character_table.char_1048_orchd2.talents[3].candidates', 'uniequip_table.equipDict.uniequip_002_orchd2', 'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard', 'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1788, 'attack': 942.0, 'defense': 231, 'resistance': 0.0, 'redeploy_seconds': 55.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '刚射', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 942.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'instant', 'hit_counts': {'刚射': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '9950db3cc65954d3ef9ba38df6874df9d14ecc494aa9456283292579422f76cf'}, {'section': 86, 'pair_id': 'active:char_1048_orchd2:double_charge', 'kind': 'active', 'field': 'double_charge', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_1048_orchd2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'power_coating': True, 'near_previous_deployment': False, 'double_charge': True}, 'context': 'active:char_1048_orchd2:double_charge checked=True', 'expected_public_projection': {'attack': 942.0, 'total_damage': None, 'components': [{'name': '刚射', 'damage_type': 'physical', 'hits': 4, 'per_hit': 1733.28, 'total': 6933.12, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '刚连射', 'damage_type': 'physical', 'hits': 5, 'per_hit': 2166.6, 'total': 10833.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['刚射', '刚连射'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'unbound_cast_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 5, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1733.28, 'hits': 4, 'total': 6933.12}, {'name': '刚连射', 'damage_type': 'physical', 'per_hit': 2166.6, 'hits': 5, 'total': 10833.0}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['首轮箭矢数量参数', 4, '支'], ['追加箭矢数量情景', 5, '支'], ['可充能次数参数', 4, '次']], 'notes': ['四箭及可选五箭保留条件量；额外充能消费、发射/飞行、强击瓶逐箭覆盖和实际结束未绑定。'], 'conditional_components': [{'name': '刚射', 'damage_type': 'physical', 'per_hit': 1733.28, 'hits': 4, 'total': 6933.12}, {'name': '刚连射', 'damage_type': 'physical', 'per_hit': 2166.6, 'hits': 5, 'total': 10833.0}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'orchid_redeploy_reference': {'scope': 'cultivated attribute and same-identity talent parameter reference', 'operator_id': 'char_1048_orchd2', 'module_id': None, 'module_level': 0, 'module_unlocked': False, 'module_attribute_delta_seconds_parameter': 0, 'after_attribute_sources_seconds_reference': 70.0, 'talent_delta_seconds_parameter': -15, 'parameter_seconds': 55.0, 'original_talent_identity': {'talent_index': 3, 'prefab_key': '3'}, 'actual_retreat_seconds': None, 'actual_defeat_seconds': None, 'actual_next_deployment_seconds': None, 'events_scheduled': False, 'native_attachment_verified': False, 'live_state_verified': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime', 'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers', 'character_table.char_1048_orchd2.talents[1].candidates', 'character_table.char_1048_orchd2.talents[3].candidates', 'uniequip_table.equipDict.uniequip_002_orchd2', 'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard', 'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1788, 'attack': 942.0, 'defense': 231, 'resistance': 0.0, 'redeploy_seconds': 55.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '刚射', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 942.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'instant', 'hit_counts': {'刚射': None, '刚连射': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '26425a27648665576865f1b2ada8de5eaa7b67754704327f64f6b4e7c78313f7'}, {'section': 86, 'pair_id': 'active:char_1041_angel2:steal_success', 'kind': 'active', 'field': 'steal_success', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_1041_angel2', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'steal_success': False}, 'context': 'active:char_1041_angel2:steal_success checked=False', 'expected_public_projection': {'attack': 918.04, 'total_damage': 108443.47499999999, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 35, 'per_hit': 2754.12, 'total': 96394.2, 'source_unit': 'operator', 'times_seconds': [0.13333333333333333, 0.7333333333333333, 1.3333333333333333, 1.9333333333333333, 2.533333333333333, 3.1333333333333333, 3.7333333333333334, 4.333333333333333, 4.933333333333334, 5.533333333333333, 6.133333333333334, 6.733333333333333, 7.333333333333333, 7.933333333333334, 8.533333333333333, 9.133333333333333, 9.733333333333333, 10.333333333333334, 10.933333333333334, 11.533333333333333, 12.133333333333333, 12.733333333333333, 13.333333333333334, 13.933333333333334, 14.533333333333333, 15.133333333333333, 15.733333333333333, 16.333333333333332, 16.933333333333334, 17.533333333333335, 18.133333333333333, 18.733333333333334, 19.333333333333332, 19.933333333333334, 20.533333333333335]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 8.75, 'per_hit': 1377.06, 'total': 12049.275}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 35, 'per_hit': 141.0, 'total': 4935.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 0.6000000000000001, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 4, 'recovery_frames': 14, 'interval_frames': 18, 'interval_seconds': 0.6, 'start_frames': [0, 18, 36, 54, 72, 90, 108, 126, 144, 162, 180, 198, 216, 234, 252, 270, 288, 306, 324, 342, 360, 378, 396, 414, 432, 450, 468, 486, 504, 522, 540, 558, 576, 594, 612], 'release_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'impact_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'times_seconds': [0.13333333333333333, 0.7333333333333333, 1.3333333333333333, 1.9333333333333333, 2.533333333333333, 3.1333333333333333, 3.7333333333333334, 4.333333333333333, 4.933333333333334, 5.533333333333333, 6.133333333333334, 6.733333333333333, 7.333333333333333, 7.933333333333334, 8.533333333333333, 9.133333333333333, 9.733333333333333, 10.333333333333334, 10.933333333333334, 11.533333333333333, 12.133333333333333, 12.733333333333333, 13.333333333333334, 13.933333333333334, 14.533333333333333, 15.133333333333333, 15.733333333333333, 16.333333333333332, 16.933333333333334, 17.533333333333335, 18.133333333333333, 18.733333333333334, 19.333333333333332, 19.933333333333334, 20.533333333333335], 'emitted_impact_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'emitted_times_seconds': [0.13333333333333333, 0.7333333333333333, 1.3333333333333333, 1.9333333333333333, 2.533333333333333, 3.1333333333333333, 3.7333333333333334, 4.333333333333333, 4.933333333333334, 5.533333333333333, 6.133333333333334, 6.733333333333333, 7.333333333333333, 7.933333333333334, 8.533333333333333, 9.133333333333333, 9.733333333333333, 10.333333333333334, 10.933333333333334, 11.533333333333333, 12.133333333333333, 12.733333333333333, 13.333333333333334, 13.933333333333334, 14.533333333333333, 15.133333333333333, 15.733333333333333, 16.333333333333332, 16.933333333333334, 17.533333333333335, 18.133333333333333, 18.733333333333334, 19.333333333333332, 19.933333333333334, 20.533333333333335], 'emitted_release_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'hit_release_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'interval_frames_by_attack': [18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 4, 'recovery_frames': 14, 'interval_frames': 18, 'interval_seconds': 0.6, 'start_frames': [0, 18, 36, 54, 72, 90, 108, 126, 144, 162, 180, 198, 216, 234, 252, 270, 288, 306, 324, 342, 360, 378, 396, 414, 432, 450, 468, 486, 504, 522, 540, 558, 576, 594, 612], 'release_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'impact_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'times_seconds': [0.13333333333333333, 0.7333333333333333, 1.3333333333333333, 1.9333333333333333, 2.533333333333333, 3.1333333333333333, 3.7333333333333334, 4.333333333333333, 4.933333333333334, 5.533333333333333, 6.133333333333334, 6.733333333333333, 7.333333333333333, 7.933333333333334, 8.533333333333333, 9.133333333333333, 9.733333333333333, 10.333333333333334, 10.933333333333334, 11.533333333333333, 12.133333333333333, 12.733333333333333, 13.333333333333334, 13.933333333333334, 14.533333333333333, 15.133333333333333, 15.733333333333333, 16.333333333333332, 16.933333333333334, 17.533333333333335, 18.133333333333333, 18.733333333333334, 19.333333333333332, 19.933333333333334, 20.533333333333335], 'emitted_impact_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'emitted_times_seconds': [0.13333333333333333, 0.7333333333333333, 1.3333333333333333, 1.9333333333333333, 2.533333333333333, 3.1333333333333333, 3.7333333333333334, 4.333333333333333, 4.933333333333334, 5.533333333333333, 6.133333333333334, 6.733333333333333, 7.333333333333333, 7.933333333333334, 8.533333333333333, 9.133333333333333, 9.733333333333333, 10.333333333333334, 10.933333333333334, 11.533333333333333, 12.133333333333333, 12.733333333333333, 13.333333333333334, 13.933333333333334, 14.533333333333333, 15.133333333333333, 15.733333333333333, 16.333333333333332, 16.933333333333334, 17.533333333333335, 18.133333333333333, 18.733333333333334, 19.333333333333332, 19.933333333333334, 20.533333333333335], 'emitted_release_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'hit_release_frames': [4, 22, 40, 58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 274, 292, 310, 328, 346, 364, 382, 400, 418, 436, 454, 472, 490, 508, 526, 544, 562, 580, 598, 616], 'interval_frames_by_attack': [18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351, 390, 429, 468, 507, 546, 585, 624, 663, 702, 741, 780, 819, 858], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.0, 'cycle_seconds': 50.56666666666666}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '开火成瘾症', 'initial_seconds': 5.0, 'recharge_seconds': 30.0, 'cycle_seconds': 50.56666666666666, 'duration_seconds': 20.566666666666666, 'total_damage': 108443.47499999999, 'total_healing': 0, 'phase_damage': 108443.47499999999, 'phase_healing': 0, 'cycle_dps': 2562.1304218852997, 'cycle_hps': 0.0, 'cycle_damage': 129558.39499999999, 'cycle_healing': 0, 'skill_attack': 918.04, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 35, '火力电台期望轰炸': 8.75, '火力电台本体生命回复': 35}, 'window_seconds': 21.000000000000004, 'window_healing': 0, 'window_dps': 5163.9749999999985, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'e625b9a22ee343ee1f4ad017604d304543652ce0ead6a9e141bf0695f88cf128'}, {'section': 86, 'pair_id': 'active:char_1041_angel2:steal_success', 'kind': 'active', 'field': 'steal_success', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_1041_angel2', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'steal_success': True}, 'context': 'active:char_1041_angel2:steal_success checked=True', 'expected_public_projection': {'attack': 918.04, 'total_damage': 123935.4, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 40, 'per_hit': 2754.12, 'total': 110164.79999999999, 'source_unit': 'operator', 'times_seconds': [0.1, 0.4666666666666667, 0.8333333333333334, 1.2, 1.5666666666666667, 1.9333333333333333, 2.3, 2.6666666666666665, 3.033333333333333, 3.4, 3.7666666666666666, 4.133333333333334, 4.5, 4.866666666666666, 5.233333333333333, 5.6, 5.966666666666667, 6.333333333333333, 6.7, 7.066666666666666, 7.433333333333334, 7.8, 8.166666666666666, 8.533333333333333, 8.9, 9.266666666666667, 9.633333333333333, 10.0, 10.366666666666667, 10.733333333333333, 11.1, 11.466666666666667, 11.833333333333334, 12.2, 12.566666666666666, 12.933333333333334, 13.3, 13.666666666666666, 14.033333333333333, 14.4]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 10.0, 'per_hit': 1377.06, 'total': 13770.599999999999}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 40, 'per_hit': 141.0, 'total': 5640.0, 'source_unit': 'operator'}], 'attack_speed': 170.0, 'base_attack_speed': 100.0, 'interval_seconds': 0.35294117647058826, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 3, 'recovery_frames': 8, 'interval_frames': 11, 'interval_seconds': 0.36666666666666664, 'start_frames': [0, 11, 22, 33, 44, 55, 66, 77, 88, 99, 110, 121, 132, 143, 154, 165, 176, 187, 198, 209, 220, 231, 242, 253, 264, 275, 286, 297, 308, 319, 330, 341, 352, 363, 374, 385, 396, 407, 418, 429], 'release_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'impact_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'times_seconds': [0.1, 0.4666666666666667, 0.8333333333333334, 1.2, 1.5666666666666667, 1.9333333333333333, 2.3, 2.6666666666666665, 3.033333333333333, 3.4, 3.7666666666666666, 4.133333333333334, 4.5, 4.866666666666666, 5.233333333333333, 5.6, 5.966666666666667, 6.333333333333333, 6.7, 7.066666666666666, 7.433333333333334, 7.8, 8.166666666666666, 8.533333333333333, 8.9, 9.266666666666667, 9.633333333333333, 10.0, 10.366666666666667, 10.733333333333333, 11.1, 11.466666666666667, 11.833333333333334, 12.2, 12.566666666666666, 12.933333333333334, 13.3, 13.666666666666666, 14.033333333333333, 14.4], 'emitted_impact_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'emitted_times_seconds': [0.1, 0.4666666666666667, 0.8333333333333334, 1.2, 1.5666666666666667, 1.9333333333333333, 2.3, 2.6666666666666665, 3.033333333333333, 3.4, 3.7666666666666666, 4.133333333333334, 4.5, 4.866666666666666, 5.233333333333333, 5.6, 5.966666666666667, 6.333333333333333, 6.7, 7.066666666666666, 7.433333333333334, 7.8, 8.166666666666666, 8.533333333333333, 8.9, 9.266666666666667, 9.633333333333333, 10.0, 10.366666666666667, 10.733333333333333, 11.1, 11.466666666666667, 11.833333333333334, 12.2, 12.566666666666666, 12.933333333333334, 13.3, 13.666666666666666, 14.033333333333333, 14.4], 'emitted_release_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'hit_release_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'interval_frames_by_attack': [11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 3, 'recovery_frames': 8, 'interval_frames': 11, 'interval_seconds': 0.36666666666666664, 'start_frames': [0, 11, 22, 33, 44, 55, 66, 77, 88, 99, 110, 121, 132, 143, 154, 165, 176, 187, 198, 209, 220, 231, 242, 253, 264, 275, 286, 297, 308, 319, 330, 341, 352, 363, 374, 385, 396, 407, 418, 429], 'release_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'impact_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'times_seconds': [0.1, 0.4666666666666667, 0.8333333333333334, 1.2, 1.5666666666666667, 1.9333333333333333, 2.3, 2.6666666666666665, 3.033333333333333, 3.4, 3.7666666666666666, 4.133333333333334, 4.5, 4.866666666666666, 5.233333333333333, 5.6, 5.966666666666667, 6.333333333333333, 6.7, 7.066666666666666, 7.433333333333334, 7.8, 8.166666666666666, 8.533333333333333, 8.9, 9.266666666666667, 9.633333333333333, 10.0, 10.366666666666667, 10.733333333333333, 11.1, 11.466666666666667, 11.833333333333334, 12.2, 12.566666666666666, 12.933333333333334, 13.3, 13.666666666666666, 14.033333333333333, 14.4], 'emitted_impact_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'emitted_times_seconds': [0.1, 0.4666666666666667, 0.8333333333333334, 1.2, 1.5666666666666667, 1.9333333333333333, 2.3, 2.6666666666666665, 3.033333333333333, 3.4, 3.7666666666666666, 4.133333333333334, 4.5, 4.866666666666666, 5.233333333333333, 5.6, 5.966666666666667, 6.333333333333333, 6.7, 7.066666666666666, 7.433333333333334, 7.8, 8.166666666666666, 8.533333333333333, 8.9, 9.266666666666667, 9.633333333333333, 10.0, 10.366666666666667, 10.733333333333333, 11.1, 11.466666666666667, 11.833333333333334, 12.2, 12.566666666666666, 12.933333333333334, 13.3, 13.666666666666666, 14.033333333333333, 14.4], 'emitted_release_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'hit_release_frames': [3, 14, 25, 36, 47, 58, 69, 80, 91, 102, 113, 124, 135, 146, 157, 168, 179, 190, 201, 212, 223, 234, 245, 256, 267, 278, 289, 300, 311, 322, 333, 344, 355, 366, 377, 388, 399, 410, 421, 432], 'interval_frames_by_attack': [11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351, 390, 429, 468, 507, 546, 585, 624, 663, 702, 741, 780, 819, 858], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.0, 'cycle_seconds': 44.43333333333334}, 'total_healing': 0, 'attack_speed_reference': 170.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '开火成瘾症', 'initial_seconds': 5.0, 'recharge_seconds': 30.0, 'cycle_seconds': 44.43333333333334, 'duration_seconds': 14.433333333333334, 'total_damage': 123935.4, 'total_healing': 0, 'phase_damage': 123935.4, 'phase_healing': 0, 'cycle_dps': 3264.448312078019, 'cycle_hps': 0.0, 'cycle_damage': 145050.32, 'cycle_healing': 0, 'skill_attack': 918.04, 'skill_attack_speed': 170.0, 'skill_attack_speed_reference': 170.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 40, '火力电台期望轰炸': 10.0, '火力电台本体生命回复': 40}, 'window_seconds': 14.11764705882353, 'window_healing': 0, 'window_dps': 8778.757499999998, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': 'b046e119e52d47913bc62ab25821a2d4ad896c97c84d186d600c03297a182ba5'}, {'section': 86, 'pair_id': 'active:char_1041_angel2:delivery_coordinate', 'kind': 'active', 'field': 'delivery_coordinate', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_1041_angel2', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'delivery_coordinate': False}, 'context': 'active:char_1041_angel2:delivery_coordinate checked=False', 'expected_public_projection': {'attack': 1151.44, 'total_damage': 113704.70000000001, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 50, 'per_hit': 1842.304, 'total': 92115.20000000001, 'source_unit': 'operator', 'times_seconds': [0.3, 0.3, 0.3, 0.3, 0.3, 1.6, 1.6, 1.6, 1.6, 1.6, 2.9, 2.9, 2.9, 2.9, 2.9, 4.2, 4.2, 4.2, 4.2, 4.2, 5.5, 5.5, 5.5, 5.5, 5.5, 6.8, 6.8, 6.8, 6.8, 6.8, 8.1, 8.1, 8.1, 8.1, 8.1, 9.4, 9.4, 9.4, 9.4, 9.4, 10.7, 10.7, 10.7, 10.7, 10.7, 12.0, 12.0, 12.0, 12.0, 12.0]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 12.5, 'per_hit': 1727.16, 'total': 21589.5}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 50, 'per_hit': 141.0, 'total': 7050.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_3_Loop', 'windup_frames': 9, 'recovery_frames': 30, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'emitted_times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'hit_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_3_Loop', 'windup_frames': 9, 'recovery_frames': 30, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'emitted_times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'hit_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351, 390, 429, 468, 507, 546, 585, 624, 663, 702, 741, 780, 819, 858, 897, 936, 975, 1014], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667, 30.166666666666668, 31.466666666666665, 32.766666666666666, 34.06666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667, 30.166666666666668, 31.466666666666665, 32.766666666666666, 34.06666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 3, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.0, 'cycle_seconds': 47.03333333333333}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '使命必达！', 'initial_seconds': 5.0, 'recharge_seconds': 35.0, 'cycle_seconds': 47.03333333333333, 'duration_seconds': 12.033333333333333, 'total_damage': 113704.70000000001, 'total_healing': 0, 'phase_damage': 113704.70000000001, 'phase_healing': 0, 'cycle_dps': 2944.545287030475, 'cycle_hps': 0.0, 'cycle_damage': 138491.78, 'cycle_healing': 0, 'skill_attack': 1151.44, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 50, '火力电台期望轰炸': 12.5, '火力电台本体生命回复': 50}, 'window_seconds': 13.0, 'window_healing': 0, 'window_dps': 8746.515384615386, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '31542b3310841ed6655ae4789fe62875c03cfb449c5ed3009648d62ac91804f5'}, {'section': 86, 'pair_id': 'active:char_1041_angel2:delivery_coordinate', 'kind': 'active', 'field': 'delivery_coordinate', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_1041_angel2', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'delivery_coordinate': True}, 'context': 'active:char_1041_angel2:delivery_coordinate checked=True', 'expected_public_projection': {'attack': 1151.44, 'total_damage': None, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 50, 'per_hit': 1842.304, 'total': 92115.20000000001, 'source_unit': 'operator', 'times_seconds': [0.3, 0.3, 0.3, 0.3, 0.3, 1.6, 1.6, 1.6, 1.6, 1.6, 2.9, 2.9, 2.9, 2.9, 2.9, 4.2, 4.2, 4.2, 4.2, 4.2, 5.5, 5.5, 5.5, 5.5, 5.5, 6.8, 6.8, 6.8, 6.8, 6.8, 8.1, 8.1, 8.1, 8.1, 8.1, 9.4, 9.4, 9.4, 9.4, 9.4, 10.7, 10.7, 10.7, 10.7, 10.7, 12.0, 12.0, 12.0, 12.0, 12.0]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 12.5, 'per_hit': 1727.16, 'total': 21589.5}, {'name': '投递坐标轰炸', 'damage_type': 'physical', 'hits': 1, 'per_hit': 2878.6000000000004, 'total': 2878.6000000000004, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 50, 'per_hit': 141.0, 'total': 7050.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_3_Loop', 'windup_frames': 9, 'recovery_frames': 30, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'emitted_times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'hit_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_3_Loop', 'windup_frames': 9, 'recovery_frames': 30, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_impact_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'emitted_times_seconds': [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 8.1, 9.4, 10.7, 12.0], 'emitted_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'hit_release_frames': [9, 48, 87, 126, 165, 204, 243, 282, 321, 360], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351, 390, 429, 468, 507, 546, 585, 624, 663, 702, 741, 780, 819, 858, 897, 936, 975, 1014], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667, 30.166666666666668, 31.466666666666665, 32.766666666666666, 34.06666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667, 13.266666666666667, 14.566666666666666, 15.866666666666667, 17.166666666666668, 18.466666666666665, 19.766666666666666, 21.066666666666666, 22.366666666666667, 23.666666666666668, 24.966666666666665, 26.266666666666666, 27.566666666666666, 28.866666666666667, 30.166666666666668, 31.466666666666665, 32.766666666666666, 34.06666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359, 398, 437, 476, 515, 554, 593, 632, 671, 710, 749, 788, 827, 866, 905, 944, 983, 1022], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 3, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '投递坐标轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 5.0, 'cycle_seconds': 47.03333333333333}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'external_event_reference': {'conditional_components': [{'name': '投递坐标轰炸', 'damage_type': 'physical', 'per_hit': 2878.6000000000004, 'hits': 1, 'total': 2878.6000000000004}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'kind': 'angel_coordinate_bomb', 'parameter_rows': [['投递坐标轰炸倍率参数', 2.5, '倍']], 'notes': ['投递坐标存在时列一次物理溅射的单目标条件伤害；立即对该处轰炸不证明目标覆盖或实际命中帧。', '本体供靶/打断窗口不定位坐标轰炸；实际覆盖、碰撞及阶段归属未核验，弹药攻击参考单独保留。'], 'window_reference': {'conditional_components': [{'name': '投递坐标轰炸', 'damage_type': 'physical', 'per_hit': 2878.6000000000004, 'hits': 1, 'total': 2878.6000000000004}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False, 'kind': 'angel_coordinate_bomb', 'parameter_rows': [['投递坐标轰炸倍率参数', 2.5, '倍']], 'notes': ['投递坐标存在时列一次物理溅射的单目标条件伤害；立即对该处轰炸不证明目标覆盖或实际命中帧。', '本体供靶/打断窗口不定位坐标轰炸；实际覆盖、碰撞及阶段归属未核验，弹药攻击参考单独保留。']}, 'actual_event_times_seconds': None}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '使命必达！', 'initial_seconds': 5.0, 'recharge_seconds': 35.0, 'cycle_seconds': 47.03333333333333, 'duration_seconds': 12.033333333333333, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': 0.0, 'cycle_damage': None, 'cycle_healing': 0, 'skill_attack': 1151.44, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 50, '投递坐标轰炸': None, '火力电台期望轰炸': 12.5, '火力电台本体生命回复': 50}, 'window_seconds': 13.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'b21a9f2d2f01599d1dd4f0d7d38f2e417baa211e4763e955d77d147267fa3882'}, {'section': 86, 'pair_id': 'active:char_1035_wisdel:overload', 'kind': 'active', 'field': 'overload', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_1035_wisdel', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'overload': False, 'ghost_count': 0, 'ghost_casts': 0}, 'context': 'active:char_1035_wisdel:overload checked=False', 'expected_public_projection': {'attack': 1048.95, 'total_damage': None, 'components': [{'name': '维什戴尔主攻击', 'damage_type': 'physical', 'hits': 18, 'per_hit': 1206.2925, 'total': 21713.265, 'source_unit': 'operator', 'times_seconds': [0.26666666666666666, 1.6666666666666667, 3.066666666666667, 4.466666666666667, 5.866666666666666, 7.266666666666667, 8.666666666666666, 10.066666666666666, 11.466666666666667, 12.866666666666667, 14.266666666666667, 15.666666666666666, 17.066666666666666, 18.466666666666665, 19.866666666666667, 21.266666666666666, 22.666666666666668, 24.066666666666666]}, {'name': '余震', 'damage_type': 'physical', 'hits': 18, 'per_hit': 603.14625, 'total': 10856.6325, 'source_unit': 'operator', 'actual_total': None}, {'name': '残影单次爆炸条件参考', 'damage_type': 'physical', 'hits': 0, 'per_hit': 1573.4250000000002, 'total': 0.0, 'source_unit': 'operator', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.4, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1035_wisdel', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 8, 'recovery_frames': 34, 'interval_frames': 42, 'interval_seconds': 1.4, 'start_frames': [0, 42, 84, 126, 168, 210, 252, 294, 336, 378, 420, 462, 504, 546, 588, 630, 672, 714], 'release_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'impact_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'times_seconds': [0.26666666666666666, 1.6666666666666667, 3.066666666666667, 4.466666666666667, 5.866666666666666, 7.266666666666667, 8.666666666666666, 10.066666666666666, 11.466666666666667, 12.866666666666667, 14.266666666666667, 15.666666666666666, 17.066666666666666, 18.466666666666665, 19.866666666666667, 21.266666666666666, 22.666666666666668, 24.066666666666666], 'emitted_impact_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'emitted_times_seconds': [0.26666666666666666, 1.6666666666666667, 3.066666666666667, 4.466666666666667, 5.866666666666666, 7.266666666666667, 8.666666666666666, 10.066666666666666, 11.466666666666667, 12.866666666666667, 14.266666666666667, 15.666666666666666, 17.066666666666666, 18.466666666666665, 19.866666666666667, 21.266666666666666, 22.666666666666668, 24.066666666666666], 'emitted_release_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'hit_release_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'interval_frames_by_attack': [42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 6, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1035_wisdel', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_A', 'windup_frames': 18, 'recovery_frames': 45, 'interval_frames': 63, 'interval_seconds': 2.1, 'start_frames': [6, 69, 132, 195, 258, 321, 384, 447, 510, 573, 636, 699], 'release_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'impact_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'times_seconds': [0.8, 2.9, 5.0, 7.1, 9.2, 11.3, 13.4, 15.5, 17.6, 19.7, 21.8, 23.9], 'emitted_impact_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'emitted_times_seconds': [0.8, 2.9, 5.0, 7.1, 9.2, 11.3, 13.4, 15.5, 17.6, 19.7, 21.8, 23.9], 'emitted_release_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'hit_release_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'interval_frames_by_attack': [63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 12, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['余震'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 10.0, 'cycle_seconds': 50.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'wisdel_secondary_reference': {'described_single_check_probability': 0.15, 'explosion_per_hit_reference': 1573.4250000000002, 'explosion_expected_count': None, 'random_independence_verified': False, 'shadow_lifecycle_verified': False, 'secondary_hit_times_seconds': None, 'source_possible': {'cast': True, 'window': True}, 's1_binding_verified': False, 'ghost_casts_requested': 0, 'ghost_per_cast_damage_reference': None, 'ghost_cast_times_seconds': None, 'ghost_full_cast_attribution_verified': False, 'ghost_declared_count_damage_reference': 0}, 'wisdel_summon_qualification_reference': {'operator_id': 'char_1035_wisdel', 'token_id': 'token_10035_wisdel_wward', 'scope': '仅固定原表第二天赋与第三技能两条本体召唤途径的培养资格资料；不证明声明来源、当前存在、实际施放或全部模组/藏品途径。', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'current_cultivation': {'elite': 2, 'level': 90, 'potential': 1}, 'talent_route': {'source_selector': 'character_table.char_1035_wisdel.talents[1].candidates[0]', 'talent_index': 1, 'prefab_key': '2', 'name': '死魂灵的余息', 'description': '部署后立刻在攻击范围内召唤一个魂灵之影，在魂灵之影周围时获得<$ba.camou>迷彩</>', 'unlock_elite': 2, 'unlock_level': 1, 'required_potential_rank': 0, 'token_key': 'token_10035_wisdel_wward', 'cultivation_qualified': True}, 'skill_route': {'source_selector': 'character_table.char_1035_wisdel.skills[2]', 'skill_number': 3, 'skill_id': 'skchr_wisdel_3', 'override_token_key': 'token_10035_wisdel_wward', 'unlock_elite': 2, 'unlock_level': 1, 'original_common_fragments': ['立刻在攻击范围内召唤', '个魂灵之影（最多存在3个，技能结束后保留）'], 'cultivation_qualified': True, 'currently_selected': False, 'selected_level_source': None}, 'actual_source_provenance': None, 'actual_presence_verified': False, 'actual_cast_clock_verified': False, 'covers_all_routes': False, 'declared_counts_reinterpreted': False}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1888, 'attack': 777.0, 'defense': 256, 'resistance': 15.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '饱和复仇', 'initial_seconds': 10.0, 'recharge_seconds': 25.0, 'cycle_seconds': 50.0, 'duration_seconds': 25.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': 0.0, 'cycle_damage': None, 'cycle_healing': 0, 'skill_attack': 1048.95, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'余震': None, '残影单次爆炸条件参考': None, '维什戴尔主攻击': 18}, 'window_seconds': 25.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '0e8d6560724e7ff5c34c19231774fec18d8b014a894fed93f0ad98b5f2114d18'}, {'section': 86, 'pair_id': 'active:char_1035_wisdel:overload', 'kind': 'active', 'field': 'overload', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_1035_wisdel', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'overload': True, 'ghost_count': 0, 'ghost_casts': 0}, 'context': 'active:char_1035_wisdel:overload checked=True', 'expected_public_projection': {'attack': 1048.95, 'total_damage': None, 'components': [{'name': '维什戴尔主攻击', 'damage_type': 'physical', 'hits': 72, 'per_hit': 965.034, 'total': 69482.448, 'source_unit': 'operator', 'actual_total': None}, {'name': '余震', 'damage_type': 'physical', 'hits': 72, 'per_hit': 482.517, 'total': 34741.224, 'source_unit': 'operator', 'actual_total': None}, {'name': '残影单次爆炸条件参考', 'damage_type': 'physical', 'hits': 0, 'per_hit': 1573.4250000000002, 'total': 0.0, 'source_unit': 'operator', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.4, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1035_wisdel', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 8, 'recovery_frames': 34, 'interval_frames': 42, 'interval_seconds': 1.4, 'start_frames': [0, 42, 84, 126, 168, 210, 252, 294, 336, 378, 420, 462, 504, 546, 588, 630, 672, 714], 'release_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'impact_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'times_seconds': [0.26666666666666666, 1.6666666666666667, 3.066666666666667, 4.466666666666667, 5.866666666666666, 7.266666666666667, 8.666666666666666, 10.066666666666666, 11.466666666666667, 12.866666666666667, 14.266666666666667, 15.666666666666666, 17.066666666666666, 18.466666666666665, 19.866666666666667, 21.266666666666666, 22.666666666666668, 24.066666666666666], 'emitted_impact_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'emitted_times_seconds': [0.26666666666666666, 1.6666666666666667, 3.066666666666667, 4.466666666666667, 5.866666666666666, 7.266666666666667, 8.666666666666666, 10.066666666666666, 11.466666666666667, 12.866666666666667, 14.266666666666667, 15.666666666666666, 17.066666666666666, 18.466666666666665, 19.866666666666667, 21.266666666666666, 22.666666666666668, 24.066666666666666], 'emitted_release_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'hit_release_frames': [8, 50, 92, 134, 176, 218, 260, 302, 344, 386, 428, 470, 512, 554, 596, 638, 680, 722], 'interval_frames_by_attack': [42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 6, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1035_wisdel', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_A', 'windup_frames': 18, 'recovery_frames': 45, 'interval_frames': 63, 'interval_seconds': 2.1, 'start_frames': [6, 69, 132, 195, 258, 321, 384, 447, 510, 573, 636, 699], 'release_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'impact_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'times_seconds': [0.8, 2.9, 5.0, 7.1, 9.2, 11.3, 13.4, 15.5, 17.6, 19.7, 21.8, 23.9], 'emitted_impact_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'emitted_times_seconds': [0.8, 2.9, 5.0, 7.1, 9.2, 11.3, 13.4, 15.5, 17.6, 19.7, 21.8, 23.9], 'emitted_release_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'hit_release_frames': [24, 87, 150, 213, 276, 339, 402, 465, 528, 591, 654, 717], 'interval_frames_by_attack': [63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 12, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['维什戴尔主攻击', '余震'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 10.0, 'cycle_seconds': 50.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'wisdel_secondary_reference': {'described_single_check_probability': 0.15, 'explosion_per_hit_reference': 1573.4250000000002, 'explosion_expected_count': None, 'random_independence_verified': False, 'shadow_lifecycle_verified': False, 'secondary_hit_times_seconds': None, 'source_possible': {'cast': True, 'window': True}, 's1_binding_verified': False, 'ghost_casts_requested': 0, 'ghost_per_cast_damage_reference': None, 'ghost_cast_times_seconds': None, 'ghost_full_cast_attribution_verified': False, 'ghost_declared_count_damage_reference': 0}, 'wisdel_summon_qualification_reference': {'operator_id': 'char_1035_wisdel', 'token_id': 'token_10035_wisdel_wward', 'scope': '仅固定原表第二天赋与第三技能两条本体召唤途径的培养资格资料；不证明声明来源、当前存在、实际施放或全部模组/藏品途径。', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'current_cultivation': {'elite': 2, 'level': 90, 'potential': 1}, 'talent_route': {'source_selector': 'character_table.char_1035_wisdel.talents[1].candidates[0]', 'talent_index': 1, 'prefab_key': '2', 'name': '死魂灵的余息', 'description': '部署后立刻在攻击范围内召唤一个魂灵之影，在魂灵之影周围时获得<$ba.camou>迷彩</>', 'unlock_elite': 2, 'unlock_level': 1, 'required_potential_rank': 0, 'token_key': 'token_10035_wisdel_wward', 'cultivation_qualified': True}, 'skill_route': {'source_selector': 'character_table.char_1035_wisdel.skills[2]', 'skill_number': 3, 'skill_id': 'skchr_wisdel_3', 'override_token_key': 'token_10035_wisdel_wward', 'unlock_elite': 2, 'unlock_level': 1, 'original_common_fragments': ['立刻在攻击范围内召唤', '个魂灵之影（最多存在3个，技能结束后保留）'], 'cultivation_qualified': True, 'currently_selected': False, 'selected_level_source': None}, 'actual_source_provenance': None, 'actual_presence_verified': False, 'actual_cast_clock_verified': False, 'covers_all_routes': False, 'declared_counts_reinterpreted': False}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1888, 'attack': 777.0, 'defense': 256, 'resistance': 15.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '饱和复仇', 'initial_seconds': 10.0, 'recharge_seconds': 25.0, 'cycle_seconds': 50.0, 'duration_seconds': 25.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': 0.0, 'cycle_damage': None, 'cycle_healing': 0, 'skill_attack': 1048.95, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'余震': None, '残影单次爆炸条件参考': None, '维什戴尔主攻击': None}, 'window_seconds': 25.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'd045727936e0f3c5c05e72233a46f40d119cc7eda1044917f381166a159e68b5'}, {'section': 86, 'pair_id': 'qualification:mizuki-E1', 'kind': 'qualification', 'field': 'enemy_below_half', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_437_mizuki', 'skill': 2, 'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'enemy_below_half': False}, 'context': 'qualification:mizuki-E1 checked=False', 'expected_public_projection': {'attack': 770.4, 'total_damage': 9013.68, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 9, 'per_hit': 770.4, 'total': 6933.599999999999, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334]}, {'name': '创伤性癔症', 'damage_type': 'magic', 'hits': 9, 'per_hit': 231.11999999999998, 'total': 2080.08, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 69, 'interval_seconds': 2.3, 'start_frames': [0, 69, 138, 207, 276, 345, 414, 483, 552], 'release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'emitted_times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'hit_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'interval_frames_by_attack': [69, 69, 69, 69, 69, 69, 69, 69, 69], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 51, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 69, 'interval_seconds': 2.3, 'start_frames': [0, 69, 138, 207, 276, 345, 414, 483, 552], 'release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'emitted_times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'hit_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'interval_frames_by_attack': [69, 69, 69, 69, 69, 69, 69, 69, 69], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 51, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [51, 156, 261, 366, 471], 'release_frames': [67, 172, 277, 382, 487], 'impact_frames': [67, 172, 277, 382, 487], 'times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_impact_frames': [67, 172, 277, 382, 487], 'emitted_times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_release_frames': [67, 172, 277, 382, 487], 'hit_release_frames': [67, 172, 277, 382, 487], 'interval_frames_by_attack': [105, 105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 6, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [51, 156, 261, 366, 471], 'release_frames': [67, 172, 277, 382, 487], 'impact_frames': [67, 172, 277, 382, 487], 'times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_impact_frames': [67, 172, 277, 382, 487], 'emitted_times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_release_frames': [67, 172, 277, 382, 487], 'hit_release_frames': [67, 172, 277, 382, 487], 'interval_frames_by_attack': [105, 105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 6, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 14.0, 'cycle_seconds': 38.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 1, 'level': 1, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1028, 'attack': 642.0, 'defense': 229, 'resistance': 20.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 0.0}, 'skill': {'name': '囚徒困境', 'initial_seconds': 14.0, 'recharge_seconds': 19.0, 'cycle_seconds': 38.0, 'duration_seconds': 19.0, 'total_damage': 9013.68, 'total_healing': 0, 'phase_damage': 9013.68, 'phase_healing': 0, 'cycle_dps': 347.0178947368421, 'cycle_hps': 0.0, 'cycle_damage': 13186.68, 'cycle_healing': 0, 'skill_attack': 770.4, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'创伤性癔症': 9, '技能攻击': 9}, 'window_seconds': 19.0, 'window_healing': 0, 'window_dps': 474.4042105263158, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '246c5d43965013ffea6abb72623143f4052041805284d5d611d45c0e579ec6d4'}, {'section': 86, 'pair_id': 'qualification:mizuki-E1', 'kind': 'qualification', 'field': 'enemy_below_half', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_437_mizuki', 'skill': 2, 'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'enemy_below_half': True}, 'context': 'qualification:mizuki-E1 checked=True', 'expected_public_projection': {'attack': 770.4, 'total_damage': 9013.68, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 9, 'per_hit': 770.4, 'total': 6933.599999999999, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334]}, {'name': '创伤性癔症', 'damage_type': 'magic', 'hits': 9, 'per_hit': 231.11999999999998, 'total': 2080.08, 'source_unit': 'operator', 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 69, 'interval_seconds': 2.3, 'start_frames': [0, 69, 138, 207, 276, 345, 414, 483, 552], 'release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'emitted_times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'hit_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'interval_frames_by_attack': [69, 69, 69, 69, 69, 69, 69, 69, 69], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 51, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_2_Loop', 'windup_frames': 16, 'recovery_frames': 24, 'interval_frames': 69, 'interval_seconds': 2.3, 'start_frames': [0, 69, 138, 207, 276, 345, 414, 483, 552], 'release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_impact_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'emitted_times_seconds': [0.5333333333333333, 2.8333333333333335, 5.133333333333334, 7.433333333333334, 9.733333333333333, 12.033333333333333, 14.333333333333334, 16.633333333333333, 18.933333333333334], 'emitted_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'hit_release_frames': [16, 85, 154, 223, 292, 361, 430, 499, 568], 'interval_frames_by_attack': [69, 69, 69, 69, 69, 69, 69, 69, 69], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 51, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [51, 156, 261, 366, 471], 'release_frames': [67, 172, 277, 382, 487], 'impact_frames': [67, 172, 277, 382, 487], 'times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_impact_frames': [67, 172, 277, 382, 487], 'emitted_times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_release_frames': [67, 172, 277, 382, 487], 'hit_release_frames': [67, 172, 277, 382, 487], 'interval_frames_by_attack': [105, 105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 6, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_437_mizuki', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack', 'windup_frames': 16, 'recovery_frames': 27, 'interval_frames': 105, 'interval_seconds': 3.5, 'start_frames': [51, 156, 261, 366, 471], 'release_frames': [67, 172, 277, 382, 487], 'impact_frames': [67, 172, 277, 382, 487], 'times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_impact_frames': [67, 172, 277, 382, 487], 'emitted_times_seconds': [2.2333333333333334, 5.733333333333333, 9.233333333333333, 12.733333333333333, 16.233333333333334], 'emitted_release_frames': [67, 172, 277, 382, 487], 'hit_release_frames': [67, 172, 277, 382, 487], 'interval_frames_by_attack': [105, 105, 105, 105, 105], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 6, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 14.0, 'cycle_seconds': 38.0}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 1, 'level': 1, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1028, 'attack': 642.0, 'defense': 229, 'resistance': 20.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 0.0}, 'skill': {'name': '囚徒困境', 'initial_seconds': 14.0, 'recharge_seconds': 19.0, 'cycle_seconds': 38.0, 'duration_seconds': 19.0, 'total_damage': 9013.68, 'total_healing': 0, 'phase_damage': 9013.68, 'phase_healing': 0, 'cycle_dps': 347.0178947368421, 'cycle_hps': 0.0, 'cycle_damage': 13186.68, 'cycle_healing': 0, 'skill_attack': 770.4, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'创伤性癔症': 9, '技能攻击': 9}, 'window_seconds': 19.0, 'window_healing': 0, 'window_dps': 474.4042105263158, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '246c5d43965013ffea6abb72623143f4052041805284d5d611d45c0e579ec6d4'}, {'section': 86, 'pair_id': 'coveredmodule:oblvns-ranged-skill-vs-normal', 'kind': 'qualification', 'field': 'ranged_attack', 'widget_checked': False, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 60, 'potential': 1, 'trust': 100, 'module_id': 'uniequip_002_oblvns', 'module_level': 3, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': False}, 'context': 'coveredmodule:oblvns-ranged-skill-vs-normal checked=False', 'expected_public_projection': {'attack': 801.0, 'total_damage': 155073.6, 'components': [{'name': '钢琴音符', 'damage_type': 'physical', 'hits': 44, 'per_hit': 1762.2, 'total': 77536.8, 'source_unit': 'operator', 'times_seconds': [1.1, 1.1, 2.2, 2.2, 3.3, 3.3, 4.4, 4.4, 5.5, 5.5, 6.6, 6.6, 7.7, 7.7, 8.8, 8.8, 9.9, 9.9, 11.0, 11.0, 12.1, 12.1, 13.2, 13.2, 14.3, 14.3, 15.4, 15.4, 16.5, 16.5, 17.6, 17.6, 18.7, 18.7, 19.8, 19.8, 20.9, 20.9, 22.0, 22.0, 23.1, 23.1, 24.2, 24.2]}, {'name': '风琴音符', 'damage_type': 'magic', 'hits': 44, 'per_hit': 1762.2, 'total': 77536.8, 'source_unit': 'operator', 'times_seconds': [1.1, 1.1, 2.2, 2.2, 3.3, 3.3, 4.4, 4.4, 5.5, 5.5, 6.6, 6.6, 7.7, 7.7, 8.8, 8.8, 9.9, 9.9, 11.0, 11.0, 12.1, 12.1, 13.2, 13.2, 14.3, 14.3, 15.4, 15.4, 16.5, 16.5, 17.6, 17.6, 18.7, 18.7, 19.8, 19.8, 20.9, 20.9, 22.0, 22.0, 23.1, 23.1, 24.2, 24.2]}], 'attack_speed': 119.0, 'base_attack_speed': 119.0, 'interval_seconds': 1.0924369747899159, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 33, 'interval_seconds': 1.1, 'start_frames': [0, 33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693], 'release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'emitted_times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'hit_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'interval_frames_by_attack': [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}, {'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 33, 'interval_seconds': 1.1, 'start_frames': [0, 33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693], 'release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'emitted_times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'hit_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'interval_frames_by_attack': [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 33, 'interval_seconds': 1.1, 'start_frames': [0, 33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353], 'release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2, 25.3, 26.4, 27.5, 28.6, 29.7, 30.8, 31.9, 33.0, 34.1, 35.2, 36.3, 37.4, 38.5, 39.6, 40.7, 41.8, 42.9, 44.0, 45.1, 46.2], 'emitted_impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'emitted_times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2, 25.3, 26.4, 27.5, 28.6, 29.7, 30.8, 31.9, 33.0, 34.1, 35.2, 36.3, 37.4, 38.5, 39.6, 40.7, 41.8, 42.9, 44.0, 45.1, 46.2], 'emitted_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'hit_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'interval_frames_by_attack': [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 8.833333333333334, 'cycle_seconds': 71.23333333333333}, 'total_healing': 0, 'attack_speed_reference': 119.0, 'base_attack_speed_reference': 119.0, 'estimate': {'training': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': 'uniequip_002_oblvns', 'module_level': 3}, 'base_stats': {'hp': 2510.0, 'attack': 801.0, 'defense': 400, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 119.0, 'attack_speed_reference': 119.0, 'block_count': 2.0}, 'skill': {'name': '残月的余响', 'initial_seconds': 8.833333333333334, 'recharge_seconds': 46.233333333333334, 'cycle_seconds': 71.23333333333333, 'duration_seconds': 25.0, 'total_damage': 155073.6, 'total_healing': 0, 'phase_damage': 155073.6, 'phase_healing': 0, 'cycle_dps': 2649.2597098736546, 'cycle_hps': 0.0, 'cycle_damage': 188715.6, 'cycle_healing': 0, 'skill_attack': 801.0, 'skill_attack_speed': 119.0, 'skill_attack_speed_reference': 119.0, 'sp_recovery_per_second': None, 'mode': 'timed', 'hit_counts': {'钢琴音符': 44, '风琴音符': 44}, 'window_seconds': 25.0, 'window_healing': 0, 'window_dps': 6202.944, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '649993035224f8ee74a58cb16eb25f0c36d49adcc51e49601af888770480ed95'}, {'section': 86, 'pair_id': 'coveredmodule:oblvns-ranged-skill-vs-normal', 'kind': 'qualification', 'field': 'ranged_attack', 'widget_checked': True, 'field_serialized': True, 'input': {'operator': 'char_4182_oblvns', 'skill': 3, 'skill_rank': 10, 'elite': 2, 'level': 60, 'potential': 1, 'trust': 100, 'module_id': 'uniequip_002_oblvns', 'module_level': 3, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True}, 'context': 'coveredmodule:oblvns-ranged-skill-vs-normal checked=True', 'expected_public_projection': {'attack': 801.0, 'total_damage': 155073.6, 'components': [{'name': '钢琴音符', 'damage_type': 'physical', 'hits': 44, 'per_hit': 1762.2, 'total': 77536.8, 'source_unit': 'operator', 'times_seconds': [1.1, 1.1, 2.2, 2.2, 3.3, 3.3, 4.4, 4.4, 5.5, 5.5, 6.6, 6.6, 7.7, 7.7, 8.8, 8.8, 9.9, 9.9, 11.0, 11.0, 12.1, 12.1, 13.2, 13.2, 14.3, 14.3, 15.4, 15.4, 16.5, 16.5, 17.6, 17.6, 18.7, 18.7, 19.8, 19.8, 20.9, 20.9, 22.0, 22.0, 23.1, 23.1, 24.2, 24.2]}, {'name': '风琴音符', 'damage_type': 'magic', 'hits': 44, 'per_hit': 1762.2, 'total': 77536.8, 'source_unit': 'operator', 'times_seconds': [1.1, 1.1, 2.2, 2.2, 3.3, 3.3, 4.4, 4.4, 5.5, 5.5, 6.6, 6.6, 7.7, 7.7, 8.8, 8.8, 9.9, 9.9, 11.0, 11.0, 12.1, 12.1, 13.2, 13.2, 14.3, 14.3, 15.4, 15.4, 16.5, 16.5, 17.6, 17.6, 18.7, 18.7, 19.8, 19.8, 20.9, 20.9, 22.0, 22.0, 23.1, 23.1, 24.2, 24.2]}], 'attack_speed': 119.0, 'base_attack_speed': 119.0, 'interval_seconds': 1.0924369747899159, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 33, 'interval_seconds': 1.1, 'start_frames': [0, 33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693], 'release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'emitted_times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'hit_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'interval_frames_by_attack': [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}, {'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 33, 'interval_seconds': 1.1, 'start_frames': [0, 33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693], 'release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'emitted_times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2], 'emitted_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'hit_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726], 'interval_frames_by_attack': [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_4182_oblvns', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 33, 'interval_seconds': 1.1, 'start_frames': [0, 33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353], 'release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2, 25.3, 26.4, 27.5, 28.6, 29.7, 30.8, 31.9, 33.0, 34.1, 35.2, 36.3, 37.4, 38.5, 39.6, 40.7, 41.8, 42.9, 44.0, 45.1, 46.2], 'emitted_impact_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'emitted_times_seconds': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11.0, 12.1, 13.2, 14.3, 15.4, 16.5, 17.6, 18.7, 19.8, 20.9, 22.0, 23.1, 24.2, 25.3, 26.4, 27.5, 28.6, 29.7, 30.8, 31.9, 33.0, 34.1, 35.2, 36.3, 37.4, 38.5, 39.6, 40.7, 41.8, 42.9, 44.0, 45.1, 46.2], 'emitted_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'hit_release_frames': [33, 66, 99, 132, 165, 198, 231, 264, 297, 330, 363, 396, 429, 462, 495, 528, 561, 594, 627, 660, 693, 726, 759, 792, 825, 858, 891, 924, 957, 990, 1023, 1056, 1089, 1122, 1155, 1188, 1221, 1254, 1287, 1320, 1353, 1386], 'interval_frames_by_attack': [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 8.833333333333334, 'cycle_seconds': 71.23333333333333}, 'total_healing': 0, 'attack_speed_reference': 119.0, 'base_attack_speed_reference': 119.0, 'estimate': {'training': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': 'uniequip_002_oblvns', 'module_level': 3}, 'base_stats': {'hp': 2510.0, 'attack': 801.0, 'defense': 400, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 119.0, 'attack_speed_reference': 119.0, 'block_count': 2.0}, 'skill': {'name': '残月的余响', 'initial_seconds': 8.833333333333334, 'recharge_seconds': 46.233333333333334, 'cycle_seconds': 71.23333333333333, 'duration_seconds': 25.0, 'total_damage': 155073.6, 'total_healing': 0, 'phase_damage': 155073.6, 'phase_healing': 0, 'cycle_dps': 2554.803930744034, 'cycle_hps': 0.0, 'cycle_damage': 181987.2, 'cycle_healing': 0, 'skill_attack': 801.0, 'skill_attack_speed': 119.0, 'skill_attack_speed_reference': 119.0, 'sp_recovery_per_second': None, 'mode': 'timed', 'hit_counts': {'钢琴音符': 44, '风琴音符': 44}, 'window_seconds': 25.0, 'window_healing': 0, 'window_dps': 6202.944, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '04d0cf83567e701a4b31ab1d976c4d4b593fc8167fbed875f01675d8186823f8'}, {'section': 86, 'pair_id': 'hidden:char_206_gnosis:frozen_at_skill_end', 'kind': 'hidden', 'field': 'frozen_at_skill_end', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_206_gnosis', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'cold_state': 0}, 'context': 'hidden:char_206_gnosis:frozen_at_skill_end checked=False', 'expected_public_projection': {'attack': 535.0, 'total_damage': None, 'components': [{'name': '高速思考', 'damage_type': 'magic', 'hits': 2, 'per_hit': 909.5, 'total': 1819.0, 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_206_gnosis', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 24, 'interval_frames': 48, 'interval_seconds': 1.6, 'start_frames': [0], 'release_frames': [14], 'impact_frames': [14], 'times_seconds': [0.4666666666666667], 'emitted_impact_frames': [14], 'emitted_times_seconds': [0.4666666666666667], 'emitted_release_frames': [14], 'hit_release_frames': [14], 'interval_frames_by_attack': [48], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': ['高速思考'], 'resource_and_damage_shared_clock': True, 'initial_seconds': None, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'gnosis_s1_reference': {'two_hit_damage_reference': 1819.0, 'per_hit_damage_reference': 909.5, 'source_possible': {'cast': True, 'window': True}, 'relative_hit_times_seconds': None, 'multi_event_binding_verified': False, 'source_acquisition_times': {'cast': [0.4666666666666667], 'window': [0.4666666666666667]}}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2035, 'attack': 535.0, 'defense': 132, 'resistance': 25.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '高速思考', 'initial_seconds': None, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 535.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'next_attack', 'hit_counts': {'高速思考': 2}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '20f2e53a6b44e90daa9f022a918e87e16fef98749b4e8e37411a73f267c7f308'}, {'section': 86, 'pair_id': 'hidden:char_206_gnosis:frozen_at_skill_end', 'kind': 'hidden', 'field': 'frozen_at_skill_end', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_206_gnosis', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'cold_state': 0}, 'context': 'hidden:char_206_gnosis:frozen_at_skill_end checked=True', 'expected_public_projection': {'attack': 535.0, 'total_damage': None, 'components': [{'name': '高速思考', 'damage_type': 'magic', 'hits': 2, 'per_hit': 909.5, 'total': 1819.0, 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_206_gnosis', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 24, 'interval_frames': 48, 'interval_seconds': 1.6, 'start_frames': [0], 'release_frames': [14], 'impact_frames': [14], 'times_seconds': [0.4666666666666667], 'emitted_impact_frames': [14], 'emitted_times_seconds': [0.4666666666666667], 'emitted_release_frames': [14], 'hit_release_frames': [14], 'interval_frames_by_attack': [48], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': ['高速思考'], 'resource_and_damage_shared_clock': True, 'initial_seconds': None, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'gnosis_s1_reference': {'two_hit_damage_reference': 1819.0, 'per_hit_damage_reference': 909.5, 'source_possible': {'cast': True, 'window': True}, 'relative_hit_times_seconds': None, 'multi_event_binding_verified': False, 'source_acquisition_times': {'cast': [0.4666666666666667], 'window': [0.4666666666666667]}}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2035, 'attack': 535.0, 'defense': 132, 'resistance': 25.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '高速思考', 'initial_seconds': None, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 535.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'next_attack', 'hit_counts': {'高速思考': 2}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '20f2e53a6b44e90daa9f022a918e87e16fef98749b4e8e37411a73f267c7f308'}, {'section': 86, 'pair_id': 'hidden:char_4087_ines:ines_first_deployment', 'kind': 'hidden', 'field': 'ines_first_deployment', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_4087_ines', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'stolen_enemy_count': 1}, 'context': 'hidden:char_4087_ines:ines_first_deployment checked=False', 'expected_public_projection': {'attack': 729.0, 'total_damage': None, 'components': [{'name': '淬影突袭物理攻击', 'damage_type': 'physical', 'hits': 1, 'per_hit': 729.0, 'total': 729.0, 'source_unit': 'operator', 'times_seconds': [0.4666666666666667]}, {'name': '淬影突袭持续法术', 'damage_type': 'magic', 'hits': 0, 'per_hit': 583.2, 'total': 0.0, 'source_unit': 'operator', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4087_ines', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 16, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0], 'release_frames': [14], 'impact_frames': [14], 'times_seconds': [0.4666666666666667], 'emitted_impact_frames': [14], 'emitted_times_seconds': [0.4666666666666667], 'emitted_release_frames': [14], 'hit_release_frames': [14], 'interval_frames_by_attack': [30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'ines_dot_reference': {'per_second_damage_reference': 583.2, 'duration_parameter_seconds': 3.0, 'interval_description_seconds': 1, 'actual_first_tick_seconds': None, 'actual_tick_count': None, 'refresh_order_verified': False, 'dot_stacks': False, 'source_possible': {'cast': True, 'window': True}}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2121, 'attack': 729.0, 'defense': 311, 'resistance': 0.0, 'redeploy_seconds': 35.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '淬影突袭', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 729.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': None, 'mode': 'next_attack', 'hit_counts': {'淬影突袭持续法术': None, '淬影突袭物理攻击': 1}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'b41555103f2b52d78a5507518998e47137e82c0163a590a3491d9b25e4d930fa'}, {'section': 86, 'pair_id': 'hidden:char_4087_ines:ines_first_deployment', 'kind': 'hidden', 'field': 'ines_first_deployment', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_4087_ines', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'stolen_enemy_count': 1}, 'context': 'hidden:char_4087_ines:ines_first_deployment checked=True', 'expected_public_projection': {'attack': 729.0, 'total_damage': None, 'components': [{'name': '淬影突袭物理攻击', 'damage_type': 'physical', 'hits': 1, 'per_hit': 729.0, 'total': 729.0, 'source_unit': 'operator', 'times_seconds': [0.4666666666666667]}, {'name': '淬影突袭持续法术', 'damage_type': 'magic', 'hits': 0, 'per_hit': 583.2, 'total': 0.0, 'source_unit': 'operator', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_4087_ines', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': False, 'animation': 'Attack', 'windup_frames': 14, 'recovery_frames': 16, 'interval_frames': 30, 'interval_seconds': 1.0, 'start_frames': [0], 'release_frames': [14], 'impact_frames': [14], 'times_seconds': [0.4666666666666667], 'emitted_impact_frames': [14], 'emitted_times_seconds': [0.4666666666666667], 'emitted_release_frames': [14], 'hit_release_frames': [14], 'interval_frames_by_attack': [30], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 0.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'ines_dot_reference': {'per_second_damage_reference': 583.2, 'duration_parameter_seconds': 3.0, 'interval_description_seconds': 1, 'actual_first_tick_seconds': None, 'actual_tick_count': None, 'refresh_order_verified': False, 'dot_stacks': False, 'source_possible': {'cast': True, 'window': True}}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2121, 'attack': 729.0, 'defense': 311, 'resistance': 0.0, 'redeploy_seconds': 35.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '淬影突袭', 'initial_seconds': 0.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 729.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': None, 'mode': 'next_attack', 'hit_counts': {'淬影突袭持续法术': None, '淬影突袭物理攻击': 1}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'b41555103f2b52d78a5507518998e47137e82c0163a590a3491d9b25e4d930fa'}, {'section': 86, 'pair_id': 'hidden:char_4182_oblvns:organ_mode', 'kind': 'hidden', 'field': 'organ_mode', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_4182_oblvns', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True}, 'context': 'hidden:char_4182_oblvns:organ_mode checked=False', 'expected_public_projection': {'attack': 785.0, 'total_damage': None, 'components': [{'name': '新月音符1', 'damage_type': 'magic', 'hits': 1, 'per_hit': 628.0, 'total': 628.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符2', 'damage_type': 'magic', 'hits': 1, 'per_hit': 577.7600000000001, 'total': 577.7600000000001, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符3', 'damage_type': 'magic', 'hits': 1, 'per_hit': 471.0, 'total': 471.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符4', 'damage_type': 'magic', 'hits': 1, 'per_hit': 364.24, 'total': 364.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符5', 'damage_type': 'magic', 'hits': 1, 'per_hit': 263.76, 'total': 263.76, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符6', 'damage_type': 'magic', 'hits': 1, 'per_hit': 207.24, 'total': 207.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符7', 'damage_type': 'magic', 'hits': 1, 'per_hit': 106.76000000000002, 'total': 106.76000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符8', 'damage_type': 'magic', 'hits': 1, 'per_hit': 31.400000000000002, 'total': 31.400000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['新月音符1', '新月音符2', '新月音符3', '新月音符4', '新月音符5', '新月音符6', '新月音符7', '新月音符8'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 3.533333333333333, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'unbound_cast_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '新月的苏醒', 'initial_seconds': 3.533333333333333, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 785.0, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'instant', 'hit_counts': {'新月音符1': None, '新月音符2': None, '新月音符3': None, '新月音符4': None, '新月音符5': None, '新月音符6': None, '新月音符7': None, '新月音符8': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '7c38a7682e2218dc6facdec5846d6f693c81958e7015b2a22942efc33b13da0c'}, {'section': 86, 'pair_id': 'hidden:char_4182_oblvns:organ_mode', 'kind': 'hidden', 'field': 'organ_mode', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_4182_oblvns', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True}, 'context': 'hidden:char_4182_oblvns:organ_mode checked=True', 'expected_public_projection': {'attack': 785.0, 'total_damage': None, 'components': [{'name': '新月音符1', 'damage_type': 'magic', 'hits': 1, 'per_hit': 628.0, 'total': 628.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符2', 'damage_type': 'magic', 'hits': 1, 'per_hit': 577.7600000000001, 'total': 577.7600000000001, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符3', 'damage_type': 'magic', 'hits': 1, 'per_hit': 471.0, 'total': 471.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符4', 'damage_type': 'magic', 'hits': 1, 'per_hit': 364.24, 'total': 364.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符5', 'damage_type': 'magic', 'hits': 1, 'per_hit': 263.76, 'total': 263.76, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符6', 'damage_type': 'magic', 'hits': 1, 'per_hit': 207.24, 'total': 207.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符7', 'damage_type': 'magic', 'hits': 1, 'per_hit': 106.76000000000002, 'total': 106.76000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符8', 'damage_type': 'magic', 'hits': 1, 'per_hit': 31.400000000000002, 'total': 31.400000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['新月音符1', '新月音符2', '新月音符3', '新月音符4', '新月音符5', '新月音符6', '新月音符7', '新月音符8'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 3.533333333333333, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'unbound_cast_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '新月的苏醒', 'initial_seconds': 3.533333333333333, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 785.0, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'instant', 'hit_counts': {'新月音符1': None, '新月音符2': None, '新月音符3': None, '新月音符4': None, '新月音符5': None, '新月音符6': None, '新月音符7': None, '新月音符8': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '7c38a7682e2218dc6facdec5846d6f693c81958e7015b2a22942efc33b13da0c'}, {'section': 86, 'pair_id': 'hidden:char_4182_oblvns:fever', 'kind': 'hidden', 'field': 'fever', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_4182_oblvns', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True}, 'context': 'hidden:char_4182_oblvns:fever checked=False', 'expected_public_projection': {'attack': 785.0, 'total_damage': None, 'components': [{'name': '新月音符1', 'damage_type': 'magic', 'hits': 1, 'per_hit': 628.0, 'total': 628.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符2', 'damage_type': 'magic', 'hits': 1, 'per_hit': 577.7600000000001, 'total': 577.7600000000001, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符3', 'damage_type': 'magic', 'hits': 1, 'per_hit': 471.0, 'total': 471.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符4', 'damage_type': 'magic', 'hits': 1, 'per_hit': 364.24, 'total': 364.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符5', 'damage_type': 'magic', 'hits': 1, 'per_hit': 263.76, 'total': 263.76, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符6', 'damage_type': 'magic', 'hits': 1, 'per_hit': 207.24, 'total': 207.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符7', 'damage_type': 'magic', 'hits': 1, 'per_hit': 106.76000000000002, 'total': 106.76000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符8', 'damage_type': 'magic', 'hits': 1, 'per_hit': 31.400000000000002, 'total': 31.400000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['新月音符1', '新月音符2', '新月音符3', '新月音符4', '新月音符5', '新月音符6', '新月音符7', '新月音符8'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 3.533333333333333, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'unbound_cast_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '新月的苏醒', 'initial_seconds': 3.533333333333333, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 785.0, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'instant', 'hit_counts': {'新月音符1': None, '新月音符2': None, '新月音符3': None, '新月音符4': None, '新月音符5': None, '新月音符6': None, '新月音符7': None, '新月音符8': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '7c38a7682e2218dc6facdec5846d6f693c81958e7015b2a22942efc33b13da0c'}, {'section': 86, 'pair_id': 'hidden:char_4182_oblvns:fever', 'kind': 'hidden', 'field': 'fever', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_4182_oblvns', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'note_count': 0, 'ranged_attack': True}, 'context': 'hidden:char_4182_oblvns:fever checked=True', 'expected_public_projection': {'attack': 785.0, 'total_damage': None, 'components': [{'name': '新月音符1', 'damage_type': 'magic', 'hits': 1, 'per_hit': 628.0, 'total': 628.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符2', 'damage_type': 'magic', 'hits': 1, 'per_hit': 577.7600000000001, 'total': 577.7600000000001, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符3', 'damage_type': 'magic', 'hits': 1, 'per_hit': 471.0, 'total': 471.0, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符4', 'damage_type': 'magic', 'hits': 1, 'per_hit': 364.24, 'total': 364.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符5', 'damage_type': 'magic', 'hits': 1, 'per_hit': 263.76, 'total': 263.76, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符6', 'damage_type': 'magic', 'hits': 1, 'per_hit': 207.24, 'total': 207.24, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符7', 'damage_type': 'magic', 'hits': 1, 'per_hit': 106.76000000000002, 'total': 106.76000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '新月音符8', 'damage_type': 'magic', 'hits': 1, 'per_hit': 31.400000000000002, 'total': 31.400000000000002, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 112.0, 'base_attack_speed': 112.0, 'interval_seconds': 1.1607142857142858, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['新月音符1', '新月音符2', '新月音符3', '新月音符4', '新月音符5', '新月音符6', '新月音符7', '新月音符8'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 3.533333333333333, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 112.0, 'base_attack_speed_reference': 112.0, 'unbound_cast_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'xiangzi_notes', 'parameter_rows': [['音符数量参数', 8, '个'], ['可充能次数参数', 2, '次']], 'notes': ['八音符倍率是条件来源参考；首个音符、后续间隔、独立碰撞与实际结束未绑定。'], 'conditional_components': [{'name': '新月音符1', 'damage_type': 'magic', 'per_hit': 628.0, 'hits': 1, 'total': 628.0}, {'name': '新月音符2', 'damage_type': 'magic', 'per_hit': 577.7600000000001, 'hits': 1, 'total': 577.7600000000001}, {'name': '新月音符3', 'damage_type': 'magic', 'per_hit': 471.0, 'hits': 1, 'total': 471.0}, {'name': '新月音符4', 'damage_type': 'magic', 'per_hit': 364.24, 'hits': 1, 'total': 364.24}, {'name': '新月音符5', 'damage_type': 'magic', 'per_hit': 263.76, 'hits': 1, 'total': 263.76}, {'name': '新月音符6', 'damage_type': 'magic', 'per_hit': 207.24, 'hits': 1, 'total': 207.24}, {'name': '新月音符7', 'damage_type': 'magic', 'per_hit': 106.76000000000002, 'hits': 1, 'total': 106.76000000000002}, {'name': '新月音符8', 'damage_type': 'magic', 'per_hit': 31.400000000000002, 'hits': 1, 'total': 31.400000000000002}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2356, 'attack': 785.0, 'defense': 425, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 112.0, 'attack_speed_reference': 112.0, 'block_count': 2.0}, 'skill': {'name': '新月的苏醒', 'initial_seconds': 3.533333333333333, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 785.0, 'skill_attack_speed': 112.0, 'skill_attack_speed_reference': 112.0, 'sp_recovery_per_second': None, 'mode': 'instant', 'hit_counts': {'新月音符1': None, '新月音符2': None, '新月音符3': None, '新月音符4': None, '新月音符5': None, '新月音符6': None, '新月音符7': None, '新月音符8': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '7c38a7682e2218dc6facdec5846d6f693c81958e7015b2a22942efc33b13da0c'}, {'section': 86, 'pair_id': 'hidden:char_1048_orchd2:double_charge', 'kind': 'hidden', 'field': 'double_charge', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_1048_orchd2', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'power_coating': True, 'near_previous_deployment': False}, 'context': 'hidden:char_1048_orchd2:double_charge checked=False', 'expected_public_projection': {'attack': 942.0, 'total_damage': None, 'components': [{'name': '飞翔瞪射箭矢', 'damage_type': 'physical', 'hits': 12, 'per_hit': 1949.94, 'total': 23399.28, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '飞翔瞪射落地', 'damage_type': 'physical', 'hits': 1, 'per_hit': 3249.8999999999996, 'total': 3249.8999999999996, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['飞翔瞪射箭矢', '飞翔瞪射落地'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 3.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'unbound_cast_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['三轮箭矢数量参数', 12, '支'], ['名义技能持续参数', 4.2, '秒'], ['起飞参数', 0.2, '秒'], ['落地参数', 0.2, '秒']], 'notes': ['三轮3/4/5箭和落地只列条件来源；4.2秒与起落参数不证明各箭、落地或结束的实际相位。'], 'conditional_components': [{'name': '飞翔瞪射箭矢', 'damage_type': 'physical', 'per_hit': 1949.94, 'hits': 12, 'total': 23399.28}, {'name': '飞翔瞪射落地', 'damage_type': 'physical', 'per_hit': 3249.8999999999996, 'hits': 1, 'total': 3249.8999999999996}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['三轮箭矢数量参数', 12, '支'], ['名义技能持续参数', 4.2, '秒'], ['起飞参数', 0.2, '秒'], ['落地参数', 0.2, '秒']], 'notes': ['三轮3/4/5箭和落地只列条件来源；4.2秒与起落参数不证明各箭、落地或结束的实际相位。'], 'conditional_components': [{'name': '飞翔瞪射箭矢', 'damage_type': 'physical', 'per_hit': 1949.94, 'hits': 12, 'total': 23399.28}, {'name': '飞翔瞪射落地', 'damage_type': 'physical', 'per_hit': 3249.8999999999996, 'hits': 1, 'total': 3249.8999999999996}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'orchid_redeploy_reference': {'scope': 'cultivated attribute and same-identity talent parameter reference', 'operator_id': 'char_1048_orchd2', 'module_id': None, 'module_level': 0, 'module_unlocked': False, 'module_attribute_delta_seconds_parameter': 0, 'after_attribute_sources_seconds_reference': 70.0, 'talent_delta_seconds_parameter': -15, 'parameter_seconds': 55.0, 'original_talent_identity': {'talent_index': 3, 'prefab_key': '3'}, 'actual_retreat_seconds': None, 'actual_defeat_seconds': None, 'actual_next_deployment_seconds': None, 'events_scheduled': False, 'native_attachment_verified': False, 'live_state_verified': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime', 'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers', 'character_table.char_1048_orchd2.talents[1].candidates', 'character_table.char_1048_orchd2.talents[3].candidates', 'uniequip_table.equipDict.uniequip_002_orchd2', 'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard', 'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1788, 'attack': 942.0, 'defense': 231, 'resistance': 0.0, 'redeploy_seconds': 55.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '飞翔瞪射', 'initial_seconds': 3.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 942.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'飞翔瞪射箭矢': None, '飞翔瞪射落地': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'a4fc08f03fcf41d982dd196dbdba85594bb4f9c401070646b4c60505afd4c76b'}, {'section': 86, 'pair_id': 'hidden:char_1048_orchd2:double_charge', 'kind': 'hidden', 'field': 'double_charge', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_1048_orchd2', 'skill': 2, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'power_coating': True, 'near_previous_deployment': False}, 'context': 'hidden:char_1048_orchd2:double_charge checked=True', 'expected_public_projection': {'attack': 942.0, 'total_damage': None, 'components': [{'name': '飞翔瞪射箭矢', 'damage_type': 'physical', 'hits': 12, 'per_hit': 1949.94, 'total': 23399.28, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '飞翔瞪射落地', 'damage_type': 'physical', 'hits': 1, 'per_hit': 3249.8999999999996, 'total': 3249.8999999999996, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.6, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'unplaced_components': ['飞翔瞪射箭矢', '飞翔瞪射落地'], 'resource_and_damage_shared_clock': False, 'initial_seconds': 3.0, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'unbound_cast_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['三轮箭矢数量参数', 12, '支'], ['名义技能持续参数', 4.2, '秒'], ['起飞参数', 0.2, '秒'], ['落地参数', 0.2, '秒']], 'notes': ['三轮3/4/5箭和落地只列条件来源；4.2秒与起落参数不证明各箭、落地或结束的实际相位。'], 'conditional_components': [{'name': '飞翔瞪射箭矢', 'damage_type': 'physical', 'per_hit': 1949.94, 'hits': 12, 'total': 23399.28}, {'name': '飞翔瞪射落地', 'damage_type': 'physical', 'per_hit': 3249.8999999999996, 'hits': 1, 'total': 3249.8999999999996}], 'source_possible': True, 'observation_seconds': None, 'collision_clock_verified': False, 'window_reference': {'kind': 'orchid_arrows', 'parameter_rows': [['三轮箭矢数量参数', 12, '支'], ['名义技能持续参数', 4.2, '秒'], ['起飞参数', 0.2, '秒'], ['落地参数', 0.2, '秒']], 'notes': ['三轮3/4/5箭和落地只列条件来源；4.2秒与起落参数不证明各箭、落地或结束的实际相位。'], 'conditional_components': [{'name': '飞翔瞪射箭矢', 'damage_type': 'physical', 'per_hit': 1949.94, 'hits': 12, 'total': 23399.28}, {'name': '飞翔瞪射落地', 'damage_type': 'physical', 'per_hit': 3249.8999999999996, 'hits': 1, 'total': 3249.8999999999996}], 'source_possible': True, 'observation_seconds': 30.0, 'collision_clock_verified': False}, 'actual_hit_times_seconds': None, 'actual_end_seconds': None}, 'orchid_redeploy_reference': {'scope': 'cultivated attribute and same-identity talent parameter reference', 'operator_id': 'char_1048_orchd2', 'module_id': None, 'module_level': 0, 'module_unlocked': False, 'module_attribute_delta_seconds_parameter': 0, 'after_attribute_sources_seconds_reference': 70.0, 'talent_delta_seconds_parameter': -15, 'parameter_seconds': 55.0, 'original_talent_identity': {'talent_index': 3, 'prefab_key': '3'}, 'actual_retreat_seconds': None, 'actual_defeat_seconds': None, 'actual_next_deployment_seconds': None, 'events_scheduled': False, 'native_attachment_verified': False, 'live_state_verified': False, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_1048_orchd2.phases[*].attributesKeyFrames[*].data.respawnTime', 'character_table.char_1048_orchd2.potentialRanks[1].buff.attributes.attributeModifiers', 'character_table.char_1048_orchd2.talents[1].candidates', 'character_table.char_1048_orchd2.talents[3].candidates', 'uniequip_table.equipDict.uniequip_002_orchd2', 'battle_equip_table.uniequip_002_orchd2.phases[*].attributeBlackboard', 'battle_equip_table.uniequip_002_orchd2.phases[*].parts[*].addOrOverrideTalentDataBundle.candidates']}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1788, 'attack': 942.0, 'defense': 231, 'resistance': 0.0, 'redeploy_seconds': 55.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '飞翔瞪射', 'initial_seconds': 3.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 942.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'飞翔瞪射箭矢': None, '飞翔瞪射落地': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'a4fc08f03fcf41d982dd196dbdba85594bb4f9c401070646b4c60505afd4c76b'}, {'section': 86, 'pair_id': 'hidden:char_1041_angel2:steal_success', 'kind': 'hidden', 'field': 'steal_success', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_1041_angel2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': []}, 'context': 'hidden:char_1041_angel2:steal_success checked=False', 'expected_public_projection': {'attack': 918.04, 'total_damage': 21114.92, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 8, 'per_hit': 2295.1, 'total': 18360.8, 'source_unit': 'operator', 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 2.0, 'per_hit': 1377.06, 'total': 2754.12}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 8, 'per_hit': 141.0, 'total': 1128.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 4.0, 'cycle_seconds': 21.4}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '天空大扫除', 'initial_seconds': 4.0, 'recharge_seconds': 12.0, 'cycle_seconds': 21.4, 'duration_seconds': 9.4, 'total_damage': 21114.92, 'total_healing': 0, 'phase_damage': 21114.92, 'phase_healing': 0, 'cycle_dps': 1415.6691588785047, 'cycle_hps': 0.0, 'cycle_damage': 30295.32, 'cycle_healing': 0, 'skill_attack': 918.04, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 8, '火力电台期望轰炸': 2.0, '火力电台本体生命回复': 8}, 'window_seconds': 10.4, 'window_healing': 0, 'window_dps': 2030.280769230769, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3257e79a0c8549feb3e638297696da6e2c8a491e38491df029e168a7ff601421'}, {'section': 86, 'pair_id': 'hidden:char_1041_angel2:steal_success', 'kind': 'hidden', 'field': 'steal_success', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_1041_angel2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': []}, 'context': 'hidden:char_1041_angel2:steal_success checked=True', 'expected_public_projection': {'attack': 918.04, 'total_damage': 21114.92, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 8, 'per_hit': 2295.1, 'total': 18360.8, 'source_unit': 'operator', 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 2.0, 'per_hit': 1377.06, 'total': 2754.12}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 8, 'per_hit': 141.0, 'total': 1128.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 4.0, 'cycle_seconds': 21.4}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '天空大扫除', 'initial_seconds': 4.0, 'recharge_seconds': 12.0, 'cycle_seconds': 21.4, 'duration_seconds': 9.4, 'total_damage': 21114.92, 'total_healing': 0, 'phase_damage': 21114.92, 'phase_healing': 0, 'cycle_dps': 1415.6691588785047, 'cycle_hps': 0.0, 'cycle_damage': 30295.32, 'cycle_healing': 0, 'skill_attack': 918.04, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 8, '火力电台期望轰炸': 2.0, '火力电台本体生命回复': 8}, 'window_seconds': 10.4, 'window_healing': 0, 'window_dps': 2030.280769230769, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3257e79a0c8549feb3e638297696da6e2c8a491e38491df029e168a7ff601421'}, {'section': 86, 'pair_id': 'hidden:char_1041_angel2:delivery_coordinate', 'kind': 'hidden', 'field': 'delivery_coordinate', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_1041_angel2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': []}, 'context': 'hidden:char_1041_angel2:delivery_coordinate checked=False', 'expected_public_projection': {'attack': 918.04, 'total_damage': 21114.92, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 8, 'per_hit': 2295.1, 'total': 18360.8, 'source_unit': 'operator', 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 2.0, 'per_hit': 1377.06, 'total': 2754.12}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 8, 'per_hit': 141.0, 'total': 1128.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 4.0, 'cycle_seconds': 21.4}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '天空大扫除', 'initial_seconds': 4.0, 'recharge_seconds': 12.0, 'cycle_seconds': 21.4, 'duration_seconds': 9.4, 'total_damage': 21114.92, 'total_healing': 0, 'phase_damage': 21114.92, 'phase_healing': 0, 'cycle_dps': 1415.6691588785047, 'cycle_hps': 0.0, 'cycle_damage': 30295.32, 'cycle_healing': 0, 'skill_attack': 918.04, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 8, '火力电台期望轰炸': 2.0, '火力电台本体生命回复': 8}, 'window_seconds': 10.4, 'window_healing': 0, 'window_dps': 2030.280769230769, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3257e79a0c8549feb3e638297696da6e2c8a491e38491df029e168a7ff601421'}, {'section': 86, 'pair_id': 'hidden:char_1041_angel2:delivery_coordinate', 'kind': 'hidden', 'field': 'delivery_coordinate', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_1041_angel2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': []}, 'context': 'hidden:char_1041_angel2:delivery_coordinate checked=True', 'expected_public_projection': {'attack': 918.04, 'total_damage': 21114.92, 'components': [{'name': '技能攻击', 'damage_type': 'physical', 'hits': 8, 'per_hit': 2295.1, 'total': 18360.8, 'source_unit': 'operator', 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667]}, {'name': '火力电台期望轰炸', 'damage_type': 'physical', 'hits': 2.0, 'per_hit': 1377.06, 'total': 2754.12}, {'name': '火力电台本体生命回复', 'damage_type': 'regeneration', 'hits': 8, 'per_hit': 141.0, 'total': 1128.0, 'source_unit': 'operator'}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.3, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}, {'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [{'unit': 'char_1041_angel2', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Attack_Loop', 'windup_frames': 8, 'recovery_frames': 31, 'interval_frames': 39, 'interval_seconds': 1.3, 'start_frames': [0, 39, 78, 117, 156, 195, 234, 273, 312, 351], 'release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_impact_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'emitted_times_seconds': [0.26666666666666666, 1.5666666666666667, 2.8666666666666667, 4.166666666666667, 5.466666666666667, 6.766666666666667, 8.066666666666666, 9.366666666666667, 10.666666666666666, 11.966666666666667], 'emitted_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'hit_release_frames': [8, 47, 86, 125, 164, 203, 242, 281, 320, 359], 'interval_frames_by_attack': [39, 39, 39, 39, 39, 39, 39, 39, 39, 39], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 30, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'unplaced_components': ['火力电台期望轰炸', '火力电台本体生命回复'], 'resource_and_damage_shared_clock': True, 'initial_seconds': 4.0, 'cycle_seconds': 21.4}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2350, 'attack': 918.04, 'defense': 150, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '天空大扫除', 'initial_seconds': 4.0, 'recharge_seconds': 12.0, 'cycle_seconds': 21.4, 'duration_seconds': 9.4, 'total_damage': 21114.92, 'total_healing': 0, 'phase_damage': 21114.92, 'phase_healing': 0, 'cycle_dps': 1415.6691588785047, 'cycle_hps': 0.0, 'cycle_damage': 30295.32, 'cycle_healing': 0, 'skill_attack': 918.04, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': 1.0, 'mode': 'ammo', 'hit_counts': {'技能攻击': 8, '火力电台期望轰炸': 2.0, '火力电台本体生命回复': 8}, 'window_seconds': 10.4, 'window_healing': 0, 'window_dps': 2030.280769230769, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '3257e79a0c8549feb3e638297696da6e2c8a491e38491df029e168a7ff601421'}, {'section': 86, 'pair_id': 'hidden:char_1035_wisdel:overload', 'kind': 'hidden', 'field': 'overload', 'widget_checked': False, 'field_serialized': False, 'input': {'operator': 'char_1035_wisdel', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'ghost_count': 0, 'ghost_casts': 0}, 'context': 'hidden:char_1035_wisdel:overload checked=False', 'expected_public_projection': {'attack': 777.0, 'total_damage': None, 'components': [{'name': '维什戴尔主攻击', 'damage_type': 'physical', 'hits': 1, 'per_hit': 893.55, 'total': 893.55, 'source_unit': 'operator', 'actual_total': None}, {'name': '余震', 'damage_type': 'physical', 'hits': 3, 'per_hit': 1072.26, 'total': 3216.7799999999997, 'source_unit': 'operator', 'actual_total': None}, {'name': '残影单次爆炸条件参考', 'damage_type': 'physical', 'hits': 0, 'per_hit': 1165.5, 'total': 0.0, 'source_unit': 'operator', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.1, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1035_wisdel', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1', 'windup_frames': 18, 'recovery_frames': 45, 'interval_frames': 63, 'interval_seconds': 2.1, 'start_frames': [0], 'release_frames': [18], 'impact_frames': [18], 'times_seconds': [0.6], 'emitted_impact_frames': [18], 'emitted_times_seconds': [0.6], 'emitted_release_frames': [18], 'hit_release_frames': [18], 'interval_frames_by_attack': [63], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': ['维什戴尔主攻击', '余震'], 'resource_and_damage_shared_clock': True, 'initial_seconds': None, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'wisdel_secondary_reference': {'described_single_check_probability': 0.15, 'explosion_per_hit_reference': 1165.5, 'explosion_expected_count': None, 'random_independence_verified': False, 'shadow_lifecycle_verified': False, 'secondary_hit_times_seconds': None, 'source_possible': {'cast': True, 'window': True}, 's1_binding_verified': False, 'ghost_casts_requested': 0, 'ghost_per_cast_damage_reference': None, 'ghost_cast_times_seconds': None, 'ghost_full_cast_attribution_verified': False, 'ghost_declared_count_damage_reference': 0}, 'wisdel_summon_qualification_reference': {'operator_id': 'char_1035_wisdel', 'token_id': 'token_10035_wisdel_wward', 'scope': '仅固定原表第二天赋与第三技能两条本体召唤途径的培养资格资料；不证明声明来源、当前存在、实际施放或全部模组/藏品途径。', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'current_cultivation': {'elite': 2, 'level': 90, 'potential': 1}, 'talent_route': {'source_selector': 'character_table.char_1035_wisdel.talents[1].candidates[0]', 'talent_index': 1, 'prefab_key': '2', 'name': '死魂灵的余息', 'description': '部署后立刻在攻击范围内召唤一个魂灵之影，在魂灵之影周围时获得<$ba.camou>迷彩</>', 'unlock_elite': 2, 'unlock_level': 1, 'required_potential_rank': 0, 'token_key': 'token_10035_wisdel_wward', 'cultivation_qualified': True}, 'skill_route': {'source_selector': 'character_table.char_1035_wisdel.skills[2]', 'skill_number': 3, 'skill_id': 'skchr_wisdel_3', 'override_token_key': 'token_10035_wisdel_wward', 'unlock_elite': 2, 'unlock_level': 1, 'original_common_fragments': ['立刻在攻击范围内召唤', '个魂灵之影（最多存在3个，技能结束后保留）'], 'cultivation_qualified': True, 'currently_selected': False, 'selected_level_source': None}, 'actual_source_provenance': None, 'actual_presence_verified': False, 'actual_cast_clock_verified': False, 'covers_all_routes': False, 'declared_counts_reinterpreted': False}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1888, 'attack': 777.0, 'defense': 256, 'resistance': 15.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '定点清算', 'initial_seconds': None, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 777.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': None, 'mode': 'next_attack', 'hit_counts': {'余震': None, '残影单次爆炸条件参考': None, '维什戴尔主攻击': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '7417c704fcf8856243b7e7b9668d0d31bc80a29fed2513c5c46caf669603712e'}, {'section': 86, 'pair_id': 'hidden:char_1035_wisdel:overload', 'kind': 'hidden', 'field': 'overload', 'widget_checked': True, 'field_serialized': False, 'input': {'operator': 'char_1035_wisdel', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90, 'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 30.0, 'healing_targets': 1, 'continuous_attacks': True, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'ghost_count': 0, 'ghost_casts': 0}, 'context': 'hidden:char_1035_wisdel:overload checked=True', 'expected_public_projection': {'attack': 777.0, 'total_damage': None, 'components': [{'name': '维什戴尔主攻击', 'damage_type': 'physical', 'hits': 1, 'per_hit': 893.55, 'total': 893.55, 'source_unit': 'operator', 'actual_total': None}, {'name': '余震', 'damage_type': 'physical', 'hits': 3, 'per_hit': 1072.26, 'total': 3216.7799999999997, 'source_unit': 'operator', 'actual_total': None}, {'name': '残影单次爆炸条件参考', 'damage_type': 'physical', 'hits': 0, 'per_hit': 1165.5, 'total': 0.0, 'source_unit': 'operator', 'actual_total': None}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.1, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'char_1035_wisdel', 'target_scope': 'enemy', 'known_animation': True, 'exact_binding': False, 'reference_binding': True, 'animation': 'Skill_1', 'windup_frames': 18, 'recovery_frames': 45, 'interval_frames': 63, 'interval_seconds': 2.1, 'start_frames': [0], 'release_frames': [18], 'impact_frames': [18], 'times_seconds': [0.6], 'emitted_impact_frames': [18], 'emitted_times_seconds': [0.6], 'emitted_release_frames': [18], 'hit_release_frames': [18], 'interval_frames_by_attack': [63], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': 'https://github.com/xulai1001/arkdps_data_collection/blob/31269be4ca10124ca3f994ab33382dfc3d502991/customdata/dps_anim.json'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'unplaced_components': ['维什戴尔主攻击', '余震'], 'resource_and_damage_shared_clock': True, 'initial_seconds': None, 'cycle_seconds': None}, 'total_healing': 0, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'wisdel_secondary_reference': {'described_single_check_probability': 0.15, 'explosion_per_hit_reference': 1165.5, 'explosion_expected_count': None, 'random_independence_verified': False, 'shadow_lifecycle_verified': False, 'secondary_hit_times_seconds': None, 'source_possible': {'cast': True, 'window': True}, 's1_binding_verified': False, 'ghost_casts_requested': 0, 'ghost_per_cast_damage_reference': None, 'ghost_cast_times_seconds': None, 'ghost_full_cast_attribution_verified': False, 'ghost_declared_count_damage_reference': 0}, 'wisdel_summon_qualification_reference': {'operator_id': 'char_1035_wisdel', 'token_id': 'token_10035_wisdel_wward', 'scope': '仅固定原表第二天赋与第三技能两条本体召唤途径的培养资格资料；不证明声明来源、当前存在、实际施放或全部模组/藏品途径。', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'current_cultivation': {'elite': 2, 'level': 90, 'potential': 1}, 'talent_route': {'source_selector': 'character_table.char_1035_wisdel.talents[1].candidates[0]', 'talent_index': 1, 'prefab_key': '2', 'name': '死魂灵的余息', 'description': '部署后立刻在攻击范围内召唤一个魂灵之影，在魂灵之影周围时获得<$ba.camou>迷彩</>', 'unlock_elite': 2, 'unlock_level': 1, 'required_potential_rank': 0, 'token_key': 'token_10035_wisdel_wward', 'cultivation_qualified': True}, 'skill_route': {'source_selector': 'character_table.char_1035_wisdel.skills[2]', 'skill_number': 3, 'skill_id': 'skchr_wisdel_3', 'override_token_key': 'token_10035_wisdel_wward', 'unlock_elite': 2, 'unlock_level': 1, 'original_common_fragments': ['立刻在攻击范围内召唤', '个魂灵之影（最多存在3个，技能结束后保留）'], 'cultivation_qualified': True, 'currently_selected': False, 'selected_level_source': None}, 'actual_source_provenance': None, 'actual_presence_verified': False, 'actual_cast_clock_verified': False, 'covers_all_routes': False, 'declared_counts_reinterpreted': False}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1888, 'attack': 777.0, 'defense': 256, 'resistance': 15.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '定点清算', 'initial_seconds': None, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': None, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': None, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 777.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'sp_recovery_per_second': None, 'mode': 'next_attack', 'hit_counts': {'余震': None, '残影单次爆炸条件参考': None, '维什戴尔主攻击': None}, 'window_seconds': 30.0, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '7417c704fcf8856243b7e7b9668d0d31bc80a29fed2513c5c46caf669603712e'}, {'pair_id': '088-native-checkbox-mechanist-S1', 'widget_checked': False, 'control_display_source': 'visible Attack-SP', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 60, 'skill_rank': 10, 'timing_mode': 'frames', 'continuous_attacks': False}, 'required_source_contract': 'Existing legacy initial/recharge/cycle and normal gate; native bool preserved, exact keys from final source', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 543.0, 'total_damage': 12624.75, 'components': [{'name': '五连击', 'damage_type': 'physical', 'hits': 15, 'per_hit': 841.65, 'total': 12624.75, 'times_seconds': [3.8, 4.0, 4.2, 4.4, 4.6, 6.3, 6.5, 6.7, 6.9, 7.1, 8.8, 9.0, 9.2, 9.4, 9.6]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.5, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'mechanist', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 75, 'interval_seconds': 2.5, 'start_frames': [0, 75, 150], 'release_frames': [75, 150, 225], 'impact_frames': [114, 120, 126, 132, 138, 189, 195, 201, 207, 213, 264, 270, 276, 282, 288], 'times_seconds': [3.8, 4.0, 4.2, 4.4, 4.6, 6.3, 6.5, 6.7, 6.9, 7.1, 8.8, 9.0, 9.2, 9.4, 9.6], 'emitted_impact_frames': [75, 150, 225], 'emitted_times_seconds': [2.5, 5.0, 7.5], 'emitted_release_frames': [75, 150, 225], 'hit_release_frames': [75, 150, 225], 'interval_frames_by_attack': [75, 75, 75], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。', '机械师S1按档案projectile_delay_time和attack@interval分配五连击；字段与客户端落地/发射行为的绑定仍待录屏校准。'], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': None, 'cycle_seconds': None}, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 3288, 'attack': 543.0, 'defense': 701, 'resistance': 0.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 3.0}, 'skill': {'name': '聚类分析', 'initial_seconds': None, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 8.333333333333334, 'total_damage': 12624.75, 'total_healing': 0, 'phase_damage': 8416.5, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'sp_type': 'INCREASE_WHEN_ATTACK', 'initial_sp': 0.0, 'sp_cost': 7, 'sp_recovery_per_second': None, 'skill_attack': 543.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'healing_targets': 1, 'window_healing': 0, 'window_damage': 12624.75, 'window_seconds': 8.333333333333334}}}, 'saved_result_full_json_sha256': '5634ff97fe04fa0711c1da7db1420275d27c440b7e65019fc3e5729426727c2c'}, {'pair_id': '088-native-checkbox-mechanist-S1', 'widget_checked': True, 'control_display_source': 'visible Attack-SP', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 60, 'skill_rank': 10, 'timing_mode': 'frames', 'continuous_attacks': True}, 'required_source_contract': 'Existing legacy initial/recharge/cycle and normal gate; native bool preserved, exact keys from final source', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 543.0, 'total_damage': 12624.75, 'components': [{'name': '五连击', 'damage_type': 'physical', 'hits': 15, 'per_hit': 841.65, 'total': 12624.75, 'times_seconds': [3.8, 4.0, 4.2, 4.4, 4.6, 6.3, 6.5, 6.7, 6.9, 7.1, 8.8, 9.0, 9.2, 9.4, 9.6]}], 'attack_speed': 100.0, 'base_attack_speed': 100.0, 'interval_seconds': 2.5, 'timing': {'mode': 'frames', 'fps': 30, 'streams': [{'unit': 'mechanist', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 75, 'interval_seconds': 2.5, 'start_frames': [0, 75, 150], 'release_frames': [75, 150, 225], 'impact_frames': [114, 120, 126, 132, 138, 189, 195, 201, 207, 213, 264, 270, 276, 282, 288], 'times_seconds': [3.8, 4.0, 4.2, 4.4, 4.6, 6.3, 6.5, 6.7, 6.9, 7.1, 8.8, 9.0, 9.2, 9.4, 9.6], 'emitted_impact_frames': [75, 150, 225], 'emitted_times_seconds': [2.5, 5.0, 7.5], 'emitted_release_frames': [75, 150, 225], 'hit_release_frames': [75, 150, 225], 'interval_frames_by_attack': [75, 75, 75], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。', '机械师S1按档案projectile_delay_time和attack@interval分配五连击；字段与客户端落地/发射行为的绑定仍待录屏校准。'], 'recharge_streams': [{'unit': 'mechanist', 'target_scope': 'enemy', 'known_animation': False, 'exact_binding': False, 'reference_binding': False, 'animation': None, 'windup_frames': None, 'recovery_frames': None, 'interval_frames': 36, 'interval_seconds': 1.2, 'start_frames': [0, 36, 72, 108, 144, 180, 216], 'release_frames': [36, 72, 108, 144, 180, 216, 252], 'impact_frames': [36, 72, 108, 144, 180, 216, 252], 'times_seconds': [1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 8.4], 'emitted_impact_frames': [36, 72, 108, 144, 180, 216, 252], 'emitted_times_seconds': [1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 8.4], 'emitted_release_frames': [36, 72, 108, 144, 180, 216, 252], 'hit_release_frames': [36, 72, 108, 144, 180, 216, 252], 'interval_frames_by_attack': [36, 36, 36, 36, 36, 36, 36], 'temporary_attack_speed': False, 'attack_speed_sample': '攻击开始帧取当前攻速；冷却/动画中途变速的客户端模板行为尚待校准', 'resume_frame': 0, 'source': '未确认；保留延迟首击情景'}], 'unplaced_components': [], 'resource_and_damage_shared_clock': True, 'initial_seconds': 8.433333333333334, 'cycle_seconds': 16.766666666666666}, 'attack_speed_reference': 100.0, 'base_attack_speed_reference': 100.0, 'estimate': {'training': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 3288, 'attack': 543.0, 'defense': 701, 'resistance': 0.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 3.0}, 'skill': {'name': '聚类分析', 'initial_seconds': 8.433333333333334, 'recharge_seconds': 8.433333333333334, 'cycle_seconds': 16.766666666666666, 'duration_seconds': 8.333333333333334, 'total_damage': 12624.75, 'total_healing': 0, 'phase_damage': 8416.5, 'phase_healing': 0, 'cycle_dps': 979.6669980119285, 'cycle_hps': 0.0, 'cycle_damage': 16425.75, 'cycle_healing': 0, 'sp_type': 'INCREASE_WHEN_ATTACK', 'initial_sp': 0.0, 'sp_cost': 7, 'sp_recovery_per_second': None, 'skill_attack': 543.0, 'skill_attack_speed': 100.0, 'skill_attack_speed_reference': 100.0, 'healing_targets': 1, 'window_healing': 0, 'window_damage': 12624.75, 'window_seconds': 8.333333333333334}}}, 'saved_result_full_json_sha256': '8b1d8d91da3c2eef2603502b3ec290233b0128b6f453608a9aeeed8b9529cd7d'}, {'pair_id': '088-hidden-checkbox-amiya-E2-S1-bounded-reference', 'widget_checked': False, 'control_display_source': 'hidden natural-SP checkbox still globally serialized', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'operator': 'char_002_amiya', 'skill': 1, 'elite': 2, 'level': 80, 'skill_rank': 10, 'timing_mode': 'continuous', 'timing': {'target_disappears_seconds': 5.75}, 'continuous_attacks': False}, 'required_source_contract': 'Actual caster reference flag and qualified talent parameter; actual acquisition/impact/recharge/cycle remain unknown', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 682.0, 'total_damage': None, 'components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 15, 'per_hit': 682.0, 'total': 10230.0, 'source_unit': 'operator', 'timing_reference': 'continuous interval conditional reference; native acquisition/release/impact unverified', 'actual_total': None}], 'attack_speed': 190.0, 'base_attack_speed': 100.0, 'interval_seconds': 0.8421052631578947, 'timing': {'mode': 'continuous', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': True, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'resource_and_damage_shared_clock': False}, 'total_healing': 0, 'attack_speed_reference': 190.0, 'base_attack_speed_reference': 100.0, 'amiya_continuous_reference': {'operator_id': 'char_002_amiya', 'skill_number': 1, 'enemy_source_excluded': False, 'declared_target_lifetime_seconds': 5.75, 'declared_target_windows_seconds': None, 'per_hit_damage_reference': 682.0, 'parameter_clock_reference': {'initial_seconds': 15.0, 'duration_seconds': 30.0, 'recharge_seconds': 30.0, 'cycle_seconds': 60.0, 'total_damage': 23870.0, 'phase_damage': 23870.0, 'cycle_damage': 36146.0, 'cycle_dps': 602.4333333333333, 'cycle_healing': 0, 'cycle_hps': 0.0, 'window_damage': 10230.0, 'window_dps': 802.3529411764706}, 'cast_reference': {'enemy_source_excluded': False, 'source_possible': True, 'observation_seconds': 30.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 35, 'per_hit': 682.0, 'total': 23870.0, 'source_unit': 'operator', 'times_seconds': [0.8421052631578947, 1.6842105263157894, 2.526315789473684, 3.3684210526315788, 4.2105263157894735, 5.052631578947368, 5.894736842105263, 6.7368421052631575, 7.578947368421052, 8.421052631578947, 9.263157894736842, 10.105263157894736, 10.94736842105263, 11.789473684210526, 12.631578947368421, 13.473684210526315, 14.315789473684209, 15.157894736842104, 16.0, 16.842105263157894, 17.684210526315788, 18.526315789473685, 19.36842105263158, 20.210526315789473, 21.052631578947366, 21.89473684210526, 22.736842105263158, 23.57894736842105, 24.421052631578945, 25.263157894736842, 26.105263157894736, 26.94736842105263, 27.789473684210524, 28.631578947368418, 29.473684210526315]}]}, 'window_reference': {'enemy_source_excluded': False, 'source_possible': True, 'observation_seconds': 12.75, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 15, 'per_hit': 682.0, 'total': 10230.0, 'source_unit': 'operator', 'times_seconds': [0.8421052631578947, 1.6842105263157894, 2.526315789473684, 3.3684210526315788, 4.2105263157894735, 5.052631578947368, 5.894736842105263, 6.7368421052631575, 7.578947368421052, 8.421052631578947, 9.263157894736842, 10.105263157894736, 10.94736842105263, 11.789473684210526, 12.631578947368421]}]}, 'recharge_reference': {'enemy_source_excluded': False, 'source_possible': True, 'observation_seconds': 30.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 18, 'per_hit': 682.0, 'total': 12276.0, 'source_unit': 'operator', 'times_seconds': [1.6, 3.2, 4.800000000000001, 6.4, 8.0, 9.600000000000001, 11.200000000000001, 12.8, 14.4, 16.0, 17.6, 19.200000000000003, 20.8, 22.400000000000002, 24.0, 25.6, 27.200000000000003, 28.8]}]}, 'natural_sp_rate_parameter': 1.0, 'required_sp_parameter': 30, 'natural_only_recharge_seconds_reference': 30.0, 'attack_sp_per_attack_parameter': 2.0, 'attack_sp_enabled_in_reference': False, 'actual_acquisition_times_seconds': None, 'actual_impact_times_seconds': None, 'actual_recharge_seconds': None, 'actual_cycle_seconds': None, 'native_clock_binding_verified': False, 'initial_scope': 'existing independent pre-cast reference unchanged', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_002_amiya.skills[0].skillId', 'character_table.char_002_amiya.talents[0].candidates', 'character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime', 'skill_table.skcom_magic_rage[3].levels[*]']}, 'estimate': {'training': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1680, 'attack': 682.0, 'defense': 121, 'resistance': 20.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '战术咏唱·γ型', 'initial_seconds': 15.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 30.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 682.0, 'skill_attack_speed': 190.0, 'skill_attack_speed_reference': 190.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'技能攻击': None}, 'window_seconds': 12.75, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '66d20e9e898068cfa9d67b339af7b0e509c09023c9bb56d13adbfd8bdd5815c4'}, {'pair_id': '088-hidden-checkbox-amiya-E2-S1-bounded-reference', 'widget_checked': True, 'control_display_source': 'hidden natural-SP checkbox still globally serialized', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'operator': 'char_002_amiya', 'skill': 1, 'elite': 2, 'level': 80, 'skill_rank': 10, 'timing_mode': 'continuous', 'timing': {'target_disappears_seconds': 5.75}, 'continuous_attacks': True}, 'required_source_contract': 'Actual caster reference flag and qualified talent parameter; actual acquisition/impact/recharge/cycle remain unknown', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 682.0, 'total_damage': None, 'components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 15, 'per_hit': 682.0, 'total': 10230.0, 'source_unit': 'operator', 'timing_reference': 'continuous interval conditional reference; native acquisition/release/impact unverified', 'actual_total': None}], 'attack_speed': 190.0, 'base_attack_speed': 100.0, 'interval_seconds': 0.8421052631578947, 'timing': {'mode': 'continuous', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': True, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'resource_and_damage_shared_clock': False}, 'total_healing': 0, 'attack_speed_reference': 190.0, 'base_attack_speed_reference': 100.0, 'amiya_continuous_reference': {'operator_id': 'char_002_amiya', 'skill_number': 1, 'enemy_source_excluded': False, 'declared_target_lifetime_seconds': 5.75, 'declared_target_windows_seconds': None, 'per_hit_damage_reference': 682.0, 'parameter_clock_reference': {'initial_seconds': 7.0, 'duration_seconds': 30.0, 'recharge_seconds': 13.999999999999995, 'cycle_seconds': 43.99999999999999, 'total_damage': 23870.0, 'phase_damage': 23870.0, 'cycle_damage': 29326.0, 'cycle_dps': 666.5000000000001, 'cycle_healing': 0, 'cycle_hps': 0.0, 'window_damage': 10230.0, 'window_dps': 802.3529411764706}, 'cast_reference': {'enemy_source_excluded': False, 'source_possible': True, 'observation_seconds': 30.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 35, 'per_hit': 682.0, 'total': 23870.0, 'source_unit': 'operator', 'times_seconds': [0.8421052631578947, 1.6842105263157894, 2.526315789473684, 3.3684210526315788, 4.2105263157894735, 5.052631578947368, 5.894736842105263, 6.7368421052631575, 7.578947368421052, 8.421052631578947, 9.263157894736842, 10.105263157894736, 10.94736842105263, 11.789473684210526, 12.631578947368421, 13.473684210526315, 14.315789473684209, 15.157894736842104, 16.0, 16.842105263157894, 17.684210526315788, 18.526315789473685, 19.36842105263158, 20.210526315789473, 21.052631578947366, 21.89473684210526, 22.736842105263158, 23.57894736842105, 24.421052631578945, 25.263157894736842, 26.105263157894736, 26.94736842105263, 27.789473684210524, 28.631578947368418, 29.473684210526315]}]}, 'window_reference': {'enemy_source_excluded': False, 'source_possible': True, 'observation_seconds': 12.75, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 15, 'per_hit': 682.0, 'total': 10230.0, 'source_unit': 'operator', 'times_seconds': [0.8421052631578947, 1.6842105263157894, 2.526315789473684, 3.3684210526315788, 4.2105263157894735, 5.052631578947368, 5.894736842105263, 6.7368421052631575, 7.578947368421052, 8.421052631578947, 9.263157894736842, 10.105263157894736, 10.94736842105263, 11.789473684210526, 12.631578947368421]}]}, 'recharge_reference': {'enemy_source_excluded': False, 'source_possible': True, 'observation_seconds': 13.999999999999995, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 8, 'per_hit': 682.0, 'total': 5456.0, 'source_unit': 'operator', 'times_seconds': [1.6, 3.2, 4.800000000000001, 6.4, 8.0, 9.600000000000001, 11.200000000000001, 12.8]}]}, 'natural_sp_rate_parameter': 1.0, 'required_sp_parameter': 30, 'natural_only_recharge_seconds_reference': 30.0, 'attack_sp_per_attack_parameter': 2.0, 'attack_sp_enabled_in_reference': True, 'actual_acquisition_times_seconds': None, 'actual_impact_times_seconds': None, 'actual_recharge_seconds': None, 'actual_cycle_seconds': None, 'native_clock_binding_verified': False, 'initial_scope': 'existing independent pre-cast reference unchanged', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_002_amiya.skills[0].skillId', 'character_table.char_002_amiya.talents[0].candidates', 'character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime', 'skill_table.skcom_magic_rage[3].levels[*]']}, 'estimate': {'training': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1680, 'attack': 682.0, 'defense': 121, 'resistance': 20.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '战术咏唱·γ型', 'initial_seconds': 7.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 30.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 682.0, 'skill_attack_speed': 190.0, 'skill_attack_speed_reference': 190.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'技能攻击': None}, 'window_seconds': 12.75, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'e860a5b544dc4cf814dc86d16aa24802937eeba2010801467207ff2dba54e416'}, {'pair_id': '088-hidden-checkbox-chen3-S3-active-warrior67', 'widget_checked': False, 'control_display_source': 'hidden natural-SP checkbox and actual applicable manual relic list item', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': ['rogue_6_relic_legacy_67'], 'operator': 'char_1050_chen3', 'skill': 3, 'elite': 2, 'level': 90, 'skill_rank': 10, 'timing_mode': 'continuous', 'continuous_attacks': False}, 'required_source_contract': 'Prepare-resolved active warrior attack-SP affects first charge; do not require masked final totals/cycle to differ', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 870.0999999999999, 'total_damage': None, 'components': [{'name': '天喟剑气', 'damage_type': 'weakness', 'hits': 1, 'per_hit': 5046.579999999999, 'total': 5046.579999999999, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '技能攻击', 'damage_type': 'weakness', 'hits': 33, 'per_hit': 1827.2099999999998, 'total': 60297.92999999999, 'source_unit': 'operator', 'times_seconds': [1.1061946902654867, 1.1061946902654867, 1.1061946902654867, 2.2123893805309733, 2.2123893805309733, 2.2123893805309733, 3.31858407079646, 3.31858407079646, 3.31858407079646, 4.424778761061947, 4.424778761061947, 4.424778761061947, 5.530973451327434, 5.530973451327434, 5.530973451327434, 6.63716814159292, 6.63716814159292, 6.63716814159292, 7.7433628318584065, 7.7433628318584065, 7.7433628318584065, 8.849557522123893, 8.849557522123893, 8.849557522123893, 9.95575221238938, 9.95575221238938, 9.95575221238938, 11.061946902654867, 11.061946902654867, 11.061946902654867, 12.168141592920353, 12.168141592920353, 12.168141592920353]}], 'attack_speed': 113.0, 'base_attack_speed': 113.0, 'interval_seconds': 1.1061946902654867, 'timing': {'mode': 'continuous', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': []}, 'total_healing': 0, 'attack_speed_reference': 113.0, 'base_attack_speed_reference': 113.0, 'chen_phase_reference': {'kind': 'swordwave', 'declared_current_hp': 0.0, 'hp_ratio_parameter': 0.06, 'minimum_attack_scale_parameter': 5.8, 'body_duration_parameter_seconds': 20.0, 'actual_collision_times_seconds': None, 'collision_clock_verified': False, 'conditional_components': [{'name': '天喟剑气', 'damage_type': 'weakness', 'per_hit': 5046.579999999999, 'hits': 1, 'total': 5046.579999999999}], 'source_possible': True, 'observation_seconds': None, 'window_reference': {'kind': 'swordwave', 'declared_current_hp': 0.0, 'hp_ratio_parameter': 0.06, 'minimum_attack_scale_parameter': 5.8, 'body_duration_parameter_seconds': 20.0, 'actual_collision_times_seconds': None, 'collision_clock_verified': False, 'conditional_components': [{'name': '天喟剑气', 'damage_type': 'weakness', 'per_hit': 5046.579999999999, 'hits': 1, 'total': 5046.579999999999}], 'source_possible': True, 'observation_seconds': 12.75}}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2910, 'attack': 870.0999999999999, 'defense': 425, 'resistance': 15.0, 'redeploy_seconds': 70.0, 'attack_speed': 113.0, 'attack_speed_reference': 113.0, 'block_count': 1.0}, 'skill': {'name': '赤霄·天喟', 'initial_seconds': 7.0, 'recharge_seconds': 25.0, 'cycle_seconds': 45.0, 'duration_seconds': 20.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': 0.0, 'cycle_damage': None, 'cycle_healing': 0, 'skill_attack': 870.0999999999999, 'skill_attack_speed': 113.0, 'skill_attack_speed_reference': 113.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'天喟剑气': None, '技能攻击': 54}, 'window_seconds': 12.75, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': 'dcc758d80c3017dce9b84374005f5563937993c39a15d191016d02b50109988e'}, {'pair_id': '088-hidden-checkbox-chen3-S3-active-warrior67', 'widget_checked': True, 'control_display_source': 'hidden natural-SP checkbox and actual applicable manual relic list item', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': ['rogue_6_relic_legacy_67'], 'operator': 'char_1050_chen3', 'skill': 3, 'elite': 2, 'level': 90, 'skill_rank': 10, 'timing_mode': 'continuous', 'continuous_attacks': True}, 'required_source_contract': 'Prepare-resolved active warrior attack-SP affects first charge; do not require masked final totals/cycle to differ', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 870.0999999999999, 'total_damage': None, 'components': [{'name': '天喟剑气', 'damage_type': 'weakness', 'hits': 1, 'per_hit': 5046.579999999999, 'total': 5046.579999999999, 'source_unit': 'operator', 'timing_reference': 'unplaced conditional source; actual collision clock unverified', 'actual_total': None}, {'name': '技能攻击', 'damage_type': 'weakness', 'hits': 33, 'per_hit': 1827.2099999999998, 'total': 60297.92999999999, 'source_unit': 'operator', 'times_seconds': [1.1061946902654867, 1.1061946902654867, 1.1061946902654867, 2.2123893805309733, 2.2123893805309733, 2.2123893805309733, 3.31858407079646, 3.31858407079646, 3.31858407079646, 4.424778761061947, 4.424778761061947, 4.424778761061947, 5.530973451327434, 5.530973451327434, 5.530973451327434, 6.63716814159292, 6.63716814159292, 6.63716814159292, 7.7433628318584065, 7.7433628318584065, 7.7433628318584065, 8.849557522123893, 8.849557522123893, 8.849557522123893, 9.95575221238938, 9.95575221238938, 9.95575221238938, 11.061946902654867, 11.061946902654867, 11.061946902654867, 12.168141592920353, 12.168141592920353, 12.168141592920353]}], 'attack_speed': 113.0, 'base_attack_speed': 113.0, 'interval_seconds': 1.1061946902654867, 'timing': {'mode': 'continuous', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': False, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': []}, 'total_healing': 0, 'attack_speed_reference': 113.0, 'base_attack_speed_reference': 113.0, 'chen_phase_reference': {'kind': 'swordwave', 'declared_current_hp': 0.0, 'hp_ratio_parameter': 0.06, 'minimum_attack_scale_parameter': 5.8, 'body_duration_parameter_seconds': 20.0, 'actual_collision_times_seconds': None, 'collision_clock_verified': False, 'conditional_components': [{'name': '天喟剑气', 'damage_type': 'weakness', 'per_hit': 5046.579999999999, 'hits': 1, 'total': 5046.579999999999}], 'source_possible': True, 'observation_seconds': None, 'window_reference': {'kind': 'swordwave', 'declared_current_hp': 0.0, 'hp_ratio_parameter': 0.06, 'minimum_attack_scale_parameter': 5.8, 'body_duration_parameter_seconds': 20.0, 'actual_collision_times_seconds': None, 'collision_clock_verified': False, 'conditional_components': [{'name': '天喟剑气', 'damage_type': 'weakness', 'per_hit': 5046.579999999999, 'hits': 1, 'total': 5046.579999999999}], 'source_possible': True, 'observation_seconds': 12.75}}, 'estimate': {'training': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 2910, 'attack': 870.0999999999999, 'defense': 425, 'resistance': 15.0, 'redeploy_seconds': 70.0, 'attack_speed': 113.0, 'attack_speed_reference': 113.0, 'block_count': 1.0}, 'skill': {'name': '赤霄·天喟', 'initial_seconds': 2.9999999999999996, 'recharge_seconds': 25.0, 'cycle_seconds': 45.0, 'duration_seconds': 20.0, 'total_damage': None, 'total_healing': 0, 'phase_damage': None, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': 0.0, 'cycle_damage': None, 'cycle_healing': 0, 'skill_attack': 870.0999999999999, 'skill_attack_speed': 113.0, 'skill_attack_speed_reference': 113.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'天喟剑气': None, '技能攻击': 54}, 'window_seconds': 12.75, 'window_healing': 0, 'window_dps': None, 'window_hps': 0.0, 'window_damage': None}}}, 'saved_result_full_json_sha256': '370a7fb4648e468082b8251e23968fdf9dba69285942d0cdd5fec8b32325c065'}, {'pair_id': '088-hidden-checkbox-amiya-E0-S1-empty-target-reference', 'widget_checked': False, 'control_display_source': 'hidden natural-SP checkbox; actual QPlainTextEdit object JSON target_windows=[]', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'operator': 'char_002_amiya', 'skill': 1, 'elite': 0, 'level': 50, 'skill_rank': 7, 'timing_mode': 'continuous', 'timing': {'target_windows': []}, 'continuous_attacks': False}, 'required_source_contract': 'E0 no emotion-absorption attack credit; true/false changes existing reference enabled flag, not actual native clock or damage supply', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 460.0, 'total_damage': 0, 'components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'timing_reference': 'continuous interval conditional reference; native acquisition/release/impact unverified'}], 'attack_speed': 160.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'continuous', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': True, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'resource_and_damage_shared_clock': False}, 'total_healing': 0, 'attack_speed_reference': 160.0, 'base_attack_speed_reference': 100.0, 'amiya_continuous_reference': {'operator_id': 'char_002_amiya', 'skill_number': 1, 'enemy_source_excluded': True, 'declared_target_lifetime_seconds': None, 'declared_target_windows_seconds': [], 'per_hit_damage_reference': 460.0, 'parameter_clock_reference': {'initial_seconds': 22.0, 'duration_seconds': 30.0, 'recharge_seconds': 32.0, 'cycle_seconds': 62.0, 'total_damage': 0, 'phase_damage': 0, 'cycle_damage': 0, 'cycle_dps': 0.0, 'cycle_healing': 0, 'cycle_hps': 0.0, 'window_damage': 0, 'window_dps': 0.0}, 'cast_reference': {'enemy_source_excluded': True, 'source_possible': False, 'observation_seconds': 30.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'times_seconds': []}]}, 'window_reference': {'enemy_source_excluded': True, 'source_possible': False, 'observation_seconds': 12.75, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'times_seconds': []}]}, 'recharge_reference': {'enemy_source_excluded': True, 'source_possible': False, 'observation_seconds': 32.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'times_seconds': []}]}, 'natural_sp_rate_parameter': 1.0, 'required_sp_parameter': 32, 'natural_only_recharge_seconds_reference': 32.0, 'attack_sp_per_attack_parameter': 0, 'attack_sp_enabled_in_reference': False, 'actual_acquisition_times_seconds': None, 'actual_impact_times_seconds': None, 'actual_recharge_seconds': None, 'actual_cycle_seconds': None, 'native_clock_binding_verified': False, 'initial_scope': 'existing independent pre-cast reference unchanged', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_002_amiya.skills[0].skillId', 'character_table.char_002_amiya.talents[0].candidates', 'character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime', 'skill_table.skcom_magic_rage[3].levels[*]']}, 'estimate': {'training': {'elite': 0, 'level': 50, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1158, 'attack': 460.0, 'defense': 81, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '战术咏唱·γ型', 'initial_seconds': 22.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 30.0, 'total_damage': 0, 'total_healing': 0, 'phase_damage': 0, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 460.0, 'skill_attack_speed': 160.0, 'skill_attack_speed_reference': 160.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'技能攻击': 0}, 'window_seconds': 12.75, 'window_healing': 0, 'window_dps': 0.0, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '050437aa84531138011a990d1a82d85055910aa092d43854a0dfeeb08a968ae0'}, {'pair_id': '088-hidden-checkbox-amiya-E0-S1-empty-target-reference', 'widget_checked': True, 'control_display_source': 'hidden natural-SP checkbox; actual QPlainTextEdit object JSON target_windows=[]', 'input': {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0, 'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0, 'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': [], 'operator': 'char_002_amiya', 'skill': 1, 'elite': 0, 'level': 50, 'skill_rank': 7, 'timing_mode': 'continuous', 'timing': {'target_windows': []}, 'continuous_attacks': True}, 'required_source_contract': 'E0 no emotion-absorption attack credit; true/false changes existing reference enabled flag, not actual native clock or damage supply', 'base_attack': 'omitted; actual read-only cultivation auto-calculated', 'UI_actual_execution': False, 'section': 88, 'expected_public_projection': {'attack': 460.0, 'total_damage': 0, 'components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'timing_reference': 'continuous interval conditional reference; native acquisition/release/impact unverified'}], 'attack_speed': 160.0, 'base_attack_speed': 100.0, 'interval_seconds': 1.0, 'timing': {'mode': 'continuous', 'fps': 30, 'streams': [], 'window_convention': '[开始帧,结束帧)，已锁定目标离开范围不取消弹体；消失另行取消', 'scenario_provided': True, 'target_scope_notes': [], 'complete': False, 'notes': ['常规攻击按30Hz逐帧调度；动画事件参考值不等于已核实的客户端攻击模板。', '只在缩短到小于动画长度时压缩常规动画；特殊循环动画、多段事件、弹道脚本仍需单独校准。'], 'recharge_streams': [], 'phase_clock_unbound': True, 'resource_and_damage_shared_clock': False}, 'total_healing': 0, 'attack_speed_reference': 160.0, 'base_attack_speed_reference': 100.0, 'amiya_continuous_reference': {'operator_id': 'char_002_amiya', 'skill_number': 1, 'enemy_source_excluded': True, 'declared_target_lifetime_seconds': None, 'declared_target_windows_seconds': [], 'per_hit_damage_reference': 460.0, 'parameter_clock_reference': {'initial_seconds': 22.0, 'duration_seconds': 30.0, 'recharge_seconds': 32.0, 'cycle_seconds': 62.0, 'total_damage': 0, 'phase_damage': 0, 'cycle_damage': 0, 'cycle_dps': 0.0, 'cycle_healing': 0, 'cycle_hps': 0.0, 'window_damage': 0, 'window_dps': 0.0}, 'cast_reference': {'enemy_source_excluded': True, 'source_possible': False, 'observation_seconds': 30.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'times_seconds': []}]}, 'window_reference': {'enemy_source_excluded': True, 'source_possible': False, 'observation_seconds': 12.75, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'times_seconds': []}]}, 'recharge_reference': {'enemy_source_excluded': True, 'source_possible': False, 'observation_seconds': 32.0, 'conditional_components': [{'name': '技能攻击', 'damage_type': 'magic', 'hits': 0, 'per_hit': 460.0, 'total': 0, 'source_unit': 'operator', 'times_seconds': []}]}, 'natural_sp_rate_parameter': 1.0, 'required_sp_parameter': 32, 'natural_only_recharge_seconds_reference': 32.0, 'attack_sp_per_attack_parameter': 0, 'attack_sp_enabled_in_reference': True, 'actual_acquisition_times_seconds': None, 'actual_impact_times_seconds': None, 'actual_recharge_seconds': None, 'actual_cycle_seconds': None, 'native_clock_binding_verified': False, 'initial_scope': 'existing independent pre-cast reference unchanged', 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'source_selectors': ['character_table.char_002_amiya.skills[0].skillId', 'character_table.char_002_amiya.talents[0].candidates', 'character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime', 'skill_table.skcom_magic_rage[3].levels[*]']}, 'estimate': {'training': {'elite': 0, 'level': 50, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'base_stats': {'hp': 1158, 'attack': 460.0, 'defense': 81, 'resistance': 10.0, 'redeploy_seconds': 70.0, 'attack_speed': 100.0, 'attack_speed_reference': 100.0, 'block_count': 1.0}, 'skill': {'name': '战术咏唱·γ型', 'initial_seconds': 22.0, 'recharge_seconds': None, 'cycle_seconds': None, 'duration_seconds': 30.0, 'total_damage': 0, 'total_healing': 0, 'phase_damage': 0, 'phase_healing': 0, 'cycle_dps': None, 'cycle_hps': None, 'cycle_damage': None, 'cycle_healing': None, 'skill_attack': 460.0, 'skill_attack_speed': 160.0, 'skill_attack_speed_reference': 160.0, 'sp_recovery_per_second': 1.0, 'mode': 'timed', 'hit_counts': {'技能攻击': 0}, 'window_seconds': 12.75, 'window_healing': 0, 'window_dps': 0.0, 'window_hps': 0.0}}}, 'saved_result_full_json_sha256': '131bd6659877d119169cf3ca024b167261ad63c70401e939ddd18e09ad53ecd0'}]
            window.run.state={**window.run.state,'operators':{},'config':{}}
            window.use_run_training.setChecked(False);window.sync_run_config()
            window.auto_relics.setChecked(False)
            window.target_enemy.setCurrentIndex(0)
            window.defense.setValue(0);window.resistance.setValue(0)
            window.cooperative.setChecked(False);window.fragile.setChecked(False)
            window.deployment_elapsed.setValue(0);window.healing_targets.setValue(1)
            window.limit_window.setChecked(True)
            window.target_buff_test.setChecked(False)
            anchors090={}
            for row090 in rows090:
                requested090=row090['input'];owner090=requested090['operator'];skill090=requested090['skill']
                reset_owner_options(owner090)
                train(owner090,{key:requested090[key] for key in
                    ('elite','level','potential','trust','module_id','module_level')},
                    {str(skill090):requested090['skill_rank']})
                assert window.skill.findData(skill090)>=0
                window.skill.setCurrentIndex(window.skill.findData(skill090))
                window.frame_timing.setChecked(requested090['timing_mode']=='frames')
                window.window_seconds.setValue(requested090['window_seconds'])
                window.continuous_attacks.setChecked(requested090['continuous_attacks'])
                assert type(window.continuous_attacks.isChecked()) is bool
                assert window.continuous_attacks.isChecked() is requested090['continuous_attacks']
                window.damage_technical.setChecked(False)
                window.normal_animation_reference.setCurrentIndex(0)
                window.skill_animation_reference.setCurrentIndex(0)
                relics(requested090['relic_ids'])
                window.timing_scenario.setPlainText(json.dumps(requested090['timing']) if 'timing' in requested090 else '')
                for key090,_label090,_default090,_maximum090,skills090 in OPTIONS.get(owner090,[]):
                    widget090=option_widgets[(owner090,key090)]
                    if key090 in requested090:
                        value090=requested090[key090]
                        widget090.setChecked(value090) if isinstance(widget090,QCheckBox) else widget090.setValue(value090)
                    if row090['section']==86 and key090==row090['field']:
                        assert isinstance(widget090,QCheckBox)
                        widget090.setChecked(row090['widget_checked'])
                        assert widget090.isChecked() is row090['widget_checked']
                        assert (skill090 in skills090) is row090['field_serialized']
                        assert widget090.isVisible() is row090['field_serialized']
                assert window.training_conditions()=={key:requested090[key] for key in
                    ('elite','level','trust','potential','module_id','module_level')}
                assert window.skill_rank_value()==requested090['skill_rank']
                assert window.normal_animation_reference.currentData() is None
                assert window.skill_animation_reference.currentData() is None
                assert '自动计算' in window.attack.text()
                profile_case090=row090;profile_trace090=[]
                before_click090=dict(entry_counts090)
                result090=click_result()
                after_click090=dict(entry_counts090)
                assert entries_delta090(before_click090,after_click090).get('calculate_damage',0)==1
                raw090=window.damage_result['scenario']
                raw_native_before090=native090(raw090)
                pending_state090={'section':row090['section'],'pair_id':row090['pair_id'],
                    'widget_checked':row090['widget_checked'],'scenario':_copy090.deepcopy(raw090),
                    'scenario_native':raw_native_before090,'result':_copy090.deepcopy(result090),
                    'result_native':native090(result090),'reports':{},
                    'actual_same_call_readonly_trace':_copy090.deepcopy(profile_trace090),'passed':False}
                actual_states090.append(pending_state090)
                for key090,value090 in requested090.items():
                    assert native090(raw090[key090])==native090(value090),(row090['pair_id'],key090,raw090[key090],value090)
                assert 'base_attack' not in raw090
                if row090['section']==86:
                    if row090['field_serialized']:
                        assert type(raw090[row090['field']]) is bool
                        assert raw090[row090['field']] is row090['widget_checked']
                    else:assert row090['field'] not in raw090
                else:
                    from rouge.catalog import catalog as catalog090
                    sp090=catalog090()['operators'][owner090]['skills'][skill090-1]['levels'][requested090['skill_rank']-1]['sp_type']
                    assert window.continuous_attacks.isVisible() is (owner090 in catalog090()['operators'] and sp090 in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME'))
                    assert window.window_seconds.value()==12.75
                    if 'timing' in requested090:
                        assert json.loads(window.timing_scenario.toPlainText())==requested090['timing']
                assert strict_json(projection090(result090))==strict_json(row090['expected_public_projection']),row090['pair_id']
                full_native090=native090(result090)
                from rouge.estimate import format_estimate as estimate090
                reports090={'estimate':estimate090(result090),'default':format_report(result090),
                    'technical':format_report(result090,technical=True)}
                pending_state090['reports']=reports090
                assert reports090['estimate']==reports090['default']
                assert window.damage_text.toPlainText()==reports090['default'].replace(chr(160),' ')
                window.damage_technical.setChecked(True);app.processEvents()
                assert window.damage_text.toPlainText()==reports090['technical'].replace(chr(160),' ')
                window.damage_technical.setChecked(False);app.processEvents()
                assert window.damage_text.toPlainText()==reports090['default'].replace(chr(160),' ')
                assert native090(result090)==full_native090
                assert native090(window.damage_result['scenario'])==raw_native_before090
                pair090=row090['pair_id']
                if row090['section']==86:
                    if not row090['widget_checked']:anchors090[pair090]=_copy090.deepcopy(result090)
                    elif row090['kind']=='hidden' or pair090=='qualification:mizuki-E1':
                        assert strict_json(result090)==strict_json(anchors090[pair090])
                    if row090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal':
                        normal_entries090=[event for event in profile_trace090 if event['event']=='actual_same_call_normal_plan_entry']
                        returned090=[event for event in profile_trace090 if event['event']=='actual_same_call_Combat_calculate_return']
                        assert len(normal_entries090)==1 and len(returned090)==1
                        assert returned090[0]['normal_plan_return_not_none'] is True
                        assert returned090[0]['actual_ranged_condition_consumed'] is True
                        assert returned090[0]['actual_selected_note_max_cnt']==12
                pending_state090.update({
                    'actual_entries':entries_delta090(before_click090,entry_counts090),
                    'explicit_three_text_requests':3,'passed':True})
                checks.append({'scope':'actual_boolean_checkbox_and_public_readonly_source090' if row090['section']==86 else
                    'actual_continuous_checkbox_and_JSON_editor_source088','section':row090['section'],
                    'pair_id':pair090,'operator':owner090,'skill':skill090,'checked':row090['widget_checked'],
                    'three_texts_match_own_result':True,'native_game_clock_verified':False,'passed':True})
                new_counts090[row090['section']]+=1
                profile_case090=None

            # Actual Back controls, no invented generic numbered Skill or additional damage call.
            train('char_196_sunbr',{'elite':2,'level':60,'trust':100,'potential':1,'module_id':None,'module_level':0})
            window.frame_timing.setChecked(True)
            for number090 in (1,2):
                window.skill.setCurrentIndex(window.skill.findData(number090))
                window.sync_animation_references('char_196_sunbr',number090)
                for role090,combo090 in (('normal',window.normal_animation_reference),('skill',window.skill_animation_reference)):
                    assert combo090.findData('char_196_sunbr:Back:Skill')==-1
                    found090=combo090.findData('char_196_sunbr:Back:Attack')
                    assert found090>0
                    combo090.setCurrentIndex(found090)
                    assert combo090.currentData()=='char_196_sunbr:Back:Attack'
                    assert combo090.isVisible()
                    assert combo090.currentText()=='背面 · 普通攻击 · 出手16帧 / 动画40帧'
                    checks.append({'scope':'actual_Back_Attack_combo_and_unnumbered_Skill_exclusion087',
                        'section':87,'operator':'char_196_sunbr','skill':number090,'combo':role090,
                        'selected_id':combo090.currentData(),'generic_Skill_absent':True,
                        'native_animation_binding_verified':False,'explicit_damage_button_clicks':0,
                        'real_combo_changes_may_trigger_automatic_calculations':True,'passed':True})
                    new_counts090[87]+=1
                    combo090.setCurrentIndex(0)

            # Exact historical public saved-state copies consumed by the existing window only.
            saved89_states090=[{'saved_sequence': 19, 'label': 'None unread retained', 'observed': {'operators': [], 'crew_count': None}, 'observed_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'operators'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'NoneType', 'value': None}]]}, 'state': {'id': 'a4235047-4005-4d90-a40a-e46fda5d3feb', 'started_at': 1791431644.4410188, 'last_read': 1791431646.4410188, 'operators': {'mechanist': {'id': 'mechanist', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.4410188, 'level': 1791431645.4410188}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.4410188, 'present': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}, 'char_151_myrtle': {'id': 'char_151_myrtle', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.4410188, 'level': 1791431645.4410188}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.4410188, 'present': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}}, 'crew_count': 2, 'selected_operator': None, 'relics': {}, 'relic_count': None, 'bar_signature': None, 'inventory_verified': False, 'inventory_confirmed_at': None, 'relic_icon_memory': None, 'history': [{'at': 1791431645.4410188, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431645.4410188, 'kind': 'operator_updated', 'id': 'char_151_myrtle', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}, 'last_node_content': None, 'node_contents': [], 'notice': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}, 'state_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'a4235047-4005-4d90-a40a-e46fda5d3feb'}], [{'type': 'str', 'value': 'started_at'}, {'type': 'float', 'hex': '0x1.ab1c4f71c39a7p+30'}], [{'type': 'str', 'value': 'last_read'}, {'type': 'float', 'hex': '0x1.ab1c4f79c39a7p+30'}], [{'type': 'str', 'value': 'operators'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}]]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 2}], [{'type': 'str', 'value': 'selected_operator'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relics'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'relic_count'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'bar_signature'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'inventory_verified'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'inventory_confirmed_at'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relic_icon_memory'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'history'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c39a7p+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}]}], [{'type': 'str', 'value': 'resources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'tactical_tools'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'config'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'maps'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'last_node_content'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'node_contents'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'notice'}, {'type': 'str', 'value': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}]]}, 'record_original_json_sha256': 'e6bec8bd0f14af4eb61eb539994f58cc0dfa696cff832a9884a750bc0d4c91b2', 'crew_observed_type': 'NoneType', 'crew_stored_type': 'int', 'crew_stored_value': 2, 'members': {'mechanist': {'present': True, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}, 'char_151_myrtle': {'present': True, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}}, 'producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR': True}, {'saved_sequence': 9, 'label': 'False unread retained', 'observed': {'operators': [], 'crew_count': False}, 'observed_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'operators'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'bool', 'value': False}]]}, 'state': {'id': '13be8a27-b4ba-484e-b55b-269058c415a0', 'started_at': 1791431644.3806927, 'last_read': 1791431646.3806927, 'operators': {'mechanist': {'id': 'mechanist', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.3806927, 'level': 1791431645.3806927}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.3806927, 'present': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}}, 'crew_count': 1, 'selected_operator': None, 'relics': {}, 'relic_count': None, 'bar_signature': None, 'inventory_verified': False, 'inventory_confirmed_at': None, 'relic_icon_memory': None, 'history': [{'at': 1791431645.3806927, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}, 'last_node_content': None, 'node_contents': [], 'notice': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}, 'state_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': '13be8a27-b4ba-484e-b55b-269058c415a0'}], [{'type': 'str', 'value': 'started_at'}, {'type': 'float', 'hex': '0x1.ab1c4f7185d45p+30'}], [{'type': 'str', 'value': 'last_read'}, {'type': 'float', 'hex': '0x1.ab1c4f7985d45p+30'}], [{'type': 'str', 'value': 'operators'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f7585d45p+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f7585d45p+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f7585d45p+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}]]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 1}], [{'type': 'str', 'value': 'selected_operator'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relics'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'relic_count'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'bar_signature'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'inventory_verified'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'inventory_confirmed_at'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relic_icon_memory'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'history'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f7585d45p+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}]}], [{'type': 'str', 'value': 'resources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'tactical_tools'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'config'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'maps'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'last_node_content'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'node_contents'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'notice'}, {'type': 'str', 'value': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}]]}, 'record_original_json_sha256': '674e0d1d3ecf51525a34f2529c22020f367f6b17d27f450c55ffaaa2940dcbe3', 'crew_observed_type': 'bool', 'crew_stored_type': 'int', 'crew_stored_value': 1, 'members': {'mechanist': {'present': True, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}}, 'producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR': True}, {'saved_sequence': 3, 'label': 'True unread preserves other member', 'observed': {'operators': [{'id': 'mechanist', 'scope': 'run', 'fields': {'level': 2}, 'skill_ranks': {}}, {'id': 'mechanist', 'scope': 'run', 'fields': {'trust': 25}, 'skill_ranks': {}}], 'crew_count': True}, 'observed_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'operators'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 2}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'trust'}, {'type': 'int', 'value': 25}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}]]}]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'bool', 'value': True}]]}, 'state': {'id': '98dae00e-7bdb-4927-98f8-5fecc33ec965', 'started_at': 1791431644.3028178, 'last_read': 1791431646.3028178, 'operators': {'mechanist': {'id': 'mechanist', 'scope': 'run', 'fields': {'elite': 0, 'level': 2, 'trust': 25}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.3028178, 'level': 1791431646.3028178, 'trust': 1791431646.3028178}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431646.3028178, 'present': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}, 'char_151_myrtle': {'id': 'char_151_myrtle', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.3028178, 'level': 1791431645.3028178}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.3028178, 'present': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}}, 'crew_count': 2, 'selected_operator': None, 'relics': {}, 'relic_count': None, 'bar_signature': None, 'inventory_verified': False, 'inventory_confirmed_at': None, 'relic_icon_memory': None, 'history': [{'at': 1791431645.3028178, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431645.3028178, 'kind': 'operator_updated', 'id': 'char_151_myrtle', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431646.3028178, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'level': 2}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431646.3028178, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'trust': 25}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}, 'last_node_content': None, 'node_contents': [], 'notice': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}, 'state_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': '98dae00e-7bdb-4927-98f8-5fecc33ec965'}], [{'type': 'str', 'value': 'started_at'}, {'type': 'float', 'hex': '0x1.ab1c4f713615ep+30'}], [{'type': 'str', 'value': 'last_read'}, {'type': 'float', 'hex': '0x1.ab1c4f793615ep+30'}], [{'type': 'str', 'value': 'operators'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 2}], [{'type': 'str', 'value': 'trust'}, {'type': 'int', 'value': 25}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f753615ep+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f793615ep+30'}], [{'type': 'str', 'value': 'trust'}, {'type': 'float', 'hex': '0x1.ab1c4f793615ep+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f793615ep+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f753615ep+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f753615ep+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f753615ep+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}]]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 2}], [{'type': 'str', 'value': 'selected_operator'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relics'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'relic_count'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'bar_signature'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'inventory_verified'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'inventory_confirmed_at'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relic_icon_memory'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'history'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f753615ep+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f753615ep+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f793615ep+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 2}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f793615ep+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'trust'}, {'type': 'int', 'value': 25}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}]}], [{'type': 'str', 'value': 'resources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'tactical_tools'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'config'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'maps'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'last_node_content'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'node_contents'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'notice'}, {'type': 'str', 'value': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}]]}, 'record_original_json_sha256': '095b8b81150943454ab1a185709008c7cf01457be961414814dd6f512115b823', 'crew_observed_type': 'bool', 'crew_stored_type': 'int', 'crew_stored_value': 2, 'members': {'mechanist': {'present': True, 'fields': {'elite': 0, 'level': 2, 'trust': 25}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}, 'char_151_myrtle': {'present': True, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}}, 'producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR': True}, {'saved_sequence': 22, 'label': 'integer0 complete empty', 'observed': {'operators': [], 'crew_count': 0}, 'observed_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'operators'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 0}]]}, 'state': {'id': '23747546-bafa-4d8d-8098-8611b8fce114', 'started_at': 1791431644.4463258, 'last_read': 1791431646.4463258, 'operators': {'mechanist': {'id': 'mechanist', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.4463258, 'level': 1791431645.4463258}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.4463258, 'present': False, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}, 'char_151_myrtle': {'id': 'char_151_myrtle', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.4463258, 'level': 1791431645.4463258}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.4463258, 'present': False, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}}, 'crew_count': 0, 'selected_operator': None, 'relics': {}, 'relic_count': None, 'bar_signature': None, 'inventory_verified': False, 'inventory_confirmed_at': None, 'relic_icon_memory': None, 'history': [{'at': 1791431645.4463258, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431645.4463258, 'kind': 'operator_updated', 'id': 'char_151_myrtle', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431646.4463258, 'kind': 'operator_no_longer_present', 'id': 'mechanist'}, {'at': 1791431646.4463258, 'kind': 'operator_no_longer_present', 'id': 'char_151_myrtle'}], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}, 'last_node_content': None, 'node_contents': [], 'notice': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}, 'state_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': '23747546-bafa-4d8d-8098-8611b8fce114'}], [{'type': 'str', 'value': 'started_at'}, {'type': 'float', 'hex': '0x1.ab1c4f71c909ap+30'}], [{'type': 'str', 'value': 'last_read'}, {'type': 'float', 'hex': '0x1.ab1c4f79c909ap+30'}], [{'type': 'str', 'value': 'operators'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}]]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'selected_operator'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relics'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'relic_count'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'bar_signature'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'inventory_verified'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'inventory_confirmed_at'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relic_icon_memory'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'history'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f75c909ap+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f79c909ap+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_no_longer_present'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f79c909ap+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_no_longer_present'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}]]}]}], [{'type': 'str', 'value': 'resources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'tactical_tools'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'config'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'maps'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'last_node_content'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'node_contents'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'notice'}, {'type': 'str', 'value': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}]]}, 'record_original_json_sha256': '6c756b20876924a72bbc9ba64c032c4d4c25fefbc20abd2823a2e1da0003438d', 'crew_observed_type': 'int', 'crew_stored_type': 'int', 'crew_stored_value': 0, 'members': {'mechanist': {'present': False, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}, 'char_151_myrtle': {'present': False, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}}, 'producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR': True}, {'saved_sequence': 6, 'label': 'integer1 complete singleton', 'observed': {'operators': [{'id': 'mechanist', 'scope': 'run', 'fields': {'level': 2}, 'skill_ranks': {}}, {'id': 'mechanist', 'scope': 'run', 'fields': {'trust': 25}, 'skill_ranks': {}}], 'crew_count': 1}, 'observed_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'operators'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 2}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'trust'}, {'type': 'int', 'value': 25}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}]]}]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 1}]]}, 'state': {'id': 'f6a0fed5-d72d-455a-ad10-307ae94c041f', 'started_at': 1791431644.3715315, 'last_read': 1791431646.3715315, 'operators': {'mechanist': {'id': 'mechanist', 'scope': 'run', 'fields': {'elite': 0, 'level': 2, 'trust': 25}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.3715315, 'level': 1791431646.3715315, 'trust': 1791431646.3715315}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431646.3715315, 'present': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}, 'char_151_myrtle': {'id': 'char_151_myrtle', 'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'char_buff_ids': [], 'char_buffs_complete': False, 'invalid_fields': [], 'invalid_skill_ranks': [], 'sources': {}, 'field_times': {'elite': 1791431645.3715315, 'level': 1791431645.3715315}, 'skill_times': {}, 'merged_from_pages': True, 'captured_at': 1791431645.3715315, 'present': False, 'char_buff_absent_ids': [], 'char_buff_pending_ids': []}}, 'crew_count': 1, 'selected_operator': None, 'relics': {}, 'relic_count': None, 'bar_signature': None, 'inventory_verified': False, 'inventory_confirmed_at': None, 'relic_icon_memory': None, 'history': [{'at': 1791431645.3715315, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431645.3715315, 'kind': 'operator_updated', 'id': 'char_151_myrtle', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431646.3715315, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'level': 2}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431646.3715315, 'kind': 'operator_updated', 'id': 'mechanist', 'fields': {'trust': 25}, 'skill_ranks': {}, 'advanced': None, 'recruitment_kind': None}, {'at': 1791431646.3715315, 'kind': 'operator_no_longer_present', 'id': 'char_151_myrtle'}], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}, 'last_node_content': None, 'node_contents': [], 'notice': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}, 'state_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'f6a0fed5-d72d-455a-ad10-307ae94c041f'}], [{'type': 'str', 'value': 'started_at'}, {'type': 'float', 'hex': '0x1.ab1c4f717c72cp+30'}], [{'type': 'str', 'value': 'last_read'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}], [{'type': 'str', 'value': 'operators'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 2}], [{'type': 'str', 'value': 'trust'}, {'type': 'int', 'value': 25}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f757c72cp+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}], [{'type': 'str', 'value': 'trust'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'scope'}, {'type': 'str', 'value': 'run'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'char_buff_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buffs_complete'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'invalid_fields'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'invalid_skill_ranks'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'sources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'field_times'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'float', 'hex': '0x1.ab1c4f757c72cp+30'}], [{'type': 'str', 'value': 'level'}, {'type': 'float', 'hex': '0x1.ab1c4f757c72cp+30'}]]}], [{'type': 'str', 'value': 'skill_times'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'merged_from_pages'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'captured_at'}, {'type': 'float', 'hex': '0x1.ab1c4f757c72cp+30'}], [{'type': 'str', 'value': 'present'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'char_buff_absent_ids'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'char_buff_pending_ids'}, {'type': 'list', 'items': []}]]}]]}], [{'type': 'str', 'value': 'crew_count'}, {'type': 'int', 'value': 1}], [{'type': 'str', 'value': 'selected_operator'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relics'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'relic_count'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'bar_signature'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'inventory_verified'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'inventory_confirmed_at'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'relic_icon_memory'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'history'}, {'type': 'list', 'items': [{'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f757c72cp+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f757c72cp+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'elite'}, {'type': 'int', 'value': 0}], [{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 1}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'level'}, {'type': 'int', 'value': 2}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_updated'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'mechanist'}], [{'type': 'str', 'value': 'fields'}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'trust'}, {'type': 'int', 'value': 25}]]}], [{'type': 'str', 'value': 'skill_ranks'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'advanced'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'recruitment_kind'}, {'type': 'NoneType', 'value': None}]]}, {'type': 'dict', 'items': [[{'type': 'str', 'value': 'at'}, {'type': 'float', 'hex': '0x1.ab1c4f797c72cp+30'}], [{'type': 'str', 'value': 'kind'}, {'type': 'str', 'value': 'operator_no_longer_present'}], [{'type': 'str', 'value': 'id'}, {'type': 'str', 'value': 'char_151_myrtle'}]]}]}], [{'type': 'str', 'value': 'resources'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'tactical_tools'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'config'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'maps'}, {'type': 'dict', 'items': []}], [{'type': 'str', 'value': 'last_node_content'}, {'type': 'NoneType', 'value': None}], [{'type': 'str', 'value': 'node_contents'}, {'type': 'list', 'items': []}], [{'type': 'str', 'value': 'notice'}, {'type': 'str', 'value': '同一局信息持续累积并保存；开始另一局时请手动清空本局读取。'}]]}, 'record_original_json_sha256': 'bfae97ba93b92a868908f6506da20e665ebed8f48dc963e6b51a4e5f05f50625', 'crew_observed_type': 'int', 'crew_stored_type': 'int', 'crew_stored_value': 1, 'members': {'mechanist': {'present': True, 'fields': {'elite': 0, 'level': 2, 'trust': 25}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}, 'char_151_myrtle': {'present': False, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}, 'sources': {}, 'scope': 'run'}}, 'producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR': True}]
            expected89_contract090={(row['saved_sequence'],row['use_run_training']):row for row in [{'saved_sequence': 19, 'saved_label': 'None unread retained', 'use_run_training': False, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist', 'char_151_myrtle'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': True}]]}, 'stored_crew_native': {'type': 'int', 'value': 2}, 'summary_crew_line_expected': '本局队伍：当前已识别 2 / 2 人', 'current_state_source_expected': 'account_fixture', 'current_fields_expected': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {'1': 10, '2': 10, '3': 10}, 'run_confirmed_fields_expected_if_run': None, 'training_conditions_expected_after_update_operator': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1, 2, 3], 'selected_skill_expected': 1, 'skill_rank_expected': 10, 'rank_label_expected': '专精 3（读取）', 'elite_label_expected': '精英 2', 'trust_label_expected': '100%（读取）', 'potential_label_expected': '1', 'module_label_expected': '未装备模组', 'levels_widget_max_expected': 90, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 19, 'saved_label': 'None unread retained', 'use_run_training': True, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist', 'char_151_myrtle'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': True}]]}, 'stored_crew_native': {'type': 'int', 'value': 2}, 'summary_crew_line_expected': '本局队伍：当前已识别 2 / 2 人', 'current_state_source_expected': 'run', 'current_fields_expected': {'elite': 0, 'level': 1, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {}, 'run_confirmed_fields_expected_if_run': ['elite', 'level'], 'training_conditions_expected_after_update_operator': {'elite': 0, 'level': 1, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1], 'selected_skill_expected': 1, 'skill_rank_expected': 7, 'rank_label_expected': '等级 7（未确认，档案预览）', 'elite_label_expected': '精英 0', 'trust_label_expected': '100%（读取）（账号档案参考，本局未确认）', 'potential_label_expected': '1（账号档案参考，本局未确认）', 'module_label_expected': '未装备模组（账号档案参考，本局未确认）', 'levels_widget_max_expected': 50, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 9, 'saved_label': 'False unread retained', 'use_run_training': False, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'NoneType', 'value': None}]]}, 'stored_crew_native': {'type': 'int', 'value': 1}, 'summary_crew_line_expected': '本局队伍：当前已识别 1 / 1 人', 'current_state_source_expected': 'account_fixture', 'current_fields_expected': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {'1': 10, '2': 10, '3': 10}, 'run_confirmed_fields_expected_if_run': None, 'training_conditions_expected_after_update_operator': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1, 2, 3], 'selected_skill_expected': 1, 'skill_rank_expected': 10, 'rank_label_expected': '专精 3（读取）', 'elite_label_expected': '精英 2', 'trust_label_expected': '100%（读取）', 'potential_label_expected': '1', 'module_label_expected': '未装备模组', 'levels_widget_max_expected': 90, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 9, 'saved_label': 'False unread retained', 'use_run_training': True, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'NoneType', 'value': None}]]}, 'stored_crew_native': {'type': 'int', 'value': 1}, 'summary_crew_line_expected': '本局队伍：当前已识别 1 / 1 人', 'current_state_source_expected': 'run', 'current_fields_expected': {'elite': 0, 'level': 1, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {}, 'run_confirmed_fields_expected_if_run': ['elite', 'level'], 'training_conditions_expected_after_update_operator': {'elite': 0, 'level': 1, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1], 'selected_skill_expected': 1, 'skill_rank_expected': 7, 'rank_label_expected': '等级 7（未确认，档案预览）', 'elite_label_expected': '精英 0', 'trust_label_expected': '100%（读取）（账号档案参考，本局未确认）', 'potential_label_expected': '1（账号档案参考，本局未确认）', 'module_label_expected': '未装备模组（账号档案参考，本局未确认）', 'levels_widget_max_expected': 50, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 3, 'saved_label': 'True unread preserves other member', 'use_run_training': False, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist', 'char_151_myrtle'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': True}]]}, 'stored_crew_native': {'type': 'int', 'value': 2}, 'summary_crew_line_expected': '本局队伍：当前已识别 2 / 2 人', 'current_state_source_expected': 'account_fixture', 'current_fields_expected': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {'1': 10, '2': 10, '3': 10}, 'run_confirmed_fields_expected_if_run': None, 'training_conditions_expected_after_update_operator': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1, 2, 3], 'selected_skill_expected': 1, 'skill_rank_expected': 10, 'rank_label_expected': '专精 3（读取）', 'elite_label_expected': '精英 2', 'trust_label_expected': '100%（读取）', 'potential_label_expected': '1', 'module_label_expected': '未装备模组', 'levels_widget_max_expected': 90, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 3, 'saved_label': 'True unread preserves other member', 'use_run_training': True, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist', 'char_151_myrtle'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': True}]]}, 'stored_crew_native': {'type': 'int', 'value': 2}, 'summary_crew_line_expected': '本局队伍：当前已识别 2 / 2 人', 'current_state_source_expected': 'run', 'current_fields_expected': {'elite': 0, 'level': 2, 'trust': 25, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {}, 'run_confirmed_fields_expected_if_run': ['elite', 'level', 'trust'], 'training_conditions_expected_after_update_operator': {'elite': 0, 'level': 2, 'trust': 25, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1], 'selected_skill_expected': 1, 'skill_rank_expected': 7, 'rank_label_expected': '等级 7（未确认，档案预览）', 'elite_label_expected': '精英 0', 'trust_label_expected': '25%（读取）', 'potential_label_expected': '1（账号档案参考，本局未确认）', 'module_label_expected': '未装备模组（账号档案参考，本局未确认）', 'levels_widget_max_expected': 50, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 22, 'saved_label': 'integer0 complete empty', 'use_run_training': False, 'owner_read_back': 'mechanist', 'roster_expected': [], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': False}]]}, 'stored_crew_native': {'type': 'int', 'value': 0}, 'summary_crew_line_expected': '本局队伍：当前已识别 0 / 0 人', 'current_state_source_expected': 'account_fixture', 'current_fields_expected': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {'1': 10, '2': 10, '3': 10}, 'run_confirmed_fields_expected_if_run': None, 'training_conditions_expected_after_update_operator': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1, 2, 3], 'selected_skill_expected': 1, 'skill_rank_expected': 10, 'rank_label_expected': '专精 3（读取）', 'elite_label_expected': '精英 2', 'trust_label_expected': '100%（读取）', 'potential_label_expected': '1', 'module_label_expected': '未装备模组', 'levels_widget_max_expected': 90, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 22, 'saved_label': 'integer0 complete empty', 'use_run_training': True, 'owner_read_back': 'mechanist', 'roster_expected': [], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': False}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': False}]]}, 'stored_crew_native': {'type': 'int', 'value': 0}, 'summary_crew_line_expected': '本局队伍：当前已识别 0 / 0 人', 'current_state_source_expected': 'account_fixture', 'current_fields_expected': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {'1': 10, '2': 10, '3': 10}, 'run_confirmed_fields_expected_if_run': None, 'training_conditions_expected_after_update_operator': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1, 2, 3], 'selected_skill_expected': 1, 'skill_rank_expected': 10, 'rank_label_expected': '专精 3（读取）', 'elite_label_expected': '精英 2', 'trust_label_expected': '100%（读取）', 'potential_label_expected': '1', 'module_label_expected': '未装备模组', 'levels_widget_max_expected': 90, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 6, 'saved_label': 'integer1 complete singleton', 'use_run_training': False, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': False}]]}, 'stored_crew_native': {'type': 'int', 'value': 1}, 'summary_crew_line_expected': '本局队伍：当前已识别 1 / 1 人', 'current_state_source_expected': 'account_fixture', 'current_fields_expected': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {'1': 10, '2': 10, '3': 10}, 'run_confirmed_fields_expected_if_run': None, 'training_conditions_expected_after_update_operator': {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1, 2, 3], 'selected_skill_expected': 1, 'skill_rank_expected': 10, 'rank_label_expected': '专精 3（读取）', 'elite_label_expected': '精英 2', 'trust_label_expected': '100%（读取）', 'potential_label_expected': '1', 'module_label_expected': '未装备模组', 'levels_widget_max_expected': 90, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}, {'saved_sequence': 6, 'saved_label': 'integer1 complete singleton', 'use_run_training': True, 'owner_read_back': 'mechanist', 'roster_expected': ['mechanist'], 'member_flags_native': {'type': 'dict', 'items': [[{'type': 'str', 'value': 'mechanist'}, {'type': 'bool', 'value': True}], [{'type': 'str', 'value': 'char_151_myrtle'}, {'type': 'bool', 'value': False}]]}, 'stored_crew_native': {'type': 'int', 'value': 1}, 'summary_crew_line_expected': '本局队伍：当前已识别 1 / 1 人', 'current_state_source_expected': 'run', 'current_fields_expected': {'elite': 0, 'level': 2, 'trust': 25, 'potential': 1, 'module_id': None, 'module_level': 0}, 'current_skill_ranks_expected': {}, 'run_confirmed_fields_expected_if_run': ['elite', 'level', 'trust'], 'training_conditions_expected_after_update_operator': {'elite': 0, 'level': 2, 'trust': 25, 'potential': 1, 'module_id': None, 'module_level': 0}, 'skill_choice_numbers_expected': [1], 'selected_skill_expected': 1, 'skill_rank_expected': 7, 'rank_label_expected': '等级 7（未确认，档案预览）', 'elite_label_expected': '精英 0', 'trust_label_expected': '25%（读取）', 'potential_label_expected': '1（账号档案参考，本局未确认）', 'module_label_expected': '未装备模组（账号档案参考，本局未确认）', 'levels_widget_max_expected': 50, 'no_current_runstate_constructor_apply_or_game_observation_executed': True}]}
            fixture89_090={'fields':{'elite':2,'level':60,'trust':100,'potential':1,'module_id':None,'module_level':0},
                'skill_ranks':{'1':10,'2':10,'3':10}}
            from rouge.run_state import RunState as RunState090
            ctor_apply_before090={key:entry_counts090.get(key,0) for key in ('RunState.__init__','RunState.apply','RunState.load')}
            consumer_records090=[]
            for saved89_090 in saved89_states090:
                for use89_090 in (False,True):
                    window.operator_observations['mechanist']={**_copy090.deepcopy(fixture89_090),'id':'mechanist'}
                    window.operator_observations['char_151_myrtle']={**_copy090.deepcopy(fixture89_090),'id':'char_151_myrtle'}
                    window.run.state=_copy090.deepcopy(saved89_090['state'])
                    replay_before090=native090(window.run.state)
                    expected89_row090=expected89_contract090[(saved89_090['saved_sequence'],use89_090)]
                    window.refresh_operator_overview()
                    window.run_summary.setText(window.run.summary())
                    window.use_run_training.setChecked(use89_090)
                    window.skill_override=False;window.level_override=False;window.display_operator=None
                    window.select_operator('mechanist');window.update_operator(preserve_level=False)
                    member89_090=saved89_090['state']['operators']['mechanist']
                    expected_run89_090=use89_090 and member89_090['present']
                    expected_state89_090={**_copy090.deepcopy(fixture89_090),'id':'mechanist'}
                    if expected_run89_090:
                        expected_state89_090={**fixture89_090,**member89_090,
                            'fields':{**fixture89_090['fields'],**member89_090['fields']},
                            'skill_ranks':member89_090['skill_ranks'],
                            'run_confirmed_fields':list(member89_090['fields'])}
                    assert native090(window.current_operator_state())==native090(expected_state89_090)
                    conditions89_090=window.training_conditions()
                    expected_conditions89_090={key:expected_state89_090['fields'][key] for key in
                        ('elite','level','trust','potential','module_id','module_level')}
                    assert native090(conditions89_090)==native090(expected_conditions89_090)
                    expected_skills89_090=[1] if expected_run89_090 else [1,2,3]
                    assert [window.skill.itemData(i) for i in range(window.skill.count())]==expected_skills89_090
                    assert window.skill.currentData()==1
                    assert window.skill_rank_value()==(7 if expected_run89_090 else 10)
                    for key89_090 in ('elite','trust','potential','module','rank'):
                        assert getattr(window,key89_090).text()==expected89_row090[key89_090+'_label_expected']
                    assert window.level.maximum()==expected89_row090['levels_widget_max_expected']
                    assert expected89_row090['summary_crew_line_expected'] in window.run_summary.text()
                    expected_roster89_090=tuple(op for op,member in saved89_090['state']['operators'].items()
                        if member['present'] and member['scope']!='account')
                    assert window.recruited_operator_ids()==expected_roster89_090
                    assert native090(window.run.state)==replay_before090
                    assert type(window.run.state['crew_count']) is int
                    row89_090={'saved_sequence':saved89_090['saved_sequence'],'use_run_training':use89_090,
                        'training':conditions89_090,'skill':window.skill.currentData(),'rank':window.skill_rank_value(),
                        'readonly_training_labels':{key:getattr(window,key).text() for key in ('elite','trust','potential','module')},
                        'readonly_skill_rank_label':window.rank.text(),'actual_summary':window.run_summary.text(),
                        'actual_roster':list(window.recruited_operator_ids()),'stored_crew_count':window.run.state['crew_count'],
                        'complete_temporary_state_native_unchanged':True,'actual_native_OCR_or_departure_verified':False,
                        'RunState_constructor_or_apply_pipeline_executed_for_replay':False,'passed':True}
                    consumer_records090.append(row89_090)
                    checks.append({'scope':'actual_saved_public_state_readonly_training_consumer089','section':89,**row89_090})
                    new_counts090[89]+=1
            ctor_apply_after090={key:entry_counts090.get(key,0) for key in ctor_apply_before090}
            assert ctor_apply_after090==ctor_apply_before090
            receipt['saved89_actual_window_consumer_records090']=consumer_records090
            receipt['saved89_replay_RunState_entries090']=entries_delta090(ctor_apply_before090,ctor_apply_after090)
            assert new_counts090=={86:44,87:4,88:8,89:10},new_counts090
            receipt['new_actual_main_thread_function_entries090']=entries_delta090(entries090_before,entry_counts090)
            assert receipt['new_actual_main_thread_function_entries090']['calculate_damage']>=52
            receipt['new_explicit_damage_button_requests090']=52
            receipt['new_actual_automatic_damage_function_entries090']=receipt['new_actual_main_thread_function_entries090']['calculate_damage']-52
            receipt['new_explicit_three_text_requests090']=156
            assert len(actual_states090)==52
            assert source_hashes()==source090_before
        finally:
            profile_case090=None;_count_enabled100=previous090
            window.run.state=state090;window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy(account090));assert window.operator_observations is window.account_cache.records
            window.use_run_training.setChecked(use090);window.run_summary.setText(summary090);window.sync_run_config()
            window.animation_previews=animation090;window.animation_preview_key=None
            window.continuous_attacks.setChecked(continuous090)
            window.update_operator();window.timing_scenario.clear();relics([])
            window.damage_technical.setChecked(technical090)
        group090_end=len(checks)
        assert group090_end-group090_start==66
        receipt['actual_additional_checks_086_090']=new_counts090
        receipt['actual_additional_rows090']=66
        receipt['inherited_expected_projection_source090_commit']='5e2ff697402d06e78b239e01f0b4307b50dd5633'
        receipt['maintained_actual_source_files100']=len(before)
        receipt['section090_scope']='Portable provenance verification is a source/tool regression already completed outside Qt. Existing Back Attack combos are exercised; generic Skill remains unnumbered and native binding unknown. No invented provenance Qt control.'
        receipt['section089_scope']='Five original saved synthetic public states replayed as temporary existing MainWindow consumers. Both training modes and present/account fallback are checked; replay is not constructor/apply pipeline, game departure or OCR observation. Startup constructor entries are measured separately.'
        # END FINAL090 ACTUAL SOURCE-BOUND ADDITIONS

        # Final visible screenshot scenario demonstrates the restored explanation.
        train('char_298_susuro',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(1));window.healing_targets.setValue(1)
        low_cost.setChecked(False);relics([]);window.limit_window.setChecked(True)
        window.window_seconds.setValue(10);window.frame_timing.setChecked(False)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        result=calculate_result()
        assert result['total_damage']==0 and result['total_healing']>0
        assert window.damage_result['scenario']['relic_ids']==[]
        assert window.damage_result['scenario']['timing_mode']=='continuous'
        assert '真实友方获取时钟未核验' in window.damage_text.toPlainText()
        checks.append({'scope':'actual_final_visible_friendly_scope_explanation','operator':'char_298_susuro',
            'mode':'continuous','window_seconds':10,'enemy_lifetime_seconds':0,'relic_ids':[],
            'report_contains_friendly_clock_unknown':True,'passed':True})
        receipt['manual_token_attribute_scope']='Public API inputs have related regression coverage; actual UI has no manual all_units effects control'
        receipt['deferred_probes']=[]
        receipt['resolved_problem']={'problem':'friendly scope report explanation was deferred after three historical attempts',
            'independent_diagnosis_source':str(diagnosis_path),'independent_diagnosis_sha256':hashlib.sha256(diagnosis_bytes).hexdigest(),
            'historical_evidence_preserved':'verification/full-045/wine-ui.json; original three failed attempts remain unchanged',
            'prior_tmp_diagnosis':'/tmp/p2-draft50/independent-diagnosis.json unavailable after machine restart; reconstructed from persistent historical receipt',
            'recovery':'Both actual report modes now assert the explicit friendly acquisition clock remains unknown',
            'current_available_probe_passed':True}
        receipt['complete_ui_validation']=False
        receipt['window_scenario']=window.damage_result['scenario']
        receipt['window_result']=window.damage_result['result']
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        calculate_button=next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估')
        calculate_button.click();app.processEvents()
        assert window.damage_result and window.damage_text.toPlainText()
        checks.append({'scope':'actual_calculate_button_click','passed':True})
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        from PySide6.QtGui import QTextCursor
        window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
        assert window.damage_text.find('真实友方获取时钟未核验')
        window.damage_text.ensureCursorVisible();app.processEvents()
        checks.append({'scope':'actual_friendly_scope_text_scrolled_visible_for_screenshot','passed':True})
        screenshot=OUT/'wine-window-100.png'
        assert window.grab().save(str(screenshot))
        receipt['window_screenshot']='wine-window-100.png'
        assert not isolated.joinpath('chat').exists()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process
        checks.append({'scope':'no_external_operations','game_captures':0,'chat_requests':0,'temporary_state':True})
        receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)-(new_end-new_start)-(latest_end-latest_start)-(current_end-current_start)-(next_end-next_start)-(group085_end-group085_start)-(group090_end-group090_start)
        assert receipt['preserved_old_checks']==152,receipt['preserved_old_checks']
        receipt['preserved_full_060_checks']=len(checks)-(new_end-new_start)-(latest_end-latest_start)-(current_end-current_start)-(next_end-next_start)-(group085_end-group085_start)-(group090_end-group090_start)
        assert receipt['preserved_full_060_checks']==231,receipt['preserved_full_060_checks']
        receipt['preserved_full_065_checks']=len(checks)-(latest_end-latest_start)-(current_end-current_start)-(next_end-next_start)-(group085_end-group085_start)-(group090_end-group090_start)
        assert receipt['preserved_full_065_checks']==459,receipt['preserved_full_065_checks']
        receipt['preserved_full_070_checks']=len(checks)-(current_end-current_start)-(next_end-next_start)-(group085_end-group085_start)-(group090_end-group090_start)
        assert receipt['preserved_full_070_checks']==841,receipt['preserved_full_070_checks']
        receipt['preserved_full_075_checks']=len(checks)-(next_end-next_start)-(group085_end-group085_start)-(group090_end-group090_start)
        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']
        receipt['preserved_full_080_checks']=len(checks)-(group085_end-group085_start)-(group090_end-group090_start)
        assert receipt['preserved_full_080_checks']==3063,receipt['preserved_full_080_checks']
        receipt['preserved_full_085_checks']=len(checks)-(group090_end-group090_start)
        assert receipt['preserved_full_085_checks']==4217,receipt['preserved_full_085_checks']
        assert len(checks)==4283,len(checks)
        receipt['total_actual_checks']=len(checks)
        window.close();app.processEvents();window=None
    required_png100=['wine-sown-tile-control-100.png','wine-movement-reference-100.png',
                     'wine-medical-trait-100.png','wine-window-100.png']
    receipt['screenshots100']=[{'file':name,'bytes':(OUT/name).stat().st_size,
        'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest()} for name in required_png100]
    assert len(receipt['screenshots100'])==4 and all(row['bytes']>0 for row in receipt['screenshots100'])
    receipt['passed']=True
    receipt['complete_ui_validation']=True
    receipt['complete_ui_validation_scope']='Only this available actual Wine Qt suite; no native Windows, game capture, private replay or desktop integration certification'
except BaseException as error:
    receipt['complete_ui_validation']=False
    receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    if window is not None:
        try:
            receipt['failure_actual_window']={'operator':window.operator.currentData(),
                'skill':window.skill.currentData(),'visible_report_text':window.damage_text.toPlainText(),
                'technical_checkbox':window.damage_technical.isChecked(),
                'last_calculation':window.damage_result,'timing_text':window.timing_scenario.toPlainText()}
            failure_screenshot=OUT/'wine-ui-failure-100.png'
            if window.grab().save(str(failure_screenshot)):
                receipt['failure_screenshot']=failure_screenshot.name
        except Exception as context_error:
            receipt['failure_context_capture_error']={'type':type(context_error).__name__,'message':str(context_error)}
finally:
    if window is not None:
        window.close()
        if app is not None:app.processEvents()
    receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    after=source_hashes();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
    additional_after100=additional_source100()
    additional_drift100=[n for n in sorted(set(_additional100)|set(additional_after100))
                         if _additional100.get(n)!=additional_after100.get(n)]
    receipt['source_additional_sha256']=_additional100
    receipt['source_additional_sha256_after']=additional_after100
    receipt['source_additional_drift']=additional_drift100
    if additional_drift100:receipt['passed']=False;receipt['complete_ui_validation']=False
    receipt['source_sha256']=before;receipt['source_sha256_after']=after;receipt['source_drift']=drift
    if drift:receipt['passed']=False;receipt['complete_ui_validation']=False
    # BEGIN FINAL090 LOSSLESS NEW STATE OUTPUT
    import gzip as _gzip090
    _statebytes090=json.dumps({'format_version':1,'actual_new_window_states':actual_states090,'expected_UI_state_rows':52,'actual_main_window_execution_only':True,'passed':receipt['passed']},ensure_ascii=False,allow_nan=False).encode('utf-8')
    _statepath090=OUT/'wine-ui-new-states-100.json.gz'
    _statepath090.write_bytes(_gzip090.compress(_statebytes090,mtime=0))
    receipt['new_state_archive090']={'file':_statepath090.name,'bytes':_statepath090.stat().st_size,'sha256':hashlib.sha256(_statepath090.read_bytes()).hexdigest(),'decoded_bytes':len(_statebytes090),'decoded_sha256':hashlib.sha256(_statebytes090).hexdigest(),'records':len(actual_states090)}
    # END FINAL090 LOSSLESS NEW STATE OUTPUT
    (OUT/'wine-ui-100.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    for owner100,name100,original100 in reversed(_restorations100):
        setattr(owner100,name100,original100)
    _timer100.cancel()
    print(json.dumps({'passed':receipt['passed'],'total_actual_checks':receipt.get('total_actual_checks'),
          'elapsed_seconds':receipt['elapsed_seconds'],'receipt':'wine-ui-100.json'},ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
