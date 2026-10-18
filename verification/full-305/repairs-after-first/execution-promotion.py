"""Explicit root repair after original all-scope attempt is terminal and archived."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,ast,json
root=Path(__file__).resolve().parents[1]
sources={
 'tests/test_map_projection_049.py':('.cache/p3-305-full-failure-triage/map049-first/PROPOSED_NOT_APPLIED-test_map_projection_049.py','7f22fab519a79d8edd4e4eb10a52b5237976c05fb7ceba0610ad58d1717339a7','test_failed_readings_retained_without_relaxed_pixel_gate'),
 'tests/test_choice_recruitment_integration_290.py':('.cache/p3-305-full-failure-triage/regression-triage/candidate/tests/test_choice_recruitment_integration_290.py','c07d2de9be9be2bbc7a7beac29f8963a50f621e5d70cef179dc5916a0c0becc3','test_all_event_choices_keep_original_eligibility_and_only_target_annotation_changes'),
 'tests/test_original_destinations.py':('.cache/p3-305-full-failure-triage/regression-triage/candidate/tests/test_original_destinations.py','80fdbedbc816fff52348fb7e2a7a5a0e7ab9b1d8d47069a56224e6bd772da42e','test_independent_scene_choices_keep_unknown_special_conditions'),
 'tests/test_peace_guardian_integration_291.py':('.cache/p3-305-full-failure-triage/regression-triage/candidate/tests/test_peace_guardian_integration_291.py','970e39203d22d7f01f252239c9bbee2cb981ebf9c140028e7d47f8de66b593d5','test_all_fixed_events_and_contexts_keep_status_checks_ids_and_non_target_fields'),
 'tests/test_batch185_mainwindow.py':('.cache/p3-305-full-failure-triage/batch185/candidate/tests/test_batch185_mainwindow.py','e2562f10847958c743d8a38502e4b65de13fbfd5cf1c11d72b80d197483964b4','test_map_position_bind_and_fixed_battle_navigation')}
def load(p):return json.loads(p.read_bytes())
def digest(raw):return sha256(raw).hexdigest()
def functions(raw):
    result={}
    def visit(node,scope=()):
        for child in getattr(node,'body',[]):
            if isinstance(child,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                key=scope+(child.name,)
                if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    assert key not in result;result[key]=ast.dump(child,include_attributes=False)
                visit(child,key)
    visit(ast.parse(raw));return result
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply-after-first-archive',action='store_true');args=parser.parse_args()
    assert args.apply_after_first_archive,'Explicit root application required; preparation never changes source.'
    archive=root/'verification/full-305/execution-attempt1/archive-manifest.json'
    manifest=load(archive)
    assert manifest['source_freeze_sha256']=='32033bd8a5ebc2920843e00ac2584a2b01bd9659ffcd46352fb69b780ecc1463'
    invocation=load(root/'verification/full-305/first-archive-invocation/process.json')
    assert invocation['actual_exit']==0 and invocation['all_25_original_component_positions_accounted_for']is True
    assert invocation['archive_manifest_sha256']==digest(archive.read_bytes())
    original=load(root/'verification/full-305/source-freeze.json')
    assert all(digest((root/name).read_bytes())==expected for name,expected in original['source_sha256'].items()),'Current first-attempt source must still be exact before repairs.'
    raw=load(root/'verification/full-305/execution-attempt1/offline/actual/windows-offline.json')
    assert raw['source_sha256']==original['source_sha256'] and raw['source_drift']==[] and len(raw['failed_cases'])==5
    output=root/'verification/full-305/repairs-after-first';assert not output.exists()
    changes=[];contents={}
    for name,(candidate,expected,method)in sources.items():
        before=(root/name).read_bytes();after=(root/candidate).read_bytes()
        assert digest(before)==original['source_sha256'][name] and digest(after)==expected,name
        first,second=functions(before),functions(after)
        assert first.keys()==second.keys(),name
        altered=[key for key in first if first[key]!=second[key]]
        assert len(altered)==1 and altered[0][-1]==method,(name,altered)
        contents[name]=(before,after)
        changes.append({'file':name,'candidate':candidate,'before_sha256':digest(before),'after_sha256':expected,
                        'changed_method':'::'.join(altered[0]),'unchanged_functions':len(first)-1})
    output.mkdir(parents=True)
    for name,(before,after)in contents.items():
        destination=output/'before'/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(before)
        (root/name).write_bytes(after)
    result={'section':305,'kind':'SOURCE_SUPPORTED_HISTORICAL_REGRESSION_FIXTURES_AFTER_FULL_FIRST_ATTEMPT',
     'at_utc':datetime.now(timezone.utc).isoformat(),'first_archive_sha256':digest(archive.read_bytes()),'changes':changes,
     'product_mechanisms_or_node_protection_reverted':False,'new_functional_section_started':False,
     'necessary_tests_or_complete_second_full_executed_by_promotion':False,
     'scope_preserved':'Original rejected whole planes, all older event field comparisons and all map coordinates/navigation assertions retained; added298 checks verified before comparison normalization; use current map selection and291 result classification.'}
    (output/'promotion.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    (output/'execution-promotion.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
