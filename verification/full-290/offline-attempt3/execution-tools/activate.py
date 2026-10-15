"""Bind immutable legacy template to FINAL A3 full/native inputs; never runs GUI."""
import argparse,json,shutil
from final_common import BASE,ROOT,TEMPLATE,BOUND,ACTIVATION,FREEZE,frozen,binding_recipe,sha,write_new,hashbytes

def main():
    p=argparse.ArgumentParser();p.add_argument('--bind-final-A3',action='store_true',required=True)
    p.add_argument('--expected-parent-commit',required=True);p.add_argument('--preparation-sha256',required=True)
    p.add_argument('--freeze-sha256',required=True);a=p.parse_args()
    if ACTIVATION.exists() or BOUND.exists():raise ValueError('Never replace an activation or execution bundle')
    meta,common,execution,data=frozen(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256)
    recipe=binding_recipe(data,a.freeze_sha256,a.expected_parent_commit)
    BOUND.mkdir()
    tools={}
    for n,oldsha in meta['template_bundle_sha256'].items():
        raw=recipe.get(n,(TEMPLATE/n).read_bytes());target=BOUND/n;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(raw)
        tools[n]=hashbytes(raw)
    record={'status':'CURRENT290_FINAL_A3_BOUND_NOT_EXECUTED','binding_ready':True,'runtime_executed':False,
        'actual_section':290,'actual_validation_attempt':3,'actual_legacy_execution_ordinal':4,
        'allowed_modes':['legacy'],'tested_worktree_parent_commit':a.expected_parent_commit,
        'root_freeze_relative':FREEZE.relative_to(ROOT).as_posix(),'root_freeze_sha256':a.freeze_sha256,
        'preparation_sha256':a.preparation_sha256,'execution_tools_sha256':tools,'scope_not_reduced':True,
        'new_offline_and_legacy_share_one_final_freeze':True,'old_raw_labels_preserved_not_execution_authority':True,
        'metadata_platform_source':'sys.platform and sys.getwindowsversion raw; avoids optional receipt WMI query',
        'fix_is_not_proof_of_previous_native_crash_root_cause':True,
        'timeouts_seconds':{'legacy_internal':3600,'legacy_supervisor':3690,'legacy_outer':3780,
                            'offline_supervisor':3600,'offline_outer':3690},
        'actual_pass_claimed':False}
    frozen(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256)
    write_new(ACTIVATION,record)
    with (BOUND/'activation-final-A3.json').open('xb') as f:f.write(ACTIVATION.read_bytes())
    print(json.dumps({'activation_sha256':sha(ACTIVATION),'bound_tools':len(tools),'runtime_started':False,'passed_claimed':False}))

if __name__=='__main__':main()
