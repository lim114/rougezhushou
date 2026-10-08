"""Narrow readonly source-text lead; no project import/execution or state read."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '0f27027e7e1f49c08f298706b599e310e299238b'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record(path, data, source_path):
    return {'source_path': source_path, 'archive_path': str(path),
            'sha256': digest(data), 'bytes': len(data)}


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


assert not (OUT / 'source-lead-receipt089.json').exists(), 'Sealed packet must remain immutable'
specs = [
    ('rouge/run_state.py', 'run-state-source-excerpts.txt', [(76, 99), (245, 265), (372, 376), (435, 450)]),
    ('rouge/run_recognition.py', 'run-recognition-source-excerpts.txt', [(68, 97), (121, 128), (184, 191)]),
    ('rouge/app.py', 'app-forwarder-source-excerpts.txt', [(888, 895)]),
    ('rouge/visual_recognition.py', 'visual-producer-source-excerpts.txt', [(134, 143)]),
]
sources = []
source_lines = {}
for relative, archive_name, ranges in specs:
    data = subprocess.run(['git', '-C', str(REPO), 'show', COMMIT + ':' + relative],
                          check=True, capture_output=True).stdout
    lines = data.decode('utf-8').splitlines()
    source_lines[relative] = lines
    snippets = []
    for first, last in ranges:
        snippets.append('Lines ' + str(first) + '-' + str(last))
        snippets.extend(str(i) + ': ' + lines[i - 1] for i in range(first, last + 1))
    archive = ('Fixed source ' + COMMIT + ':' + relative + '\nFull source SHA256 ' + digest(data) +
               '\nFull source bytes ' + str(len(data)) + '\n\n' + '\n'.join(snippets) + '\n').encode('utf-8')
    (OUT / archive_name).write_bytes(archive)
    sources.append({'source_path': COMMIT + ':' + relative, 'source_sha256': digest(data),
                    'source_bytes': len(data), 'ranges': ranges,
                    **record(OUT / archive_name, archive, COMMIT + ':' + relative),
                    'archive_is_bounded_text_excerpt_not_full_source': True})

state = source_lines['rouge/run_state.py']
assert state[86].strip() == 'full_crew=type(crew) is int and len(incoming)==crew'
assert state[371].strip() == "crew=observed.get('crew_count')"
assert state[373].strip() == 'if crew is not None:'
assert state[374].strip() == "state['crew_count']=crew"
assert state[440].strip() == "if crew is not None and len({m['id'] for m in members})==crew:"
assert state[443].strip() == "member['present']=False"
apply_crew_occurrences = [{'line': i, 'text': state[i - 1]} for i in range(245, 451)
                          if 'crew' in state[i - 1]]
assert [item['line'] for item in apply_crew_occurrences] == [372, 374, 375, 441]
recognition = source_lines['rouge/run_recognition.py']
assert recognition[73].strip() == "values={int(t['text']) for t in texts if valid(t)}"
assert recognition[85].strip().startswith('values={int(text)')
assert recognition[90].strip().startswith('values={int(text)')
assert recognition[96].strip() == 'return None'
assert "crew_count=near_number(image,texts,crew,engine,side='right') if crew else None" in recognition[123]
assert "if crew:crew_count=near_number(image,texts,crew,engine,side='right')" in recognition[126]
assert "'crew_count':crew_count" in recognition[187]
assert 'self.run.apply(observed,captured_at)' in source_lines['rouge/app.py'][888]
assert "'crew_count':None" in source_lines['rouge/visual_recognition.py'][136]

diagnostic = '''Readonly preparation command attempted rg on guessed tests/test_run_state.py and tests/test_run_recognition.py alongside rouge source.
Exit code: 2.
stderr:
rg: tests/test_run_state.py: No such file or directory (os error 2)
rg: tests/test_run_recognition.py: No such file or directory (os error 2)
No tests, application imports, RunState construction/apply, helpers, network or state reads occurred. No repeat of the absent-path query. Subsequent exact fixed-commit source reads succeeded.
'''
(OUT / 'preparation-diagnostic.txt').write_text(diagnostic, encoding='utf-8')
write_json('source-lead-receipt089.json', {
    'version': 1, 'status': 'STATIC_LEAD_PENDING_REPRO', 'fixed_commit': COMMIT,
    'scope': 'crew_count only; separate from section088 repeated_attack. Readonly source text/hash inspection, no application or Python expression repro.',
    'sources': sources, 'apply_crew_text_occurrences': apply_crew_occurrences,
    'no_local_prior_crew_type_check': 'Entire RunState.apply lines245-450 read. Existing initial timestamp/run-id and member-buff validations do not type-check crew_count. The four literal crew-name occurrences are get, None predicate, store, completeness predicate. App.apply_run_observation forwards the observation directly to RunState.apply.',
    'static_lead': {
        'quantity_overwrite': 'Every observed crew value other than None is stored at375, including bool and float.',
        'false_empty_boundary': 'Python numeric equality lets len(empty_unique_ids)==False evaluate true. If the observation passes earlier apply branches and reaches441, an empty member list plus crew_count False satisfies completeness and marks previously present members absent at444 with history event445.',
        'other_aliases': 'True can equal unique count1 and integral float can equal a list count, so these invalid types can also establish completeness. They are static language/branch facts, not measured RunState results.',
        'restoration_mismatch': 'restore_origin_discovery_buffs87 already uses type(crew) is int; it excludes bool and float from its complete-list barrier. apply441 currently lacks that restriction.',
        'confirmed_public_bug': False,
        'runtime_repro_or_saved_state_read': False,
    },
    'actual_producer': {
        'near_number': '68-97 returns an element of an int-converted set, literal integer0 in two above-only verified-zero paths, or None. No Boolean/float crew output is emitted by this source.',
        'crew_binding': 'read_run124 and127 invoke near_number(side=right), then188 return crew_count unchanged. Crew right-side path does not use the above-only verified-zero helper branch.',
        'visual_fallback': 'visual_recognition137 explicitly emits crew_count None.',
        'reachability_limit': 'No evidence that genuine recognition produces False or float; this is an unchecked observed-input contract lead at RunState.apply. No claim of a real user observation, saved-state corruption or OCR misread.',
    },
    'minimal_guard_suggestion_only': {
        'position': 'Normalize crew locally immediately after observed.get at372 and before store375; reuse the normalized local variable for complete-list441. Existing repair87 already excludes bool/float.',
        'validity': 'Use exact type int and nonnegative count; invalid bool/float/other input becomes unknown for this count rather than an integer alias. No upper bound, type coercion or global-validator change proposed.',
        'valid_zero': 'Integer0 plus empty unique incoming roster must retain the existing full-empty-list removal behavior.',
        'valid_positive_partial': 'Positive integer plus fewer unique observed ids must not establish a full list or erase absent unseen members.',
        'unknown': 'None remains unread: do not replace stored crew count or establish list completeness.',
        'invalid': 'Invalid bool or float must neither replace stored count nor authorize complete-list removal; unrelated valid page evidence can still follow existing behavior.',
        'product_patch_created': False,
    },
    'unknowns_and_restart': ['Need root authorization for isolated temporary-state runtime reproduction and tests before any product-bug confirmation or numbered product section.',
                            'Future repro must satisfy existing timestamp/run-id and relic/member paths without hiding old errors, and assert full state/history/file preservation for invalid inputs.',
                            'Cover False/True/0.0/1.0, exact-int zero, positive complete/partial, None, unique-vs-duplicate member identities. Do not infer default relic or other state contracts from this source-only lead.',
                            'If fixed source changes or a prior crew validator is added, rebind in a new sidecar; do not change sealed packet.'],
    'counts': {'product_imports': 0, 'RunState_constructions': 0, 'RunState_apply_calls': 0, 'application_API': 0,
               'helpers': 0, 'tests': 0, 'private_state_reads': 0, 'Qt': 0, 'Wine': 0, 'network': 0,
               'tracked_mutations': 0, 'product_drafts': 0},
    'preparation_diagnostic_path': str(OUT / 'preparation-diagnostic.txt'),
})
note = '''第89节候选：STATIC_LEAD_PENDING_REPRO，未作公开运行时确认。

固定root86 0f27027。RunState.apply372读取crew；374只排None，375覆盖保存数量；441只有非None与unique成员数==crew即可建立完整队伍，444标缺席。完整函数245-450没有crew类型前置校验。False与空unique计数的数值相等可触发此分支，但本审没有构造状态、运行apply或确认真实输入曾发生；所有推论以旧分支正常到达441为条件。

同类restore_origin_discovery_buffs87已经type(crew)isint严格排bool/float。真实near_number读数是int或None（crew走side=right），视觉fallback明确None；不能把这一接口边界线索说成真实OCR失误。

最小建议仅在372读取后局部将非exact-int/非负计数归未知，375数量写入和441完整性判断共用该值。保留合法整数0+空清单清除；正整数缺页、None不清；bool/float不能覆盖数量或建立完整清单。无产品补丁，没有改变其它记录合并或制定全局校验。

0API/helper/test/Qt/Wine/私有state读取/tracked改动。保留一次rg猜测两个不存在test路径退出2的只读准备诊断，未执行任何测试或重试路径。后续须授权临时状态最小复现与完整state/history/file断言才可确认bug或推进产品小节。此lead不混第88节连续攻击布尔flag。
'''
(OUT / 'NOTE.md').write_text(note, encoding='utf-8')
receipt_data = (OUT / 'source-lead-receipt089.json').read_bytes()
write_json('source-handoff089.json', {'version': 1, 'status': 'STATIC_LEAD_PENDING_REPRO', 'fixed_commit': COMMIT,
    'receipt': record(OUT / 'source-lead-receipt089.json', receipt_data, 'generated readonly static source review'),
    'confirmed_public_bug': False, 'product_patch': False, 'calls': 0,
    'next_step': 'Root-authorized isolated temporary-state repro with exact types/whole state and history before product confirmation.'})
names = ['seal_source_lead089.py', 'run-state-source-excerpts.txt', 'run-recognition-source-excerpts.txt',
         'app-forwarder-source-excerpts.txt', 'visual-producer-source-excerpts.txt', 'preparation-diagnostic.txt',
         'source-lead-receipt089.json', 'NOTE.md', 'source-handoff089.json']
source_map = {archive: COMMIT + ':' + relative for relative, archive, _ in specs}
items = [record(OUT / name, (OUT / name).read_bytes(), source_map.get(name, 'generated external readonly review artifact')) for name in names]
write_json('v1-public-files-manifest089.json', {'version': 1, 'status': 'FINAL_FROZEN_SOURCE_LEAD', 'files': items,
    'file_count': len(items), 'total_bytes': sum(item['bytes'] for item in items), 'all_public': True,
    'excluded': ['manifest self hash', 'all private state, original whole source copies and product trees', 'every previous sealed086/087/088 artifact'],
    'counts': {'API': 0, 'helpers': 0, 'tests': 0, 'Qt': 0, 'Wine': 0, 'tracked': 0}})
for item in items:
    data = Path(item['archive_path']).read_bytes()
    assert len(data) == item['bytes'] and digest(data) == item['sha256']
for name in ('source-handoff089.json', 'v1-public-files-manifest089.json'):
    print(json.dumps(record(OUT / name, (OUT / name).read_bytes(), 'generated external readonly review artifact')))
print(json.dumps({'file_count': len(items), 'total_bytes': sum(item['bytes'] for item in items), 'status': 'STATIC_LEAD_PENDING_REPRO'}))
