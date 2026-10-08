"""Recovered independent final closure and explicit public sealing, no public API calls."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT.with_name('p2-amiya-regeneration-talent-qualification-079-independent')
BASE = Path(json.loads((ROOT / 'baseline-path.json').read_text())['source_path'])


def digest(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


freeze = json.loads((ROOT / 'draft-freeze79.json').read_text())
assert digest(ROOT / 'changes79.patch') == {
    key: freeze['patch'][key] for key in ('sha256', 'bytes')}
for rel, meta in freeze['draft_files'].items():
    assert digest(ROOT / 'draft' / rel) == meta
assert json.loads((REVIEW / 'independent-source-static79.json').read_text())['status'] == 'PASS'
comparison = json.loads((REVIEW / 'independent-strict-comparison79.json').read_text())
assert comparison['status'] == 'PASS'
log = (REVIEW / 'independent-new-tests79.log').read_text()
assert 'Ran 8 tests' in log and log.rstrip().endswith('OK')
apply = subprocess.run(['git', 'apply', '--check', str(ROOT / 'changes79.patch')],
                       cwd=BASE, capture_output=True, text=True)
write(REVIEW / 'independent-patch-check79.json', {
    'baseline': str(BASE), 'command': 'git apply --check changes79.patch',
    'exit_code': apply.returncode, 'stdout': apply.stdout, 'stderr': apply.stderr,
    'patched_or_tracked_files': False})
assert apply.returncode == 0, apply.stderr
receipt = {
    'status': 'PASS_FINAL_FROZEN', 'section': 79,
    'baseline_commit': freeze['baseline_commit'],
    'reviewer': 'review_079_resume; recovered earlier readonly source/design review',
    'actual_medical_char_patch_form_no_base_name_fallback': True,
    'frozen_two_line_engine_gate_and_CRLF_preserved': True,
    'baseline_files_verified': 716, 'unchanged_old_draft_files_verified': 715,
    'saved_author_pairs_strictly_recompared_no_repeated_calls': 1366,
    'saved_author_counts': comparison['sets']['saved_author_1366']['counts'],
    'fresh_independent_pairs': 62, 'fresh_independent_public_calls': 124,
    'fresh_independent_counts': comparison['sets']['fresh_independent_62']['counts'],
    'new_tests_passed': 8, 'author_related_36_not_repeated_by_reviewer': True,
    'qualified_E1_E2_zeroATK_native_unknown_and_other_forms_whole_output_unchanged': True,
    'HP0_ordinary_input': 'Unavailable, not tested; no unused base_hp or fabricated _verified_rule claim.',
    'prepared_failures': 'No new review preparation failures; prior author first-test failure and source-shape corrections retained.',
    'GUI_Wine_native_Windows_game_validation': False,
    'tracked_mutations': False,
    'frozen_product_patch_draft_hashes': {'changes79.patch': digest(ROOT / 'changes79.patch'),
                                      **{rel: digest(ROOT / 'draft' / rel) for rel in freeze['draft_files']}},
}
write(REVIEW / 'independent-review-final79.json', receipt)
files = []
for path in sorted(REVIEW.rglob('*')):
    if path.is_file() and path.name != 'independent-public-manifest79.json' and '__pycache__' not in path.parts:
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(REVIEW)), **digest(path)})
write(REVIEW / 'independent-public-manifest79.json', {
    'format_version': 1, 'status': 'FINAL_SEALED', 'section': 79,
    'file_count': len(files), 'files': files, 'manifest_self_excluded': True,
    'no_whole_source_tree': True, 'total_bytes': sum(f['bytes'] for f in files)})
assert not (ROOT / 'independent').exists()
(ROOT / 'independent').mkdir()
for row in files:
    source = Path(row['source_path'])
    target = ROOT / 'independent' / row['archive_path']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert digest(target) == {key: row[key] for key in ('sha256', 'bytes')}
shutil.copyfile(REVIEW / 'independent-public-manifest79.json',
                ROOT / 'independent' / 'independent-public-manifest79.json')
handoff = json.loads((ROOT / 'handoff.json').read_text())
handoff['status'] = 'FINAL_FROZEN_INDEPENDENT_PASS'
handoff['independent_review_final'] = {
    'path': str(ROOT / 'independent' / 'independent-review-final79.json'),
    **digest(REVIEW / 'independent-review-final79.json')}
handoff['independent_public_manifest'] = {
    'path': str(ROOT / 'independent' / 'independent-public-manifest79.json'),
    **digest(REVIEW / 'independent-public-manifest79.json')}
handoff['recovered_external_seal_only_product_patch_unchanged'] = True
write(ROOT / 'handoff.json', handoff)
validation = json.loads((ROOT / 'validation79.json').read_text())
validation['status'] = 'AUTHOR_AND_INDEPENDENT_PASS_FINAL'
validation['independent_saved_pairs_strict_recompare'] = 1366
validation['independent_fresh_pairs'] = 62
validation['independent_fresh_public_calls'] = 124
validation['independent_counts'] = comparison['sets']['fresh_independent_62']['counts']
validation['independent_new_tests_passed'] = 8
write(ROOT / 'validation79.json', validation)
note = (ROOT / 'NOTE.md').read_text()
old = '独立审阅正在对冻结稿执行 source/code、窄 fresh 完整公共对照、新旧测试及保存的 1366 份完整矩阵严格复比；没有重算大矩阵。'
new = ('正式独审已通过：716 个基线文件和 715 个未改旧文件逐字节核验，医疗形态原件/20 级技能/INC-X 精确绑定再次核验；'
       '独立严格复比全部 1366 对保存 JSON/报告，不重算作者矩阵。另行 62 对窄 fresh 对照共 124 次普通公共调用，'
       '16 对仅未解锁天赋计数/说明修正，36 对成功整份相同，10 对原错误相同；8 个新测试通过。'
       '较早的只读来源/设计证据和全部作者准备诊断均保留。恢复封包只更新外部回执/说明/清单，冻结产品源与补丁未改；'
       '未运行 GUI/Wine/原生 Windows。')
assert note.count(old) == 1
(ROOT / 'NOTE.md').write_text(note.replace(old, new))
seal = subprocess.run(['python', str(ROOT / 'seal_public79.py')], capture_output=True, text=True)
assert seal.returncode == 0, seal.stderr
manifest = json.loads((ROOT / 'public-artifacts-manifest.json').read_text())
for row in manifest['files']:
    assert digest(Path(row['source_path'])) == {key: row[key] for key in ('sha256', 'bytes')}
for rel, meta in freeze['draft_files'].items():
    assert digest(ROOT / 'draft' / rel) == meta
assert digest(ROOT / 'changes79.patch') == {key: freeze['patch'][key] for key in ('sha256', 'bytes')}
print(json.dumps({'status': 'FINAL_FROZEN_INDEPENDENT_PASS', 'file_count': manifest['file_count'],
                  'patch': digest(ROOT / 'changes79.patch'), 'handoff': digest(ROOT / 'handoff.json'),
                  'manifest': digest(ROOT / 'public-artifacts-manifest.json'),
                  'independent_final': digest(REVIEW / 'independent-review-final79.json')}, ensure_ascii=False))
