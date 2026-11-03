import hashlib
import json
import datetime
import subprocess
from pathlib import Path

REPO = Path('/workspace/rougezhushou')
OUT = Path(__file__).parent


def metadata(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


character_path = REPO / '.cache/p2-s1-binding/character_table.json'
skill_path = REPO / '.cache/p2-s1-binding/skill_table.json'
character = json.loads(character_path.read_text())
skills = json.loads(skill_path.read_text())
bindings = {}
selectors = {}
for public, native, slot, skill_id in (
        ('mechanist', 'char_4230_mcnist', 1, 'skchr_mcnist_2'),
        ('mechanist', 'char_4230_mcnist', 2, 'skchr_mcnist_3'),
        ('silverash', 'char_1045_svash2', 1, 'skchr_svash2_2')):
    binding = character[native]['skills'][slot]
    assert binding['skillId'] == skill_id
    bindings[f'character_table.{native}.skills[{slot}]'] = binding
    selectors[f'skill_table.{skill_id}.levels'] = skills[skill_id]['levels']

references = []
for path in (REPO / 'research/p2-charge-clock/source-receipt.json',
             REPO / 'research/p2-empty-enemy-scope/source-receipt.json',
             Path('/workspace/.continuation/p2-after-051/shield-draft/research/p2-shield-break-reference/source-receipt.json'),
             Path('/workspace/.continuation/p2-after-051/shield-draft/research/p2-shield-break-reference/NOTE.md')):
    references.append(metadata(path))

receipt = {
    'game_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'observed_root_head_at_source_rehash': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
    'sources_rehashed_this_run': [metadata(character_path), metadata(skill_path)],
    'bindings': bindings, 'exact_skill_selectors': selectors,
    'reused_evidence_files': references,
    'active_declared_count_fields': {
        'mechanist.S2': ['shield_break_count'], 'mechanist.S3': ['charge_count'],
        'silverash.S2': ['activation_count', 'deployment_stacks']},
    'existing_backend_domain': 'Finite nonnegative integer-valued numbers; deployment_stacks at most 2. Existing field-specific integer floats/numeric strings and errors are retained.',
    'existing_gui_domain': {
        'shield_break_count': 'QSpinBox 0..100', 'charge_count': 'QSpinBox 0..100',
        'activation_count': 'QSpinBox 0..100 default1', 'deployment_stacks': 'QSpinBox 0..2'},
    'gui_source': {'path': 'rouge/app.py', 'range_lines': '639..662',
                   'serialized_integer_readouts_lines': '1032..1034'},
    'meaning_scope': {
        'shield_break_count': 'Declared whole-skill total of explosions hitting the current target; not a verified ammo count or event clock.',
        'charge_count': 'Declared conditional collision-hit count; not a verified full-cast assignment or collision clock.',
        'activation_count': 'Declared own S2 activation count; full single-skill estimate retains own once.',
        'deployment_stacks': 'Declared beneficiary deployment trigger count; source description supports at most two layers, not extra event timing.'},
    'section53_source_provenance': 'Research/source files rehashed from the external section51-based draft; observed later root commit recorded separately. Frozen section51 matrix is not integrated-head validation.',
    'new_event_input_or_callback_added': False, 'new_gameplay_upper_limit_added': False,
    'native_validation_performed': False}
(OUT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'original_skill_bindings': len(bindings), 'skill_levels_retained': 30,
                  'raw_tables_rehashed_this_run': 2}))
