"""Bind selected existing evidence and seal design; no project imports/calls."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/p2-continuous-attack-control-visibility091-source')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bound(path, archive):
    data = path.read_bytes()
    return {'source_path': str(path), 'archive_path': archive, 'bytes': len(data), 'sha256': sha(data)}


def write_json(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


manifest_path = SOURCE / 'manifest-source091.json'
assert sha(manifest_path.read_bytes()) == 'e085ece169ef52cfd97a4f656bd1cf370bdc29ae78abd13e7e14962e01435c78'
original = json.loads(manifest_path.read_bytes())
assert original['format_version'] == 1 and original['file_count'] == 34
by_archive = {r['archive_path']: r for r in original['files']}
selected = ['handoff-source091.json', 'visibility-source-receipt091.json',
            'app-continuous-control-all-references091.json',
            'existing-saved-output-projection091.json', 'source-reconstruction091.json',
            'bounded-curated-source-data091.json', 'source87/rouge/app.py',
            'source87/rouge/operator_engine.py', 'source87/rouge/catalog.py',
            'source87/rouge/relics.py', 'source87/rouge/offline_scope.py']
bindings = []
for name in selected:
    row = by_archive[name]
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], name
    bindings.append(dict(row))
refs = json.loads((SOURCE / 'app-continuous-control-all-references091.json').read_bytes())
assert refs['state_initialization']['checked_default'] is True
assert refs['serialization']['native_bool_producer'] == 'self.continuous_attacks.isChecked()'
assert refs['visibility']['line'] == 960
projection = json.loads((SOURCE / 'existing-saved-output-projection091.json').read_bytes())
assert projection['source16_bool_Amiya_E2_hidden_positive'] is True
assert projection['baseline60_bool_chen3_S3_warrior67_hidden_positive'] is True
assert projection['reference_only_Gummy_received118_False_True_whole_native_same'] is True
source_binding = {
    'status': 'SELECTED_EXISTING_EVIDENCE_BYTES_BOUND_NO_SOURCE_REAUDIT_OR_RECALCULATION',
    'named_source_commit': '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
    'source34_original_manifest': bound(manifest_path, manifest_path.name),
    'source34_original_count': 34, 'source34_original_total_bytes': 1138235,
    'selected_source_files_bound': bindings,
    'full_source34_reaudit_or_sourceprobes_repeated': False,
    'catalog_direct_Git_object_read_during_design': {
        'git_blob_sha1': 'fe6788a146129ea788a47e06b44beab59be07779', 'bytes': 1624372,
        'sha256': '061079249952deda98d6b391f577cec7fa2c67a018599155df1ea11d2205a01b',
        'source': 'Exact existing named-source-reconstruction metadata; plain Git cat-file/JSON only, no catalog() call.',
        'bounded_projection': ['mechanist S1 attack/S2–3 natural', 'Amiya S1–3 natural',
                               'Chen3 S1–3 natural', 'Silverash S1–3 natural',
                               'Gummy S1–2 natural', 'Kaltsit S1–3 natural'],
        'unimplemented_owner_qualification': 'catalog.py merges normalized implemented owner profiles; app1005–1023 preserves early-return status for absent owner/no skill.'},
    'source_locations': {'creation_default_and_row': [566, 567, 568],
                         'visibility': [949, 960, 967], 'serialization': [1028],
                         'explicit_button': [707, 708], 'existing_refresh_paths': [524, 553, 846, 847, 854, 856, 998],
                         'OPTIONS_only_toggle': [661, 667, 677],
                         'natural_consumers_engine': [1311, 1317, 1334, 1337],
                         'actual_qualification': ['selected_talents13–26', 'relics.prepare/offline_scope partition+matches']},
    'existing_saved_case_identifiers': {'mechanist': [1, 2], 'Amiya_E2S1': [9, 10],
                                       'Silverash_no_attack_credit': [13, 14],
                                       'Chen3_warrior67': [33, 34], 'Gummy118_reference': [19, 20],
                                       'Amiya_E0_E1_old_text_not_UI_bool': [15, 16, 17, 18]},
    'actual_GUI_transition_already_verified': False,
    'current91_app_or_backend_baseline_frozen': False,
    'new_project_API_helper_formatter_tests_Qt_Wine_network_calls': 0}
binding_path = OUT / 'source-binding091.json'
write_json(binding_path, source_binding)
design = {'status': 'REVIEWABLE_PRE_IMPLEMENTATION_DESIGN_ONLY_PENDING_FULL90',
          'planned_product_scope': ['app.update_skill_options continuous row visibility',
                                    'fixed continuous checkbox tooltip at creation'],
          'visibility': 'Implemented owner + valid selected skill + sp_type attack or natural; otherwise hidden, current value kept.',
          'preserved': ['same widget identity/defaultTrue', 'no setChecked/reset/value migration',
                        'native bool isChecked serialization', 'existing signals/explicit calculation button',
                        'backend numeric/unknown/report behavior'],
          'no_new_activation_helper': True, 'precise_processed_rule_visibility': 'Deferred outside this minimal scope',
          'unknowns': ['native acquisition/SP release/attachment/full clocks',
                       'received/event reference_only', 'E0/E1 old reference rows are text, not new bool measures'],
          'P1': 'paused', 'recognition': 'last',
          'formal_author_dependency': 'Full90 final and root explicit current-base scope/budget',
          'product_patch_created': False, 'new_calls': 0,
          'source_binding': str(binding_path), 'acceptance_plan': str(OUT / 'acceptance-plan091.json')}
design_path = OUT / 'design091.json'
write_json(design_path, design)
handoff_path = OUT / 'handoff-design091.json'
write_json(handoff_path, {'status': design['status'], 'candidate_section': 91, 'numbered_section_completed': False,
                          'source34_manifest': source_binding['source34_original_manifest'],
                          'design': bound(design_path, design_path.name),
                          'source_binding': bound(binding_path, binding_path.name),
                          'original_source34_unchanged': True, 'tracked_or_product_patch_mutations': 0,
                          'new_API_helper_formatter_tests_Qt_Wine_network_calls': 0,
                          'next_action': 'Root reviews design; only after full90 root triggers formal91 author with actual baseline/budget.',
                          'public_manifest': str(OUT / 'manifest-design091.json')})
files = [bound(p, p.name) for p in sorted(OUT.iterdir()) if p.is_file()]
manifest = {'version': 1, 'status': design['status'], 'files': files,
            'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files),
            'original_source34_referenced_not_copied_or_modified': True, 'new_project_calls': 0}
public_path = OUT / 'manifest-design091.json'
write_json(public_path, manifest)
for row in files:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256']
print(json.dumps({'status': design['status'], 'files': len(files), 'bytes': manifest['total_bytes'],
                  'manifest': bound(public_path, public_path.name), 'handoff': bound(handoff_path, handoff_path.name),
                  'new_project_calls': 0}))
