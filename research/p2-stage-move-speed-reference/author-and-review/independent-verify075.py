from copy import deepcopy
import collections
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

P=Path(__file__).parent
BASE=P/'baseline';DRAFT=P/'draft075'
COMMIT='dbf1e698f56cbba03793ed13769a9f6dae2c5ff6'
KEY='stage_move_speed_rune_reference'


def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


expected_hashes={'rouge/spawn_reference.py':'8cc132abaeac2beda7964a5830012b43b49e99158c4b528d80ed00a42cc59cb4',
                 'rouge/battle_preview.py':'316af4334fb33c0657dc79f2e6433bab76b900e3f4d7ca3a8149de431e172fdb'}
assert sha(P/'section75.patch')=='a5ed5009e65b5d04fc687eda4ec77dcd8922dc978a7ab3a62c5ec69176483d02'
for name,digest in expected_hashes.items():assert sha(DRAFT/name)==digest
freeze=json.loads((P/'baseline-freeze075.json').read_text())
assert freeze['frozen_commit']==COMMIT and freeze['snapshot_includes_root_wip']is False
assert len(freeze['files'])==freeze['file_count']==2177
entries=subprocess.check_output(['git','-C','/workspace/rougezhushou','ls-tree','-r','-z',COMMIT]).split(b'\0')
blobs={}
for row in entries:
    if row:
        meta,name=row.split(b'\t',1);blobs[name.decode()]=meta.split()[2].decode()
for name,row in freeze['files'].items():
    data=(BASE/name).read_bytes()
    assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blobs[name]
    if name not in expected_hashes:assert (DRAFT/name).read_bytes()==data
patchpaths={line.split(' b/')[1]for line in (P/'section75.patch').read_text().splitlines()if line.startswith('diff --git ')}
assert patchpaths==set(expected_hashes)|{'tests/test_stage_move_speed_reference.py'}
check=P/'independent-patch-check075'
for name in expected_hashes:
    target=check/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/name,target)
assert not (check/'tests/test_stage_move_speed_reference.py').exists()
for args in (['git','apply','--check',str(P/'section75.patch')],['git','apply',str(P/'section75.patch')]):
    result=subprocess.run(args,cwd=check,capture_output=True,text=True);assert result.returncode==0,result.stderr
assert all((check/name).read_bytes()==(DRAFT/name).read_bytes()for name in expected_hashes)
assert (check/'tests/test_stage_move_speed_reference.py').read_bytes()==(P/'test_stage_move_speed_reference.py').read_bytes()

source=json.loads((P/'source-receipt075.json').read_text())
raw_data=(P/'level_rogue6_3-6.json').read_bytes()
assert len(raw_data)==233958 and hashlib.sha256(raw_data).hexdigest()=='2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296'
raw=json.loads(raw_data)
assert source['frozen_repository_commit']==COMMIT
assert raw['runes'][0]==source['raw_rune_complete']
assert raw['runes'][0]['blackboard'][2]=={'key':'move_speed','value':1.5,'valueStr':None}
assert raw['options']['moveMultiplier']==source['stage_option_parameter']==.5
battle=json.loads((BASE/'rouge/data/battle-previews.json').read_text())
assert len(battle['stages'])==105
inventory=[]
for sid,stage in battle['stages'].items():
    for ri,rune in enumerate(stage.get('runes',[])):
        for bi,field in enumerate(rune.get('blackboard',[])):
            if field['key']=='move_speed':inventory.append((sid,ri,bi))
assert inventory==[('ro6_n_3_6',0,2),('ro6_e_3_6',0,2)]
for sid,difficulty in (('ro6_n_3_6','NORMAL'),('ro6_e_3_6','FOUR_STAR')):
    stage=battle['stages'][sid]
    assert stage['runes']==raw['runes'] and stage['movement_multiplier']==.5 and stage['difficulty']==difficulty
    assert stage['level_source']=={key:source['raw_stage_source'][key]for key in ('url','sha256','bytes')}
