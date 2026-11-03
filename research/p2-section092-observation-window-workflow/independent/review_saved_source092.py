"""Independent saved/source review only. No project imports or runtime calls."""
import ast
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import difflib
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

AUTHOR = Path('/workspace/.continuation/p2-window-target-timing-flow-092-author')
REPO = Path('/workspace/rougezhushou')
HERE = Path(__file__).resolve().parent
FIXED = '59961ec3d633ac91b01014fb06b357d45e5979f7'
EXPECTED_MANIFEST = '1ccb6c01dd85d9a1d3e9f87e1158bb6c2de8b8d6ad1838f4e7c08d659f915f27'
EXPECTED_HANDOFF = '95be8dca4ac40f85066c6458c547873e2dd717f6c4e7a4a11acbd9da85f9e73f'
STATUS = 'PASS_saved-source-review-passed/root_runtime_pending'
ZERO = dict.fromkeys(('imports', 'API', 'helper', 'formatter', 'tests', 'Qt', 'Wine'), 0)


def require(ok, label):
    if not ok:
        raise AssertionError(label)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def json_load(path):
    return json.loads(Path(path).read_bytes())


def binding(path):
    path = Path(path)
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def check_file(item, path=None):
    path = Path(path or item.get('source_path') or item.get('path'))
    raw = path.read_bytes()
    require(type(item['bytes']) is int and len(raw) == item['bytes'], f'bytes: {path}')
    require(sha(raw) == item['sha256'], f'SHA256: {path}')
    return raw


