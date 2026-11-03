import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent
REVIEW = Path('/workspace/.continuation/p2-warning-order-081-independent')
sha = lambda data: hashlib.sha256(data).hexdigest()
review_path = REVIEW / 'independent-review-final081.json'
manifest_path = REVIEW / 'independent-public-manifest081.json'
assert sha(review_path.read_bytes()) == '779ea8296051c0c3b98caba9d077998bafc8c8ddd8789155a307748a75158160'
assert sha(manifest_path.read_bytes()) == '3df89fbdca9708af156bf5757c3744b70f7ab8c463c8a4f6684c6d4c180a9cd1'
review = json.loads(review_path.read_bytes())
assert review['status'] == 'PASS_FINAL_FROZEN'
review_manifest = json.loads(manifest_path.read_bytes())
assert review_manifest['format_version'] == 1 and isinstance(review_manifest['files'], list)
assert len(review_manifest['files']) == 22
for row in review_manifest['files']:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], row['source_path']
author = json.loads((OUT / 'author-frozen-receipt.json').read_bytes())
assert sha((OUT / 'relic-warning-order-081.patch').read_bytes()) == author['patch_sha256']
for key, path in [('draft_relics_sha256', OUT / 'draft/rouge/relics.py'),
                  ('new_test_sha256', OUT / 'draft/tests/test_relic_warning_order.py'),
                  ('note_draft_sha256', OUT / 'NOTE.draft.md'),
                  ('source_receipt_sha256', OUT / 'source-receipt.json'),
                  ('comparison_receipt_sha256', OUT / 'comparison-receipt.json')]:
    assert sha(path.read_bytes()) == author[key], key
compression = json.loads((OUT / 'compressed-matrix-receipt.json').read_bytes())
for name, proof in compression.items():
    data = (OUT / proof['gzip_path']).read_bytes()
    assert sha(data) == proof['gzip_sha256'] and len(data) == proof['gzip_bytes']
    original = gzip.decompress(data)
    assert len(original) == proof['original_bytes'] and sha(original) == proof['original_sha256']

note = (OUT / 'NOTE.draft.md').read_text()
note += '''
正式独立复核已通过：717份baseline与716份未改旧文件、单条CRLF语句及3个原始selector全部核验；保存的140对/280次作者调用独立按类型严格重比通过，未重跑矩阵。另8个独立输入跨7/101两seed共32次实际calculate_damage调用，每seed5个完整成功保持与3个原错误保持，draft两seed字节相同。独审另跑8项新测试通过；未重复作者58项旧相关检查。

准备失败完整保留：作者第一次生成新测试patch时缺a/、b/分隔符，独审git apply --numstat发现会放仓库根，在任何root集成前纠正。原patch/原freeze/修正脚本和诊断均存档；只变两条运输header，源码/测试/280次矩阵没有改动或重跑。修正后numstat精确为rouge/relics.py及tests/test_relic_warning_order.py，作者及独审均只读apply--check通过。独审初次比较漏既有human phrase匿名替换的白名单，原脚本/日志保留；从冻结纯formatter AST精确派生后重比保存结果通过，未新增数值调用、未修改产品。

本交接可供第80节全量验证完成后集成。根须注册8项新测试、应用手术式patch、运行当前分支source/相关/精选检查及记录第81节。提供root-current-source-081.py但作者未运行它，不能将外部冻结字节验证写成根当前已通过。Wine/Qt/原生Windows/游戏仍无本作者新增验收。
'''
with (OUT / 'NOTE.md').open('x', encoding='utf-8') as f:
    f.write(note)
