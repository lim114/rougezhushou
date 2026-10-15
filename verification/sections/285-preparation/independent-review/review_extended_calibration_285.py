"""Bounded independent285 adapter review; no game/Qt/full-matrix rerun."""
from copy import deepcopy
from pathlib import Path
import hashlib
import importlib
import importlib.machinery
import json
import subprocess
import sys
import traceback
import types
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'rouge/app.py').is_file())
OUT=HERE/'independent-adapter-review-285.json'
assert not OUT.exists()
EXPECTED={'rouge/calibration.py':'4d06ebb2a09f119f6dc5391aa36b7fe9ca3999fe81b54f710817eed753bc1263',
          'rouge/offline_tools_view.py':'996bfc0f55fcf19cf75457fb596e484f68a9a96ca005f72375bda1ec24aef1d1'}
for name,expected in EXPECTED.items():
    raw=(ROOT/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
    sealed=HERE/('reviewed-'+Path(name).name);assert not sealed.exists();sealed.write_bytes(raw)
sys.path.insert(0,str(ROOT))
from rouge import calibration as core
from rouge.damage import calculate_damage
from rouge.panel_native_finalization import panel_native_finalization
original_receipt=ROOT/'.cache/section285-preparation/original-scope-counterexamples/receipt.json'
original=json.loads(original_receipt.read_bytes())
checks=[];probes=[];fatal=None

def check(name,ok):checks.append({'name':name,'passed':bool(ok)})

def invoke(name,fn,payload):
    pristine=deepcopy(payload)
    value=fn(payload)
    probes.append({'name':name,'input':pristine,'actual_output':deepcopy(value)})
    check(name+'/input_unchanged',payload==pristine)
    return value

def matrix_spy(name,payload):
    calls=[]
    real=core.calculate_damage
    def traced(scenario):
        calls.append(deepcopy(scenario))
        return real(scenario)
    with patch.object(core,'calculate_damage',side_effect=traced):
        value=invoke(name,lambda s:core.skill_matrix(s),payload)
    probes[-1]['actual_main_call_inputs']=calls
    return value,calls

try:
    # These are precisely the sole author's actual original inputs, not a
    # reenactment mislabeled as original. Only corrected behavior is run here.
    for case in original['cases']:
        name=case['id'];scenario=deepcopy(case['input'])
        result,calls=matrix_spy('same_original_'+name,scenario)
        probes[-1]['same_input_as_original_receipt']=True
        check(name+'/selected_input_unchanged',scenario==case['input'])
        if name=='skill_scoped_animation':
            first,second=result['rows']
            check(name+'/two_skills_normal',len(calls)==2 and [r['skill'] for r in result['rows']]==[1,2])
            check(name+'/original_selected_action_kept',calls[1]['timing']['animation_reference']==scenario['timing']['animation_reference'])
            check(name+'/derived_action_removed', 'animation_reference' not in calls[0]['timing'])
            check(name+'/common_windows_kept',all(s['timing']['target_windows']==[[0,30]] for s in calls))
            check(name+'/omission_explained',any(x['field']=='timing.animation_reference' for x in first['omitted_conditions']) and not second['omitted_conditions'])
        else:
            check(name+'/all_legacy_nine_calculated',len(calls)==9 and len(result['rows'])==9)
            own=[s for s in calls if s['operator']==scenario['operator']]
            other=[s for s in calls if s['operator']!=scenario['operator']]
            check(name+'/original_recipient_kept',all(s['char_buff_ids']==scenario['char_buff_ids'] for s in own))
            check(name+'/foreign_recipient_removed',all('char_buff_ids' not in s for s in other))
            check(name+'/foreign_omission_visible',all(any(x['field']=='char_buff_ids' for x in row['omitted_conditions']) for row in result['rows'] if row['operator_key']!=scenario['operator']))
            if name=='snack_recipient_leaks_to_foreign_owner':
                for row,s in zip(result['rows'],calls):
                    if s['operator']!=scenario['operator']:
                        pure=deepcopy(s);pure.pop('char_buff_ids',None)
                        direct=calculate_damage(pure)
                        check(name+'/'+s['operator']+str(s['skill'])+'/foreign_initial_no_snack',row['initial_seconds_reference']==direct['estimate']['skill']['initial_seconds'])
        for row in result['rows']:
            check(name+'/'+row['operator_key']+str(row['skill'])+'/not_actual',row['actual_skill_rank'] is None and row['native_verified'] is False and row['native_clock_verified'] is False and row['native_panel_reference']['complete_native_panel'] is False)

    # The actual old valid no-special-conditions legacy9 semantic subset remains
    # byte-for-byte equivalent as data; newly attached identities are additive.
    old_raw=subprocess.check_output(['git','show','HEAD:rouge/calibration.py'],cwd=ROOT)
    assert hashlib.sha256(old_raw).hexdigest()=='72fa76dcb8592b7eb539ddc4d9440cb84e92449d30795b3de9bf9b81f0006691'
    old_dir=HERE/'old284-calibration-only';assert not old_dir.exists();old_dir.mkdir()
    (old_dir/'calibration.py').write_bytes(old_raw)
    name='independent_old284_calibration_for285'
    package=types.ModuleType(name);package.__package__=name;package.__path__=[str(old_dir),str(ROOT/'rouge')]
    package.__spec__=importlib.machinery.ModuleSpec(name,loader=None,is_package=True)
    sys.modules[name]=package
    old=importlib.import_module(name+'.calibration')
    payload={'operator':'mechanist','skill':3,'charge_count':0}
    before=old.skill_matrix(deepcopy(payload))
    after=invoke('legacy_default_nine_semantic_subset',core.skill_matrix,payload)
    check('legacy9/default_unchanged_count',len(before['rows'])==len(after['rows'])==9 and after['selection_mode']=='legacy_first_three')
    check('legacy9/all_old_row_fields_unchanged',all({k:new[k] for k in prior}==prior for prior,new in zip(before['rows'],after['rows'])))
    check('legacy9/source_native_marker_same',before['source']==after['source'] and before['native_verified'] is after['native_verified'] is False)

    # Actual panel result ownership: a supplied real main result is copied by
    # the adapter without a second native evaluator call. Temporary mocks only
    # affect this independent process, never product source files.
    declared={'operator':'char_151_myrtle','skill':2}
    main=calculate_damage(deepcopy(declared))
    with patch.object(core,'calculate_damage',return_value=deepcopy(main)) as main_call, \
         patch('rouge.panel_native_finalization.panel_native_finalization',side_effect=AssertionError('adapter attempted a second native evaluation')):
        panel=invoke('extended_panel_same_actual_main_return_copy',core.panel_layers,declared)
    check('panel/native_exact_main',panel['native_panel_reference']==main['panel_native_finalization'])
    check('panel/one_main_call',main_call.call_count==1)
    check('panel/not_aliased_mutable_result',panel['native_panel_reference'] is not main['panel_native_finalization'])
    check('panel/not_actual',panel['native_verified'] is False and panel['native_panel_reference']['actual_panel'] is None)

    result,calls=matrix_spy('cultivation_locked_skill_not_evaluated',{'operator':'char_151_myrtle','skill':1,'elite':0,'level':1,'skill_rank':7})
    check('locked/only_one_main_call',len(calls)==1 and calls[0]['skill']==1)
    check('locked/second_named_not_evaluated',result['rows'][1]['name'] and result['rows'][1]['unlocked'] is False and result['rows'][1]['unlock_reasons'] and result['rows'][1]['native_panel_reference'] is None)
    check('locked/all_actual_ranks_unknown',all(r['declared_skill_rank']==7 and r['actual_skill_rank'] is None for r in result['rows']))

    rejects=[('foreign_owner_extended',lambda:core.skill_matrix({'operator':'char_151_myrtle','skill':2},operators=['char_1050_chen3'])),
             ('legacy_only_cultivation',lambda:core.cultivation_curve({'operator':'char_151_myrtle','skill':2},levels=[1])),
             ('legacy_only_modules',lambda:core.module_stages({'operator':'char_151_myrtle','skill':2})),
             ('invalid_original_action_not_hidden',lambda:core.skill_matrix({'operator':'char_1037_amiya3','skill':2,'timing':{'animation_reference':'char_1037_amiya3:Front:Skill_1_Attack'}})),
             ('internal_actual_injection',lambda:core.panel_layers({'operator':'char_151_myrtle','skill':2,'_native_verified':True}))]
    for label,fn in rejects:
        try:fn();error=None
        except ValueError as exception:error={'type':type(exception).__name__,'message':str(exception)}
        probes.append({'name':label,'expected_rejection':True,'actual_error':error})
        check(label+'/rejected',error is not None)
    check('source/frozen_unchanged',all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected for name,expected in EXPECTED.items()))
except BaseException as error:
    fatal={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    check('unexpected_fatal',False)

report={'kind':'SECTION285_INDEPENDENT_LIMITED_ADAPTER_REVIEW','source_sha256':EXPECTED,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'actual_original_counterexamples_receipt':str(original_receipt.relative_to(ROOT)),
        'actual_original_counterexamples_receipt_sha256':hashlib.sha256(original_receipt.read_bytes()).hexdigest(),
        'original_failures_not_reenacted_or_overwritten':True,
        'same_original_inputs_retested_on_corrected_source':3,
        'probes':probes,'probe_count':len(probes),'checks':checks,'check_count':len(checks),
        'failed':[c for c in checks if not c['passed']],'unexpected_fatal':fatal,
        'scope':'Three original corrected scope counterexamples, legacy9 field compatibility, exact main return ownership, locks and five admission guards. Not root119-panel/skill matrix, author14 suite, native code or Windows review.',
        'new_native_fresh_spans':0,'game_or_chat_operation':False,'private_state_read_or_modified':False,
        'production_or_other_author_cache_modified':False}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'probes':len(probes),'checks':len(checks),'failed':report['failed'],'fatal':fatal,
                  'receipt_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}))
raise SystemExit(bool(report['failed']))