def git_read(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def repo_state():
    return {'branch': git_read('branch', '--show-current').decode().strip(),
            'head': git_read('rev-parse', 'HEAD').decode().strip(),
            'porcelain': git_read('status', '--porcelain').decode()}


def native_encode(value):
    kind = type(value)
    if value is None:
        return ['none']
    if kind is bool:
        return ['bool', value]
    if kind is int:
        return ['int', str(value)]
    if kind is float:
        return ['float', value.hex()]
    if kind is str:
        return ['str', value]
    if kind in (list, tuple):
        return ['list' if kind is list else 'tuple', [native_encode(v) for v in value]]
    if kind is dict:
        return ['dict', [[native_encode(k), native_encode(v)] for k, v in value.items()]]
    if kind in (set, frozenset):
        return ['set' if kind is set else 'frozenset',
                sorted((native_encode(v) for v in value), key=canonical)]
    if kind is bytes:
        return ['bytes', value.hex()]
    raise AssertionError(f'unsupported native type {kind}')


def native_decode(tree):
    require(type(tree) is list and tree and type(tree[0]) is str, 'typed-native node')
    tag = tree[0]
    require(len(tree) == (1 if tag == 'none' else 2), f'node arity {tag}')
    if tag == 'none':
        value = None
    elif tag == 'bool':
        require(type(tree[1]) is bool, 'bool payload')
        value = tree[1]
    elif tag in ('int', 'float', 'str', 'bytes'):
        require(type(tree[1]) is str, f'{tag} payload')
        value = {'int': int, 'float': float.fromhex, 'str': str, 'bytes': bytes.fromhex}[tag](tree[1])
    elif tag in ('list', 'tuple', 'set', 'frozenset'):
        require(type(tree[1]) is list, f'{tag} payload')
        values = [native_decode(x) for x in tree[1]]
        value = {'list': list, 'tuple': tuple, 'set': set, 'frozenset': frozenset}[tag](values)
    elif tag == 'dict':
        require(type(tree[1]) is list, 'dict payload')
        value = {}
        for entry in tree[1]:
            require(type(entry) is list and len(entry) == 2, 'dict entry arity')
            key, val = (native_decode(x) for x in entry)
            require(key not in value, 'duplicate native dict key')
            value[key] = val
    else:
        raise AssertionError(f'unsupported native tag {tag}')
    return value


def checked_native(tree, label):
    value = native_decode(tree)
    require(native_encode(value) == tree, f'lossless native reconstruction: {label}')
    return value


def gzip_load(receipt):
    require(set(receipt) == {'path', 'compressed_bytes', 'compressed_sha256', 'decoded_bytes', 'decoded_sha256'},
            'gzip receipt schema')
    path = Path(receipt['path'])
    require(path.parent == AUTHOR / 'saved', 'saved gzip location')
    compressed = path.read_bytes()
    require(len(compressed) == receipt['compressed_bytes'] and sha(compressed) == receipt['compressed_sha256'],
            f'compressed gzip binding: {path}')
    decoded = gzip.decompress(compressed)
    require(len(decoded) == receipt['decoded_bytes'] and sha(decoded) == receipt['decoded_sha256'],
            f'decoded gzip binding: {path}')
    return json.loads(decoded)


def write_json(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


before = repo_state()
require(before == {'branch': 'codex/p2-development', 'head': FIXED, 'porcelain': ''}, 'fixed clean repository before')
manifest_path = AUTHOR / 'FINAL-manifest092.json'
handoff_path = AUTHOR / 'author-handoff092.json'
require(binding(manifest_path)['sha256'] == EXPECTED_MANIFEST, 'supplied FINAL manifest SHA')
require(binding(handoff_path)['sha256'] == EXPECTED_HANDOFF, 'supplied author handoff SHA')
manifest = json_load(manifest_path)
handoff = json_load(handoff_path)
inventory = {str(f.relative_to(AUTHOR)): binding(f) for f in sorted(AUTHOR.rglob('*')) if f.is_file()}
require(not any(f.is_symlink() for f in AUTHOR.rglob('*')), 'author no symlinks')
require(manifest['fixed_root_commit'] == handoff['fixed_root_commit'] == FIXED, 'fixed source commit metadata')
require(manifest['file_count'] == handoff['payload_file_count'] == len(manifest['files']) == 51,
        '51 manifest members')
require(manifest['total_bytes'] == handoff['payload_total_bytes'] == 2555186, 'payload byte budget')
require(manifest['excluded_metadata'] == ['FINAL-manifest092.json', 'author-handoff092.json'], 'excluded metadata schema')
require(manifest['manifest_and_handoff_excluded_to_avoid_circular_bindings'] is True
        and manifest['root_archive_must_also_include_excluded_metadata'] is True, 'noncircular metadata archive rule')
require(manifest['finalstopwrite'] is True and handoff['finalstopwrite'] is True, 'author FINALSTOPWRITE declaration')
payload_names = []
for item in manifest['files']:
    require(set(item) == {'source_path', 'archive_path', 'bytes', 'sha256'}, 'payload member schema')
    archive = Path(item['archive_path'])
    require(not archive.is_absolute() and '..' not in archive.parts, 'relative archive path')
    require(Path(item['source_path']) == AUTHOR / archive, 'author source/archive path binding')
    check_file(item)
    payload_names.append(item['archive_path'])
require(len(set(payload_names)) == 51, 'unique manifest members')
require(set(inventory) == set(payload_names) | set(manifest['excluded_metadata']), 'actual inventory exactly manifest+metadata')
require(sum(inventory[x]['bytes'] for x in payload_names) == 2555186, 'actual payload total bytes')
check_file(handoff['manifest'])
check_file(handoff['diagnostic'])
check_file(handoff['source_static_proof'])
for item in handoff['candidate_products'].values():
    check_file(item)

# Read the fixed Git tree and local files without importing any project modules.
tree = {}
for record in git_read('ls-tree', '-rz', FIXED).split(b'\0'):
    if record:
        meta, path = record.split(b'\t', 1)
        mode, kind, oid = meta.split(b' ')
        if kind == b'blob':
            tree[path.decode()] = oid.decode()
maintained = json_load(AUTHOR / 'maintained730-git-and-current-hashes092.json')
require(maintained['actual_root_commit'] == FIXED and maintained['file_count'] == 730
        and len(maintained['files']) == 730, 'maintained730 schema')
maintained_paths = set()
for item in maintained['files']:
    raw = check_file(item)
    relative = str(Path(item['source_path']).relative_to(REPO))
    require(relative not in maintained_paths, 'unique maintained source')
    maintained_paths.add(relative)
    require(item['git_ref'] == FIXED and tree[relative] == item['git_blob'], 'maintained source in fixed Git tree')
    blob_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob_sha == item['git_blob'], f'actual file equals fixed Git blob: {relative}')
require(sum(x['bytes'] for x in maintained['files']) == maintained['total_bytes'] == 26071424,
        'maintained730 actual byte total')
baseline_leaves = sorted(f for f in (AUTHOR / 'actual91-leaves').rglob('*') if f.is_file())
require(len(baseline_leaves) == 11, 'actual91 leaf count')
for path in baseline_leaves:
    relative = str(path.relative_to(AUTHOR / 'actual91-leaves'))
    raw = path.read_bytes()
    require(raw == (REPO / relative).read_bytes(), f'actual91 current leaf: {relative}')
    require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == tree[relative],
            f'actual91 fixed Git leaf: {relative}')

