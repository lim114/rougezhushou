"""Root source declaration, NOT a claim that future offline/legacy tests pass."""
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from final_common import BASE,ROOT,FREEZE,PRIOR_SHA,prepared,source_state,prior_archives,module_reference,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--declare-final-A3-full-inputs',action='store_true',required=True)
    p.add_argument('--expected-parent-commit',required=True);p.add_argument('--preparation-sha256',required=True)
    a=p.parse_args()
    if FREEZE.exists():raise ValueError('Never overwrite a source declaration')
    meta,common,execution,old=prepared(a.expected_parent_commit,a.preparation_sha256)
    live,supp,native,delta=source_state(meta,common,old)
    archives=prior_archives(meta)
    necessary=module_reference(a.expected_parent_commit,meta)
    record={'section':290,'root_declared':True,'actual_validation_attempt':3,
        'checked_at':datetime.now(timezone.utc).isoformat(),'phase':'final_A3_inputs_declared_runtime_validation_pending',
        'parent_commit':a.expected_parent_commit,'branch':'codex/p2-development',**live,
        'supplemental_public_inputs_sha256':supp,'legacy_native_source_sha256':native,
        'legacy_source_additional_sha256':meta['original_legacy_additional_sha256'],
        'prior_attempt_freeze_sha256':PRIOR_SHA,'source_transition':delta,
        'preparation_sha256':a.preparation_sha256,'preparation_tools_sha256':meta['new_tools_sha256'],
        'template_bundle_sha256':meta['template_bundle_sha256'],'prior_archives':archives,
        'necessary_module_check':necessary,'new_offline_and_legacy_share_one_final_freeze':True,
        'A2_current_and_P3_reuse_requires_two_exact_nonproduction_source_equivalence':True,
        'all_historical_source_maps_same_freeze':False,'required_final_segments':['offline','legacy4','original_typed'],
        'future_actual_segment_PASS_is_NOT_a_freeze_prerequisite':True,
        'actual_full_or_GUI_execution_claimed':False,'available_checks_passed_claimed':False,
        'complete_repository_validation_claimed':False,'private_state_included':False}
    again=source_state(meta,common,old)
    if (again!=(live,supp,native,delta) or prior_archives(meta)!=archives):raise ValueError('Input drift during declaration')
    prepared(a.expected_parent_commit,a.preparation_sha256);write_new(FREEZE,record)
    print(json.dumps({'freeze_relative':FREEZE.relative_to(ROOT).as_posix(),'freeze_sha256':sha(FREEZE),
        'runtime_started':False,'passed_claimed':False},ensure_ascii=False))

if __name__=='__main__':main()
