"""Exact public final A3 output archive, only after actual success of that segment."""
import argparse,json,shutil
from pathlib import Path
from final_common import BASE,ROOT,BOUND,TEMPLATE,FREEZE,ACTIVATION,bound,owned_segment,closed,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--seal-passed-final-A3-segment',choices=('offline','legacy'),required=True)
    p.add_argument('--container',type=Path,required=True)
    for k in ('expected-parent-commit','preparation-sha256','freeze-sha256','activation-sha256'):p.add_argument('--'+k,required=True)
    a=p.parse_args();mode=a.seal_passed_final_A3_segment
    meta,common,execution,data,act=bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    source,own=owned_segment(a.container,mode,a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    ledger=json.loads((source/'orchestration.json').read_bytes());observed,sup,details=closed(source/mode,execution)
    if (ledger.get('status')!='terminal' or observed['actual_observed_popen_exit']!=0 or sup['child_primary_exit']!=0
            or sup['timed_out'] is not False or sup['supervisor_sha256']!=sha(BASE/'supervisor3690.py')
            or observed.get('argv')!=ledger.get('argv') or sup.get('argv')!=ledger.get('argv',[])[9:]):
        raise ValueError('Actual successful segment Popen/job/source closure required')
    if mode=='offline':
        raw=json.loads((source/'offline/actual/windows-offline.json').read_bytes())
        closure=json.loads((source/'offline/actual/final-A3-offline-source-closure.json').read_bytes())
        if (raw.get('available_checks_passed') is not True or raw.get('source_sha256')!=data['source_sha256']
                or raw.get('selectors')!=data['selectors'] or closure.get('offline_available_checks_passed') is not True
                or closure.get('actual_suite_exit')!=0 or closure.get('source_drift')!=[]
                or closure.get('root_freeze_sha256')!=a.freeze_sha256):raise ValueError('Complete430-selector offline actual result required')
        archive='offline-attempt3'
    else:
        audit=json.loads((source/'legacy/independent-saved-readback-audit.json').read_bytes())
        obs2,sup2,_=closed(source/'readback',execution);r=json.loads((source/'readback/readback-orchestration.json').read_bytes())
        if (r.get('status')!='terminal' or obs2['actual_observed_popen_exit']!=0 or sup2['child_primary_exit']!=0
                or sup2['timed_out'] is not False or sup2['supervisor_sha256']!=sha(BASE/'supervisor3690.py')
                or obs2.get('argv')!=r.get('argv') or sup2.get('argv')!=r.get('argv',[])[9:]
                or audit.get('passed') is not True or audit.get('complete_runtime_checks')!=4283
                or audit.get('saved_rows')!=52 or audit.get('current_revised_assertions')!=862
                or audit.get('readonly_trace_empty_rows_not_invented')!=26
                or audit.get('original552_maintry_sha256')!='11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'):
            raise ValueError('Actual original complete52-state typed readback required')
        archive='legacy-retry-attempt4'
    destination=ROOT/'verification/full-290'/archive
    if destination.exists():raise ValueError('Never overwrite an archive')
    destination.mkdir(parents=True)
    manifest={'kind':'FULL290_FINAL_A3_EXACT_SEGMENT_ARCHIVE','files':{},'mode':mode,
        'source_freeze_sha256':a.freeze_sha256,'parent_commit':a.expected_parent_commit,'source_container':str(source),
        'preparation_sha256':a.preparation_sha256,'activation_sha256':a.activation_sha256,
        'actual_validation_attempt':3,'actual_legacy_execution_ordinal':4 if mode=='legacy' else None,
        'actual_segment_passed':True,'actual_original_typed_passed':mode=='legacy',
        'PNG_visual_inspection_claimed':False,'all_historical_segments_same_freeze':False,
        'combined_full_pass_claimed':False,'private_or_arbitrary_tree_copied':False}
    def copy(path,name,boundary):
        rel=Path(name)
        if (rel.is_absolute() or '..' in rel.parts or path.is_symlink() or not path.is_file()
                or not path.resolve().is_relative_to(boundary.resolve())):raise ValueError('Exact regular public output only')
        value=sha(path);target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True)
        with path.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
        if sha(path)!=value or sha(target)!=value:raise ValueError('Original changed during archive copy')
        manifest['files'][rel.as_posix()]={'sha256':value,'bytes':target.stat().st_size}
    for n in ('owned-execution.json','orchestration.json'):copy(source/n,n,source)
    names=[mode]+(['readback'] if mode=='legacy' else [])
    controls=('controller-process.json','controller-supervisor.stdout.log','controller-supervisor.stderr.log',
        'supervisor.json','supervisor.json.stdout.log','supervisor.json.stderr.log','process.exit','process-exit-origin.json')
    for name in names:
        for n in controls:copy(source/name/n,name+'/'+n,source/name)
    if mode=='legacy':
        copy(source/'readback/readback-orchestration.json','readback/readback-orchestration.json',source)
        copy(source/'legacy/independent-saved-readback-audit.json','legacy/independent-saved-readback-audit.json',source)
    actual=source/mode/'actual'
    for path in sorted(actual.iterdir()):
        if not path.is_file() or path.is_symlink() or path.suffix not in ('.json','.log','.png','.gz'):
            raise ValueError('Unexpected nested/other actual output requires review')
        copy(path,mode+'/actual/'+path.name,actual)
    for n in meta['new_tools_sha256']:copy(BASE/n,'execution-tools/'+n,BASE)
    for n in ('preparation.json','READY.json','static-preparation-evidence.json',mode+'-once.json'):
        copy(BASE/n,'execution-tools/'+n,BASE)
    for n in act['execution_tools_sha256']:copy(BOUND/n,'executed-legacy-bundle/'+n,BOUND)
    for n in meta['template_bundle_sha256']:copy(TEMPLATE/n,'immutable-template-bundle/'+n,TEMPLATE)
    copy(ACTIVATION,'activation-final-A3.json',BASE)
    copy(FREEZE,'root-source-freeze-final-A3.json',ROOT)
    for n in meta['necessary_module_public_sha256']:copy(ROOT/n,'necessary-module-public/'+n,ROOT)
    for n in meta['prior_archive_manifest_sha256']:
        copy(ROOT/'verification/full-290'/n/'archive-manifest.json','prior-archive-manifests/'+n+'.json',ROOT)
    bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    write_new(destination/'archive-manifest.json',manifest)
    print(json.dumps({'archive':str(destination),'manifest_sha256':sha(destination/'archive-manifest.json'),
        'mode':mode,'segment_passed':True,'combined_pass_claimed':False},ensure_ascii=False))

if __name__=='__main__':main()
