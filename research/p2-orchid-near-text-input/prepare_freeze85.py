"""Freeze successful author source/results; copy only exact sealed source evidence."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil

OUT=Path(__file__).parent
SOURCE=Path('/workspace/.continuation/p2-orchid-boolean-consumer-085-independent-source')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=json.loads((OUT/'baseline-freeze085.json').read_text())
for name,row in freeze['public_source_files'].items():
 assert sha(OUT/'baseline'/name)==row['sha256'],name
 if name!='rouge/damage.py':assert sha(OUT/'draft'/name)==row['sha256'],name
assert sha(OUT/'draft/rouge/damage.py')==freeze['draft_damage_sha256']
assert 'Ran 9 tests' in (OUT/'new-tests085.log').read_text() and (OUT/'new-tests085.log').read_text().rstrip().endswith('OK')
related=json.loads((OUT/'related-tests-receipt085.json').read_text())
assert related['passed'] and related['tests_run']==40 and related['skipped']==0
comp=json.loads((OUT/'matrix-comparison085.json').read_text())
assert comp['pairs']==197 and comp['classifications']=={'text_rejected':94,'same_success':79,'same_error':24}
assert sha(OUT/'public-baseline085.json')==comp['baseline_sha256']
assert sha(OUT/'public-draft085.json')==comp['draft_sha256']

manifest=SOURCE/'public-artifacts-manifest.json'
assert sha(manifest)=='a5047e145b400668b7f27f17ba9087a17b56945d79f567856b0088b619364962'
rows=json.loads(manifest.read_text())['files'];assert len(rows)==22
for row in rows:
 path=Path(row['source_path']);assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],str(path)
for row in rows:
 target=OUT/'source-only'/row['archive_path'];target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(row['source_path'],target)
 assert sha(target)==row['sha256']
shutil.copyfile(manifest,OUT/'source-only/public-artifacts-manifest.json')

patch=''.join(difflib.unified_diff((OUT/'baseline/rouge/damage.py').read_bytes().decode().splitlines(keepends=True),
 (OUT/'draft/rouge/damage.py').read_bytes().decode().splitlines(keepends=True),fromfile='a/rouge/damage.py',tofile='b/rouge/damage.py',n=3))
test=OUT/'draft/tests/test_orchid_near_text_input.py'
patch+=''.join(difflib.unified_diff([],test.read_text().splitlines(keepends=True),fromfile='/dev/null',tofile='b/tests/test_orchid_near_text_input.py',n=3))
(OUT/'section85.patch').write_bytes(patch.encode())

result={'status':'explicit_author_source_tests_matrix_frozen_formal_review_pending',
 'fixed_commit':freeze['fixed_commit'],'baseline_public_source_count':len(freeze['public_source_files']),
 'unchanged_old_draft_public_files_checked':len(freeze['public_source_files'])-1,
 'allowed_changed_files':['rouge/damage.py','tests/test_orchid_near_text_input.py'],
 'patch_sha256':sha(OUT/'section85.patch'),'draft_damage_sha256':sha(OUT/'draft/rouge/damage.py'),
 'new_test_sha256':sha(test),'baseline_json_sha256':sha(OUT/'public-baseline085.json'),
 'draft_json_sha256':sha(OUT/'public-draft085.json'),'comparison_sha256':sha(OUT/'matrix-comparison085.json'),
 'source_handoff_sha256':sha(SOURCE/'handoff.json'),'source_manifest_sha256':sha(manifest),
 'new_tests':9,'old_related_tests':40,'failures':0,'errors':0,'skipped':0,
 'matrix_pairs':197,'matrix_calculate_damage_calls':394,'matrix_classes':comp['classifications'],
 'old_related_calculate_damage_calls':1328,'new_test_call_counter':'Not instrumented; no aggregateall-public-calltotal is claimed.',
 'public_baseline_historical_reuse':False,'original_record_comparison_helper_calls':94,
 'changed_condition':'Selectednamed Orchid near_previous_deployment strings only; no decoding.',
 'integration':'Surgical late-hunk insertion only, preserve root83/84 late guards; never overwrite older complete damage.py. Root registers test module in verify_cloud.',
 'GUI_executed':False,'Wine_executed':False,'tracked_edits':False}
(OUT/'author-freeze085.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