freeze = json_load(AUTHOR / 'pre-public-freeze092.json')
require(freeze['file_count'] == len(freeze['files']) == 14, 'prepublic freeze14 schema')
for item in freeze['files']:
    check_file(item)
require(all(v == 0 for v in freeze['calls_at_freeze'].values()), 'freeze calls zero')
old_manifest = json_load(AUTHOR / 'old49-manifest-immutable.json')
prior = handoff['prior49_archive']
old_root = Path(prior['path'])
old_original_manifest = Path(prior['manifest']['path'])
check_file(prior['manifest'])
require((AUTHOR / 'old49-manifest-immutable.json').read_bytes() == old_original_manifest.read_bytes(),
        'old49 manifest immutable reference exact')
require(old_manifest['file_count'] == len(old_manifest['files']) == 49, 'old49 member schema')
old_names = set()
for item in old_manifest['files']:
    require(set(item) == {'source_path', 'archive_path', 'bytes', 'sha256'}, 'old49 member fields')
    archive = Path(item['archive_path'])
    require(not archive.is_absolute() and '..' not in archive.parts, 'old49 safe archive path')
    require(item['archive_path'] not in old_names, 'old49 unique archive path')
    old_names.add(item['archive_path'])
    check_file(item, old_root / archive)
require(sum(item['bytes'] for item in old_manifest['files']) == old_manifest['total_bytes'] == 1048120,
        'old49 actual payload bytes')
require((AUTHOR / 'old49-candidate-static-proof-immutable.json').read_bytes()
        == (old_root / 'candidate-static-proof.json').read_bytes(), 'old49 static proof immutable reference')
old_proof = json_load(AUTHOR / 'old49-candidate-static-proof-immutable.json')
transport = json_load(AUTHOR / 'actual91-transport-proof092.json')
require(transport['actual_root_commit'] == FIXED and len(transport['products']) == 2, 'actual91 transport source binding')
for product in old_proof['products']:
    name = Path(product['candidate_path']).name
    old_bytes = (AUTHOR / 'actual91-leaves' / 'rouge' / name).read_bytes()
    new_bytes = (AUTHOR / 'candidate' / 'rouge' / name).read_bytes()
    require(old_bytes == (old_root / 'prospective91-base' / 'rouge' / name).read_bytes(), 'old49/actual91 baseline exact')
    require(new_bytes == (old_root / 'candidate' / 'rouge' / name).read_bytes(), 'old49/actual91 candidate exact')
    require((len(old_bytes), sha(old_bytes), len(new_bytes), sha(new_bytes))
            == (product['old_bytes'], product['old_sha256'], product['new_bytes'], product['new_sha256']),
            'old49 declared leaf bindings')

# Independently apply the four authorized textual blocks in memory and compare full bytes/AST.
window_tip = '只改变当前技能模型的观察范围，不把输入秒数当作技能持续时间；实际已计窗口见报告。已计窗口为0秒时不计算窗口平均DPS/HPS，未定位来源与未知回转仍保持原说明。'
timing_old = '秒数以技能开启为0；初动使用initial_target_windows等独立部署时间轴。此处为测试情景，当前尚未从战斗画面自动跟踪。动画参考值会自动加载；不要在这里填写培养属性。'
timing_extra = '区间按30Hz模拟帧换算，换算后结束须晚于开始。关闭逐帧时，常规连续攻击参考不按供靶/移动/中断区间逐帧调度；目标消失声明和友方潜在治疗仍按已有范围处理，未知时钟不补算。'
app_old = "        self.limit_window = QCheckBox('使用指定输出窗口（秒）')\r\n"
app_new = "        self.limit_window = QCheckBox('使用指定观察窗口（秒）')\r\n" + ''.join([
    f"        self.limit_window.setToolTip('{window_tip}')\r\n",
    f"        self.window_seconds.setToolTip('{window_tip}')\r\n",
    "        self.limit_window.toggled.connect(lambda:self.calculate())\r\n",
    "        self.window_seconds.valueChanged.connect(lambda:self.calculate())\r\n"])
