"""Root-only declaration for independent full legacy retry; no GUI execution."""
import argparse,json
from retry_common import BASE,ROOT,ACTIVATION,FREEZE,FREEZE_SHA,prepared,prior_closed_and_sealed,sha,write_new

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--declare-legacy-retry-after-sealed-A2',action='store_true',required=True)
    p.add_argument('--expected-parent-commit',required=True);p.add_argument('--preparation-sha256',required=True)
    a=p.parse_args()
    if ACTIVATION.exists():raise ValueError('Never replace an activation record')
    meta,common,execution,frozen=prepared(a.expected_parent_commit,a.preparation_sha256)
    prior=prior_closed_and_sealed(a.expected_parent_commit,execution)
    record={'status':'CURRENT290_LEGACY_RETRY_BOUND_NOT_EXECUTED','binding_ready':True,
        'runtime_executed':False,'actual_section':290,'validation_segment':'legacy_retry',
        'actual_legacy_execution_ordinal':3,'allowed_modes':['legacy'],
        'tested_worktree_parent_commit':a.expected_parent_commit,
        'root_freeze_relative':FREEZE.relative_to(ROOT).as_posix(),'root_freeze_sha256':FREEZE_SHA,
        'execution_tools_sha256':meta['candidate_bundle_tools_sha256'],'scope_not_reduced':True,
        'preparation_sha256':a.preparation_sha256,'prior_A2_closed_and_sealed':prior,
        'full_scope':{'saved_states':52,'checks':4283,'assert_AST':862,'maintry_asserts':552,
                      'projections':42,'exact_admissions':10,'empty_traces':26},
        'timeouts_seconds':{'fixture_internal':3600,'owned_supervisor':3690,'controller_outer':3780},
        'inherited_raw_261_275_ATTEMPT2_labels_preserved_not_execution_authority':True,
        'actual_pass_claimed':False}
    prepared(a.expected_parent_commit,a.preparation_sha256)
    write_new(ACTIVATION,record)
    print(json.dumps({'activation_sha256':sha(ACTIVATION),'runtime_started':False,'passed_claimed':False}))

if __name__=='__main__':main()
