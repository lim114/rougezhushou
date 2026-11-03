"""Static receiver-to-producer field audit plus saved581 shape; no app imports."""
import ast
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE/'public-schema-085'
sources={name:(PACKAGE/'rouge'/name).read_text().replace('\r\n','\n')for name in
    ('operator_engine.py','enemy_environment.py','haruka_healing_reference.py','uncertain_sources.py','run_modifiers.py')}
def assignment(name,target):
    text=sources[name];tree=ast.parse(text)
    node=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)
        and any(ast.unparse(t)==target for t in n.targets))
    return {'producer_file':'rouge/'+name,'producer_target':target,
        'line':node.lineno,'source_excerpt':ast.get_source_segment(text,node),
        'literal_dict_keys':[k.value for k in node.value.keys if isinstance(k,ast.Constant)]
            if isinstance(node.value,ast.Dict)else None}

estimate=assignment('operator_engine.py',"result['estimate']")
tree=ast.parse(sources['operator_engine.py'])
estimate_node=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)
    and any(ast.unparse(t)=="result['estimate']"for t in n.targets))
skill=next(v for k,v in zip(estimate_node.value.keys,estimate_node.value.values)
    if isinstance(k,ast.Constant)and k.value=='skill')
skill_keys={k.value for k in skill.keys if isinstance(k,ast.Constant)}
assert {'mode','duration_seconds','cycle_seconds','cycle_damage','cycle_healing','skill_attack'}<=skill_keys
stats=assignment('operator_engine.py','self.stats');assert 'attack'in stats['literal_dict_keys']
neural=assignment('operator_engine.py','self.neural_relic_reference')
assert {'periodic_damage_scheduled','preexisting_break_assumed'}<=set(neural['literal_dict_keys'])
redeploy=assignment('operator_engine.py',"result['orchid_redeploy_reference']")
assert {'events_scheduled','native_attachment_verified','actual_retreat_seconds','actual_next_deployment_seconds'}<=set(redeploy['literal_dict_keys'])
unbound=assignment('operator_engine.py',"result['unbound_cast_reference']")
assert {'actual_hit_times_seconds','actual_end_seconds','window_reference'}<=set(unbound['literal_dict_keys'])
external=assignment('operator_engine.py',"result['external_event_reference']")
assert {'actual_event_times_seconds','window_reference'}<=set(external['literal_dict_keys'])
enemy=assignment('enemy_environment.py','enemy')
assert 'level_type'in enemy['literal_dict_keys']and 'id'not in enemy['literal_dict_keys']
healing_tree=ast.parse(sources['haruka_healing_reference.py'])
healing_node=next(n for n in ast.walk(healing_tree)if isinstance(n,ast.Return)and isinstance(n.value,ast.Dict))
healing_keys={k.value for k in healing_node.value.keys if isinstance(k,ast.Constant)}
assert {'actual_target_count','actual_acquisition_times_seconds','native_composition_verified','native_attachment_verified'}<=healing_keys
collision_tree=ast.parse(sources['uncertain_sources.py'])
collision_function=next(n for n in collision_tree.body if isinstance(n,ast.FunctionDef)and n.name=='preserve_unplaced_sources')
collision=next(n for n in ast.walk(collision_function)if isinstance(n,ast.Return)and isinstance(n.value,ast.Dict))
assert 'collision_clock_verified'in {k.value for k in collision.value.keys if isinstance(k,ast.Constant)}

failure=HERE/'public-schema-resume085-failure.json.gz'
raw=failure.read_bytes();assert hashlib.sha256(raw).hexdigest()=='e64c99c83dff40e262ee616ca7b50cb54945c26674e24b1dafb903d107e0f7f8'
saved=json.loads(gzip.decompress(raw));current=saved['current_result'];target=saved['current_input']['target_enemy']
processed=current['run_resolution']['enemy']
assert processed['enemy_id']==target['enemy_id']and processed['level']==target['level']and processed['stage_id']==target['stage_id']
assert processed['level_type']=='BOSS'and 'id'not in processed
assert len(saved['completed_records'])==580 and saved['fresh_public_calls_in_resume']==512
assert saved['source_hashes_before']==saved['source_hashes_after']
paths={
    'neural_reference':'result.neural_relic_reference <- Combat.neural exact dict; River selected only',
    'mantra_reference':'result.external_event_reference <- full.plan external_event_reference, kind mantra_events; actual_event_times None added at output',
    'enemy_identity':'result.run_resolution.enemy <- resolve enemy={**target,...}; enemy_id/stage_id/level target keys; level_type copied from unique catalog record',
    'haruka_reference':'result.haruka_healing_reference <- full/shown reference(profile,scenario,skill); actual friendly fields and native flags source dict',
    'haruka_attack':'result.attack <- shown.attack; estimate.skill.skill_attack <- full.attack; estimate.base_stats.attack <- self.stats.attack',
    'haruka_mode':'plan non-normal S2 reads repeat at any allowed E1/E2; timed default vs infinite; infinite has duration/cycle None',
    'orchid_talent':'source-selected 翔虫机动 enters self.atk_bonus before stats/plan; raw input string guard changes no producer fields',
    'orchid_redeploy':'result.orchid_redeploy_reference <- exact owner-specific dict; near bool affects only attack, no redeploy events',
    'orchid_cast':'result.unbound_cast_reference <- full.plan orchid_arrows + preserve_unplaced_sources; collision flag False, actual hit/end None added at output',
    'orchid_zero_scope':'preserve_unplaced_sources excludes only window0 or lifetime0; empty hostile windows alone do not establish arrow collision clock',
}
receipt={'status':'PASS_REMAINING_RECEIVERS_MATCH_EXACT_FINAL_PUBLIC_PRODUCERS',
    'root_commit':'2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b',
    'source_hashes':{name:hashlib.sha256((PACKAGE/'rouge'/name).read_bytes()).hexdigest()for name in sources},
    'receiver_paths':paths,'producer_excerpts':{'stats':stats,'neural':neural,'redeploy':redeploy,'unbound':unbound,'external':external,'enemy':enemy},
    'estimate_skill_literal_fields':sorted(skill_keys),'haruka_reference_literal_fields':sorted(healing_keys),
    'actual_saved581_counterexample_enemy_keys':list(processed),'saved580_complete_records':580,
    'saved581_source_unchanged':True,'API_calls':0,'formatter_calls':0,'qualification_helper_calls':0,
    'Qt_executed':False,'Wine_executed':False,'unrun_requests':573}
with (HERE/'remaining-contract-field-audit085.json').open('x')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'status':receipt['status'],'saved581_enemy_shape_verified':True,'API_calls':0,'formatter_calls':0}))