damage_old = "            if skill.get('window_seconds'):\n                rows.append(metric('window_seconds','伤害观察窗口',skill['window_seconds'],'秒'))\n"
damage_new = "            if skill.get('window_seconds') is not None:\n                rows.append(metric('window_seconds','伤害观察窗口',skill['window_seconds'],'秒'))\n            if skill.get('window_seconds'):\n"
healing_old = "            if skill.get('window_seconds'):\n                rows.append(metric('window_hps','窗口平均 HPS',window_healing/skill['window_seconds'] if window_healing is not None else None,'治疗/秒'))\n"
healing_new = "            if skill.get('window_seconds') is not None:\n                rows.append(metric('window_seconds','治疗观察窗口',skill['window_seconds'],'秒'))\n" + healing_old
replacements = {
    'app.py': [(app_old, app_new),
               (f"        self.timing_scenario.setToolTip('{timing_old}')\r\n",
                f"        self.timing_scenario.setToolTip('{timing_old}{timing_extra}')\r\n")],
    'reporting.py': [(damage_old, damage_new), (healing_old, healing_new)]}
source_scope = []
patch = ''
for name, blocks in replacements.items():
    original_raw = (AUTHOR / 'actual91-leaves' / 'rouge' / name).read_bytes()
    candidate_raw = (AUTHOR / 'candidate' / 'rouge' / name).read_bytes()
    original, candidate = original_raw.decode(), candidate_raw.decode()
    expected = original
    inverse = candidate
    for old, new in blocks:
        require(expected.count(old) == 1 and inverse.count(new) == 1, f'authorized unique block: {name}')
        expected = expected.replace(old, new, 1)
        inverse = inverse.replace(new, old, 1)
    require(expected.encode() == candidate_raw and inverse.encode() == original_raw, f'whole-byte source scope: {name}')
    old_ast, new_ast = ast.parse(original), ast.parse(candidate)
    expected_function = 'make_damage_tab' if name == 'app.py' else 'build_report'
    old_fns = [n for n in ast.walk(old_ast) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == expected_function]
    new_fns = [n for n in ast.walk(new_ast) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == expected_function]
    require(len(old_fns) == len(new_fns) == 1, 'single authorized function')
    old_fns[0].body = []
    new_fns[0].body = []
    require(ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False),
            f'all other AST including signature exact: {name}')
    require((candidate_raw.count(b'\r\n') == candidate_raw.count(b'\n')) if name == 'app.py'
            else b'\r' not in candidate_raw, f'original newline convention: {name}')
    patch += ''.join(difflib.unified_diff(original.splitlines(keepends=True), candidate.splitlines(keepends=True),
                                        fromfile=f'a/rouge/{name}', tofile=f'b/rouge/{name}'))
    source_scope.append({'name': name, 'baseline': binding(AUTHOR / 'actual91-leaves' / 'rouge' / name),
                         'candidate': binding(AUTHOR / 'candidate' / 'rouge' / name),
                         'authorized_replacement_blocks': 2, 'only_changed_function': expected_function,
                         'whole_byte_inverse_exact': True, 'all_other_AST_including_signatures_exact': True})
require(patch.encode() == (AUTHOR / 'candidate-flow092.patch').read_bytes(), 'independently regenerated exact patch')
require(sum(line.startswith('@@ ') for line in patch.splitlines()) == 4, 'four patch hunks')
require({str(f.relative_to(AUTHOR / 'candidate')) for f in (AUTHOR / 'candidate').rglob('*') if f.is_file()}
        == {'rouge/app.py', 'rouge/reporting.py'}, 'only two candidate files')

