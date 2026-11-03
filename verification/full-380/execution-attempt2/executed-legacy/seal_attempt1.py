"""Seal actual failed attempt1 evidence and exact used tool bytes, never overwrite it."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD=ROOT/'.cache/full275-legacy-bundle'
OUT=HERE/'attempt1-original-seal'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise ValueError('Retain existing failure seal; do not overwrite')
    actual_paths=json.loads((ROOT/'.cache/full275-current-execution-paths.json').read_bytes())
    source=Path(actual_paths['legacy_actual']).resolve()
    status=Path(actual_paths['legacy_status']).resolve()
    supervisor=json.loads(status.read_bytes())
    if supervisor['status']!='completed' or supervisor['child_primary_exit']!=1 or supervisor['timed_out']:
        raise ValueError('Expected actual terminal attempt1 failure was not verified')
    closure=json.loads((source/'native275-launcher-closure.json').read_bytes())
    receipt=json.loads((source/'wine-ui-100.json').read_bytes())
    if receipt['passed'] or closure['source_drift'] or closure['executed_tool_drift']:
        raise ValueError('Actual failure or exact used-source closure does not match')
    binding=json.loads((OLD/'activation275.json').read_bytes())
    for name,expected in binding['execution_tools_sha256'].items():
        if sha(OLD/name)!=expected:raise ValueError('Used attempt1 tool source changed: '+name)
    OUT.mkdir(parents=True,exist_ok=False)
    manifest={}
    def copy_tree(source_folder,target_folder):
        for p in sorted(source_folder.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            relative=p.relative_to(source_folder);target=target_folder/relative
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
            if sha(target)!=sha(p):raise ValueError('Failure archive copy did not preserve exact bytes')
            manifest[target.relative_to(OUT).as_posix()]={'bytes':target.stat().st_size,'sha256':sha(target)}
    copy_tree(source,OUT/'actual')
    copy_tree(OLD,OUT/'used-tools')
    for p in (status,status.with_name(status.name+'.stdout.log'),status.with_name(status.name+'.stderr.log')):
        target=OUT/p.name;shutil.copyfile(p,target)
        manifest[target.relative_to(OUT).as_posix()]={'bytes':target.stat().st_size,'sha256':sha(target)}
    freeze=ROOT/binding['root_freeze_relative'];target=OUT/'root-declared-source-freeze.json'
    shutil.copyfile(freeze,target);manifest[target.name]={'bytes':target.stat().st_size,'sha256':sha(target)}
    if sha(target)!=binding['root_freeze_sha256']:raise ValueError('Root freeze source bytes differ')
    record={'kind':'SECTION275_ACTUAL_LEGACY_ATTEMPT1_FAILURE_AND_USED_SOURCE_SEAL',
            'source_freeze_sha256':sha(target),'actual_child_exit':supervisor['child_primary_exit'],
            'actual_supervisor_exit':supervisor['supervisor_exit'],'timed_out':False,
            'actual_completed_appends':len(receipt['checks']),'passed':False,
            'failure':receipt['failure'],'source_drift':closure['source_drift'],
            'qt_cleanup':closure['qt_cleanup'],'raw_originals':manifest,
            'calculation_or_game_api_result_rewritten':False,'private_state_accessed':False,
            'game_operations':0,'chat_requests':0}
    (OUT/'seal.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'sealed':True,'actual_appends':record['actual_completed_appends'],
                      'raw_files':len(manifest),'failure':receipt['failure']['type'],
                      'source_drift':closure['source_drift']},ensure_ascii=False))


if __name__=='__main__':main()
