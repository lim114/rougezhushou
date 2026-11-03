"""Strictly inspect saved source/data/results without importing product code."""
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / 'public-fixture090'
PACKET = FIXTURE / 'research/p2-gummy-back-animation-reference/source-packet087'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def strict(value):
    if isinstance(value, dict):
        return ('dict', tuple((key, strict(item)) for key, item in value.items()))
    if isinstance(value, list):
        return ('list', tuple(strict(item) for item in value))
    if isinstance(value, float):
        return ('float', value.hex())
    return (type(value).__name__, value)

def fields(seconds):
    seconds = float(seconds)
    raw = seconds * 30
    normalized = round(raw) if abs(raw - round(raw)) <= 1e-5 else raw
    return {'seconds': seconds, 'raw_frames_30hz': raw,
        'strict_ceil_frames_30hz': math.ceil(raw),
        'representation_normalized_frames_30hz': normalized,
        'ceil_frames_30hz': math.ceil(normalized)}

data = json.loads((FIXTURE / 'rouge/data/original-animation-references.json').read_bytes())
source = json.loads((PACKET / 'parse-Back-result.json').read_bytes())
backs = [row for row in data['operators']['char_196_sunbr']['records'] if row['orientation'] == 'Back']
assert len(backs) == len(source['animations']) == 5
expected = []
for animation in source['animations']:
    name = animation['name']
    duration = fields(animation['duration_seconds'])
    events = [{'name': row['name'], **fields(row['seconds'])} for row in animation['events']]
    attack = [row for row in events if row['name'] == 'OnAttack']
    reasons = []
    if len(attack) != 1:
        reasons.append('not exactly one OnAttack event')
    elif not 0 < attack[0]['seconds'] < duration['seconds']:
        reasons.append('OnAttack must be strictly inside positive animation duration')
    if not ('Attack' in name or name.startswith('Skill')):
        reasons.append('not a named attack or skill animation')
    if 'Loop' in name:
        reasons.append('loop named animation requires separate lifecycle binding')
    if 'Begin' in name or 'End' in name or 'Restart' in name:
        reasons.append('transition animation requires separate lifecycle binding')
    if len(events) != 1:
        reasons.append('multiple or absent named events require separate binding')
    row = {'id': 'char_196_sunbr:Back:' + name, 'orientation': 'Back', 'skin': 'original',
        'animation': name, 'spine_version': source['skeleton']['spine_version'],
        'duration': duration, 'events': events,
        'selectable_as_conventional_reference': not reasons, 'unverified_reasons': reasons,
        'runtime_binding_verified': False,
        'source': {'url': source['resource']['source_url'], 'sha256': source['resource']['sha256'],
            'git_blob': source['resource']['git_blob_sha1'], 'bytes': source['resource']['bytes']}}
    if not reasons:
        row['preview'] = {'windup_frames': attack[0]['ceil_frames_30hz'],
            'recovery_frames': duration['ceil_frames_30hz'] - attack[0]['ceil_frames_30hz'],
            'animation_frames': duration['ceil_frames_30hz']}
    expected.append(row)
assert strict(backs) == strict(expected)
plan = json.loads((HERE / 'risk-plan-frozen090.json').read_bytes())
receipt = json.loads((HERE / 'fresh-four-direct-verifier-receipt090.json').read_bytes())
assert receipt['passed'] is True
assert receipt['fresh_verifier_function_entries'] == receipt['fresh_direct_verifier_entries'] == 4
assert receipt['fresh_CLI_invocations'] == 0
saved = []
for risk in plan['risks']:
    resultpath = HERE / 'risk-results' / (risk['id'] + '.json')
    row = json.loads(resultpath.read_bytes())
    assert row['expected_code'] == row['exception']['code'] == risk['expected_code']
    assert row['exception']['class'] == 'ProvenanceError' and row['unexpected'] is None
    assert row['file_hashes_before'] == row['file_hashes_after']
    rawgzip = Path(row['saved_mutated_full_references_gzip']['source_path']).read_bytes()
    assert sha(rawgzip) == row['saved_mutated_full_references_gzip']['sha256']
    raw = gzip.decompress(rawgzip)
    assert len(raw) == row['full_references_decoded_bytes'] and sha(raw) == row['full_references_decoded_sha256']
    altered = json.loads(raw)
    repaired = json.loads(raw)
    if 'record_id' in risk:
        changed = next(r for r in altered['operators']['char_196_sunbr']['records'] if r['id'] == risk['record_id'])
        assert strict(changed[risk['key']]) == (risk['new']['type'], risk['new']['value'])
        target = next(r for r in repaired['operators']['char_196_sunbr']['records'] if r['id'] == risk['record_id'])
        target[risk['key']] = risk['old']['value']
    else:
        pointer = risk['pointer']
        original_container = data
        altered_container = altered
        repaired_container = repaired
        for key in pointer[:-1]:
            original_container = original_container[key]
            altered_container = altered_container[key]
            repaired_container = repaired_container[key]
        assert strict(altered_container[pointer[-1]]) == strict(risk['new']['value'])
        repaired_container[pointer[-1]] = original_container[pointer[-1]]
    assert strict(repaired) == strict(data), 'Only one frozen target changes in each full saved input'
    saved.append({'risk_id': risk['id'], 'complete_input_inverse_strict': True,
        'expected_exception_and_readonly_source_bound': True,
        'result_sha256': sha(resultpath.read_bytes())})
out = {'format_version': 1, 'status': 'PASS_ZERO_CALL_FULL_SAVED_FOUR_AND_BACK5_TYPED_SOURCE_REVIEW', 'passed': True,
    'Back5_full_native_structure_float_hex_type_list_and_insertion_order_exact': True,
    'policy': 'Existing frame representation source AST verified separately; no game-clock statement',
    'source_extraction_sha256': sha((PACKET / 'parse-Back-result.json').read_bytes()),
    'all_four_saved_complete_inputs_only_target_change_and_inverse_exact': saved,
    'fresh_verifier_function_entries': 0, 'fresh_CLI_invocations': 0,
    'application_API_helper_formatter_source_parser_network_Qt_Wine_calls': 0,
    'earlier_fresh_four_not_reexecuted': True, 'author28_and_source28_not_reexecuted': True}
(HERE / 'saved-only-and-Back5-review090.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': out['status'], 'verifier_calls': 0,
    'sha256': sha((HERE / 'saved-only-and-Back5-review090.json').read_bytes())}))