inputs = json_load(AUTHOR / 'public-inputs092.json')
case_ids = ['damage-zero', 'finite-healing-zero', 'friendly-healing-enemy-zero', 'finite-healing-long']
require([x['id'] for x in inputs['cases']] == case_ids, 'four frozen cases only')
cases = {x['id']: x['input'] for x in inputs['cases']}
saved, ledgers, caches, gzip_receipts = {}, {}, {}, []
for variant in ('baseline', 'draft'):
    ledger = json_load(AUTHOR / f'{variant}-actual-ledger092.json')
    require(ledger['status'] == 'PASS' and ledger['variant'] == variant, 'saved ledger variant/status')
    require(ledger['actual_public_entries'] == 4 and len(ledger['saved_records']) == 4, 'saved API entries')
    require(ledger['public_entry_trace'] == [{'case_id': c, 'phase': 'public'} for c in case_ids], 'API trace exact')
    require(ledger['external_formatter_requests'] == [{'case_id': c, 'mode': m} for c in case_ids
                                                     for m in ('estimate', 'default', 'technical')], 'external formatter requests trace')
    expected_formatters = []
    for case in case_ids:
        for request, module, function, technical in [('estimate', 'rouge.estimate', 'format_estimate', None),
                ('estimate', 'rouge.reporting', 'format_report', False),
                ('default', 'rouge.reporting', 'format_report', False),
                ('technical', 'rouge.reporting', 'format_report', True)]:
            expected_formatters.append({'case_id': case, 'request': request, 'module': module,
                                       'function': function, 'technical': technical})
    require(ledger['actual_formatter_entries'] == expected_formatters, 'actual formatter entry trace')
    require(all(ledger[k] == 0 for k in ('explicit_external_project_helper_calls', 'Qt', 'Wine', 'tests')),
            'historical saved external helpers/Qt/Wine/tests zero')
    require(ledger['source_current_730_verified_before_run'] is True and ledger['no_actual_Qt_or_app_import'] is True,
            'historical ledger boundary declarations')
    saved[variant] = {}
    for index, receipt in enumerate(ledger['saved_records'], 1):
        record = gzip_load(receipt)
        gzip_receipts.append(receipt)
        case = record['case_id']
        require(case == case_ids[index - 1] and case not in saved[variant], 'saved case order/uniqueness')
        require(record['variant'] == variant and record['error'] is None, 'successful saved variant result')
        require(record['input_before'] == native_encode(cases[case]) == record['input_after'], 'caller native before/after exact')
        checked_native(record['input_before'], f'{variant}/{case}/input')
        require(record['input_JSON_before'] == canonical(cases[case]) == record['input_JSON_after'], 'caller JSON before/after exact')
        require(record['caller_unchanged'] is True, 'saved caller equality declaration')
        result = checked_native(record['result_native_tree'], f'{variant}/{case}/result')
        require(record['result_native_tree'] == record['result_after_formatters_native_tree'], 'formatter post-result native exact')
        require(canonical(result) == record['result_JSON'], 'whole result native/JSON exact binding')
        require(set(record['texts']) == {'estimate', 'default', 'technical'}, 'three saved text modes')
        require(all(type(v) is str and v for v in record['texts'].values()), 'nonempty saved text')
        require(record['texts']['estimate'] == record['texts']['default'], 'saved estimate/default exact')
        require(record['ledger_after_call'] == {'actual_public_entries': index,
                'external_formatter_requests': index * 3, 'actual_formatter_entries': index * 4}, 'saved cumulative entry counts')
        saved[variant][case] = (record, result)
    cache = gzip_load(ledger['saved_cache'])
    gzip_receipts.append(ledger['saved_cache'])
    require(len(cache) == 9, 'nine complete observed cache objects')
    expected_observer_trace = []
    for name, entry in cache.items():
        require(set(entry) == {'first_native_tree', 'final_native_tree', 'first_phase', 'first_case_id', 'equal_complete_native_tree'},
                'complete cache entry schema')
        require(entry['first_native_tree'] == entry['final_native_tree'] and entry['equal_complete_native_tree'] is True,
                'complete cache first/final native exact')
        checked_native(entry['first_native_tree'], f'{variant}/{name}/cache')
        digest = sha(canonical(entry['first_native_tree']).encode())
        expected_observer_trace.append({'cache': name, 'case_id': entry['first_case_id'], 'phase': entry['first_phase']})
        for record, _ in saved[variant].values():
            require(set(record['observed_cache_state_after_call']) == set(cache), 'per-case complete observed cache keys')
            observed = record['observed_cache_state_after_call'][name]
            require(observed == {'native_tree_sha256': digest, 'equal_first_native_tree': True}, 'saved per-call cache digest/equality')
    require(ledger['observed_cached_function_returns'] == expected_observer_trace, 'saved first cache-return trace')
    caches[variant] = cache
    ledgers[variant] = ledger
require(caches['baseline'] == caches['draft'], 'whole cache packets equal across variants')
require(len(gzip_receipts) == len({x['path'] for x in gzip_receipts}) == 10, 'ten distinct saved gzip bindings')
diagnostic = json_load(AUTHOR / 'seal-diagnostic092.json')
require(diagnostic['verification']['saved_gzip_receipts'] == gzip_receipts, 'seal diagnostic gzip receipt bindings')

