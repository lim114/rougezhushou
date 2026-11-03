import gzip, hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
strict = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
records = json.loads(gzip.decompress((OUT / 'public-whole-outcomes.json.gz').read_bytes()))
sources = json.loads((OUT / 'pinned-four-owner-selectors.json').read_bytes())
selected = json.loads((OUT / 'selected-talents-and-conditional-relic-selectors.json').read_bytes())
checks = []

def result(record_id):
    record = records[record_id]
    assert record['outcome']['accepted']
    return record['outcome']['result']

def check(name, ids, predicate, detail):
    assert predicate, name
    checks.append({'claim': name, 'public_record_ids': ids, 'verified_readonly': True, 'detail': detail})

for mode, offset in (('frames', 0), ('continuous', 30)):
    ids = [408 + offset, 409 + offset, 410 + offset]
    check('Ines E0 stolen count 0/1/2 complete outcomes equal ' + mode, ids, len({strict(records[i]['outcome']) for i in ids}) == 1, 'Raw first talent begins E1L1; missing steal_atk fallback is zero. Old integer field validation remains active; this is not a request to change idle type contract.')
    for ids in ([417 + offset, 418 + offset], [419 + offset, 420 + offset]):
        check('Mizuki absent E2 second talent condition false/true complete outcomes equal ' + mode + ' E' + str(records[ids[0]]['input']['elite']), ids, strict(records[ids[0]]['outcome']) == strict(records[ids[1]]['outcome']), 'First talent is already unlocked at E0L1, with .2 arts scale; second talent attack bonus begins E2L1.')
    ids = [423 + offset, 424 + offset]
    check('Gnosis E0 no cold fragile multiplier ' + mode, ids, strict(result(ids[0])['components']) == strict(result(ids[1])['components']), 'The complete report carries different chosen-state descriptors, while the damage component is equal. State2 independently applies the previously proved universal frozen resistance -15, not an absent talent bonus.')
    i = 432 + offset
    shadow = next(c for c in result(i)['components'] if c['name'] == '残影单次爆炸条件参考')
    check('Wisdel E0 absent Good Gift produces no shadow damage or false pending ' + mode, [i], shadow['per_hit'] == shadow['total'] == shadow['hits'] == 0 and 'actual_total' not in shadow, 'Intrinsic class aftershock and S1 action clock retain their own legitimate pending flags. Positive manual ghost declarations remain separate provenance-unknown source declarations as section74 requires.')

talent_minimums = {}
for owner, data in sources.items():
    facts = []
    for index, group in enumerate(data['talents']):
        candidates = group['candidates']
        first = min(candidates, key=lambda c: (int(c['unlockCondition']['phase'][-1]), c['unlockCondition']['level'], c['requiredPotentialRank']))
        facts.append({'talent_index': index, 'name': first['name'], 'minimum_qualification': first['unlockCondition'], 'requiredPotentialRank': first['requiredPotentialRank'], 'raw_description': first['description'], 'raw_blackboard': first['blackboard']})
    talent_minimums[owner] = facts

