"""Independent, static-only guard boundary review. No project imports."""
import ast
import hashlib
import json
from pathlib import Path

AUTHOR=Path('/workspace/.continuation/p2-after086-finite-input-source')
OUT=Path(__file__).resolve().parent
BASE='2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
MANIFEST_SHA='58d25683715beef74e048b26c3e27014616e7c6b33cfded4d147ce9a8a825bb1'
HANDOFF_SHA='ffa3cc6943d8833efb65a897a4fc64d12ee37278bdfd3e3cd627f05d4af4c5b1'


def sha(data):return hashlib.sha256(data).hexdigest()


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')


def ordered(text,*tokens):
    indices=[text.index(token) for token in tokens]
    assert indices==sorted(indices),tokens
    return [{'text':token,'offset':index} for token,index in zip(tokens,indices)]


def main():
    assert sha((AUTHOR/'public-artifacts-manifest.json').read_bytes())==MANIFEST_SHA
    assert sha((AUTHOR/'handoff.json').read_bytes())==HANDOFF_SHA
    handoff=json.loads((AUTHOR/'handoff.json').read_bytes())
    assert handoff['fixed_commit']==BASE
    findings=json.loads((AUTHOR/'findings.json').read_bytes())
    assert findings['actionable_candidates']==[] and findings['confirmed_missing_public_float_consumer_guards']==[]
    assert any('derived arithmetic overflow' in s for s in findings['limits'])
    rows=json.loads((AUTHOR/'guard-function-excerpts.json').read_bytes())
    assert len(rows)==18
    functions={}
    code_files={}
    proof=[]
    for row in rows:
        name=row['source_path']
        data=(AUTHOR/'fixed-public'/name).read_bytes()
        text=(AUTHOR/'fixed-public'/name).read_text(encoding='utf-8');tree=ast.parse(text)
        matches=[node for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
                 and node.lineno==row['line'] and node.end_lineno==row['end_line']]
        assert len(matches)==1,(name,row['function'])
        segment=ast.get_source_segment(text,matches[0])
        assert segment==row['source'],(name,row['function'])
        functions[row['function']]=segment
        code_files[name]={'path':name,'bytes':len(data),'sha256':sha(data)}
        proof.append({'path':name,'function':row['function'],'line':row['line'],'end_line':row['end_line'],
                      'exact_excerpt_matches_static_ast':True,'excerpt_sha256':sha(segment.encode())})
    for name in ('Combat.value','build_estimate.nonnegative','finite','_single','_fp','context_value'):
        assert 'math.isfinite(' in functions[name],name
    assert "value=float(value)" in functions['Combat.value']
    assert "integer and key!='healing_targets' and isinstance(value,bool)" in functions['Combat.option']
    assert 'return self.value(value,key,maximum,integer)' in functions['Combat.option']
    assert 'if isinstance(value,bool):raise ValueError' in functions['finite']
    assert 'try:value=float(value)' in functions['finite']
    assert "except (TypeError,ValueError)" in functions['finite']
    assert 'if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)' in functions['_single']
    assert 'except (OverflowError,struct.error)' in functions['_single']
    assert '_single(_single(value)*_Q32)' in functions['_fp']
    assert '-(1<<63)<=scaled<(1<<63)' in functions['_fp']
    sequences={
        'public_preparation':ordered(functions['_prepare_damage'],"if not isinstance(skill,int)",
             "if not isinstance(rank,int)",'attributes=operator_attributes(',"if profile['skills'][skill-1]",
             'active_counts=[]','scenario,run_resolution=prepare_run(scenario)',
             'scenario,resolution=prepare(scenario,profile)','scenario,attributes=prepare_attribute_runes(scenario,attributes)',
             'AttackTimeline(scenario)'),
        'extended_constructor':ordered(functions['Combat.__init__'],"for effect in self.effects:",
             "self.enemy_def=self.option('enemy_defense',0)","self.enemy_res=self.option('enemy_resistance',0,maximum=100)",
             "for field in ('window_seconds','skill_duration_seconds'):","self.base=float(scenario['base_attack'])",
             "self.value(self.base,'基础攻击')",'self.apply_self_talents()'),
        'legacy_scalars_before_declared_counts':ordered(functions['_skill_damage_base'],
             "for field in ('base_attack','enemy_defense','enemy_resistance','window_seconds','companion_attack'):",
             "if not math.isfinite(value)","for field in ('skill_rank','activation_count','deployment_stacks','shield_break_count','charge_count'):")}
    prepare=functions['_prepare_damage']
    assert "if has_healing(scenario['operator'],skill):" in prepare
    assert "if scenario['operator']=='char_1037_amiya3' and skill==2:" in prepare
    assert "if scenario['operator']=='char_4087_ines':" in prepare
    assert "declared_counts.get((scenario['operator'],skill),())" in prepare
    enemy=functions['resolve_enemy']
    assert "if not target:" in enemy and "scenario.pop('enemy_weight',None)" in enemy
    assert enemy.index("scenario['enemy_defense']=stats['def'];scenario['enemy_resistance']=stats['magicResistance']")>enemy.index("if len(candidates)!=1:")
    assert "scenario['enemy_is_boss']=record['level_type']=='BOSS'" in enemy
    assert "if not rules:\n            continue" in functions['apply_attribute_runes']
    assert "preview = apply_attribute_runes({**attributes, 'attack': original_attack}, runes)" in functions['prepare_attribute_runes']
    timing=(AUTHOR/'fixed-public/rouge/timing.py').read_text()
    assert "def frame_time(seconds):return math.ceil(finite(seconds,'时间',3600)*FPS-1e-9)" in timing
    assert "start,end=map(frame_time,pair)" in functions['AttackTimeline.ranges']
    assert "if end<=start:raise ValueError" in functions['AttackTimeline.ranges']
    save('guard-subreceipt.json',{'status':'FINAL_SEALED_PASS_BOUNDED_STATIC_ONLY','fixed_commit':BASE,
         'author_manifest_sha256':MANIFEST_SHA,'author_handoff_sha256':HANDOFF_SHA,
         'all_18_excerpts_exactly_matched_fixed_source_ast':True,'excerpt_newline_layer':'Path.read_text universal-newline, same as author; original byte hashes preserved separately','source_files_read':list(code_files.values()),
         'excerpt_proof':proof,'static_error_order_sequences':sequences,
         'confirmed_absent_guards':[],'actionable_candidates':[],
         'scope_confirmed':[
             'Existing finite gates are at selected engine/scalar/option/timing/relic/native-conversion consumers.',
             'Public skill, rank and cultivation/module validation precedes prepare_run, relic/rune preparation and engine checks.',
             'Selected fixed enemy identity assigns defense, resistance and boss state after identity/source validation; overwritten stale manual input is not independently a defect.',
             'Integer raw-bool guards retain owner/capability scopes; noninteger Combat.value conversion is not a global bool prohibition.',
             'A rune-free attack is not checked by _fp; its later engine finite gate remains the checked boundary.',
             'finite timing and range endpoints reject nonfinite values before frame conversion; old ordering is preserved in source.',
             '_single has finite/type checks and native packing overflow handling; _fp has scaled finite/range checks.',
             'Finite input validation does not prove every derived sum/product finite; no global arithmetic-safety claim.'
         ],
         'bridge_boundary':'This child reads saved _prepare_damage and resolve_enemy endpoints. Saved package does not contain run_modifiers.py; this child does not independently establish the middle prepare_run->resolve_enemy bridge. Parent may supply fixed Git-byte evidence separately.',
         'historical_numbertypes_and_zero_aliases':'Historical saved receipts only, no new execution or matrix claims.',
         'counters':{'API_calls':0,'project_helper_calls':0,'tests':0,'Qt':0,'Wine':0,'product_patches':0,'tracked_edits':0,'matrices':0},
         'limits':findings['limits'],'read_discovery_diagnostic':'Initial rg included the not-yet-created independent parent directory and returned a missing-path diagnostic; subsequent reads used existing author paths only. No dependent product/API process.',
         'preparation_attempts':2,'preparation_failures':1,'preparation_failure':'CRLF raw text versus universal-newline author AST excerpt; failed version/log/diagnostic retained, corrected text-read layer only, no project process started.',
         'patch_transport_preparation_error':'First apply_patch did not match combined limits/read_discovery line; no edit applied or dependent process. Corrected using exact inspected line.',
         'stop':'Release slot; reopen only for named actually consumed field with exact absent finite guard and separately authorized public evidence.'})
    names=['review_guard_scope.py','guard-subreceipt.json','NOTE.md','review-guard-scope-attempt-1.py','preparation-diagnostic-attempt-1.json','preparation-attempt-1.log']
    files=[]
    for name in names:
        data=(OUT/name).read_bytes()
        files.append({'source_path':str(OUT/name),'archive_path':name,'bytes':len(data),'sha256':sha(data)})
    save('public-artifacts-manifest.json',{'format_version':1,'files':files,'count':len(files),
         'total_bytes':sum(row['bytes'] for row in files),'stage':'static_child_review','no_whole_source_tree_copied':True})
    print(json.dumps({'passed':True,'files':len(files),'bytes':sum(row['bytes'] for row in files),
         'receipt_sha256':sha((OUT/'guard-subreceipt.json').read_bytes()),
         'manifest_sha256':sha((OUT/'public-artifacts-manifest.json').read_bytes()),'new_API_calls':0}))


if __name__=='__main__':main()