pair_evidence = []
summary = json_load(AUTHOR / 'saved-comparison-summary092.json')
for case in case_ids:
    old_record, old_result = saved['baseline'][case]
    new_record, new_result = saved['draft'][case]
    require(old_record['input_before'] == new_record['input_before'], 'paired caller input exact')
    expected_section = 'damage' if case == 'damage-zero' else 'healing'
    effective = old_result['estimate']['skill']['window_seconds']
    altered = deepcopy(new_result)
    old_sections = {x['id']: x for x in old_result['report']['sections']}
    require(len(old_sections) == len(old_result['report']['sections']), 'unique baseline report sections')
    require([x['id'] for x in altered['report']['sections']] == list(old_sections), 'section IDs/order exact')
    removed = []
    for section in altered['report']['sections']:
        if section['id'] != expected_section:
            continue
        require(not any(x['key'] == 'window_seconds' for x in old_sections[section['id']]['metrics']), 'baseline qualified row absent')
        positions = [i for i, x in enumerate(section['metrics']) if x['key'] == 'window_seconds']
        require(len(positions) == 1, 'one added qualified window row')
        row = section['metrics'].pop(positions[0])
        label = '伤害观察窗口' if expected_section == 'damage' else '治疗观察窗口'
        require(native_encode(row) == native_encode({'key': 'window_seconds', 'label': label, 'value': effective, 'unit': '秒'}),
                'exact added row types/value/order')
        require(effective is not None, 'qualified effective window non-None')
        removed.append({'section_id': section['id'], 'row': row, 'native_value': native_encode(row['value'])})
    require(len(removed) == 1, 'one removal only')
    require(native_encode(altered) == old_record['result_native_tree'], 'whole typed-native result inverse exact')
    require(canonical(altered) == old_record['result_JSON'], 'whole JSON result inverse exact')
    text_evidence = {}
    line = removed[0]['row']['label'] + '：' + f'{effective:.2f}' + ' 秒'
    for mode in ('estimate', 'default', 'technical'):
        original_text, draft_text = old_record['texts'][mode], new_record['texts'][mode]
        require(line not in original_text.splitlines(), 'baseline added text line absent')
        pieces = draft_text.splitlines(keepends=True)
        matches = [i for i, piece in enumerate(pieces) if piece.rstrip('\r\n') == line]
        require(len(matches) == 1, 'one qualified saved line only')
        del pieces[matches[0]]
        require(''.join(pieces) == original_text, 'entire saved text inverse exact')
        text_evidence[mode] = {'removed_lines': [line], 'remaining_saved_text_exact': True,
                             'baseline_sha256': sha(original_text.encode()), 'draft_sha256': sha(draft_text.encode())}
    skill = old_result['estimate']['skill']
    qualified_metrics = next(s['metrics'] for s in new_result['report']['sections'] if s['id'] == expected_section)
    if case in ('damage-zero', 'finite-healing-zero'):
        require(type(effective) is float and effective.hex() == '0x0.0p+0', 'typed float zero effective window')
        require(not any(r['key'] in ('window_dps', 'window_hps') for r in qualified_metrics), 'zero average row omission preserved')
    if case == 'friendly-healing-enemy-zero':
        require(cases[case]['timing']['target_disappears_seconds'] == 0 and effective == 6.0
                and skill['window_healing'] == 4760.0, 'saved friendly healing with enemy disappearance zero')
    if case == 'finite-healing-long':
        require(cases[case]['window_seconds'] == 60.0 and effective == 30.0 == skill['duration_seconds'],
                'saved requested60/effective30 finite healing boundary')
    pair_evidence.append({'case_id': case, 'qualified_section': expected_section,
        'requested_window_native': native_encode(cases[case]['window_seconds']), 'effective_window_native': native_encode(effective),
        'unchanged_observed_window_damage': skill.get('window_damage'), 'unchanged_observed_window_healing': skill.get('window_healing'),
        'removed_qualified_rows': removed, 'whole_native_inverse_exact': True, 'whole_JSON_inverse_exact': True,
        'three_saved_text_inverses': text_evidence, 'caller_unchanged_both': True, 'result_unchanged_by_formatters_both': True})
require(pair_evidence == summary['pairs'], 'author pair summary independently reconstructed exact')
request_counts = Counter(x['mode'] for l in ledgers.values() for x in l['external_formatter_requests'])
entry_counts = Counter(x['function'] + ('_technical' if x['technical'] else '_default') if x['function'] == 'format_report'
                       else x['function'] for l in ledgers.values() for x in l['actual_formatter_entries'])
