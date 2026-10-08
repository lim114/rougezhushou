"""Read-only source/saved-evidence audit; no project imports, API calls or tests."""
import ast
import difflib
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
AUTHOR = Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-draft')
ROOT_PROPOSAL = Path('/workspace/.continuation/p2-section086-root-test-contract-supplement')
BASE = '9ef5a469673502754db3be320a8eece9a7fd18d4'
ERROR = 'double_charge 不接受文本条件；请使用布尔值。'
ORIGINAL = ROOT_PROPOSAL / 'test_orchid_near_text_input-original085.py'
ADAPTED = ROOT_PROPOSAL / 'test_orchid_near_text_input-adapted086.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def binding(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(data), 'sha256': sha(data)}


def save(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return path


def ast_key(node):
    return ast.dump(node, include_attributes=False)


def excerpt(path, ranges):
    lines = path.read_text(encoding='utf-8').splitlines()
    return {**binding(path), 'excerpts': [
        {'first_line': start, 'last_line': end,
         'lines': [{'line': n, 'text': lines[n-1]} for n in range(start, end+1)]}
        for start, end in ranges]}


def main():
    final_manifest = AUTHOR / 'archivable-public-manifest-final86.json'
    assert sha(final_manifest.read_bytes()) == '4a2ca8dc22ddd13b0319bdb12544102b680d7a87722366806c9de728e12a7b58'
    manifest = json.loads(final_manifest.read_bytes())
    # Bind only the specific frozen sources and saved evidence read here.
    sources = {row['source_path']: row for row in manifest['files']}
    frozen = json.loads((AUTHOR / 'review-freeze86.json').read_bytes())
    approved = []
    for row in frozen['files']:
        path = Path(row['source_path'])
        data = path.read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        declared = sources[str(path)]
        assert declared['bytes'] == len(data) and declared['sha256'] == sha(data)
        current = (REPO / row['path']).read_bytes()
        assert current == data, row['path']
        approved.append({'path': row['path'], **binding(path), 'current_root_exact': True})

    proposal_path = ROOT_PROPOSAL / 'migration-proposal.json'
    proposal = json.loads(proposal_path.read_bytes())
    original = ORIGINAL.read_bytes()
    adapted = ADAPTED.read_bytes()
    assert sha(original) == proposal['original_sha256'] == '8fd8cdaf383ab54945404ad33c5f610c2fc2e4bb018800b1a8bed3193a0dce86'
    assert sha(adapted) == proposal['adapted_sha256'] == '62c74f4f094442e689e60d5e6306fbdd6cec357173ff7a295bb5c47cf93af901'
    historical = subprocess.check_output(['git', '-C', str(REPO), 'show', BASE + ':tests/test_orchid_near_text_input.py'])
    assert historical == original
    assert b'\r\n' not in original + adapted
    old_line = "        self.assertEqual(record({**args,'double_charge':'false'}),default)\n"
    new_lines = ("        # Section86 rejects text at this actual S1 consumer; S2/S3 stay ignored.\n"
                 "        with self.assertRaisesRegex(ValueError,'^double_charge 不接受文本条件；请使用布尔值。$'):\n"
                 "            record({**args,'double_charge':'false'})\n")
    old_text = original.decode('utf-8')
    new_text = adapted.decode('utf-8')
    assert old_text.count(old_line) == 1 and old_text.replace(old_line, new_lines, 1) == new_text
    old_tree, new_tree = ast.parse(old_text), ast.parse(new_text)
    target = 'test_double_charge_scope_defaults_and_unbound_clock_are_preserved'
    old_method = next(n for n in ast.walk(old_tree) if isinstance(n, ast.FunctionDef) and n.name == target)
    new_method = next(n for n in ast.walk(new_tree) if isinstance(n, ast.FunctionDef) and n.name == target)
    assert len(old_method.body) == len(new_method.body)
    changes = [i for i, (a, b) in enumerate(zip(old_method.body, new_method.body)) if ast_key(a) != ast_key(b)]
    assert changes == [3]
    old_method.body[3] = new_method.body[3]
    assert ast_key(old_tree) == ast_key(new_tree)

    # Check registration's one original insertion, without repeating the root's
    # whole 720/719-file audits or writing its sealed checker/receipts.
    registry_path = REPO / 'scripts/verify_cloud.py'
    registry = registry_path.read_bytes()
    base_registry = (AUTHOR / 'baseline/scripts/verify_cloud.py').read_bytes()
    token = b'MODULES = (\n'
    insertion = b'    "tests.test_remaining_boolean_condition_text_input",\n'
    assert base_registry.count(token) == 1
    assert registry == base_registry.replace(token, token + insertion, 1)

    damage = AUTHOR / 'draft/rouge/damage.py'
    engine = AUTHOR / 'draft/rouge/operator_engine.py'
    engine_tree = ast.parse(engine.read_text(encoding='utf-8'))
    get_lines = sorted(n.lineno for n in ast.walk(engine_tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == 'get' and n.args
        and isinstance(n.args[0], ast.Constant) and n.args[0].value == 'double_charge')
    assert get_lines == [1031, 1034, 1314, 1441]
    damage_text = damage.read_text(encoding='utf-8')
    assert "if op=='char_1048_orchd2' and number==1:conditions+=('double_charge',)" in damage_text
    assert damage_text.index("result['report']=build_report(scenario,result)") < damage_text.index('conditions={')
    excerpt_path = save('source-excerpts.json', {
        'damage': excerpt(damage, [(306, 357)]),
        'engine': excerpt(engine, [(1023, 1037), (1308, 1317), (1439, 1453)]),
        'old_test': excerpt(ORIGINAL, [(109, 124)]),
        'adapted_test': excerpt(ADAPTED, [(109, 126)])})

    chosen = (137, 138, 139, 140, 141, 142, 209, 259, 267, 268)
    saved = {}
    saved_bindings = []
    for side in ('baseline', 'draft'):
        path = AUTHOR / (side + '-matrix.jsonl.gz')
        data = path.read_bytes()
        declared = sources[str(path)]
        assert len(data) == declared['bytes'] and sha(data) == declared['sha256']
        saved_bindings.append(binding(path))
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            saved[side] = {r['index']: r for line in stream if (r := json.loads(line))['index'] in chosen}
        assert tuple(saved[side]) == chosen
    saved_receipts = []
    for index in chosen:
        before, after = saved['baseline'][index], saved['draft'][index]
        assert before['field'] == after['field'] == 'double_charge'
        assert before['input_typed_before'] == after['input_typed_before']
        assert before['input_unchanged'] and before['catalog_unchanged']
        assert after['input_unchanged'] and after['catalog_unchanged']
        same = None
        if index in (137, 138, 139, 140, 267, 268):
            assert before['outcome'] == 'accepted'
            assert after['outcome'] == 'error' and after['error_type'] == 'ValueError' and after['error_message'] == ERROR
        elif index in (141, 142, 209):
            assert before['outcome'] == after['outcome'] == 'accepted'
            same = all(before[key] == after[key] for key in ('result_typed', 'result', 'reports'))
            assert same
        else:
            assert before['outcome'] == after['outcome'] == 'error'
            assert (before['error_type'], before['error_message']) == (after['error_type'], after['error_message'])
            assert before['error_message'] == 'near_previous_deployment 不接受文本条件；请使用布尔值。'
        saved_receipts.append({'index': index, 'label': before['label'], 'input': before['input'],
            'baseline_outcome': before['outcome'], 'draft_outcome': after['outcome'],
            'draft_error': after.get('error_message'), 'whole_native_json_and_three_texts_same': same})

    receipt = save('static-contract-migration-receipt.json', {
        'status': 'PASS_STATIC_CONTRACT_MIGRATION', 'base_commit': BASE,
        'original_section86_manifest': binding(final_manifest),
        'root_proposal': binding(proposal_path), 'original_test': binding(ORIGINAL), 'adapted_test': binding(ADAPTED),
        'original_test_exact_git_object': True, 'single_assertion_ast_node_replaced': True,
        'all_other_test_ast_nodes_unchanged': True, 'only_text_change_is_replacement_and_comment': True,
        'qualification': {'owner': 'char_1048_orchd2', 'skill': 1,
            'late_guard': 'reject str only after old calculation/finisher/report and earlier text guards',
            'other_skills': 'S2/S3 inactive for double_charge', 'default_and_nonstr': 'original engine truthiness/default True untouched',
            'source_get_lines': get_lines,
            'consumers': 'S1 optional five-arrow component/parameter; first/recharge time-SP and initial/cycle event-SP cost use existing expressions'},
        'approved_products_and_new_test_current_root_exact': approved,
        'current_registry': binding(registry_path), 'registry_exact_original_single_insertion': True,
        'saved_evidence_bindings': saved_bindings, 'saved_rows_read_only': saved_receipts,
        'old720_vs_migrated719': 'Root reports sealed checker passed 720 before this old-test migration. After migration 719 old source files plus this one test require the separate root supplemental checker; this author audit does not repeat either whole audit or overwrite prior evidence.',
        'source_and_saved_only': True, 'new_API_calls': 0, 'new_project_helper_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
        'tracked_edits': 0, 'original130_modified': False,
        'fresh_targeted_selected': 'No author execution. Root reports targeted1 PASS and selected attempt2 1027run/1026pass/1 historicalskip/0error; root owns the original logs and separate719+1 checker evidence.',
        'limits': 'No new clock, probability, native attachment, game validation or universal old-error precedence claim.'})
    prep = save('read-only-preparation-note.json', {
        'event': 'One rg read referenced draft-root/tests instead of draft-root/draft/tests and reported path missing; the matrix_plan read in that same call succeeded.',
        'missing_path': str(AUTHOR / 'tests/test_remaining_boolean_condition_text_input.py'),
        'correct_path': str(AUTHOR / 'draft/tests/test_remaining_boolean_condition_text_input.py'),
        'corrected_by_read_only_followup': True, 'new_API_calls': 0, 'dependent_project_calls': 0,
        'product_test_failure': False})
    note = OUT / 'NOTE.md'
    with note.open('x', encoding='utf-8') as stream:
        stream.write('旧测试的 S1 double_charge 文本兼容断言与第 86 节实际消费条件上的拒绝文本合同冲突。\n\n'
            '这里只读确认提案精确替换一条断言及新增说明；其余布尔值、默认值、S2/S3忽略字段和未绑定时钟断言 AST 完全不变。两产品及新测试仍与正式冻结字节相同，registry 保留原唯一插入。已有保存矩阵的相关行与源码一致，没有新执行项目。\n\n'
            '迁移前 root 已保存720件其余旧源码校验；迁移后须按719件不变加1件旧测试合同迁移另作 root 补证，本包不声称重跑或覆盖旧720收据。原130件及其manifest不改。root 负责 tracked 应用、定向测试及精选第二轮。\n')
    handoff = save('handoff-final.json', {
        'status': 'FINAL_SEALED_STATIC_PASS', 'receipt': binding(receipt),
        'manifest_path': str(OUT / 'public-manifest.json'),
        'migration': 'Approve the one old S1 text assertion contract migration based on sealed86 source and saved evidence.',
        'root_next': 'Archive this supplement with root-owned migration, targeted/selected and719+1 source receipts, then commit86. No author API/test rerun.',
        'new_API_calls': 0, 'new_project_helper_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0, 'tracked_edits': 0,
        'original130_immutable': True, 'stop_changes': True})
    paths = [Path(__file__), receipt, excerpt_path, prep, note, handoff, proposal_path, ORIGINAL, ADAPTED]
    rows = []
    for path in paths:
        row = binding(path)
        row['archive_path'] = ('author/' if path.parent == OUT else 'root-proposal/') + path.name
        rows.append(row)
    manifest_out = save('public-manifest.json', {'version': 1, 'status': 'FINAL_SEALED', 'files': rows,
        'file_count': len(rows), 'total_bytes': sum(r['bytes'] for r in rows)})
    for row in rows:
        assert binding(Path(row['source_path'])) == {k: row[k] for k in ('source_path', 'bytes', 'sha256')}
    print(json.dumps({'status': 'FINAL_SEALED_STATIC_PASS', 'files': len(rows),
        'bytes': sum(r['bytes'] for r in rows), 'manifest': binding(manifest_out), 'handoff': binding(handoff),
        'receipt': binding(receipt), 'new_API_calls': 0, 'tests': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