enum=source['native_attribute_enum']
assert sha(Path(enum['source_path']))==enum['source_sha256']
native=json.loads(Path(enum['source_path']).read_text());matches=[]
def walk(value):
    if isinstance(value,dict):
        if value.get('name')=='MOVE_SPEED'and value.get('type')=='Torappu.AttributeType':matches.append(value)
        for child in value.values():walk(child)
    elif isinstance(value,list):
        for child in value:walk(child)
walk(native)
assert matches==[enum['complete_move_speed_field']]
native_search=source['existing_parsed_native_search']
assert len(native_search['files'])==177
for row in native_search['files']:
    data=Path(row['path']).read_bytes()
    assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256']
    assert all(needle not in data.decode(errors='replace')for needle in native_search['needles'])
expected_reference={'parameter':1.5,'rune_key':'enemy_attribute_mul','blackboard_key':'move_speed',
    'source_selector':'$.runes[0].blackboard[2]',
    'source':{key:source['raw_stage_source'][key]for key in ('url','sha256','bytes')},
    'difficulty_mask_parameter':'FOUR_STAR','profession_mask_parameter':1023,'buildable_mask_parameter':'ALL',
    'native_target_writer_layer_verified':False,'combined_with_stage_multiplier_speed':None,
    'complete_effective_speed_verified':False}


def compare(before,after):
    assert len(before['records'])==len(after['records'])
    counts=collections.Counter()
    for old,new in zip(before['records'],after['records']):
        assert old['api']==new['api']and old['request']==new['request']
        if 'group'in old:assert old['group']==new['group']
        for row in (old,new):
            if 'full_result'in row:assert hashlib.sha256(canonical(row['full_result']).encode()).hexdigest()==row['full_result_sha256']
        if 'error'in old:
            assert old['error']==new.get('error')and 'full_result'not in new
            counts['prior_complete_error_unchanged']+=1
        elif old['api']=='enemy_preview'and old['request']['stage_id']=='ro6_e_3_6':
            trimmed=deepcopy(new['full_result'])
            movement=trimmed['preview']['movement_reference']
            assert movement.pop(KEY)==expected_reference
            assert movement['complete_effective_speed_verified']is False
            subtotal=movement['base_times_stage_speed']
            additions=['关卡移速符文参数参考：1.5',
                '基础移速×关卡倍率小计：'+('未知'if subtotal is None else f'{subtotal:g}'),
                '符文与关卡倍率合成的移速：未知；原生目标、写入及叠加层尚未核验。',
                '关卡移速参数来源：'+expected_reference['source']['url']]
            lines=trimmed['technical_text'].splitlines()
            assert all(lines.count(line)==1 for line in additions)
            for line in additions:lines.remove(line)
            trimmed['technical_text']='\n'.join(lines)
            assert trimmed==old['full_result']
            counts['only_exact_reference_and_four_technical_lines_added']+=1
        else:
            assert old['full_result']==new.get('full_result')and 'error'not in new
            counts['whole_json_and_text_unchanged']+=1
    return dict(counts)