require(dict(request_counts) == {'estimate': 8, 'default': 8, 'technical': 8}, 'recorded24 request modes')
require(dict(entry_counts) == {'format_estimate': 8, 'format_report_default': 16, 'format_report_technical': 8}, 'recorded32 formatter entries')
require(manifest['recorded_original_execution'] == handoff['execution'] == {
    'public_API_entries': 8, 'external_formatter_requests': 24, 'actual_formatter_entries': 32}, 'author historical execution binding')
require(manifest['new_project_calls_this_seal'] == handoff['new_project_calls_this_seal'] == ZERO, 'author sealing calls zero')
require(diagnostic['complete_goal_attempts'] == 2 and diagnostic['known_prior_transport_failures'] == 1
        and diagnostic['current_attempt_result'] == 'completed', 'author sealing failure boundary preserved')
boundary = json_load(AUTHOR / 'root-attempt-boundary091-immutable.json')
require(boundary['observed_total_preparation_failures'] == 4 and boundary['no_claim_three_attempt_rule_was_fully_followed_in_old_preparation'] is True,
        'older preparation stop-boundary failure preserved')

after = repo_state()
require(after == before, 'repository still fixed and clean after saved/source review')
require({str(f.relative_to(AUTHOR)): binding(f) for f in sorted(AUTHOR.rglob('*')) if f.is_file()} == inventory,
        'every author file unchanged after independent review')
evidence = {'format_version': 1, 'status': STATUS, 'author_actual_inventory': inventory,
    'source_scope': source_scope, 'saved_gzip_receipts': gzip_receipts, 'saved_pair_inverse_evidence': pair_evidence,
    'recorded_original_execution': {'public_API_entries': 8, 'external_formatter_requests': 24, 'actual_formatter_entries': 32},
    'recorded_original_external_request_modes': dict(request_counts), 'recorded_original_formatter_entries': dict(entry_counts),
    'cache_packet_count': 2, 'complete_observed_cache_objects_per_variant': 9,
    'complete_observed_cache_first_final_and_across_variants_exact': True,
    'cache_scope': ledgers['baseline']['cache_scope'], 'prepublic_frozen_files_verified': 14,
    'actual91_fixed_leaves_verified': 11, 'maintained_current_fixed_Git_files_verified': 730,
    'maintained_current_fixed_Git_bytes': 26071424, 'old49_archived_files_verified': 49,
    'old49_archived_bytes': 1048120, 'old49_manifest_binding': binding(old_original_manifest),
    'author_seal_failure_boundary': {'complete_goal_attempts': 2, 'known_prior_transport_failures': 1,
        'prior_failure_evidence_origin': diagnostic['prior_failure']['evidence_origin'],
        'current_attempt_result': 'completed'},
    'older_preparation_failure_boundary': {'binding': binding(AUTHOR / 'root-attempt-boundary091-immutable.json'),
        'observed_total_preparation_failures': 4, 'historical_stop_boundary_violation_preserved': True},
    'repository_before': before, 'repository_after': after, 'author_all_53_files_unchanged': True,
    'project_calls_this_review': ZERO, 'executed_author_scripts': [], 'whole_source_tree_copies_this_review': 0,
    'tracked_edits_this_review': 0}
