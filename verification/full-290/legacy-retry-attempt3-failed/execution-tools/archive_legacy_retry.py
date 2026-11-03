"""Exact public successful legacy retry + independent original typed readback archive."""
import argparse,json,shutil
from pathlib import Path
from retry_common import BASE,ROOT,BUNDLE,FREEZE,FREEZE_SHA,ACTIVATION,activated,owned_retry,closed,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--seal-closed-legacy-retry-and-original-readback',action='store_true',required=True)
    p.add_argument('--container',type=Path,required=True);p.add_argument('--expected-parent-commit',required=True)
    p.add_argument('--preparation-sha256',required=True);p.add_argument('--activation-sha256',required=True);a=p.parse_args()
    meta,common,execution,frozen,binding=activated(a.expected_parent_commit,a.preparation_sha256,a.activation_sha256)
    source,own=owned_retry(a.container,a.expected_parent_commit,a.preparation_sha256,a.activation_sha256)
    for name,ledger_name in (('legacy','orchestration.json'),('readback','readback/readback-orchestration.json')):
        observed,sup,details=closed(source/name,execution)
        ledger=json.loads((source/ledger_name).read_bytes())
        if (ledger.get('status')!='terminal' or observed['actual_observed_popen_exit']!=0
                or sup['child_primary_exit']!=0 or sup['timed_out'] is not False
                or sup['supervisor_sha256']!=sha(BASE/'supervisor3690.py')
                or observed.get('argv')!=ledger.get('argv') or sup.get('argv')!=ledger.get('argv',[])[9:]):
            raise ValueError('Full retry and original independent readback must both actually pass')
    audit=json.loads((source/'legacy/independent-saved-readback-audit.json').read_bytes())
    if (audit.get('passed') is not True or audit.get('complete_runtime_checks')!=4283
            or audit.get('saved_rows')!=52 or audit.get('current_revised_assertions')!=862
            or audit.get('original552_maintry_sha256')!='11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
            or audit.get('readonly_trace_empty_rows_not_invented')!=26):
        raise ValueError('Complete original typed scope is required, never a partial substitute')
    destination=ROOT/'verification/full-290/legacy-retry-attempt3'
    if destination.exists():raise ValueError('Never replace an actual legacy-retry archive')
    destination.mkdir(parents=True)
    manifest={'kind':'FULL290_EXACT_LEGACY_RETRY3_AND_ORIGINAL_TYPED_ARCHIVE',
        'files':{},'source_freeze_sha256':FREEZE_SHA,'parent_commit':a.expected_parent_commit,
        'source_container':str(source),'actual_validation_segment':'legacy_retry',
        'actual_legacy_execution_ordinal':3,'activation_sha256':a.activation_sha256,
        'preparation_sha256':a.preparation_sha256,'actual_typed_passed':True,
        'inherited_raw_labels_preserved_not_execution_authority':True,
        'all_other_segments_passed_or_single_run_claimed':False,'PNG_visual_inspection_claimed':False,
        'private_state_or_arbitrary_tree_copied':False}
    def copy(path,name,boundary):
        rel=Path(name)
        if (rel.is_absolute() or '..' in rel.parts or path.is_symlink() or not path.is_file()
                or not path.resolve().is_relative_to(boundary.resolve())):raise ValueError('Exact regular public file only')
        before=sha(path);target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True)
        with path.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
        if sha(path)!=before or sha(target)!=before:raise ValueError('Original changed during exact copy')
        manifest['files'][rel.as_posix()]={'sha256':before,'bytes':target.stat().st_size}
    for name in ('owned-execution.json','orchestration.json'):
        copy(source/name,name,source)
    controls=('controller-process.json','controller-supervisor.stdout.log','controller-supervisor.stderr.log',
        'supervisor.json','supervisor.json.stdout.log','supervisor.json.stderr.log','process.exit','process-exit-origin.json')
    for name in ('legacy','readback'):
        for filename in controls:copy(source/name/filename,name+'/'+filename,source/name)
    copy(source/'readback/readback-orchestration.json','readback/readback-orchestration.json',source)
    copy(source/'legacy/independent-saved-readback-audit.json','legacy/independent-saved-readback-audit.json',source)
    actual=source/'legacy/actual'
    if actual.is_symlink() or not actual.resolve().is_relative_to(source):raise ValueError('Actual output escaped')
    for path in sorted(actual.iterdir()):
        if not path.is_file() or path.is_symlink() or path.suffix not in ('.json','.log','.png','.gz'):
            raise ValueError('Unexpected nested output must be reviewed')
        copy(path,'legacy/actual/'+path.name,actual)
    for name in meta['new_tools_sha256']:
        copy(BASE/name,'execution-tools/'+name,BASE)
    for name in meta['candidate_bundle_tools_sha256']:
        copy(BUNDLE/name,'executed-legacy-bundle/'+name,BUNDLE)
    for name in ('preparation.json','READY.json','static-preparation-evidence.json','execution-once.json'):
        copy(BASE/name,'execution-tools/'+name,BASE)
    copy(ACTIVATION,'executed-legacy-bundle/activation-retry290.json',BASE)
    copy(FREEZE,'root-source-freeze-repair-original.json',ROOT)
    for name in ('execution-attempt2','p3-supplementary-attempt2'):
        copy(ROOT/'verification/full-290'/name/'archive-manifest.json','prior-A2/'+name+'-archive-manifest.json',ROOT)
    activated(a.expected_parent_commit,a.preparation_sha256,a.activation_sha256)
    write_new(destination/'archive-manifest.json',manifest)
    print(json.dumps({'archive':str(destination),'manifest_sha256':sha(destination/'archive-manifest.json'),
        'files':len(manifest['files']),'actual_typed_passed':True,'combined_pass_claimed':False},ensure_ascii=False))

if __name__=='__main__':main()
