"""Verify the archived section-087 animation addition without executing a reader.

This is a read-only maintenance command. It verifies saved source metadata and
the fixed public snapshot, not rendering, native bindings or game clocks.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re

EVIDENCE_RELATIVE = Path('research/p2-gummy-back-animation-reference/source-packet087')
DATA_RELATIVE = Path('rouge/data/original-animation-references.json')
PACKET_SHA = 'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265'
EXTRACTION_SHA = '2b3785b65d526bf74329f249b90bf2034c02eb79708e25ec12bdebe73709dd77'
BASELINE_SHA = '28d9be1dd6fe6f91dc5773b1c685ea78fb0bb403d25c4f26d933adcfcbad3f9e'
RESOURCE_SHA = '09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2'
RESOURCE_BLOB = '473df5c69d7e3552f6937f749bd42dd9e974ca01'
RESOURCE_COMMIT = 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd'
READER_COMMIT = '8b4844bd4b193ba9e54487ed397a777993cbad56'
READER_SHA = 'f1e0a31b9906e4d4daf2733857d21381ddbbe75adec7f4d83e1cc9b2b070dfc1'
OPERATOR = 'char_196_sunbr'
SOURCE_URL = ('https://raw.githubusercontent.com/fexli/ArknightsResource/'
              + RESOURCE_COMMIT + '/spine/char_196_sunbr/char_196_sunbr/Back/char_196_sunbr.skel')
REQUIRED_LEAVES = (
    'parse-Back-result.json', 'parse-Back-operation.json',
    'reacquired/Back/char_196_sunbr.skel',
    'history/original-animation-references.json.gz',
    'official-reader/official-source/spine-ts/build/spine-core.js',
    'official-reader/official-source/spine-ts/build/spine-core.d.ts',
)
COUNTS = {'operators': 32, 'source_skeletons': 64, 'animations': 928,
          'selectable_references': 162, 'unverified_or_transition_references': 766,
          'missing_skeletons': 0}
OLD_COUNTS = {'operators': 32, 'source_skeletons': 64, 'animations': 923,
              'selectable_references': 160, 'unverified_or_transition_references': 763,
              'missing_skeletons': 1}


class ProvenanceError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class OutsideSupportedSnapshot(ProvenanceError):
    def __init__(self, message):
        super().__init__('outside_supported_snapshot', message)


def require(condition, code, message):
    if not condition:
        raise ProvenanceError(code, message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    try:
        return path.read_bytes()
    except OSError as error:
        raise ProvenanceError('input_unavailable', 'Cannot read required input: ' + str(path)) from error


def decode(raw, label):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'invalid_json', label + ': duplicate JSON key ' + key)
            result[key] = value
        return result

    def nonfinite(value):
        raise ProvenanceError('invalid_json', label + ': non-finite JSON number ' + value)

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (ValueError, UnicodeError) as error:
        if isinstance(error, ProvenanceError):
            raise
        raise ProvenanceError('invalid_json', label + ': invalid JSON') from error


def same_typed(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same_typed(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(same_typed(a, b) for a, b in zip(left, right))
    return left == right


def safe_archive_path(value):
    require(isinstance(value, str) and value != '', 'invalid_manifest', 'Missing archive_path')
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and '\\' not in value
            and all(part not in ('.', '..') and ':' not in part for part in path.parts),
            'invalid_manifest', 'Unsafe archive_path: ' + value)
    return path


def frames(seconds):
    # Existing build_original_animation_048 representation policy; no game tick rule.
    value = float(seconds) * 30
    normalized = round(value) if abs(value - round(value)) <= 1e-5 else value
    return {'seconds': float(seconds), 'raw_frames_30hz': value,
            'strict_ceil_frames_30hz': math.ceil(value),
            'representation_normalized_frames_30hz': normalized,
            'ceil_frames_30hz': math.ceil(normalized)}


def expected_records(source):
    records = []
    for animation in source['animations']:
        name = animation['name']
        events = [{'name': item['name'], **frames(item['seconds'])} for item in animation['events']]
        duration = frames(animation['duration_seconds'])
        on_attack = [event for event in events if event['name'] == 'OnAttack']
        reasons = []
        if len(on_attack) != 1:
            reasons.append('not exactly one OnAttack event')
        elif not 0 < on_attack[0]['seconds'] < duration['seconds']:
            reasons.append('OnAttack must be strictly inside positive animation duration')
        if not ('Attack' in name or name.startswith('Skill')):
            reasons.append('not a named attack or skill animation')
        if 'Loop' in name:
            reasons.append('loop named animation requires separate lifecycle binding')
        if 'Begin' in name or 'End' in name or 'Restart' in name:
            reasons.append('transition animation requires separate lifecycle binding')
        if len(events) != 1:
            reasons.append('multiple or absent named events require separate binding')
        record = {'id': OPERATOR + ':Back:' + name, 'orientation': 'Back', 'skin': 'original',
                  'animation': name, 'spine_version': source['skeleton']['spine_version'],
                  'duration': duration, 'events': events,
                  'selectable_as_conventional_reference': not reasons,
                  'unverified_reasons': reasons, 'runtime_binding_verified': False,
                  'source': {'url': SOURCE_URL, 'sha256': RESOURCE_SHA,
                             'git_blob': RESOURCE_BLOB, 'bytes': 32563}}
        if not reasons:
            windup = on_attack[0]['ceil_frames_30hz']
            total = duration['ceil_frames_30hz']
            record['preview'] = {'windup_frames': windup, 'recovery_frames': total - windup,
                                 'animation_frames': total}
        records.append(record)
    return records


def verify(repository_root=None, references_path=None, evidence_dir=None):
    root = Path(repository_root) if repository_root is not None else Path(__file__).resolve().parents[1]
    data_path = Path(references_path) if references_path is not None else root / DATA_RELATIVE
    packet = (Path(evidence_dir) if evidence_dir is not None else root / EVIDENCE_RELATIVE).resolve()
    manifest_raw = read(packet / 'public-artifacts-manifest087.json')
    require(sha(manifest_raw) == PACKET_SHA, 'manifest_hash_mismatch', 'Source packet manifest hash differs')
    manifest = decode(manifest_raw, 'Source manifest')
    require(type(manifest.get('format_version')) is int and manifest['format_version'] == 1
            and isinstance(manifest.get('files'), list), 'invalid_manifest', 'Expected a v1 file manifest')
    index = {}
    for item in manifest['files']:
        require(isinstance(item, dict), 'invalid_manifest', 'Invalid file manifest entry')
        name = item.get('archive_path')
        safe_archive_path(name)
        require(name not in index, 'invalid_manifest', 'Duplicate archive_path: ' + name)
        require(type(item.get('bytes')) is int and item['bytes'] >= 0
                and isinstance(item.get('sha256'), str)
                and re.fullmatch('[0-9a-f]{64}', item['sha256']) is not None,
                'invalid_manifest', 'Invalid size/hash for ' + name)
        index[name] = item
    raw_inputs = {}
    verified = []
    for name in REQUIRED_LEAVES:
        require(name in index, 'invalid_manifest', 'Required leaf absent from manifest: ' + name)
        path = (packet / name).resolve()
        require(path.is_relative_to(packet), 'unsafe_input_path', 'Input escapes evidence directory: ' + name)
        raw = read(path)
        entry = index[name]
        require(len(raw) == entry['bytes'] and sha(raw) == entry['sha256'],
                'source_hash_mismatch', 'Source size/hash differs: ' + name)
        raw_inputs[name] = raw
        verified.append({'archive_path': name, 'bytes': len(raw), 'sha256': sha(raw)})
    skeleton = raw_inputs['reacquired/Back/char_196_sunbr.skel']
    blob = hashlib.sha1(b'blob ' + str(len(skeleton)).encode() + b'\0' + skeleton).hexdigest()
    require(sha(skeleton) == RESOURCE_SHA and blob == RESOURCE_BLOB,
            'resource_identity_mismatch', 'Back skeleton identity differs')
    source_raw = raw_inputs['parse-Back-result.json']
    require(sha(source_raw) == EXTRACTION_SHA, 'extraction_identity_mismatch', 'Extraction identity differs')
    source = decode(source_raw, 'Back extraction')
    operation = decode(raw_inputs['parse-Back-operation.json'], 'Saved reader operation')
    require(source['orientation'] == 'Back' and source['skeleton']['spine_version'] == '3.8.99'
            and source['resource']['source_url'] == SOURCE_URL
            and source['resource']['sha256'] == RESOURCE_SHA
            and source['resource']['git_blob_sha1'] == RESOURCE_BLOB
            and source['resource']['bytes'] == 32563
            and source['official_bundle_sha256'] == READER_SHA
            and operation['official_commit'] == READER_COMMIT,
            'source_metadata_mismatch', 'Saved source metadata differs')
    require(all(operation.get(key) is False for key in (
        'render_validation', 'atlas_or_texture_source_acquisition',
        'game_binding_or_clock_claims', 'reader_source_modified',
        'bone_or_slot_replacement', 'EOF_consumption_claim')),
        'source_scope_mismatch', 'Saved reader operation exceeds metadata scope')
    try:
        baseline_raw = gzip.decompress(raw_inputs['history/original-animation-references.json.gz'])
    except (OSError, EOFError) as error:
        raise ProvenanceError('baseline_unreadable', 'Historical baseline gzip is invalid') from error
    require(len(baseline_raw) == 1283952 and sha(baseline_raw) == BASELINE_SHA,
            'baseline_hash_mismatch', 'Historical baseline differs')
    baseline = decode(baseline_raw, 'Historical baseline')
    data = decode(read(data_path), 'Animation references')
    require(isinstance(data, dict) and isinstance(data.get('operators'), dict),
            'invalid_data', 'Animation references must contain operator profiles')
    if data.get('source_commit') != RESOURCE_COMMIT:
        raise OutsideSupportedSnapshot('This command supports the section-087 pinned resource snapshot only')
    additions = data.get('source_additions')
    require(isinstance(additions, list) and len(additions) > 0,
            'addition_metadata_mismatch', 'Missing section-087 source addition')
    if len(additions) != 1:
        raise OutsideSupportedSnapshot('Additional source additions are outside the supported section-087 snapshot')
    require(isinstance(additions[0], dict), 'addition_metadata_mismatch', 'Invalid source addition')
    require(data.get('fps') == 30 and type(data['fps']) is int
            and data.get('frame_normalization_tolerance') == 1e-5,
            'representation_policy_mismatch', 'The existing 30Hz representation policy differs')
    require(data.get('binding_status') == 'explicit_offline_reference_only'
            and data.get('default_numeric_behavior_changed') is False,
            'binding_scope_mismatch', 'Default offline binding scope differs')
    profile = data['operators'].get(OPERATOR)
    require(isinstance(profile, dict) and isinstance(profile.get('records'), list),
            'invalid_data', 'Missing Gummy animation records')
    records = profile['records']
    require(all(isinstance(record, dict) for record in records), 'invalid_data', 'Invalid animation record')
    require(all(record.get('orientation') in ('Front', 'Back') for record in records),
            'invalid_data', 'Invalid Gummy record orientation')
    back = [record for record in records if record.get('orientation') == 'Back']
    require(all(record.get('runtime_binding_verified') is False for record in back)
            and additions[0].get('runtime_binding_inferred') is False,
            'binding_scope_mismatch', 'Saved metadata cannot verify native binding')
    generic = next((record for record in back if record.get('id') == OPERATOR + ':Back:Skill'), None)
    require(generic is not None and generic.get('animation') == 'Skill'
            and re.match(r'^Skill_?(\d+)(?:_|$)', generic['animation']) is None,
            'generic_skill_binding_mismatch', 'Generic Skill must retain its unnumbered source name')
    expected = expected_records(source)
    require(same_typed(back, expected), 'derived_records_mismatch', 'The five derived Back records differ')
    expected_addition = {
        'operator': OPERATOR, 'orientation': 'Back', 'record_ids': [record['id'] for record in expected],
        'source_commit': RESOURCE_COMMIT, 'source_sha256': RESOURCE_SHA,
        'git_blob': RESOURCE_BLOB, 'bytes': 32563,
        'source_packet_manifest_sha256': PACKET_SHA, 'extraction_sha256': EXTRACTION_SHA,
        'official_reader_commit': READER_COMMIT, 'official_reader_bundle_sha256': READER_SHA,
        'runtime_binding_inferred': False,
        'scope': ('Newly reacquired source metadata only. Historical parser identity/root cause, exact EOF, '
                  'rendering, native skill/normal/skin binding and lifecycle clocks remain unknown.')}
    require(same_typed(additions[0], expected_addition), 'addition_metadata_mismatch', 'Source addition metadata differs')
    require(all(isinstance(p, dict) and isinstance(p.get('records'), list)
                and isinstance(p.get('missing_sources'), list) for p in data['operators'].values()),
            'invalid_data', 'Invalid operator profile')
    all_records = [record for p in data['operators'].values() for record in p['records']]
    if len(all_records) > COUNTS['animations']:
        raise OutsideSupportedSnapshot('Additional animation records are outside the supported section-087 snapshot')
    require(all(isinstance(record, dict) and type(record.get('selectable_as_conventional_reference')) is bool
                and isinstance(record.get('source'), dict)
                and isinstance(record['source'].get('url'), str) for record in all_records),
            'invalid_data', 'Invalid reference eligibility/source metadata')
    actual_counts = {
        'operators': len(data['operators']),
        'source_skeletons': len({record['source'].get('url') for record in all_records}),
        'animations': len(all_records),
        'selectable_references': sum(record['selectable_as_conventional_reference'] for record in all_records),
        'unverified_or_transition_references': sum(not record['selectable_as_conventional_reference'] for record in all_records),
        'missing_skeletons': sum(len(p['missing_sources']) for p in data['operators'].values())}
    require(same_typed(data.get('counts'), COUNTS) and same_typed(actual_counts, COUNTS),
            'counts_mismatch', 'The supported snapshot counts differ')
    inverse = decode(json.dumps(data).encode(), 'Inverse working copy')
    inverse_profile = inverse['operators'][OPERATOR]
    inverse_profile['records'] = [record for record in inverse_profile['records'] if record['orientation'] != 'Back']
    inverse_profile['missing_sources'] = baseline['operators'][OPERATOR]['missing_sources']
    inverse['counts'] = OLD_COUNTS
    del inverse['source_additions']
    inverse_raw = (json.dumps(inverse, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n').encode()
    require(inverse_raw == baseline_raw, 'historical_inverse_mismatch', 'Existing 923-record dataset differs from the real historical baseline')
    return {
        'format_version': 1, 'passed': True, 'status': 'verified_supported_snapshot',
        'scope': 'Section-087 saved metadata and five-record addition only',
        'source_packet_manifest_sha256': PACKET_SHA,
        'verified_leaf_count': len(verified), 'verified_leaves': verified,
        'added_back_records': 5, 'original_records_preserved': 923,
        'full_historical_inverse_byte_exact': True, 'counts': actual_counts,
        'generic_skill_has_skill_number': False, 'runtime_binding_verified': False,
        'source_skeleton_parser_calls': 0, 'network_calls': 0,
        'application_API_calls': 0, 'project_helper_calls': 0,
        'verifier_function_entries': 1,
        'unverified': ['Native skill/normal/skin binding and clocks',
                       'Rendering/atlas/texture geometry', 'EOF consumption',
                       'Historical parser identity and root cause']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path)
    parser.add_argument('--references', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    args = parser.parse_args(argv)
    try:
        report = verify(args.repository_root, args.references, args.evidence_dir)
        exit_code = 0
    except ProvenanceError as error:
        outside = isinstance(error, OutsideSupportedSnapshot)
        report = {'format_version': 1, 'passed': False,
                  'status': 'outside_supported_snapshot' if outside else 'verification_failed',
                  'code': error.code, 'message': str(error), 'verifier_function_entries': 1,
                  'source_skeleton_parser_calls': 0, 'network_calls': 0,
                  'application_API_calls': 0, 'project_helper_calls': 0}
        exit_code = 2 if outside else 1
    # ASCII JSON also works with a Windows console's non-UTF-8 stdout encoding.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
