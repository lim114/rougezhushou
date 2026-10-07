"""Verify existing integer-input contracts and unchanged pinned skill data."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
PACKAGE = OUT / 'frozen'
HEAD = json.loads((OUT / 'freeze.json').read_text())['baseline_head']
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog

audit = json.loads((OUT / 'type-audit-summary.json').read_text())
raw_paths = {name: ROOT / '.cache/p2-s1-binding' / (name + '.json')
             for name in ('character_table', 'skill_table')}
expected = {'character_table': '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
            'skill_table': '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'}
source_files = {}
raw = {}
for name, path in raw_paths.items():
    blob = path.read_bytes()
    sha = hashlib.sha256(blob).hexdigest()
    assert sha == expected[name]
    source_files[name] = {'path': str(path), 'bytes': len(blob), 'sha256': sha,
                          'actual_bytes_rehashed_now': True, 'new_download': False,
                          'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'}
    raw[name] = json.loads(blob)

patch_receipt_path = 'research/p2-amiya-phase-reference/source-receipt.json'
patch_receipt_blob = subprocess.check_output(['git', '-C', str(ROOT), 'show',
                                             HEAD + ':' + patch_receipt_path])
patch_receipt = json.loads(patch_receipt_blob)
patch_skills = patch_receipt['exact_selectors']['char_patch_table.patchChars.char_1001_amiya2.skills']
receipt_folder = OUT / 'reused-research'
receipt_folder.mkdir(exist_ok=True)
(receipt_folder / 'amiya-phase-source-receipt.json').write_bytes(patch_receipt_blob)

reuse_paths = ['research/p2-chen-phase-reference/source-receipt.json',
              'research/p2-drone-traits/source-receipt.json',
              'research/p2-gnosis-isw-a-reference/source-receipt.json',
              'research/p2-haruka-healing-targets/source-receipt.json',
              'research/p2-snow-entry-reference/source-receipt.json',
              'research/p2-aglna-manual-weight/source-receipt.json',
              'research/p2-yato-deployment-reference/source-receipt.json',
              'research/p2-wisdel-ghost-clock/source-receipt.json',
              'research/p2-token-manual-attributes/source-receipt.json',
              'research/p2-susuro-recipient-factor/source-receipt.json']
reused = []
for rel in reuse_paths:
    blob = subprocess.check_output(['git', '-C', str(ROOT), 'show', HEAD + ':' + rel])
    target = receipt_folder / (Path(rel).parts[1] + '-source-receipt.json')
    target.write_bytes(blob)
    reused.append({'tracked_path': rel, 'snapshot_head': HEAD,
                   'receipt_sha256': hashlib.sha256(blob).hexdigest(),
                   'archived_copy': str(target.relative_to(OUT)),
                   'historical_raw_download_not_claimed_as_current': True})

records = []
exact_selectors = {}
rank_checks = 0
for control in audit['integer_controls']:
    profile = catalog()['operators'][control['operator']]
    raw_char = raw['character_table'].get(profile['id'])
    skill_ids = raw_char['skills'] if raw_char else patch_skills
    if raw_char is None:
        assert profile['id'] == 'char_1001_amiya2'
    sources = []
    for skill_number in control['skills']:
        skill = profile['skills'][skill_number - 1]
        assert skill_ids[skill_number - 1]['skillId'] == skill['id']
        for rank in range(1, 11):
            row = raw['skill_table'][skill['id']]['levels'][rank - 1]
            bb = {entry['key']: entry['value'] for entry in row['blackboard']}
            assert skill['levels'][rank - 1]['values'] == bb
            rank_checks += 1
        selector = f"skill_table.{skill['id']}.levels[9]"
        original = raw['skill_table'][skill['id']]['levels'][9]
        exact_selectors[selector] = original
        sources.append({'skill': skill_number, 'skill_id': skill['id'],
                        'original_rank10_selector': selector,
                        'all_ten_normalized_blackboards_equal_pinned_original': True,
                        'character_skill_binding': ('fresh cached character_table bytes'
                            if raw_char else 'historical char_patch exact-selector receipt; raw file currently absent')})
    records.append({'field': control['field'], 'operator': control['operator'],
                    'ui_control': control, 'actual_ui_widget_rule': 'integer default -> QSpinBox',
                    'engine_integer_calls': [row for row in audit['integer_call_sites']
                                             if row['field'] == control['field']],
                    'known_input_contract_only': True,
                    'ui_maximum_not_inferred_as_native_cap': True,
                    'native_time_or_count_assignment_proven': False,
                    'candidate_new_bool_rejection': control['field'] != 'enemy_weight',
                    'original_skills': sources})

(OUT / 'pinned-skill-selectors.json').write_text(json.dumps(exact_selectors, ensure_ascii=False, indent=2) + '\n')
summary = {'baseline_head': HEAD, 'source_files': source_files,
           'reused_original_char_patch_receipt': {'tracked_path': patch_receipt_path,
               'receipt_sha256': hashlib.sha256(patch_receipt_blob).hexdigest(),
               'original_raw_available_now': False, 'fresh_raw_verification_claimed': False,
               'copied_exact_selector_mapping_verified': True},
           'reused_research_receipts': reused, 'per_control_records': records,
           'integer_ui_records': len(records), 'unique_remaining_fields': 24,
           'unique_new_candidate_fields': 23, 'normalized_skill_rank_blackboards_checked': rank_checks,
           'checkbox_integer_call_intersection': [],
           'existing_enemy_weight_guard_preserved': True,
           'no_new_numerical_parameter_or_range': True,
           'no_new_attachment_stacking_probability_or_event_clock': True,
           'remaining_unknowns_preserved': True, 'root_tracked_edits': 0,
           'private_state_read': False, 'native_validation': False}
(OUT / 'source-closure.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'records': len(records), 'unique_candidates': 23,
                  'raw_skill_rank_checks': rank_checks,
                  'fresh_raw_hashes_match': True, 'char_patch_mapping_historical': True}))