handoff = {'status': 'FINAL_FROZEN_PASS_READY_AFTER_FULL_080', 'section': 81,
           'baseline_commit': author['baseline_commit'],
           'topic': 'Stable order of existing unknown-stacking warnings and corresponding record pending entries',
           'patch': str(OUT / 'relic-warning-order-081.patch'), 'patch_sha256': author['patch_sha256'],
           'product_scope': 'One CRLF set iteration to first-declared dict.fromkeys; no formula, field, source, message or unknown model change.',
           'draft_relics_sha256': author['draft_relics_sha256'], 'new_test_sha256': author['new_test_sha256'],
           'new_test_module': 'tests.test_relic_warning_order', 'new_tests_passed': 8,
           'author_related_run': 58, 'author_related_passed': 48, 'author_related_historical_skipped': 10,
           'author_unique_scenarios': 35, 'author_hash_seeds': [0, 1, 42, 314159],
           'author_calculate_damage_calls': 280, 'author_distinct_old_outputs': 4,
           'author_distinct_draft_outputs': 1,
           'author_matrix_draft_sha256': 'b7d668831d417888b7a73c4f22e3f508e21cc5f8ea24dad3b6233304b49c5191',
           'source_prepare_probes_separate_from_matrix': 3,
           'independent_saved_pairs_recompared_without_calculation': 140,
           'independent_unique_scenarios': 8, 'independent_hash_seeds': [7, 101],
           'independent_calculate_damage_calls': 32, 'independent_new_tests_passed': 8,
           'independent_final_receipt': str(review_path), 'independent_final_sha256': sha(review_path.read_bytes()),
           'independent_manifest_sha256': sha(manifest_path.read_bytes()),
           'author_patch_transport_preparation_error_and_reviewer_whitelist_preparation_preserved': True,
           'root_current_checks_executed_by_author': False,
           'root_source_script': str(OUT / 'root-current-source-081.py'),
           'required_root_actions': ['Finish full section080 cadence first.',
                                     'Verify final explicit manifest hashes before applying patch.',
                                     'Apply patch only and register tests.test_relic_warning_order in verify_cloud.MODULES.',
                                     'Run provided current root source script after registration; run appropriate current related and selected checks.',
                                     'Archive all listed explicit artifacts, update checkpoint/remaining work, commit and tag section081.'],
           'manifest_path': str(OUT / 'archivable-public-manifest.json'),
           'gui_executed': False, 'wine_executed': False, 'native_windows_verified': False,
           'tracked_mutations': False}
with (OUT / 'handoff.json').open('x', encoding='utf-8') as f:
    json.dump(handoff, f, ensure_ascii=False, indent=2)
    f.write('\n')
names = ['NOTE.md', 'NOTE.draft.md', 'prepare.py', 'freeze-receipt.json', 'run-public.py',
         'make-cases.py', 'public-cases.json', 'compare.py', 'comparison-receipt.json',
         'source-check.py', 'source-receipt.json', 'new-tests.log', 'related-tests.log',
         'test-receipt.json', 'seal-author.py', 'compressed-matrix-receipt.json',
         'author-frozen-receipt.json', 'author-frozen-before-path-fix.json',
         'relic-warning-order-081.patch', 'relic-warning-order-081-before-path-fix.patch',
         'fix-patch-path.py', 'patch-path-preparation-receipt.json', 'root-current-source-081.py',
         'draft/rouge/relics.py', 'draft/tests/test_relic_warning_order.py', 'finalize.py', 'handoff.json']
names += [proof['gzip_path'] for proof in compression.values()]
files = []
for name in names:
    path = OUT / name
    data = path.read_bytes()
    files.append({'source_path': str(path), 'archive_path': name, 'bytes': len(data), 'sha256': sha(data)})
files.extend({**row, 'archive_path': 'independent/' + row['archive_path']} for row in review_manifest['files'])
files.append({'source_path': str(manifest_path), 'archive_path': 'independent/' + manifest_path.name,
              'bytes': manifest_path.stat().st_size, 'sha256': sha(manifest_path.read_bytes())})
assert len({r['archive_path'] for r in files}) == len(files)
manifest = {'format_version': 1, 'section': 81, 'status': 'FINAL_SEALED', 'files': files,
            'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files),
            'large_json_lossless_gzip': compression, 'manifest_self_excluded': True,
            'whole_frozen_source_trees_not_duplicated': True, 'public_artifacts_only': True,
            'all_independent_22_files_and_independent_manifest_included': True}
with (OUT / 'archivable-public-manifest.json').open('x', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'status': 'FINAL_SEALED', 'files': len(files),
                  'handoff_sha256': sha((OUT / 'handoff.json').read_bytes()),
                  'manifest_sha256': sha((OUT / 'archivable-public-manifest.json').read_bytes()),
                  'patch_sha256': author['patch_sha256']}, ensure_ascii=False))
