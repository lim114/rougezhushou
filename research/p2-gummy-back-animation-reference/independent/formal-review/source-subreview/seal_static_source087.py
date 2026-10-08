"""Readonly byte/hash and plain-text review; never import or run project code.

No JSON input decoding, AST/regex/source parser, Git apply, test, formatter,
helper, application API, network, Qt or Wine calls. Only this external packet
is written. Existing frozen author/source packets are never changed.
"""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-gummy-back-animation-reference-087-draft')
REPO = Path('/workspace/rougezhushou')
OLD = '9ef5a469673502754db3be320a8eece9a7fd18d4'
ROOT86 = '0f27027e7e1f49c08f298706b599e310e299238b'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def metadata(path, data):
    return {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}


def pinned(relative, expected):
    path = AUTHOR / relative
    data = path.read_bytes()
    assert sha(data) == expected, str(path)
    return data


def git_bytes(commit, path):
    return subprocess.run(['git', '-C', str(REPO), 'show', commit + ':' + path],
                          check=True, capture_output=True).stdout


def excerpt(data, first, last):
    lines = data.decode('utf-8').splitlines()
    return [{'line': i, 'text': lines[i - 1]} for i in range(first, last + 1)]


def write_json(name, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    (OUT / name).write_bytes(data)


assert not (OUT / 'static-source-receipt087.json').exists(), 'Packet already sealed; create a new sidecar instead'
freeze = pinned('author-freeze087.json', 'f19a69e6dcba6c1368910a0b7c529af1f0e7083f3d4e3561ab5e5c8ad9559b1a')
transport = pinned('root86-transport-receipt.json', 'ca9bfb0467c345b4cfbf44013350152240df8e6607762d839a2357ddde5e1ef9')
patch = pinned('product087.patch', '05d4f78b2bc319b0d87bb80f4d32366e27565d26c5b459800a773d7e7362cb93')
registry_base = pinned('root86-verify_cloud.py', '5cc41f11d7d91cd35ab6b9221ba7572baa9d6e8976618a35305626923e56c7de')
registry_new = pinned('registered-verify_cloud087.py', 'b2da5be3e6d309d97a01746161e63fa450f62ff5f9abb9c26fbfcd7abb91b3e8')
new_line = b'    "tests.test_gummy_back_animation_reference",\n'
assert registry_base == git_bytes(ROOT86, 'scripts/verify_cloud.py')
assert registry_base.count(new_line) == 0 and registry_new.count(new_line) == 1
assert registry_new.replace(new_line, b'', 1) == registry_base
assert b'\r' not in registry_base and b'\r' not in registry_new

targets = [
    ('rouge/data/original-animation-references.json', '390deaa49bb353cface07b555c65a970b15a7ff1b58002008664e7872793ef53',
     '28d9be1dd6fe6f91dc5773b1c685ea78fb0bb403d25c4f26d933adcfcbad3f9e', 'CRLF'),
    ('tests/test_original_animation_048.py', '0418b5982c289954d557e06482a832502479ab75c57cf1aec6dc62df0137b4e8',
     'ae3f6c804031d5dbbed89dc2743e5e1df721dba55cfcbab7e943fae2cb84a0cb', 'LF'),
    ('tests/test_gummy_back_animation_reference.py', 'a68f2b57d5464b135515f9a48f81156c5f21721027aaaaf96f3af5d55939ad05', None, 'LF'),
]
tree_names = subprocess.run(['git', '-C', str(REPO), 'ls-tree', '-r', '--name-only', ROOT86],
                            check=True, capture_output=True).stdout.splitlines()
target_receipts = []
target_data = {}
for path, draft_sha, old_sha, ending in targets:
    draft = pinned('draft/' + path, draft_sha)
    target_data[path] = draft
    if old_sha is not None:
        old = git_bytes(OLD, path)
        root = git_bytes(ROOT86, path)
        assert sha(old) == old_sha and root == old
        baseline = metadata(ROOT86 + ':' + path, root)
    else:
        assert path.encode() not in tree_names
        baseline = {'path': ROOT86 + ':' + path, 'absent': True}
    lf, crlf = draft.count(b'\n'), draft.count(b'\r\n')
    assert (lf == crlf and crlf > 0) if ending == 'CRLF' else crlf == 0 and b'\r' not in draft
    target_receipts.append({**metadata(AUTHOR / 'draft' / path, draft), 'baseline': baseline,
                            'line_endings': ending, 'LF_count': lf, 'CRLF_count': crlf})
expected_headers = sorted('diff --git a/' + path + ' b/' + path for path, *_ in targets)
actual_headers = [line.decode('utf-8') for line in patch.splitlines() if line.startswith(b'diff --git ')]
assert sorted(actual_headers) == expected_headers and len(actual_headers) == 3

consumers = [
    ('rouge/animation_reference.py', '3e0c98edfec28e13db3263fc0240e872ed6aaaac53f02729f0e4d17e139b2f1f'),
    ('rouge/timing.py', '1de2c21196049fe41265c3b0bba3c851ace730ff1b5a091a8f9a1cbe287ddab8'),
    ('rouge/estimate.py', 'c507348af56f26bb3628684badad5d0c08102eb59ea8199d37cab9ddda86601a'),
    ('rouge/reporting.py', '70ef12ed860c08ce4f471d2be0e9c5cbcec40a64ad7b91d6078c2d99d11254ae'),
    ('scripts/build_original_animation_048.py', 'b27c4d80010e721bc519748c17203780ebab7a98386d0e7b139f2268bffc8d5e'),
    ('scripts/build_animation_selection_048.py', '86271f1e85332dc518e0c7ad9586e4969e0f2f12180d8e9aaa3a38021c8a2b45'),
]
consumer_receipts = []
texts = {}
for path, expected in consumers:
    old, root = git_bytes(OLD, path), git_bytes(ROOT86, path)
    assert root == old and sha(old) == expected
    assert (AUTHOR / 'baseline' / path).read_bytes() == old
    assert (AUTHOR / 'draft' / path).read_bytes() == old
    consumer_receipts.append({**metadata(ROOT86 + ':' + path, root), 'old_9ef_and_author_trees_equal': True})
    texts[path] = root
different = []
for path, old_sha, root_sha in [
    ('rouge/damage.py', '4b756392c9536323fd5ec8110e61eaa9373113e28828caeae25f5e846d73e389',
     '6cc15cf93eb52fc42120fff6b795e2cbbf2903cf0af8d7d293ffea9f73f121c6'),
    ('rouge/operator_engine.py', '071b60914f40a0281c7acc8e3648520b496a448339f8d9b8c983fde47955ada4',
     'c6a7b5e5cd444480f3579a8174246a31f891cb7a2b1c93bbf0826aa4a7765c68'),
]:
    old, root = git_bytes(OLD, path), git_bytes(ROOT86, path)
    assert sha(old) == old_sha and sha(root) == root_sha and old != root
    different.append({'path': path, 'old_9ef': metadata(OLD + ':' + path, old),
                      'root86': metadata(ROOT86 + ':' + path, root),
                      'transport_allowed': False, 'reason': 'Preserve integrated root86 source; never copy author old tree'})

data = target_data['rouge/data/original-animation-references.json']
selection_at = data.index(b'  "selection_derivation": {')
addition_at = data.index(b'  "source_additions": [')
assert selection_at < addition_at
historical = data[selection_at:addition_at]
new_metadata = data[addition_at:]
assert b'f933b0a62942210fe72c627175acf278fa4a2ab66f287c63baba1943b90581f6' in historical
assert b'"runtime_binding_inferred": false' in historical
for literal in (
    b'09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2',
    b'473df5c69d7e3552f6937f749bd42dd9e974ca01', b'"bytes": 32563',
    b'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265',
    b'2b3785b65d526bf74329f249b90bf2034c02eb79708e25ec12bdebe73709dd77',
    b'8b4844bd4b193ba9e54487ed397a777993cbad56',
    b'f1e0a31b9906e4d4daf2733857d21381ddbbe75adec7f4d83e1cc9b2b070dfc1',
    b'"runtime_binding_inferred": false', b'lifecycle clocks remain unknown.',
):
    assert literal in new_metadata
for name in ('Attack', 'Default', 'Idle', 'Skill', 'Start'):
    assert ('char_196_sunbr:Back:' + name).encode() in new_metadata
method_receipts = []
for path in ('tests/test_gummy_back_animation_reference.py', 'tests/test_original_animation_048.py'):
    methods = [{'line': i, 'definition': line} for i, line in enumerate(target_data[path].decode('utf-8').splitlines(), 1)
               if line.startswith('    def test_')]
    assert len(methods) == (7 if 'test_gummy' in path else 10)
    method_receipts.append({'path': path, 'methods': methods, 'method_count': len(methods), 'executed_by_this_child': False})
runner = pinned('run_related.py', '72add8f1d351fa8c079693b9f563c1f486f1d7d3251dd49de6a1919b407fa1a9')
assert b'method.__unittest_skip__=True' in runner and b'if not cache.exists():' in runner

receipt = {
    'version': 1, 'status': 'PASS_STATIC_FINAL_FROZEN', 'author_baseline': OLD, 'actual_transport_baseline': ROOT86,
    'scope': 'Readonly byte/hash and literal source-text review only. No product code imported or executed; no JSON input decoding/AST/regex/frame/source parser.',
    'bound_author_freeze': metadata(AUTHOR / 'author-freeze087.json', freeze),
    'bound_transport_receipt': metadata(AUTHOR / 'root86-transport-receipt.json', transport),
    'three_product_targets': target_receipts,
    'patch': {**metadata(AUTHOR / 'product087.patch', patch), 'exact_three_headers': actual_headers,
              'registry_in_patch': False, 'git_apply_executed_by_child': False},
    'root86_registry': {'base': metadata(ROOT86 + ':scripts/verify_cloud.py', registry_base),
                        'proposal': metadata(AUTHOR / 'registered-verify_cloud087.py', registry_new),
                        'single_added_line': new_line.decode(), 'inverse_equals_entire_root86_file': True,
                        'preserves_existing86_MODULES_and_all_other_bytes': True, 'child_applied': False},
    'six_unchanged_consumers': consumer_receipts, 'two_changed_sources_excluded_from_transport': different,
    'metadata_lineage': {'selection_derivation': 'Historical 048 source filtering provenance retained; not a claim that new Back records were regenerated from that historical source.',
                         'source_additions': 'Separate new Back5 pinned-resource/parser/extraction metadata, with explicit runtime_binding_inferred false and native/EOF/rendering/history unknowns.',
                         'literal_metadata_excerpt': data[selection_at:].decode('utf-8'),
                         'raw_source_or_parser_reexecuted': False, 'whole_old923_records_compared': False},
    'source_contract': {
        'choices': 'First requires published selectable_as_conventional_reference. Attack prefix is ordinary eligible normal/skill; Skill requires a numeric suffix matching selected skill. Literal Skill has no numeric match. This is not a UI-option-count assertion.',
        'label': 'Generic label fallback does not authorize selection; label is invoked for descriptor after choices/id match.',
        'descriptor': 'Absent identity returns None; explicit identity must match current owner/skill/normal eligible list or raises existing public error. Native binding remains false.',
        'manual_override': 'AttackTimeline validates both reference identities before preview frame values; manual frame values override only unit=None and are reported overridden_by_preview. A later default request lacks reference metadata.',
        'representation': 'Unchanged source builder FPS=30, EPSILON_FRAMES=1e-5 representation tolerance; strict ceil retained. No native tick/lifecycle measurement or parser execution.',
        'publication_scope': 'Product data publishes five additional offline source records. No runtime consumer code, default selection, native animation binding, or clock policy is changed by these three product paths.',
        'counts_boundary': 'Four advertised deltas (+5 records,+2 source-eligible,+3 unverified,-1 missing) are author literals; parent independently checks full records/counts. Source eligibility is not UI choice count.',
    },
    'fixed_root86_source_excerpts': {
        'rouge/animation_reference.py': excerpt(texts['rouge/animation_reference.py'], 13, 51),
        'rouge/timing.py': excerpt(texts['rouge/timing.py'], 167, 172) + excerpt(texts['rouge/timing.py'], 200, 206) + excerpt(texts['rouge/timing.py'], 260, 274) + excerpt(texts['rouge/timing.py'], 329, 347),
        'scripts/build_original_animation_048.py': excerpt(texts['scripts/build_original_animation_048.py'], 15, 28) + excerpt(texts['scripts/build_original_animation_048.py'], 65, 80),
        'scripts/build_animation_selection_048.py': excerpt(texts['scripts/build_animation_selection_048.py'], 7, 20),
    },
    'test_source_only': {'modules': method_receipts,
                         'new7_contracts': ['eligible Attack and generic Skill rejection', 'friendly explicit reference retains incomplete/exact false', 'zero window/recipient', 'S1 clocks stay unknown', 'manual/default separation', 'generic/missing/cross-owner errors', 'strict/normalized source frame values and no other-side fill'],
                         'old_source_method_count': 10,
                         'related_runner': {**metadata(AUTHOR / 'run_related.py', runner), 'excerpt': excerpt(runner, 19, 27)},
                         'cache_skip': 'Old first method requires original skeleton-downloads.json and raw skeleton bytes. The author related runner conditionally sets that one method skipped when cache is absent; no such skip decorator is in the old test module. No raw64 reconstruction or rerun by child.',
                         'author_or_parent_runtime_results': 'Not independently executed or asserted by this static child; parent owns formal numerical/new-test checks.'},
    'preparation_diagnostics': ['An earlier readonly rg filename inventory included baseline/draft archives and produced truncated output; it made no mutations. Final checks use exact paths and bounded text reads. No static-check failure occurred.'],
    'prohibited_call_counts': {'product_imports': 0, 'helpers': 0, 'application_API': 0, 'formatters': 0, 'tests': 0, 'JSON_input_decoder': 0, 'source_or_frame_parser': 0, 'network': 0, 'Qt': 0, 'Wine': 0, 'tracked_edits': 0},
    'restart_conditions': ['Author freeze/patch/test bytes or transport root commit change: create new review sidecar and rebind exact hashes.', 'Native clock/binding/rendering/EOF or historical parser-root-cause claims need separate direct evidence.', 'Root alone applies three-path patch plus one registry line and performs current-tree related/full verification; never replace root86 damage/engine or whole registry with old author tree.'],
}
for name, content in [('bound-author-freeze087.json', freeze), ('bound-root86-transport-receipt.json', transport),
                      ('bound-root86-verify_cloud.py', registry_base), ('bound-registered-verify_cloud087.py', registry_new),
                      ('bound-product087.patch', patch)]:
    (OUT / name).write_bytes(content)
write_json('static-source-receipt087.json', receipt)
note = '''第87节静态来源独审封存：PASS_STATIC_FINAL_FROZEN。

绑定作者9ef冻结与实际root86 0f27027运输。三产品路径/字节/换行/patch headers一致，六相关consumer与原9ef一致。实际root86 damage/engine已变，必须保留根实现；注册提议只加一个MODULES条目，删除该49字节行后整个文件与固定root86源码逐字节相同。

selection_derivation是历史048筛选来源；新Back5用source_additions另记固定资源、提取及官方reader来源。属于产品离线参考资料发布，没有运行时consumer代码、默认选择或原生时钟绑定改动。源eligible包含literal Skill，但现有choices必须Attack或匹配编号Skill；label的generic文字不能授权Skill选择。Attack也须显式identity才消费。未统计UI选项。

原30Hz/1e-5仅浮点表示归一化合同。严格ceil及normalized值保留。manual preview先验证两个reference身份，再覆盖unit=None帧，并带override标记；后续default无referencemetadata。未据此外推客户端时钟、皮肤、生命周期、EOF、历史parser错误根因。

仅静态读7个新测试和现有原动画模块10个test_方法；没有运行任何测试。作者related runner在缓存不存在时动态跳过原始64资源核验首方法，而非原test模块自带skip。作者及父独审的实际API/test结果由父审计绑定，本子审未重复。父负责旧923记录、新原始5、完整计数和实际测试。

0应用导入/helper/API/formatter/test/JSON输入解析/source帧解析/network/Qt/Wine/tracked改动。仅封存外部可公开文本/哈希文件，不复制大JSON、64skel、作者整树或旧封存目录。readonly inventory一次输出截断已记receipt；无静态核验失败。
'''
(OUT / 'NOTE.md').write_text(note, encoding='utf-8')
write_json('source-handoff087.json', {
    'version': 1, 'status': 'PASS_STATIC_FINAL_FROZEN', 'receipt': metadata(OUT / 'static-source-receipt087.json', (OUT / 'static-source-receipt087.json').read_bytes()),
    'author_freeze_sha256': sha(freeze), 'root86_commit': ROOT86, 'registered_proposal_sha256': sha(registry_new),
    'transport': 'Exact three product paths plus one root86 registry line; preserve root86 damage/engine and all other registry bytes.',
    'runtime_calls': 0, 'tracked_edits': 0, 'note': 'Static child only; parent formal numeric/test results and root current-tree verification are separate.'})
names = ['seal_static_source087.py', 'bound-author-freeze087.json', 'bound-root86-transport-receipt.json',
         'bound-root86-verify_cloud.py', 'bound-registered-verify_cloud087.py', 'bound-product087.patch',
         'static-source-receipt087.json', 'NOTE.md', 'source-handoff087.json']
files = [metadata(OUT / name, (OUT / name).read_bytes()) for name in names]
write_json('v1-public-files-manifest087.json', {'version': 1, 'status': 'FINAL_FROZEN', 'files': files,
    'file_count': len(files), 'total_bytes': sum(f['bytes'] for f in files), 'all_public': True,
    'excluded': ['Manifest itself to avoid self hash', 'Whole draft/baseline trees, large product JSON and old923-record comparison', 'Original64 skeletons/parser cache and every previous sealed packet'],
    'prohibited_calls': receipt['prohibited_call_counts']})
for item in files:
    current = Path(item['path']).read_bytes()
    assert len(current) == item['bytes'] and sha(current) == item['sha256']
for name in ['source-handoff087.json', 'v1-public-files-manifest087.json']:
    item = metadata(OUT / name, (OUT / name).read_bytes())
    print(json.dumps(item, ensure_ascii=False))
print(json.dumps({'file_count': len(files), 'total_bytes': sum(f['bytes'] for f in files), 'status': 'PASS_STATIC_FINAL_FROZEN'}))