conditions = selected['owner_matched_existing_conditional_rules']
sets = [{r['relic_id'] for r in conditions[owner]} for owner in conditions]
assert all(ids == sets[0] for ids in sets)
receipt = {
    'schema_version': 1,
    'baseline_head': '225cb66dc89143a3cd3a884bd6c62f47ed9d36bc',
    'conclusion': 'No supported new cultivation numeric/unknown repair candidate among the four assigned owners; no patch authored.',
    'not_a_completed_numbered_section': True,
    'qualified_api_claims': checks,
    'original_talent_minimum_qualification_facts': talent_minimums,
    'conditional_relic_scope': {'same_existing_13_recipient_applicable_conditional_relic_ids_for_all_four': sorted(sets[0]), 'no_owner_specific_raw_talent_gate_or_missing_condition_bug_demonstrated': True, 'not_an_exhaustive_native_relic_audit': True},
    'deferred_contract_question': {'owner': 'char_206_gnosis', 'record_ids': list(range(468, 477)), 'control_label': '全程状态：0无、1寒冷、2冻结', 'existing_reference_note': '初始未寒冷不证明后续不会寒冷', 'scope': 'cold_state multiplier reference contract differs from ISW-A actual lifecycle coverage wording', 'production_change': False, 'restart_conditions': ['Define and source-confirm whether cold_state is a global multiplier reference assumption or verified full actual cold coverage declaration.', 'Obtain matching native ISW-A attachment and coverage/lifecycle evidence before assigning actual DOT zero or deriving first tick/count.'], 'do_not_infer': ['raw blackboard is not an attachment script', 'E0 owner cannot invalidate externally declared frozen or ghost sources', 'initial state alone cannot establish future actual source absence']},
    'validation_limit': '477 actual frozen public calculate calls with complete strict JSON, all three text reports, or exact exception. These are readonly program observations, not current native/client verification.',
}
(OUT / 'readonly-conclusion-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
note = '''# Four-owner cultivation source audit (read only)

Frozen public implementation: `225cb66dc89143a3cd3a884bd6c62f47ed9d36bc`.
Original character / module tables: pinned `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`, retained public bytes rehashed without new downloads.

No supported new repair was found in the assigned Gnosis, Mizuki, Ines and Wisdel qualification paths. This audit is not a completed numbered section and has no production patch.

Ines E0 has no first talent, and zero attack-steal fallback makes count0/1/2 full outcomes identical in both timing modes. Mizuki's primary arts talent exists at E0 (.2 original scale); the E2 second-talent low-HP flag is numerically neutral at E0/E1 and gives identical complete outputs. Gnosis E0 cold0/cold1 damage components coincide because absent talent multiplier falls back to1; frozen still applies the separately proved universal -15 resistance rule. Wisdel E0 absent Good Gift gives zero shadow hits/damage and no shadow actual_total pending. The class aftershock / actual S1 action and independently declared ghost sources preserve their existing unresolved clocks.

477 public API calls are retained as complete strict JSON plus standard report, technical report and estimate, or exact error. 381 accepted and96 error outcomes include closed elite/skill/rank and cultivation/module boundaries. These observations do not constitute native/client verification. No input or cached catalog mutation occurred.

The Gnosis cold_state control says “全程状态” while the ISW-A actual source note says “初始未寒冷不证明后续不会寒冷”. Nine S2/module-stage records preserve this discrepancy; they are not sufficient evidence to assign actual DOT zero. Restart by clarifying/source-confirming the scenario contract, and by obtaining the exact ISW-A native attachment/coverage/lifecycle source for any actual clock claim. Raw blackboard values do not prove scripts or coexistence.

The matched conditional collectible selectors are the same existing13 relic IDs for all four profiles. No four-owner talent-specific missing-condition defect was demonstrated; general relic/native coverage remains outside this negative conclusion.

No tracked source, private state, Windows/Wine execution, native binary download or sealed previous-section artifact was changed.
'''
(OUT / 'READONLY_AUDIT.md').write_text(note)
names = ('freeze_and_sources.py', 'freeze75-receipt.json', 'pinned-four-owner-selectors.json', 'source-reuse-receipt.json', 'public_probes.py', 'public-whole-outcomes.json.gz', 'public-probe-receipt.json', 'selected-talents-and-conditional-relic-selectors.json', 'public-pair-comparison.json', 'summarize.py', 'readonly-conclusion-receipt.json', 'READONLY_AUDIT.md')
files = []
for name in names:
    data = (OUT / name).read_bytes()
    files.append({'source_path': str(OUT / name), 'archive_path': 'readonly-four-owner-cultivation-audit/' + name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
(OUT / 'public-artifacts-manifest-v1.json').write_text(json.dumps({'schema_version': 1, 'kind': 'readonly negative cultivation audit; not completed numbered section; no patch', 'files': files}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'public_files': len(files), 'public_bytes': sum(f['bytes'] for f in files), 'manifest_sha256': hashlib.sha256((OUT / 'public-artifacts-manifest-v1.json').read_bytes()).hexdigest(), 'conclusion_sha256': hashlib.sha256((OUT / 'readonly-conclusion-receipt.json').read_bytes()).hexdigest()}))
