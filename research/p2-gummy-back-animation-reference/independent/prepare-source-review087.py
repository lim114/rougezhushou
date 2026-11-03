"""Source/static preparation only. No production imports, API or Spine reader calls."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
BASE = '9ef5a469673502754db3be320a8eece9a7fd18d4'
SOURCE = ROOT.parent / 'p2-gummy-back-parser-source087'
OFFICIAL = ROOT.parent / 'p2-gummy-back-parser-source087-official-reader'
SNAP = ROOT / 'source-snapshots'
SNAP.mkdir(exist_ok=True)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def dump(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

bindings = []
source_paths = ['rouge/data/original-animation-references.json',
                'scripts/build_original_animation_048.py', 'scripts/build_animation_selection_048.py',
                'rouge/animation_reference.py']
assert subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], check=True,
    capture_output=True, text=True).stdout.strip() == BASE
for relative in source_paths:
    raw = subprocess.run(['git', '-C', str(REPO), 'show', BASE + ':' + relative],
        check=True, capture_output=True).stdout
    p = SNAP / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    if relative.endswith('.json'):
        p = p.with_suffix(p.suffix + '.gz')
        p.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
        assert gzip.decompress(p.read_bytes()) == raw
    else:
        p.write_bytes(raw)
    bindings.append({'source_path': relative, 'baseline_commit': BASE,
        'archive_path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
        'sha256': digest(p.read_bytes()), 'original_bytes': len(raw), 'original_sha256': digest(raw),
        'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()})

selected_sources = [
    (SOURCE, 'parse-Back-result.json'), (SOURCE, 'parse-Front-result.json'),
    (SOURCE, 'front-control-receipt.json'), (SOURCE, 'final-handoff087.json'),
    (SOURCE, 'public-artifacts-manifest087.json'),
    (OFFICIAL, 'saved-source-result-review087.json'),
    (OFFICIAL, 'source-contract-receipt087.json'), (OFFICIAL, 'choices-source-independent-review087.json')]
for base, name in selected_sources:
    src = base / name
    p = SNAP / ('official-proof' if base == OFFICIAL else 'source-operation') / name
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, p)
    assert src.read_bytes() == p.read_bytes()
    bindings.append({'source_path': str(src), 'archive_path': str(p.relative_to(ROOT)),
        'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes()),
        'scope': 'Selected immutable saved receipt only; not revalidation or repetition of the original 102-file source operation'})

raw = gzip.decompress((SNAP / 'rouge/data/original-animation-references.json.gz').read_bytes())
text = raw.decode('utf-8')
baseline = json.loads(raw)
assert digest(raw) == '28d9be1dd6fe6f91dc5773b1c685ea78fb0bb403d25c4f26d933adcfcbad3f9e'
assert baseline['counts'] == {'operators': 32, 'source_skeletons': 64, 'animations': 923,
    'selectable_references': 160, 'unverified_or_transition_references': 763, 'missing_skeletons': 1}
assert baseline['fps'] == 30 and baseline['frame_normalization_tolerance'] == 1e-5
assert baseline['binding_status'] == 'explicit_offline_reference_only'
assert baseline['default_numeric_behavior_changed'] is False
profiles = baseline['operators']
old_records = [record for profile in profiles.values() for record in profile['records']]
assert len(old_records) == 923
assert all(record['runtime_binding_verified'] is False for record in old_records)
assert len({record['id'] for record in old_records}) == 923
assert len({(profile['id'], record['orientation']) for profile in profiles.values() for record in profile['records']}) == 63
gummy = profiles['char_196_sunbr']
assert len(gummy['records']) == 9
assert gummy['missing_sources'] == [{'orientation': 'Back', 'reason': 'Error: boneData cannot be null.'}]

# Index each literal record object, including its existing internal indentation.
# This is JSON decoding of the public dataset, never a skeleton/source-runtime parse.
decoder = json.JSONDecoder()
indexes = []
arrays = list(re.finditer(r'"records": \[', text))
assert len(arrays) == 32
for match in arrays:
    cursor = match.end()
    while True:
        while text[cursor].isspace() or text[cursor] == ',':
            cursor += 1
        if text[cursor] == ']':
            break
        start = cursor
        record, cursor = decoder.raw_decode(text, cursor)
        assert isinstance(record, dict) and record['id']
        piece = text[start:cursor].encode('utf-8')
        indexes.append({'id': record['id'], 'literal_object_bytes': len(piece),
            'literal_object_sha256': digest(piece),
            'strict_JSON_type_value_sha256': digest(json.dumps(record, ensure_ascii=False,
                sort_keys=True, separators=(',', ':')).encode('utf-8'))})
assert len(indexes) == len(old_records) == 923
assert {row['id'] for row in indexes} == {record['id'] for record in old_records}
dump('baseline923-record-byte-index087.json', {'version': 1, 'baseline_commit': BASE,
    'dataset_sha256': digest(raw), 'record_count': 923,
    'scope': 'Literal old record object bytes and exact JSON type/value digest for final draft comparison',
    'records': indexes})

back = json.loads((SNAP / 'source-operation/parse-Back-result.json').read_text())
assert back['skeleton']['spine_version'] == '3.8.99'
assert back['resource']['sha256'] == '09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2'
assert back['resource']['git_blob_sha1'] == '473df5c69d7e3552f6937f749bd42dd9e974ca01'
assert back['resource']['bytes'] == 32563
assert [a['name'] for a in back['animations']] == ['Attack', 'Default', 'Idle', 'Skill', 'Start']
facts = []
for animation in back['animations']:
    times = [('duration', animation['duration_seconds'])] + [(event['name'], event['seconds']) for event in animation['events']]
    frame_facts = []
    for name, seconds in times:
        value = seconds * 30
        normalized = round(value) if abs(value - round(value)) <= 1e-5 else value
        frame_facts.append({'field': name, 'seconds': seconds, 'raw_frames_30hz': value,
            'strict_ceil_frames_30hz': math.ceil(value), 'representation_normalized_frames_30hz': normalized,
            'ceil_frames_30hz': math.ceil(normalized)})
    reasons = []
    on_attack = [event for event in animation['events'] if event['name'] == 'OnAttack']
    if len(on_attack) != 1:
        reasons.append('not exactly one OnAttack event')
    elif not 0 < on_attack[0]['seconds'] < animation['duration_seconds']:
        reasons.append('OnAttack must be strictly inside positive animation duration')
    name = animation['name']
    if not ('Attack' in name or name.startswith('Skill')):
        reasons.append('not a named attack or skill animation')
    if 'Loop' in name:
        reasons.append('loop named animation requires separate lifecycle binding')
    if 'Begin' in name or 'End' in name or 'Restart' in name:
        reasons.append('transition animation requires separate lifecycle binding')
    if len(animation['events']) != 1:
        reasons.append('multiple or absent named events require separate binding')
    facts.append({'saved_animation': name, 'new_record_id': 'char_196_sunbr:Back:' + name,
        'policy_frame_facts': frame_facts, 'policy_eligible': not reasons,
        'policy_unverified_reasons_in_order': reasons,
        'preview_if_eligible': {'windup_frames': frame_facts[1]['ceil_frames_30hz'],
            'recovery_frames': frame_facts[0]['ceil_frames_30hz'] - frame_facts[1]['ceil_frames_30hz'],
            'animation_frames': frame_facts[0]['ceil_frames_30hz']} if not reasons else None,
        'raw_event_names': [event['name'] for event in animation['events']],
        'game_runtime_binding_verified': False})
assert sum(row['policy_eligible'] for row in facts) == 2

receipt = {'version': 1, 'status': 'PREPARATION_SOURCE_CONTRACT_PASS_FINAL_DRAFT_PENDING',
    'prepared_at_utc': datetime.now(timezone.utc).isoformat(), 'baseline_commit': BASE,
    'input_bindings': bindings, 'baseline_counts': baseline['counts'],
    'expected_post_append_counts': {'operators': 32, 'source_skeletons': 64, 'animations': 928,
        'selectable_references': 162, 'unverified_or_transition_references': 766, 'missing_skeletons': 0},
    'declared_source_inventory_vs_available_sources': {'baseline_declared_inventory': 64,
        'baseline_available_operator_face_pairs': 63, 'expected_available_after_append': 64,
        'source_skeletons_count_does_not_increment_to_65': True},
    'new_saved_source_record_facts': facts,
    'original923_preservation_contract': 'All original id/order/literal object bytes and exact JSON types/values unchanged; only append five Gummy Back objects, clear sole Gummy Back current missing entry and update four counts.',
    'baseline_selection_derivation_must_remain_exact': baseline['selection_derivation'],
    'top_level_binding_default_numeric_scope_FPS_tolerance_unchanged': True,
    'frame_rule_scope': '30 Hz and 1e-5-frame representation normalization are inherited data policy, not measurement of gameplay ticks or event binding.',
    'choice_boundary': 'Literal Skill is eligible metadata but matches neither Attack prefix nor numbered Skill regex. Attack is ordinary conditional on published selectable record and explicit selection; normal or skill branch can admit ordinary references under existing code.',
    'new_UI_option_count_or_native_binding_inferred': False,
    'events_schema': 'Existing name plus inherited frames(time) only. Actual extra event payload remains saved source evidence, not silently invented product schema.',
    'old_error_history': 'Original visible Back boneData error remains immutable source history; recovered resource removes current missing entry without asserting old root cause or historical reader identity.',
    'reviewer_execution_counts': {'application_API': 0, 'production_helper': 0, 'formatter': 0,
        'tests': 0, 'source_runtime_parser': 0, 'network': 0, 'Qt': 0, 'Wine': 0, 'tracked_changes': 0},
    'final_source_freeze_received': False,
    'next': 'Wait for author final source/test/generator freeze, then precise product delta and saved review; bounded fresh calls only after separate coordination.'}
dump('source-preparation-receipt087.json', receipt)
print(json.dumps({'status': receipt['status'], 'path': str(ROOT / 'source-preparation-receipt087.json'),
    'bytes': (ROOT / 'source-preparation-receipt087.json').stat().st_size,
    'sha256': digest((ROOT / 'source-preparation-receipt087.json').read_bytes()),
    'old_record_byte_index_count': len(indexes), 'source_only_new_API_calls': 0}))