write_json('independent-evidence092.json', evidence)
receipt = {'format_version': 1, 'status': STATUS, 'review_scope': 'saved-source-review-passed',
    'root_runtime_status': 'pending', 'fixed_root_commit': FIXED,
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(), 'author_directory': str(AUTHOR),
    'author_manifest': binding(manifest_path), 'author_handoff': binding(handoff_path),
    'author_payload_file_count': 51, 'author_payload_total_bytes': 2555186,
    'candidate_products': handoff['candidate_products'], 'independent_evidence': binding(HERE / 'independent-evidence092.json'),
    'checker': binding(Path(__file__)),
    'verified': {'gzip_bindings': 10, 'saved_results_native_JSON_caller_postformatter': 8,
        'whole_typed_native_and_JSON_pair_inverses': 4, 'entire_saved_text_inverses': 12,
        'complete_cache_packets': 2, 'complete_observed_cache_objects_per_variant': 9,
        'frozen_prepublic_files': 14, 'fixed_actual91_source_leaves': 11,
        'maintained_current_fixed_Git_files': 730, 'old49_archived_payload_files': 49,
        'source_candidate_files': 2, 'authorized_app_blocks': 2, 'authorized_reporting_blocks': 2},
    'product_scope': 'Only MainWindow.make_damage_tab observation-window label/tooltips and toggled/valueChanged calculate signals plus timing tooltip; build_report damage/healing length rows use window_seconds is not None. Existing average guards and all other source bytes/AST are preserved.',
    'saved_result_scope': 'Four frozen successful input pairs; remove exactly one qualified report window_seconds row and one corresponding saved line per text mode. All remaining whole typed-native values/types/order, JSON, texts, caller inputs, formatter post-results and complete observed cache first/final trees are exact.',
    'recorded_original_execution': manifest['recorded_original_execution'],
    'project_calls_this_review': ZERO, 'tracked_edits_this_review': 0, 'whole_source_tree_copies_this_review': 0,
    'author_all_files_unchanged': True, 'old49_not_copied_here': True,
    'failure_boundary': 'Historical four preparation failures and stop-boundary violation remain in immutable root-attempt-boundary091. Author sealing complete-goal attempts=2, prior transport failures=1; prior transport detail is parent-message evidence, without original tool output in author packet. This review completed its saved/source objective without project runtime calls.',
    'limitations': ['No project API/helper/formatter/tests/Qt/Wine calls were made for this review; historical8/24/32 counts are verified from saved ledgers only.',
        'Signal delivery, actual project-window behavior, regression and root archive acceptance remain for root runtime validation.',
        'Only four saved successful inputs are covered; error/guard behavior is unchanged statically and was not freshly executed.',
        'Complete cache preservation covers nine observed first/final dict/list data returns. Cold initialization is recorded; cache-hit entry counts and all cache functions were not measured.',
        'No native Windows/game clocks, hidden activation/tick/stack/probability rules or generic long-window clipping claim is established. Unknown mechanics remain unknown.'],
    'root_next_actions': ['Apply exactly the two bound candidate products only after this saved-source receipt passes integration validation.',
        'Run appropriate root regression and actual project window acceptance; retain native Windows/game limitations.',
        'Archive author51 payload files plus excluded author manifest/handoff with separate root bindings; archive this minimal independent packet with separate root bindings.'],
    'receipt_and_review_manifest_handoff_excluded_from_self_binding': True, 'finalstopwrite': True}
write_json('independent-review-receipt092.json', receipt)
review_payload = [binding(HERE / name) for name in ('review_saved_source092.py', 'independent-evidence092.json', 'independent-review-receipt092.json')]
review_manifest = {'format_version': 1, 'status': STATUS, 'fixed_root_commit': FIXED,
    'files': [{'source_path': x['path'], 'archive_path': Path(x['path']).name, 'bytes': x['bytes'], 'sha256': x['sha256']} for x in review_payload],
    'file_count': 3, 'total_bytes': sum(x['bytes'] for x in review_payload),
    'excluded_metadata': ['FINAL-review-manifest092.json', 'review-handoff092.json'],
    'manifest_and_handoff_excluded_to_avoid_circular_bindings': True,
    'root_archive_must_also_include_excluded_metadata': True, 'finalstopwrite': True}
write_json('FINAL-review-manifest092.json', review_manifest)
review_handoff = {'format_version': 1, 'status': STATUS, 'fixed_root_commit': FIXED,
    'review_directory': str(HERE), 'receipt': binding(HERE / 'independent-review-receipt092.json'),
    'manifest': binding(HERE / 'FINAL-review-manifest092.json'),
    'payload_file_count': 3, 'payload_total_bytes': review_manifest['total_bytes'],
    'excluded_metadata_to_include_in_root_archive': review_manifest['excluded_metadata'],
    'project_calls_this_review': ZERO, 'tracked_edits_this_review': 0, 'finalstopwrite': True}
write_json('review-handoff092.json', review_handoff)
for item in review_manifest['files']:
    check_file(item)
check_file(review_handoff['receipt'])
check_file(review_handoff['manifest'])
require({f.name for f in HERE.iterdir() if f.is_file()} == set(x['archive_path'] for x in review_manifest['files'])
        | set(review_manifest['excluded_metadata']), 'minimal final review packet exact inventory')
print(canonical({'status': STATUS, 'receipt': review_handoff['receipt'],
    'manifest': review_handoff['manifest'], 'handoff': binding(HERE / 'review-handoff092.json'),
    'project_calls_this_review': ZERO, 'finalstopwrite': True}))