before=json.loads((P/'baseline-results075.json').read_text());after=json.loads((P/'draft-results075.json').read_text())
assert before['public_calls']==after['public_calls']==2745
main=compare(before,after)
assert main=={'only_exact_reference_and_four_technical_lines_added':80,'whole_json_and_text_unchanged':2630,'prior_complete_error_unchanged':35}
supp_before=json.loads((P/'baseline-supplemental-sp075.json').read_text());supp_after=json.loads((P/'draft075-supplemental-sp075.json').read_text())
assert supp_before['public_calls']==supp_after['public_calls']==24
for old,new in zip(supp_before['records'],supp_after['records']):
    assert old['request']==new['request']and old['full_result']==new['full_result']
    for row in (old,new):assert hashlib.sha256(canonical(row['full_result']).encode()).hexdigest()==row['full_result_sha256']
    result=new['full_result'];args=new['request']
    assert result['estimate']['skill']['sp_recovery_per_second']==1.2
    if args.get('four_sui'):
        assert all(result['estimate']['skill'][key]is None for key in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'))
old=json.loads((P/'independent-baseline-results075.json').read_text());new=json.loads((P/'independent-draft-results075.json').read_text())
assert old['calls']==new['calls']==65 and old['caller_and_caches_unchanged']and new['caller_and_caches_unchanged']
fresh=compare(old,new)
assert fresh=={'only_exact_reference_and_four_technical_lines_added':12,'whole_json_and_text_unchanged':46,'prior_complete_error_unchanged':7}
for row in new['records']:
    args=row['request']
    if row['api']=='calculate_damage'and args.get('four_sui')and 'full_result'in row:
        result=row['full_result'];skill=result['estimate']['skill'];ref=result['shu_periodic_sp_reference']
        assert skill['sp_recovery_per_second']==1.2 and ref['events_scheduled']is False
        assert all(skill[key]is None for key in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'))
        assert all(ref[key]is None for key in ('first_tick_seconds','actual_tick_times_seconds','clock_origin','reset_rule','blocked_credit_rule'))
        if args['window_seconds']==0:assert result['total_damage']==result['total_healing']==0
for name,digest in expected_hashes.items():assert sha(DRAFT/name)==digest
receipt={'status':'independent_review_passed','blockers':[],
    'baseline_commit':COMMIT,'baseline_files_verified_against_manifest_and_actual_committed_git_blobs':2177,
    'unchanged_old_public_draft_files':2175,
    'patch_sha256':sha(P/'section75.patch'),'changed_source_hashes':expected_hashes,
    'patch_apply_check_and_exact_two_sources_plus_test_reconstruction':True,
    'raw_stage_sha256':sha(P/'level_rogue6_3-6.json'),'raw_stage_bytes':233958,
    'source_checked_complete_runes':True,'source_checked_option_field_only':'options.moveMultiplier',
    'all_105_stage_rune_literal_inventory_rechecked':True,'native_cached_texts_rehashed_exact_search':177,
    'native_enum_move_speed_field_checked_without_writer_layer_inference':True,
    'fresh_paired_scenarios':65,'public_calls':130,'fresh_counts':fresh,'new_tests_passed':8,
    'saved_author_pairs_strictly_recompared':2769,'saved_main_pairs':2745,'saved_supplemental_sp_pairs':24,
    'saved_main_counts':main,'saved_supplemental_sp_complete_json_unchanged':24,
    'author_calls_not_rerun':5538,'author_related_tests':{'run':64,'passed':61,'missing_public_fixtures_explicitly_skipped':3},
    'bounded_scope':'Exact emergency stage original move_speed parameter reference and four technical text lines only. Old base-times-stage subtotal, default enemy text, complete/scope, all damage/environment/training math and periodic clocks are unchanged. No native target writer or layer composition is inferred.',
    'initial_environment_read_rejected_not_source_failure':True,
    'no_tracked_edits':True,'no_private_state_reads':True,'no_wine_or_gui_or_binary_downloads':True,
    'artifact_sha256':{name:sha(P/name)for name in ('independent-verify075.py','independent-probe075.py','independent-baseline-results075.json','independent-draft-results075.json','independent-new-tests075.log','independent-initial-environment-rejection075.json','independent-native-lead-review075.json','source-receipt075.json','section75.patch','test_stage_move_speed_reference.py','baseline-results075.json','draft-results075.json','baseline-supplemental-sp075.json','draft075-supplemental-sp075.json','matrix-comparison075.json','supplemental-sp-comparison075.json')}}
path=P/'independent-review075.json';path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'fresh_pairs':65,'fresh_calls':130,'fresh_counts':fresh,'saved_pairs':2769,'main_counts':main,'supplemental_sp_pairs':24,'new_tests_passed':8,'receipt_sha256':sha(path)}))
