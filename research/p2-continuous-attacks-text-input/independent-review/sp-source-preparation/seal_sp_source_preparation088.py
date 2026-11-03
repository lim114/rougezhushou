"""Readonly source preparation. No project import/execution or JSON input parse."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
SAVED = Path('/workspace/.continuation/p2-section088-candidate-audit')
COMMIT = '0f27027e7e1f49c08f298706b599e310e299238b'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(source_path, archive_path, data):
    return {'source_path': str(source_path), 'archive_path': str(archive_path), 'sha256': sha(data), 'bytes': len(data)}


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


assert not (OUT / 'sp-source-preparation-receipt088.json').exists(), 'Do not rewrite a sealed packet'
specs = [
    ('rouge/sp_events.py', 'sp-events-source-excerpts.txt', [(27, 53), (56, 141), (174, 184)]),
    ('rouge/timing.py', 'timing-source-excerpts.txt', [(41, 81), (94, 101), (160, 179)]),
    ('rouge/operator_engine.py', 'engine-caller-source-excerpts.txt', [(1311, 1350), (1408, 1455), (1471, 1475)]),
    ('rouge/estimate.py', 'legacy-caller-source-excerpts.txt', [(92, 101), (157, 182), (197, 205)]),
    ('rouge/damage.py', 'per-core-order-source-excerpts.txt', [(235, 245), (273, 285), (288, 303), (307, 326), (335, 358)]),
]
source_receipts = []
text = {}
for relative, name, ranges in specs:
    data = subprocess.run(['git', '-C', str(REPO), 'show', COMMIT + ':' + relative],
                          capture_output=True, check=True).stdout
    # The root is integrating section087 in other tracked paths. Bind only these
    # current consumer source bytes, rather than claiming the whole tree clean.
    current = (REPO / relative).read_bytes()
    assert current == data, 'Requested current consumer changed: ' + relative
    lines = data.decode('utf-8').splitlines()
    text[relative] = lines
    parts = ['Fixed source ' + COMMIT + ':' + relative, 'Full source sha256 ' + sha(data),
             'Full source bytes ' + str(len(data)), '']
    for first, last in ranges:
        parts.append('Lines ' + str(first) + '-' + str(last))
        parts.extend(str(i) + ': ' + lines[i - 1] for i in range(first, last + 1))
    snippet = ('\n'.join(parts) + '\n').encode('utf-8')
    (OUT / name).write_bytes(snippet)
    source_receipts.append({'source_path': COMMIT + ':' + relative, 'source_sha256': sha(data),
                            'source_bytes': len(data), 'current_worktree_equals_fixed_source': True,
                            'ranges': ranges, 'bounded_excerpt': record(COMMIT + ':' + relative, OUT / name, snippet)})

events = text['rouge/sp_events.py']
timing = text['rouge/timing.py']
assert events[130].strip() == "attacks = scenario.get('continuous_attacks', True)"
assert events[131].strip() == 'if (native_attack > 0 and attacks) or wait_next_attack:'
assert events[135].strip() == 'if attacks and native_attack > 0:'
assert events[177].strip().endswith('if attacks else None')
assert timing[64].strip() == 'if incoming_interval is not None:'
assert timing[68].strip() == "elif scenario.get('continuous_attacks',True):"
assert timing[77].strip() == 'if wait_next_attack:'

saved_specs = [
    ('source-handoff088.json', 'b06d68e6d5c9ec0979d9d4316dcc002e3c0b7e84c4652a714ee2f0810dac34e6', True),
    ('public-source16-summary.json', '2b977fa6b63e58f647ecc7fcda820e9eb9b8bccc92a1702ac7e5b725ba8a7f5d', True),
    ('saved-source16-comparison.json', '878df870e0e1e91eff1985ee4bd2063d8f4e2f61638c056fded8c903fa0d4280', True),
    ('public-source16.jsonl.gz', '8fca26d426756c49103459d615a5176415dc8991ae2fa7f1385cbb9a07839881', False),
    ('sp-subreview/handoff-sp-negative088.json', 'adfa4c6709bed37dd4915a4c75cbec26072ecdad69de5bb2e2d9a1fc3c902029', False),
    ('sp-subreview/sp-negative-source-receipt088.json', '05ff623ccbab1f250fd4faf46a813c0b7f1cc4a2349dee694ed4fe3d7c21f963', False),
    ('sp-subreview/public-artifacts-manifest-sp088.json', '257a332c0773afc26c37dfac229a9c964fcc75d3e30e980f00e89103b1e57c13', False),
]
bindings = []
copied_saved = []
for relative, expected, copy in saved_specs:
    data = (SAVED / relative).read_bytes()
    assert sha(data) == expected, relative
    archive = OUT / ('bound-' + Path(relative).name) if copy else None
    if copy:
        archive.write_bytes(data)
        copied_saved.append(archive.name)
    bindings.append({**record(SAVED / relative, archive if archive else 'external immutable reference only', data),
                     'copied_to_this_packet': copy, 'decoded_or_recomputed': False})

diagnostic = '''One readonly preparation command ran git show without -C from the external saved-evidence directory.
stderr: fatal: not a git repository (or any of the parent directories): .git
The piped text selection produced no source content; independent sha256sum outputs in the same command were still readable and did not depend on that source read. No product import/helper/API/test/state read occurred. Final preparation uses explicit git -C /workspace/rougezhushou for every source read and check=True. No source receipt was sealed from failed output.
An earlier batched display of independently successful source/metadata reads was output-truncated; bounded reads and exact path checks were used afterward. Original source16/API comparison was not rerun.
'''
(OUT / 'preparation-diagnostics.txt').write_text(diagnostic, encoding='utf-8')
receipt = {
    'version': 1, 'status': 'SOURCE_PREPARATION_FROZEN_PENDING_AUTHOR_FORMAL_FREEZE',
    'fixed_commit': COMMIT, 'formal_product_review': False,
    'scope': 'Only SP event/periodic continuous_attacks consumers, exact current code/caller order and existing sealed source evidence. No project/helper/API/test execution, source parser, input JSON decoder or new draft.',
    'sources': source_receipts, 'existing_saved_metadata_bindings': bindings,
    'event_charge_actual_qualification': {
        'native_attack': '90 chooses skill sp_increment for INCREASE_WHEN_ATTACK, else caller attack_sp;91 adds attached attack_sp rules. Actual local total must be >0 for outgoing attack-SP credit at136-139. Do not infer a positive value merely from event-SP presence.',
        'incoming': '95 computes native_incoming only for INCREASE_WHEN_TAKEN_DAMAGE;102 credits it only for explicit incoming attack events. received/event callbacks are assembled97-104 separately from outgoing stream.',
        'flag': '131 keeps raw get/default truthiness. Outgoing stream exists132 when native_attack>0 and attacks, OR independently when wait_next_attack.',
        'incoming_only_ignored_boundary': 'When actual native_attack<=0 and wait_next_attack=False, this function produces no outgoing stream or outgoing credit from continuous_attacks. Its raw read is not evidence that the flag changes the incoming-only calculation. Other caller/normal-plan consumers can still independently consume the flag.',
        'wait_next_attack_exception': 'wait_next_attack independently creates stream at132-135 even with native_attack0 or attacks false. If ready is not None,174-178 seeks next legal attack start and returns None when attacks is false. This is a separate flag effect and prevents a global native_attack0=>inactive rule.',
        'not_all_event_SP_union': 'has_event_sp covers received_sp/event_sp non-token rules, but neither has_event_sp nor any event table alone proves continuous_attacks is an active input. Use actual outgoing/native/caller/wait-next conditions, not all-owner/skill membership.',
    },
    'periodic_helper_actual_qualification': {
        'priority': '65 tests incoming_interval is not None before69 elif continuous_attacks. Any non-None incoming argument, including integer0, selects the incoming branch and suppresses the outgoing continuous branch; only positive incoming adds credits66-68.',
        'stream': '60-63 constructs timeline and attack stream before incoming/outgoing branch, regardless flag.69 keeps raw truthiness only for outgoing release credits when incoming_interval=None.',
        'wait_next': '78-80 uses stream next start after readiness without consulting continuous_attacks. Preserve this existing helper behavior; it differs from event_charge178.',
        'caller': 'Current extended INCREASE_WHEN_TAKEN_DAMAGE callers1348/1349/1419/1436 pass incoming_interval explicitly and omit wait_next_attack; attack-SP callers1341/1342/1416/1432 pass next_attack mode when relevant.',
    },
    'caller_and_error_order': {
        'prepared_source': 'damage._prepare_damage235 onward selects/validates skill/rank/attributes, then run/relic/attribute preparations273-277 before per-core evaluation. This is a bounded local ordering fact, not all outer errors.',
        'extended': 'engine legacy/mixed/attack/incoming recharge1311-1350 and frame/lockout/cycle1408-1438 precede event overrides1439-1452. Event path requires has_event_sp and mode not deployment/passive; call passes actual Amiya talent attack_sp and wait_next_attack mode1441-1450.',
        'legacy': 'estimate173 only checks has_event_sp; calls174-180 do not pass attack_sp or wait_next_attack, so defaults0/False apply. Existing charge/lockout/full computation can fail earlier.',
        'event_local_errors': 'event_phases67 validates supplied table schema before missing-phase early return80-82. Missing required phase returns before incoming_interval duplicate-input conflict86-88. Offset/block/recharge work72-75 occurs before that return; AttackTimeline129 validation comes later. Do not promise identical error reachability for all phases.',
        'periodic_local_errors': 'Recharge requirement/required-zero shortcut45-46, wine horizon48, config finite56-57, timeline60 and stream62 all precede incoming/outgoing branch65-71. Thus an incoming-only ignored flag does not imply helpers are error-free.',
        'late_report_boundary': 'Per-core evaluation uses Combat.calculate or legacy skill+estimate296-302, finishers and report307-321, then already integrated83-86 text guards322-358. Future condition guard must preserve the established old errors of its actual call path; no global outer-helper/error equivalence is claimed.',
    },
    'standalone_contract': 'Do not add new text rejection/coercion to sp_events.charge, periodic_charge_seconds, charge_seconds or other standalone helper entrypoints based on this preparation. Existing raw get/default truthiness stays unchanged; product guard, if authorized after author freeze, needs actual prepared-consumer scope and independent checks.',
    'historical_evidence_limit': 'The bound existing source16 summary/compare metadata describes three active controls and one inactive control. This child only rehashes their frozen public bytes and does not decode gzip, compare/reproduce16, call formatters, remeasure counters, or expand that saved coverage to event/periodic/qualification/old-error paths. Old SPnegative remains separate: no new SP multiplier/negative-source mechanism defect is confirmed.',
    'unknowns': ['Native timers, callback/lifecycle/attachment/stacking behavior are not inferred.', 'All event-SP scenarios do not share one continuous_attacks qualification.', 'Author product source/test/matrix formal freeze is still awaited; this is not a formal successful product review or count packet.'],
    'counts': {'application_imports': 0, 'application_API': 0, 'helpers': 0, 'formatters': 0, 'tests': 0,
               'source_parser': 0, 'JSON_input_decoder': 0, 'network': 0, 'Qt': 0, 'Wine': 0,
               'tracked_mutations': 0, 'product_drafts': 0, 'original_source16_reruns': 0},
    'restart': ['Wait for parent explicit author formal source/test/matrix freeze before any formal code or numerical review.', 'If these five current source bytes change, bind the new actual root source in a new sidecar; no old packet changes.', 'Parent/source080 handles new qualification union and root89 saved-source review; no extra agent/task/API expansion by this child.'],
    'diagnostics': str(OUT / 'preparation-diagnostics.txt'),
}
write_json('sp-source-preparation-receipt088.json', receipt)
note = '''第88节SP consumer纯来源准备封存；等待作者明确source/test/matrix正式冻结，尚非正式产品独审。

event_charge outgoing credit必须actual native_attack>0并且continuous truthy；incoming-only/native_attack0/wait=False此flag不决定该函数输出。wait_next_attack另行建stream，ready存在时又用continuous决定是否允许下个attack slot，因此不能把native_attack0一概忽略，更不能所有event-SP一概active。

periodic_charge incoming_interval is not None分支优先，即0也跳过continuous outgoing；函数提前建stream，wait-next随后不读continuous找slot。保留这个与event_charge不同的旧合同。standalone helper原rawtruthiness不得因本准备而加验证/强制转换。

extended与legacy eventcaller门控、attack_sp/wait-next参数不同；event schema/缺phase早return/incoming冲突/timeline与periodic config/stream错误先后已用固定代码片段记录。晚期per-core report和现83–86 guard之前旧路径错误保持；没有外推所有outer错误先后。

现root在别的tracked路径集成87，不把全树称clean。本准备五个消费者实际bytes均与固定0f27027相同。只绑定旧16source/public metadata和gzip hash，没有解压、重比、重跑、累计或伪造formal预算计数。旧SP阴性、89lead、87及其它sealed目录全部不改。

0API/helper/formatter/test/sourceparser/JSON输入解析/network/Qt/Wine/tracked/productdraft。记录一次外部cwd漏git-C导致的只读git failure及一次成功批读输出截断；最终脚本每项check=True、explicitgit-C，全部来源hash封好。原生clock/attachment/概率/叠加保持未知。
'''
(OUT / 'NOTE.md').write_text(note, encoding='utf-8')
receipt_bytes = (OUT / 'sp-source-preparation-receipt088.json').read_bytes()
write_json('sp-source-preparation-handoff088.json', {'version': 1,
    'status': 'SOURCE_PREPARATION_FROZEN_PENDING_AUTHOR_FORMAL_FREEZE', 'fixed_commit': COMMIT,
    'receipt': record('generated narrow readonly source preparation', OUT / 'sp-source-preparation-receipt088.json', receipt_bytes),
    'formal_product_review': False, 'new_product_calls': 0, 'tracked_mutations': 0,
    'key_boundary': 'native_attack>0 outgoing versus wait_next_attack exception; periodic incoming non-None priority; standalone raw truthiness retained.',
    'next': 'Parent explicit final author freeze required for separate formal code/typed/public/test review.'})
names = ['seal_sp_source_preparation088.py', *[name for _, name, _ in specs], *copied_saved,
         'preparation-diagnostics.txt', 'sp-source-preparation-receipt088.json', 'NOTE.md', 'sp-source-preparation-handoff088.json']
source_map = {name: COMMIT + ':' + relative for relative, name, _ in specs}
for relative, _, copy in saved_specs:
    if copy:
        source_map['bound-' + Path(relative).name] = str(SAVED / relative)
items = [record(source_map.get(name, 'generated external readonly preparation artifact'), OUT / name,
                (OUT / name).read_bytes()) for name in names]
write_json('v1-public-files-manifest088.json', {'version': 1, 'status': 'FINAL_FROZEN_SOURCE_PREPARATION',
    'files': items, 'file_count': len(items), 'total_bytes': sum(item['bytes'] for item in items), 'all_public': True,
    'excluded': ['manifest itself for self hash', 'Large source16 gzip/native public objects and whole repo/source copies', 'All previously sealed negative/87/89 evidence directories'],
    'formal_product_review': False, 'counts': receipt['counts']})
for item in items:
    data = Path(item['archive_path']).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256']
for name in ('sp-source-preparation-handoff088.json', 'v1-public-files-manifest088.json'):
    print(json.dumps(record('generated external preparation evidence', OUT / name, (OUT / name).read_bytes())))
print(json.dumps({'file_count': len(items), 'total_bytes': sum(item['bytes'] for item in items), 'formal_review': False}))
