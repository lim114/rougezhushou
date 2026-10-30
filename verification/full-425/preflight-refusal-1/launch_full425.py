"""Explicit future425 launch, gated on installed source and actual functional checks."""
from pathlib import Path
from hashlib import sha256
import argparse,json,re,runpy,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]

def digest(path):return sha256(path.read_bytes()).hexdigest()
def write_new(path,value):
    assert not path.exists();path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args();assert args.execute
    cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==424 and cp['last_verified_cloud_save']['section']==424
    prior=json.loads((R/'verification/full-410/summary.json').read_bytes());assert prior['available_checks_passed']and prior['scope_not_reduced']and prior['actual_root_controller_exit']==0
    spec=json.loads((R/'.cache/spec425.json').read_bytes());base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));source=base['source']()
    unit,native,process=[json.loads((R/spec[key]).read_bytes())for key in('unit_receipt','native_receipt','native_process_receipt')]
    assert all(row['passed']and row['source_sha256_after']==source and row['source_sha256_before']==source for row in(unit,native,process))
    assert native['section']==425 and native['qpa']=='windows'and not any(native['external_operation_attempts'].values())
    folder=R/'.cache/full425-prepared/attempt-1';assert not folder.exists()
    candidate=R/'.cache/full425-candidate-repaired/attempt-1';ready=json.loads((candidate/'CONTROLLER_READY425.json').read_bytes())
    for name,pin in ready['files'].items():assert digest(candidate/name)==pin['sha256']and(candidate/name).stat().st_size==pin['bytes']
    shutil.copytree(candidate,folder)
    post=R/'.cache/full425-post';assert not post.exists();shutil.copytree(R/'.cache/full425-post-candidate',post)
    subprocess.run([sys.executable,'-B','-X','utf8',str(R/'.cache/build_full425_prior_visual_registry.py')],cwd=R,check=True)
    # Only already-public exact canonical files, never private cache discovery.
    sys.path.insert(0,str(folder));common=runpy.run_path(str(folder/'full425_common.py'))
    for binding in common['CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS']:
        name=binding['public_path']
        if not name.startswith('verification/full-425/'):continue
        target=R/name;original=R/name.replace('verification/full-425/','verification/full-410/',1)
        assert digest(original)==binding['sha256']and original.stat().st_size==binding['bytes']and not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
    count=int(re.search(r'Ran (\d+) tests?',(R/spec['unit_receipt']).with_name('stderr.txt').read_text('utf8'))[1])
    necessary={**unit,'section':425,'kind':'functional425_actual_unittest_process_with_count','methods_ran':count,'underlying_process_receipt':base['pin'](spec['unit_receipt']),'original_receipt_not_rewritten':True,'qt_exec_exit_invented':False}
    necessary_path=R/'verification/sections/425-functional-necessary.json';write_new(necessary_path,necessary)
    input_path=R/'verification/sections/425-full-input.json';write_new(input_path,{'section':425,'references':{'necessary':necessary_path.relative_to(R).as_posix(),'native':spec['native_receipt'],'native_process':spec['native_process_receipt']}})
    parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();python=str(R/'.venv/Scripts/python.exe')
    subprocess.run([python,'-B','-X','utf8',str(folder/'declare_current425.py'),'--source-finalized','--expected-parent-commit',parent,'--functional-receipts',str(input_path)],cwd=R,check=True)
    freeze=R/'verification/full-425/source-freeze-attempt1.json';freeze_sha=digest(freeze)
    subprocess.run([python,'-B','-X','utf8',str(folder/'activate_full425.py'),'--activate','--expected-parent-commit',parent,'--freeze-sha256',freeze_sha],cwd=R,check=True)
    activation_sha=digest(folder/'activation425.json');write_new(R/'.cache/full425-launch-input.json',{'parent':parent,'freeze_sha256':freeze_sha,'activation_sha256':activation_sha,'actual_full_started_yet':False})
    return subprocess.call([python,'-B','-X','utf8',str(folder/'run_owned_full425.py'),'--execute','--expected-parent-commit',parent,'--freeze-sha256',freeze_sha,'--activation-sha256',activation_sha],cwd=R)

if __name__=='__main__':raise SystemExit(main())
