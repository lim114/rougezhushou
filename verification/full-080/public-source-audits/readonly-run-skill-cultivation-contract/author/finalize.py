import gzip, hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
IND = OUT / 'independent'
freeze = json.loads((OUT / 'freeze75-receipt.json').read_bytes())
verified = 0
for name, expected in freeze['files'].items():
    source = OUT / ('frozen75' if name.startswith('rouge/') else 'prior-receipts') / name
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected['sha256'] and len(raw) == expected['bytes'], name
    verified += 1
flow = json.loads((OUT / 'synthetic-flow-probe-receipt.json').read_bytes())
raw = gzip.decompress((OUT / 'synthetic-flow-public-whole-outcomes.json.gz').read_bytes())
assert hashlib.sha256(raw).hexdigest() == flow['raw_sha256'] and len(raw) == flow['raw_bytes']
source = json.loads((IND / 'independent-source-layer-receipt.json').read_bytes())
topic = gzip.decompress((IND / source['archived_original']['file']).read_bytes())
assert hashlib.sha256(topic).hexdigest() == source['original_topic']['sha256'] and len(topic) == source['original_topic']['bytes']
conclusion = {'schema_version': 1, 'status': 'READONLY_DEFER_INSUFFICIENT_ACCOUNT_TO_RUN_BINDING', 'baseline_head': freeze['baseline_head'], 'game_original_commit': source['original_topic']['commit'], 'not_a_completed_numbered_section': True, 'new_gate_or_mathematics': False, 'production_patch': None, 'supported_original_facts': ['Six first-recruitment tips explicitly give an elite-one capability ceiling.', 'Six charUpgradeTable pairs explicitly give PHASE_1/common7/mastery0 and PHASE_2/common7/mastery3 parameters.', 'Character common training/per-skill unlock/mastery training records and ten-level skill parameters are distinct source layers.'], 'unproved_binding': ['Account common ranks5..7 actually used by an already unlocked S1 in an E0 temporary form.', 'Version-specific consumer of charUpgradeTable selecting rows and combining account common/mastery rank with current run elite/promotion and recruitment kind.', 'Exact official help defining temporary-form common-rank/mastery inheritance.'], 'restart_conditions': ['Version-pinned explicit official help contract naming account skill rank/mastery and temporary run form.', 'Public readable row consumer plus account/run field binding and promotion/recruitment selection.', 'A reproducible matching observation distinguishing account rank/mastery, run elite, selected skill and effective rank across temporary form and promotion.'], 'current_code_observed': ['Present run member uses only noninvalid run skill_ranks; account ranks are not silently borrowed.', 'Unknown rank is a labeled preview7 belowE2 and10 atE2.', 'Promotion invalidates old run ranks; producer separately queries E2 mastery evidence.', 'Existing UI skill availability and API elite/mastery gates remain unchanged.'], 'validation': {'author_public_calculate_calls': flow['actual_public_calculate_calls'], 'accepted': flow['accepted'], 'exact_error_outcomes': flow['errors'], 'author_flow_method': 'exact immutable AST bodies and expressions with synthetic controls', 'actual_qt_or_native': False, 'independent_source_public_calculate_calls': 0, 'full_frozen_source_and_prior_receipts_unchanged': verified, 'public_outcome_gzip_verified': True, 'pinned_topic_gzip_verified': True, 'linux_full_app_import_failure_retained_and_not_retried': True}, 'boundaries': {'root_working_tree_edited': False, 'private_state_used': False, 'native_binary_downloaded': False, 'wine_or_game_used': False, 'prior_sealed_sections_changed': False, 'fresh_network_download': False}}
(OUT / 'final-readonly-conclusion.json').write_text(json.dumps(conclusion, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': conclusion['status'], 'frozen_files_verified': verified, 'conclusion_sha256': hashlib.sha256((OUT / 'final-readonly-conclusion.json').read_bytes()).hexdigest()}))
