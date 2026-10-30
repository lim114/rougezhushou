"""Queue exact PNGs from already-terminal owned components; never claim full PASS."""
from pathlib import Path
from hashlib import sha256
import json,sys
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());B=R/'.cache/full440-prepared/attempt-4'
sys.path.insert(0,str(B));from full440_common import bound,sha
launch=json.loads((R/'.cache/full440-launch-input-attempt4.json').read_bytes());PARENT=launch['parent'];FREEZE=launch['freeze_sha256'];ACTIVATION=launch['activation_sha256']
bound(PARENT,FREEZE,ACTIVATION)
once=json.loads((B/'full440-once.json').read_bytes());container=Path(once['container']);authority=json.loads((container/'owned-execution.json').read_bytes());assert authority['root_freeze_sha256']==FREEZE and authority['activation_sha256']==ACTIVATION
ledger=json.loads((container/'orchestration.json').read_bytes());registry_path=R/'verification/full-440/public-prior-visual-registry-v3.json';registry=json.loads(registry_path.read_bytes());known=set(registry['entries'])
queue_path=R/'.cache/440-attempt4-preterminal-image-queue.json';queue=json.loads(queue_path.read_bytes())if queue_path.exists()else{'copied_sha256':{},'batches':[]}
rows=[]
for step in ledger['steps']:
    if step['status'].startswith('not_run_'):
        assert step['name']=='legacy_typed' and not(container/step['name']).exists();continue
    assert step['status']=='terminal'and step['owned_job_no_live_execution_verified']is True
    mode=step['name'];folder=container/mode/'actual'
    for path in sorted(folder.glob('*.png')):
        assert path.is_file()and not path.is_symlink();raw=path.read_bytes();pin=sha256(raw).hexdigest()
        if pin in known or pin in queue['copied_sha256']:continue
        destination=R/'verification/full-440/preterminal-visual-originals-attempt4'/mode/path.name;assert not destination.exists();destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
        row={'file':destination.relative_to(R).as_posix(),'sha256':pin,'bytes':len(raw),'actual_source_file':str(path),'component':mode,'actual_component_primary_exit':step['child_primary_exit'],'step_receipt_file':str(container/mode/'step.json'),'step_receipt_sha256':sha(container/mode/'step.json'),'full_root_execution_terminal_or_passed_claimed':False,'whole_original_png_bytes_preserved':True,'reviewed':False}
        rows.append(row);queue['copied_sha256'][pin]=row
if rows:
    index=len(queue['batches'])+1;manifest=R/f'verification/full-440/preterminal-visual-queue-attempt4/batch{index}.json';assert not manifest.exists();manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps({'section':440,'attempt':4,'kind':'exact_terminal_component_pngs_pending_root_visual_review','source_freeze_sha256':FREEZE,'activation_sha256':ACTIVATION,'actual_root_status_at_queue':json.loads((B/'root-launch/controller-process.json').read_bytes())['status'],'images':rows,'tests_or_windows_started':False,'private_state_read_copied_or_restored':False,'full_scope_success_not_claimed':True},ensure_ascii=False,indent=2)+'\n','utf8');queue['batches'].append(manifest.relative_to(R).as_posix());queue_path.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'new_unique_pngs_queued':len(rows),'pending_unique_copies':len(queue['copied_sha256']),'latest_manifest':queue['batches'][-1]if queue['batches']else None,'full_scope_not_complete':ledger['status']!='all_required_components_terminal'},ensure_ascii=False))
