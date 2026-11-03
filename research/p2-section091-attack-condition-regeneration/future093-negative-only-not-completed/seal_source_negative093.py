"""Bounded source-only packet. Never imports or executes the project."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def put(name, data):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def js(name, value):
    put(name, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


inputs = {}
fixed = {}
for name in ('rouge/summons.py', 'rouge/reporting.py', 'rouge/relics.py',
             'rouge/operator_options.py'):
    data = git('show', BASE + ':' + name)
    put('fixed-git/' + name, data)
    current = (ROOT / name).read_bytes()
    fixed[name] = {'commit': BASE, 'git_blob': git('rev-parse', BASE + ':' + name).decode().strip(),
                   'bytes': len(data), 'sha256': sha(data),
                   'working_read_bytes': len(current), 'working_read_sha256': sha(current),
                   'working_equal_fixed': current == data}
    if current != data:
        put('working-read/' + name, current)

catalog_bytes = git('show', BASE + ':rouge/data/catalog.json')
catalog = json.loads(catalog_bytes)
current_catalog = (ROOT / 'rouge/data/catalog.json').read_bytes()
assert current_catalog == catalog_bytes, 'catalog changed; stop before evidence interpretation'
alias = catalog['operators']['kaltsit']
assert alias['id'] == 'char_1052_kalts2'
assert list(alias['tokens']) == ['token_10068_kalts2_mtship']
assert alias['modules'] == []
js('fixed-git/catalog-kaltsit-alias-record.json', alias)
fixed['rouge/data/catalog.json'] = {
    'commit': BASE, 'bytes': len(catalog_bytes), 'sha256': sha(catalog_bytes),
    'git_blob': git('rev-parse', BASE + ':rouge/data/catalog.json').decode().strip(),
    'working_equal_fixed': True,
    'saved_object_selector': 'operators.kaltsit',
    'full_catalog_copy_in_packet': False,
}

raw_info = {}
raw_values = {}
raw_specs = {
    'character_table': (ROOT / '.cache/p2-s1-binding/character_table.json',
                        '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'),
                       'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'),
                           '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
}
for name, (path, expected) in raw_specs.items():
    data = path.read_bytes()
    assert sha(data) == expected, (name, 'pinned original mismatch')
    raw_info[name] = {'path': str(path), 'bytes': len(data), 'sha256': sha(data),
                      'original_commit': GAME, 'raw_bytes_rehashed': True,
                      'new_download': False, 'full_raw_copy_in_packet': False,
                      'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/' + GAME + '/zh_CN/gamedata/excel/' + name + '.json'}
    # No new all-module/phase audit: battle_equip is hashed only.
    if name != 'battle_equip_table':
        raw_values[name] = json.loads(data)

char = raw_values['character_table']['char_1052_kalts2']
equip = raw_values['uniequip_table']['equipDict']
matches = {key: value for key, value in equip.items() if value.get('charId') == 'char_1052_kalts2'}
assert char['displayTokenDict'] == {'token_10068_kalts2_mtship': True}
assert not matches
js('selected-original-identity.json', {
    'source_commit': GAME,
    'character_selector': 'character_table.char_1052_kalts2',
    'character_complete_original_object': char,
    'uniequip_selector_query': 'uniequip_table.equipDict values whose charId == char_1052_kalts2',
    'uniequip_matching_original_records': matches,
    'query_uses_full_rehashed_pinned_equipDict': True,
    'current_hotfix_checked': False,
    'no_inference_of_absence_in_other_versions': True,
})

reused = [
    (Path('/workspace/.continuation/p2-summon-module-source-next-audit/source-inventory-receipt.json'), 'reused/source-inventory-receipt.json'),
    (Path('/workspace/.continuation/p2-summon-module-source-next-audit/pinned-owned-token-module-selectors.json'), 'reused/pinned-owned-token-module-selectors.json'),
    (Path('/workspace/.continuation/p2-summon-module-source-next-audit/public-artifacts-manifest-v1.json'), 'reused/public-artifacts-manifest-v1.json'),
    (Path('/workspace/.continuation/p2-passive-qualification-candidates088/negative-review-receipt.json'), 'reused/passive-negative088.json'),
    (ROOT / 'research/p2-wang-token-module-reference/NOTE.md', 'reused/wang-completed-reference-NOTE.md'),
    (ROOT / 'research/p2-token-duration/NOTE.md', 'reused/token-duration-completed-reference-NOTE.md'),
    (Path('/workspace/.continuation/p2-run-environment-audit-after-070/NOTE071.md'), 'reused/environment-completed071-NOTE.md'),
    (Path('/workspace/.continuation/p2-cultivation-talent-audit-after-075/NOTE077.md'), 'reused/cultivation-completed077-NOTE.md'),
]
for path, name in reused:
    data = path.read_bytes()
    put(name, data)
    inputs[str(path)] = {'bytes': len(data), 'sha256': sha(data), 'packet_path': name}

js('preparation-read-diagnostics.json', {
    'status': 'source-only preparation diagnostics; no product execution',
    'events': [
        {'kind': 'oversized_read_output', 'attempt_count': 1,
         'cause': 'An initial broad research rg search reached saved result JSON and long lines; tool output was truncated.',
         'source_before_interpretation_used': False,
         'recovery': 'Stopped broad result-content searches; used explicit known receipt paths, static keys and bounded source spans.',
         'exact_full_console_saved': False, 'product_edits': 0},
        {'kind': 'missing_markdown_glob', 'attempt_count': 1,
         'command': 'rg on p2-summon-module-source-next-audit/*.md and *receipt*.json',
         'exit_code': 2,
         'cause': 'The directory has no .md file; rg reported the nonexistent glob while receipt read succeeded.',
         'recovery': 'Used the enumerated source-inventory-receipt.json and original manifest without retrying the nonexistent glob.',
         'product_edits': 0},
    ],
    'same_problem_unresolved_after_three_attempts': False,
    'numeric_prototype_created': False,
    'tests_or_project_helpers_run': False,
})

js('source-read-receipt093.json', {
    'status': 'FINAL_BOUNDED_NEGATIVE', 'prepared_utc': datetime.now(timezone.utc).isoformat(),
    'fixed_product_commit': BASE,
    'working_tree_context': 'Root section 091 changes are present and root alone owns tracked edits; fixed Git snapshots remain distinct from working reads.',
    'head_at_seal': git('rev-parse', 'HEAD').decode().strip(),
    'branch_at_seal': git('branch', '--show-current').decode().strip(),
    'fixed_and_working_sources': fixed, 'pinned_originals': raw_info, 'reused_inputs': inputs,
    'prior_inventory_scope': {'modules': 8, 'phases': 24,
                              'scope_reused_without_reexecuting_prior_script': True,
                              'new_all_module_phase_selector_audit': False},
    'new_source_fact': 'Current product alias kaltsit is char_1052_kalts2 with tactical-anchor token, not original Kaltsit/Mon3tr. Full pinned equipDict has zero charId matches for this identity.',
    'confirmed_positive_functional_candidates': 0,
    'numeric_candidate': None, 'product_patch': None,
    'not_a_completed_section093': True,
    'independent_p2_fallback_review': {
        'shared_token_parameters': 'Existing direct-cost/duration scopes and manual all_units token panel pipeline are already implemented; their existence does not prove token deployment or life.',
        'cultivation_qualification': 'Reused completed 077 and bounded negative 088 receipts; no new counterexample identified and no prior matrix rerun.',
        'run_environment': 'Reused completed 071 source conditions; actual account activation and native outbuff/map consumers still need a distinct source binding.',
        'window_controls': 'Excluded; separately assigned root section092 and section091 actual UI.'},
    'restart_conditions': {
        'identity': 'A distinct supported identity, pinned module record, or version-matched current evidence must exist before proposing an original Kaltsit/Mon3tr route.',
        'wang_limits': 'Exact token_10064_wang_stone1 prefab/talent attachment and producer/consumer binding for manual, extra and S3-generated counts; no inventory-to-presence inference.',
        'mechanist_barrier': 'Exact mcnist_equip_1_3_p3 callback/attachment plus HP operand, first pulse/reset and alive-window evidence before scheduling or combining numeric shield effects.',
        'wisdel_module': 'Distinct exact ghost/module binding or independent current event/panel evidence; raw absence of token fields is not proof that native scripts have no effect.',
        'deepcolor': 'Independent version-matched livepanel/hotfix evidence; existing pinned proof is not current game certification.',
        'environment': 'Exact rogue_6_outbuff and mode/map consumer binding with account-state evidence before applying new values.'},
    'counts': {'new_project_API_calls': 0, 'new_project_helper_calls': 0,
               'tests': 0, 'Qt': 0, 'Wine': 0, 'network_calls': 0,
               'tracked_edits_by_author': 0, 'private_state_reads': 0},
    'full_original_tables_retained_at_existing_public_paths': True,
    'packet_contains_bounded_objects_and_prior_original_selectors_not_full_raw_tables': True,
})

put('NOTE.md', '''# 召唤物模组第93功能组来源准备：有界负证

固定产品来源为2cbc45f，第91节working改动另存并明确标记。本包只是来源准备，不是完成第93节；作者没有项目调用、测试、Qt/Wine、网络、私态读取或tracked修改。

当前kaltsit alias是凯尔希·思衡托char_1052_kalts2和战术锚点。固定完整character与uniequip原件重核SHA后，原char.displayTokenDict和完整equipDict精确身份查询均支持这一映射；此版本该身份的模组原记录为0。原凯尔希/Mon3tr不能据名字套入此身份，这也不证明当前热更新没有新增模块。

先前8模组24阶段的原始selector审计逐字复用，没有重跑全表。深海色已知费用/HP/在场参考、望固定费用与机械师持续参数都已有实现。剩余Wang数量、机械师屏障、Wisdel原生继承和Deepcolor当前版本仍缺各自明确绑定，参数不能制造新时钟、加法、倍率或实际存在。

独立备用范围仅复用已完成071/077及有界负证088，核对当前共享token参数和manual/all_units报告管道。没有确认新的资格/报告/错误合同缺陷，不建立镜像测试或数值草案。窗口控制由其他功能组负责，避免重叠。

source-read-receipt093.json逐项列出源SHA、fixed Git/实际working区别、已复用范围及恢复条件；selected-original-identity.json保留完整被选char原对象和真实空查询结果。完整原表仍在已有公开路径，本小包只保留有界原件/选择器，绝不称包含完整表。两项只读准备问题单独记录于preparation-read-diagnostics.json，均未延续到产品工作。
'''.encode())

files = []
for path in sorted(OUT.rglob('*')):
    if path.is_file():
        data = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': path.relative_to(OUT).as_posix(),
                      'bytes': len(data), 'sha256': sha(data)})
manifest = {'schema_version': 1, 'status': 'FINAL_V1_STOPWRITE',
            'kind': 'bounded source-only negative; not a completed section', 'files': files}
js('public-artifacts-manifest-v1.json', manifest)
manifest_bytes = (OUT / 'public-artifacts-manifest-v1.json').read_bytes()
js('final-handoff093.json', {'status': 'FINAL_V1_STOPWRITE', 'packet_dir': str(OUT),
                            'manifest': 'public-artifacts-manifest-v1.json',
                            'manifest_sha256': sha(manifest_bytes),
                            'payload_files': len(files), 'payload_bytes': sum(row['bytes'] for row in files),
                            'manifest_and_handoff_self_excluded': True,
                            'confirmed_positive_candidates': 0, 'section093_completed': False,
                            'root_is_only_product_integration_owner': True})
print(json.dumps({'payload_files': len(files), 'payload_bytes': sum(row['bytes'] for row in files),
                  'manifest_sha256': sha(manifest_bytes),
                  'handoff_sha256': sha((OUT / 'final-handoff093.json').read_bytes())}))
