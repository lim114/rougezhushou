"""Add already-real root direct reviews, without changing older origins or methods."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,struct
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());parent=R/'verification/full-440/public-prior-visual-registry-v3.json';data=json.loads(parent.read_bytes());output=R/'verification/full-440/public-prior-visual-registry-v4.json';assert not output.exists();proofs=[];count=0
for proof_path in sorted((R/'verification/full-440/preterminal-root-direct-review-attempt4').glob('*.json')):
    proof=json.loads(proof_path.read_bytes());assert proof['review_actor']=='/root'and not proof['blocking_visual_issues']and proof['viewing_performed_by_this_script']is False and proof['root_recorded_only_after_actual_tool_viewing']is True
    proof_name=proof_path.relative_to(R).as_posix();proof_sha=sha256(proof_path.read_bytes()).hexdigest();proofs.append({'file':proof_name,'sha256':proof_sha,'bytes':proof_path.stat().st_size})
    for index,row in enumerate(proof['images']):
        assert row['reviewed']and row['method']=='direct_view'and row['review_actor']=='/root'and row['actual_new_view_image_called']and row['actual_pixels_visually_reviewed']and row['visual_blocking_issue']is False
        path=R/row['file'];raw=path.read_bytes();pin=sha256(raw).hexdigest();assert pin==row['sha256']and pin not in data['entries'];assert raw.startswith(b'\x89PNG\r\n\x1a\n')
        origin={'actor':'/root','review_method':'root_direct_visual_review','original_png':row['file'],'leaf_proof':proof_name,'leaf_proof_sha256':proof_sha}
        chain={'proof':proof_name,'proof_sha256':proof_sha,'row':['images',index],'png':row['file'],'png_sha256':pin,'method':'root_direct_visual_review'}
        alias={'png':row['file'],'proof':proof_name,'proof_sha256':proof_sha,'row':['images',index],'actual_original_reviewer':'/root','actual_original_review_method':'root_direct_visual_review','evidence_chain':[chain]}
        data['entries'][pin]={'sha256':pin,'bytes':len(raw),'size':list(struct.unpack('>II',raw[16:24])),'review_origins':[origin],'preferred_origin':origin,'verified_public_png_aliases':[alias]};count+=1
data['historical_before_preterminal_extension']={key:data.get(key)for key in('built_at_utc','registered_unique_png_sha256','accepted_proof_rows','actual_reviewers','new_original_PNG_view_image_calls','no_new_visual_inspection_claim')}
data['actual_reviewers']=dict(data['actual_reviewers']);data['actual_reviewers']['/root']=data['actual_reviewers'].get('/root',0)+count
data.update(registered_unique_png_sha256=len(data['entries']),accepted_proof_rows=data['accepted_proof_rows']+count,new_original_PNG_view_image_calls=count,no_new_visual_inspection_claim=False)
extension={'actor':'/root','at_utc':datetime.now(timezone.utc).isoformat(),'parent_registry':{'file':parent.relative_to(R).as_posix(),'sha256':sha256(parent.read_bytes()).hexdigest()},'new_actual_direct_root_view_calls':count,'proofs':proofs,'registry_builder_itself_viewed_images':False,'earlier_entries_origins_and_methods_unchanged':True,'full_suite_success_not_claimed':True,'scope':'Exact prior viewing of already-terminal component PNGs in this same440 attempt. Final reuse requires whole archived PNG byte equality; interaction/mechanism/root-PASS is never inferred.'}
correction_path=R/'verification/full-440/preterminal-review-order-correction-attempt4.json'
if correction_path.exists():
    correction=json.loads(correction_path.read_bytes())
    assert correction['root_has_now_actually_seen_each_original']is True
    assert sha256((R/correction['original_record']).read_bytes()).hexdigest()==correction['original_sha256']
    assert all(sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256'] for row in correction['images'])
    extension['record_order_corrections']=[{'file':correction_path.relative_to(R).as_posix(),'sha256':sha256(correction_path.read_bytes()).hexdigest(),'limits':'The batch9 second image was actually reviewed after the original recorder; the separate later confirmation is retained. No claim of pre-recorder viewing for that image.'}]
data['full440_preterminal_extension']=extension;data['public_derivation']['full440_preterminal_extension']=extension
output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'registry':output.relative_to(R).as_posix(),'sha256':sha256(output.read_bytes()).hexdigest(),'added_actual_direct_views':count,'unique_PNGs':len(data['entries'])}))
