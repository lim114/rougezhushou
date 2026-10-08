"""Prepare only external portable CLI sources and real public input copies."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/p2-animation-provenance-portability-090-source')
BASE = '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)


def report(name, value):
    write(OUT / name, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


old_receipt = json.loads((SOURCE / 'source-read-receipt090.json').read_bytes())
transport = []
for item in old_receipt['captured_files']:
    rel = item['repository_path']
    raw = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
    assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], rel
    transport.append({'repository_path': rel, 'bytes': len(raw), 'sha256': sha(raw),
                      'now_actual_git_commit': BASE,
                      'original_source_evidence_status_preserved': item['evidence_status']})
assert len(transport) == 21
report('source-transport-619090.json', {
    'format_version': 1, 'baseline_commit': BASE, 'source_proposal_original_baseline': old_receipt['baseline_commit'],
    'all_21_source_files_now_match_actual_git': True, 'files': transport,
    'original_source28_manifest_and_handoff_unchanged': True,
    'prior_19Git_2working_tree_observation_not_rewritten': True,
    'not_a_repeat_of_root_315_archive_closure': True,
    'application_helper_test_parser_download_Qt_Wine_calls': 0})

manifest_rel = 'research/p2-gummy-back-animation-reference/source-packet087/public-artifacts-manifest087.json'
manifest = json.loads(subprocess.check_output(['git', 'show', BASE + ':' + manifest_rel], cwd=ROOT))
leaves = ['parse-Back-result.json', 'parse-Back-operation.json',
          'reacquired/Back/char_196_sunbr.skel', 'history/original-animation-references.json.gz',
          'official-reader/official-source/spine-ts/build/spine-core.js',
          'official-reader/official-source/spine-ts/build/spine-core.d.ts']
fixture_paths = ['rouge/data/original-animation-references.json', manifest_rel]
fixture_paths.extend(str(Path(manifest_rel).parent / leaf) for leaf in leaves)
fixtures = []
for rel in fixture_paths:
    raw = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
    write(OUT / 'draft' / rel, raw)
    fixtures.append({'path': rel, 'bytes': len(raw), 'sha256': sha(raw),
                     'real_public_input_copied_from_git': BASE})

base_readme = subprocess.check_output(['git', 'show', BASE + ':README.md'], cwd=ROOT)
base_registry = subprocess.check_output(['git', 'show', BASE + ':scripts/verify_cloud.py'], cwd=ROOT)
write(OUT / 'baseline/README.md', base_readme)
write(OUT / 'baseline/scripts/verify_cloud.py', base_registry)
newline = '\r\n' if b'\r\n' in base_readme else '\n'
addition = '\n'.join([
    '## 离线动画来源校核', '',
    '维护者可在任意工作目录运行 `python scripts/verify_original_animation_provenance.py`（使用脚本的实际路径），'
    '或以 `--repository-root`、`--references`、`--evidence-dir` 指定迁移后的公开文件。'
    '该命令只读已归档资料，输出 JSON，不依赖旧绝对路径或 timing-048 cache，不解析或下载资源。', '',
    '范围固定为第87节古米 Back 的6个必要公开来源文件、真实历史923条数据与新增5条记录。'
    '成功退出0，缺失或校核失败退出1，超出支持快照退出2；后续新增来源不会自动获得认证。'
    '30Hz仅沿用现有表示政策，泛称 Skill 无技能编号；原生绑定、渲染几何、EOF和实际时钟继续未验证。', ''
]).replace('\n', newline).encode()
draft_readme = base_readme + addition
write(OUT / 'draft/README.md', draft_readme)
literal = b'    "tests.test_original_animation_provenance",\n'
assert base_registry.count(b'MODULES = (\n') == 1 and literal not in base_registry
registered = base_registry.replace(b'MODULES = (\n', b'MODULES = (\n' + literal, 1)
write(OUT / 'registered-verify_cloud090.py', registered)
report('registry-proposal090.json', {
    'format_version': 1, 'baseline_commit': BASE, 'path': 'scripts/verify_cloud.py',
    'baseline_bytes': len(base_registry), 'baseline_sha256': sha(base_registry),
    'new_entry_literal': literal.decode(), 'proposed_bytes': len(registered),
    'proposed_sha256': sha(registered), 'inverse_to_baseline_exact': registered.replace(literal, b'', 1) == base_registry,
    'root_rebase_after_section89_required': True})

patch = ''
for rel in ['scripts/verify_original_animation_provenance.py',
            'tests/test_original_animation_provenance.py', 'README.md']:
    old = base_readme if rel == 'README.md' else b''
    new = (OUT / 'draft' / rel).read_bytes()
    patch += ''.join(difflib.unified_diff(old.decode().splitlines(keepends=True),
                                       new.decode().splitlines(keepends=True),
                                       fromfile='a/' + rel if old else '/dev/null', tofile='b/' + rel))
write(OUT / 'product090.patch', patch.encode())
report('author-plan090.json', {
    'format_version': 1, 'baseline_commit': BASE,
    'source_baseline_transport_to_actual_root89_pending': True,
    'new_test_methods': 6, 'maximum_author_verifier_entries': 28,
    'normal_CLI_precheck_planned': 1,
    'new_tests_planned': {'CLI_invocations': 10, 'CLI_internal_verify_entries': 10, 'direct_verify_entries': 17},
    'public_fixtures': fixtures, 'public_fixture_bytes_unchanged': True,
    'existing_core_data_or_gameplay_sources_changed': False,
    'public_build_sources_already_added_by_root_619_no_duplicate_patch': True,
    'no_301_102_matrices_315_closure_or_two_parses_repeated': True,
    'source_parser_download_application_API_project_helper_formatter_Qt_Wine_calls': 0,
    'tests_executed_so_far': 0})
report('preparation-diagnostics090.json', {
    'format_version': 1,
    'optional_init_path_discovery': {'exit_code': 1,
        'description': 'rg --files found no tests/scripts __init__.py; dependent README read skipped; resumed as a standalone bounded read',
        'product_test_API_or_source_parser_calls': 0},
    'source_proposal_initial_freeze_failure_preserved_immutable_elsewhere': True,
    'product_failures': 0, 'preflight_failures': 0, 'tests_executed': 0})
print(json.dumps({'prepared': True, 'transport_actual_git_files': len(transport),
                  'real_public_fixture_files': len(fixtures), 'planned_author_verify_entries': 28,
                  'root89_transport_pending': True, 'tests_run': 0}))
