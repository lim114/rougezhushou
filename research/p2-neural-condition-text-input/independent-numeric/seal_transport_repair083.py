"""Exact header-only packaging repair review; preserve all earlier sealed files."""
from pathlib import Path
import copy
import hashlib
import json

OUT=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-neural-condition-text-input-083')
SIDE=OUT/'packaging-repair083'
SIDE.mkdir()
def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
initial_manifest=OUT/'public-artifacts-manifest.json'
assert sha(initial_manifest.read_bytes())=='e7f64d1f4ae5cf46700174d44e5f4c1a2c59c03d7fa6bd2a99046881e95c8721'
original_rows=json.loads(initial_manifest.read_bytes())['files']
assert len(original_rows)==118
for row in original_rows:
    data=Path(row['source_path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
old_patch=(OUT/'fixed-author-inputs/draft.patch').read_bytes()
new_patch=(AUTHOR/'draft.patch').read_bytes()
assert sha(old_patch)=='b0883fc2abbc9d7d26c538c84c6ee6a342ada5ed68e8fca42237c2b0da93a403'
assert sha(new_patch)=='4d23463e553dcca35e10ebba701512a146d570cc5da8f6c861c451e22b59d246'
assert len(old_patch)==789 and len(new_patch)==793
repairs=[(b'diff --git arouge/damage.py brouge/damage.py\n',b'diff --git a/rouge/damage.py b/rouge/damage.py\n'),
         (b'--- arouge/damage.py\n',b'--- a/rouge/damage.py\n'),
         (b'+++ brouge/damage.py\n',b'+++ b/rouge/damage.py\n')]
repaired=old_patch
for before,after in repairs:
    assert repaired.count(before)==1
    repaired=repaired.replace(before,after,1)
assert repaired==new_patch
assert old_patch[old_patch.index(b'@@'):]==new_patch[new_patch.index(b'@@'):]
old_formal=json.loads((OUT/'fixed-author-inputs/formal-draft-freeze083.json').read_bytes())
new_formal=json.loads((AUTHOR/'formal-draft-freeze083.json').read_bytes())
expected=copy.deepcopy(old_formal)
expected['files']['draft.patch']={'bytes':793,'sha256':sha(new_patch)}
expected['patch_sha256']=sha(new_patch)
expected['header_preparation_repaired']=True
assert new_formal==expected
assert (AUTHOR/'initial-preparation-patch-header083.patch').read_bytes()==old_patch
assert (AUTHOR/'initial-formal-draft-freeze083.json').read_bytes()==(OUT/'fixed-author-inputs/formal-draft-freeze083.json').read_bytes()
for rel in ['rouge/damage.py','rouge/operator_engine.py','tests/test_neural_condition_text_input.py']:
    current=(AUTHOR/'draft'/rel).read_bytes()
    original=(OUT/'fixed-author-inputs'/rel).read_bytes()
    assert current==original
    assert sha(current)==new_formal['files'][rel]['sha256']
transport=json.loads((AUTHOR/'source-only-transport083.json').read_bytes())
assert transport['passed']is True and transport['API_calls']==0 and transport['source_patch_only']is True
assert transport['patch_sha256']==sha(new_patch) and transport['numstat']=='5\t0\trouge/damage.py\n'
assert transport['new_test_sha256']=='9f57f7cf9351e21292f286d4dc2266873117534fefc38901c6423728b9af09ba'
assert Path(transport['new_test_source_path']).read_bytes()==(OUT/'fixed-author-inputs/tests/test_neural_condition_text_input.py').read_bytes()
apply_receipt=json.loads((AUTHOR/'root82-apply-check083.json').read_bytes())
assert apply_receipt['passed']is True and apply_receipt['returncode']==0 and apply_receipt['API_calls']==0
assert apply_receipt['attempt']==3 and apply_receipt['no_fourth_attempt']is True
bindings=[]
names=['draft.patch','formal-draft-freeze083.json','initial-preparation-patch-header083.patch',
       'initial-formal-draft-freeze083.json','patch-header-preparation083.json','root82-apply-check083.json',
       'source-only-transport083.json','preparation-diagnostics083.json']
for name in names:
    source=AUTHOR/name;data=source.read_bytes();target=SIDE/name
    with target.open('xb') as f:f.write(data)
    assert source.read_bytes()==data
    bindings.append({'source_path':str(source),'archive_path':str(target.relative_to(OUT)),'bytes':len(data),'sha256':sha(data)})
review={'status':'passed_header_only_transport_repair','API_calls':0,'tests_rerun':0,'apply_checks_rerun':0,
    'initial_118_manifest_sha256':sha(initial_manifest.read_bytes()),'initial_118_files_all_bytes_unchanged':True,
    'final_patch_sha256':sha(new_patch),'old_patch_sha256':sha(old_patch),
    'patch_length_delta':4,'exactly_three_header_lines_four_prefixes_repaired':True,
    'every_hunk_byte_unchanged':True,'damage_engine_and_frozen9tests_bytes_unchanged':True,
    'formal_freeze_only_patch_bytes_hash_and_repair_marker_changed':True,
    'root_source_only5add0delete_transport_bound':True,'root_prior_third_apply_check_receipt_bound_only':True,
    'new_test_transport':'Root copies exact independently-tested frozen new test bytes; source patch deliberately contains no test hunk.',
    'new_test_source_path':transport['new_test_source_path'],'new_test_archive_path':'fixed-author-inputs/tests/test_neural_condition_text_input.py',
    'new_test_sha256':transport['new_test_sha256'],'author_packaging_bindings':bindings,
    'prior_numerical_review_conclusions_unchanged':True,
    'independent_formal_actual_public_calls_remain':373,'source_history8_not_rerun':True,
    'tracked_mutations':False,'Qt':False,'Wine':False}
save(SIDE/'independent-transport-review083.json',review)
(SIDE/'NOTE.md').write_text('第83节最终传输补审：原118件已在作者header修复消息到达前封存，全部保持字节与哈希不变。最终补丁仅在三行header的四处a/、b/前缀增加四字节；所有@@之后hunk、damage、engine及已独立运行的9个新测试源字节不变。正式源补丁是5新增/0删除，仅damage；root另复制固定新测试文件。旧formal/patch与全部包装诊断原样保存，不改写先前测试记录。\n\n此补审仅静态读取和严格比较，0API、0重跑测试、0重跑applychecker；绑定作者已通过第三次apply-check和root接受的source-only合同。40配对、9新测试、432保存结果的独立结论不变，正式独立总373调用。请使用final-handoff.json与final-public-artifacts-manifest.json作为最终传输清单，原public-artifacts-manifest.json及handoff.json保留为修复前历史。\n',encoding='utf-8')
handoff={'status':'final_sealed_independent_numeric_and_transport_passed','no_blocker':True,
    'baseline_commit':'b5a40f30683bfc0945decaabbd4db5914c28427f',
    'final_source_patch_path':str(SIDE/'draft.patch'),'final_source_patch_sha256':sha(new_patch),
    'source_patch_contract':'Only five additions to damage.py; copy exact frozen test file separately.',
    'new_test_source_path':str(OUT/'fixed-author-inputs/tests/test_neural_condition_text_input.py'),
    'new_test_archive_path':'fixed-author-inputs/tests/test_neural_condition_text_input.py',
    'new_test_sha256':transport['new_test_sha256'],
    'numerical_review_sha256':sha((OUT/'independent-review083.json').read_bytes()),
    'transport_review_sha256':sha((SIDE/'independent-transport-review083.json').read_bytes()),
    'prior_118_manifest_preserved_sha256':sha(initial_manifest.read_bytes()),
    'independent_fresh_public_calls':373,'independent_pairs':40,
    'independent_pair_counts':{'text_rejected':11,'whole_success_unchanged':15,'exact_old_errors_unchanged':14},
    'new_tests':9,'instrumented_new_test_public_calls':293,
    'author_saved_pairs_readonly_checked':432,'author_saved_counts':{'text_rejected':116,'whole_success_unchanged':256,'exact_old_errors_unchanged':60},
    'post_repair_new_API_calls':0,'post_repair_tests_or_apply_checks_repeated':0,
    'original_preparation_evidence_preserved':True,'source8_not_rerun':True,
    'tracked_mutations':False,'Qt':False,'Wine':False,'ready_for_root_integration':True}
save(OUT/'final-handoff.json',handoff)
all_names=[row['archive_path'] for row in original_rows]+['public-artifacts-manifest.json','seal-numeric083.log','seal_transport_repair083.py','final-handoff.json']
all_names += [str(p.relative_to(OUT)) for p in sorted(SIDE.rglob('*')) if p.is_file()]
assert len(all_names)==len(set(all_names))
rows=[]
for name in sorted(all_names):
    p=OUT/name;data=p.read_bytes();rows.append({'source_path':str(p),'archive_path':name,'bytes':len(data),'sha256':sha(data)})
save(OUT/'final-public-artifacts-manifest.json',{'format_version':1,'status':'final_sealed_independent_numeric_and_transport_passed',
    'files':rows,'actual_independent_fresh_public_calls':373,'bytes':sum(r['bytes'] for r in rows),
    'post_repair_new_API_calls':0,'original118_preserved':True,'final_patch_sha256':sha(new_patch)})
assert all(len(Path(r['source_path']).read_bytes())==r['bytes'] and sha(Path(r['source_path']).read_bytes())==r['sha256'] for r in rows)
print(json.dumps({'status':'passed','files':len(rows),'bytes':sum(r['bytes'] for r in rows),
    'fresh_public_calls_remain':373,'final_handoff_sha256':sha((OUT/'final-handoff.json').read_bytes()),
    'final_manifest_sha256':sha((OUT/'final-public-artifacts-manifest.json').read_bytes()),
    'transport_review_sha256':sha((SIDE/'independent-transport-review083.json').read_bytes())}))
