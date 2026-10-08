"""Independent JSON/source receipt review only; no reader, bundle or product calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import math

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'p2-gummy-back-parser-source087'
SNAP = ROOT / 'saved-reader-snapshots'
SNAP.mkdir(exist_ok=True)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def info(path, original=None):
    raw = path.read_bytes()
    return {'source_path': str(original or path), 'archive_path': str(path.relative_to(ROOT)),
            'bytes': len(raw), 'sha256': sha(raw)}

files = ['parse-Front-operation.json', 'parse-Back-operation.json',
         'parse-Front-result.json', 'parse-Back-result.json',
         'parse-Front.log', 'parse-Back.log', 'front-control-receipt.json',
         'front-control.log', 'compare_saved_front_control.py',
         'transport-and-attempt-scope.json', 'tls-preservation-check.json']
bindings = []
for name in files:
    src = PARENT / name
    dst = SNAP / name
    shutil.copy2(src, dst)
    assert dst.read_bytes() == src.read_bytes()
    bindings.append(info(dst, src))

approved = json.loads((ROOT / 'source-contract-receipt087.json').read_text())
acquired = json.loads((ROOT / 'parent-source-snapshots/git-acquisition-receipt.json').read_text())
header = json.loads((ROOT / 'parent-source-snapshots/header-only-receipt.json').read_text())
old = json.loads((ROOT / 'parent-source-snapshots/history/gummy-visible-production-record.json').read_text())
ops = {}
results = {}
summaries = []
for orientation, counts in [('Front', (47, 49, 9)), ('Back', (34, 28, 5))]:
    operation = json.loads((SNAP / f'parse-{orientation}-operation.json').read_text())
    result_path = SNAP / f'parse-{orientation}-result.json'
    result = json.loads(result_path.read_text())
    log = json.loads((SNAP / f'parse-{orientation}.log').read_text())
    resource = next(row for row in acquired['resources'] if row['orientation'] == orientation)
    hdr = next(row for row in header['resources'] if row['orientation'] == orientation)
    assert operation['orientation'] == result['orientation'] == log['orientation'] == orientation
    assert operation['official_commit'] == approved['official_commit']
    assert operation['full_skeleton_parser_calls'] == 1
    assert operation['application_API_helper_formatter_test_Qt_Wine_calls'] == 0
    assert operation['reader_returned'] is True and log['reader_returned'] is True
    assert operation['resource'] == result['resource'] == resource
    assert operation['official_bundle']['sha256'] == result['official_bundle_sha256'] == approved['official_bundle']['sha256']
    assert operation['reviewed_factory']['sha256'] == result['reviewed_factory_sha256'] == approved['research_attachment_factory']['sha256']
    assert operation['result']['bytes'] == result_path.stat().st_size
    assert operation['result']['sha256'] == sha(result_path.read_bytes())
    assert operation['input_copy'] == {'byte_offset': 0, 'byte_length': resource['bytes'],
        'backing_buffer_bytes': resource['bytes'], 'sha256': resource['sha256']}
    assert operation['after_read_byte_invariance'] == {'input_sha256': resource['sha256'],
        'resource_file_sha256': resource['sha256'], 'input_unchanged': True, 'resource_file_unchanged': True}
    for key in ['render_validation', 'atlas_or_texture_source_acquisition',
                'game_binding_or_clock_claims', 'reader_source_modified',
                'bone_or_slot_replacement', 'EOF_consumption_claim']:
        assert operation[key] is False
    # Current resource identity verification reads bytes only. It does not parse their format.
    raw = Path(resource['source_path']).read_bytes()
    assert len(raw) == resource['bytes'] and sha(raw) == resource['sha256']
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == resource['git_blob_sha1']
    assert result['skeleton']['spine_version'] == hdr['spine_version_string'] == '3.8.99'
    assert result['skeleton']['hash'] == hdr['skeleton_hash_string']
    bones, slots, animations = result['bones'], result['slots'], result['animations']
    assert (len(bones), len(slots), len(animations)) == counts
    assert result['skeleton']['bone_count'] == len(bones)
    assert result['skeleton']['slot_count'] == len(slots)
    assert operation['result']['animation_count'] == len(animations)
    assert [bone['index'] for bone in bones] == list(range(len(bones)))
    assert bones[0]['parent_index'] is None
    assert all(type(bone['parent_index']) is int and 0 <= bone['parent_index'] < bone['index'] for bone in bones[1:])
    assert [slot['index'] for slot in slots] == list(range(len(slots)))
    assert all(type(slot['bone_index']) is int and 0 <= slot['bone_index'] < len(bones) for slot in slots)
    assert len({a['name'] for a in animations}) == len(animations)
    assert all(math.isfinite(a['duration_seconds']) and a['duration_seconds'] >= 0 for a in animations)
    events = [event for a in animations for event in a['events']]
    assert len(events) == operation['result']['source_event_count'] == 3
    assert all(math.isfinite(event['seconds']) for event in events)
    expected_log = {'orientation': orientation, 'reader_returned': True,
        'bone_count': len(bones), 'slot_count': len(slots),
        'animations': [{'name': a['name'], 'duration_seconds': a['duration_seconds'],
                       'events': [{'name': e['name'], 'seconds': e['seconds']} for e in a['events']]} for a in animations]}
    assert log == expected_log
    summaries.append({'orientation': orientation, 'bone_count': len(bones), 'slot_count': len(slots),
        'animation_count': len(animations), 'event_count': len(events),
        'read_metadata_only': True, 'resource_sha256': resource['sha256'],
        'result_sha256': sha(result_path.read_bytes()), 'raw_byte_identity_rechecked': True})
    ops[orientation] = operation
    results[orientation] = result

assert datetime.fromisoformat(ops['Front']['finished_at']) < datetime.fromisoformat(ops['Back']['started_at'])
source_runner = ROOT / 'parent-source-snapshots/read_official_source.js'
assert source_runner.read_bytes() == (PARENT / 'read_official_source.js').read_bytes()
assert sha((ROOT / 'official-source/spine-ts/build/spine-core.js').read_bytes()) == approved['official_bundle']['sha256']
assert sha((ROOT / 'research_attachment_factory087.js').read_bytes()) == approved['research_attachment_factory']['sha256']

front = {a['name']: a for a in results['Front']['animations']}
old_records = old['operator']['records']
assert len(old_records) == len(front) == 9
assert {a['animation'] for a in old_records} == set(front)
front_comparisons = []
for prior in old_records:
    current = front[prior['animation']]
    assert prior['spine_version'] == results['Front']['skeleton']['spine_version']
    assert prior['duration']['seconds'] == current['duration_seconds']
    assert [{'name': e['name'], 'seconds': e['seconds']} for e in prior['events']] == [{'name': e['name'], 'seconds': e['seconds']} for e in current['events']]
    assert (prior['source']['sha256'], prior['source']['bytes'], prior['source']['git_blob']) == (results['Front']['resource']['sha256'], results['Front']['resource']['bytes'], results['Front']['resource']['git_blob_sha1'])
    front_comparisons.append({'animation': prior['animation'], 'exact_duration_version_event_and_resource_identity': True})
control = json.loads((SNAP / 'front-control-receipt.json').read_text())
assert control['passed'] is True and control['front_source_records_compared'] == 9
assert control['fresh_skeleton_parser_calls'] == 0
assert control['application_API_helper_formatter_test_Qt_Wine_calls'] == 0
assert {row['animation'] for row in control['comparisons']} == set(front)
for row in control['comparisons']:
    current = front[row['animation']]
    assert all(row[key] is True for key in ['version_exact', 'duration_seconds_exact', 'event_names_and_seconds_exact', 'source_identity_exact'])
    assert row['duration_seconds'] == current['duration_seconds']
    assert row['events'] == [{'name': e['name'], 'seconds': e['seconds']} for e in current['events']]
control_mtime = datetime.fromtimestamp((PARENT / 'front-control-receipt.json').stat().st_mtime, timezone.utc)
assert control_mtime < datetime.fromisoformat(ops['Back']['started_at'])

back = {a['name']: a for a in results['Back']['animations']}
assert set(back) == {'Attack', 'Default', 'Idle', 'Skill', 'Start'}
candidates = []
for name, seconds in [('Attack', 0.5333333611488342), ('Skill', 0.4333333373069763)]:
    animation = back[name]
    assert animation['duration_seconds'] == 1.3333333730697632
    assert len(animation['events']) == 1
    event = animation['events'][0]
    assert event['name'] == 'OnAttack' and event['seconds'] == seconds
    assert event['int_value'] == 0 and event['float_value'] == 0 and event['string_value'] == '' and event['audio_path'] is None
    candidates.append({'animation': name, 'duration_seconds': animation['duration_seconds'],
        'event_name': event['name'], 'event_seconds': event['seconds'],
        'status': 'Conventional source-reference candidate only; native binding unverified'})
assert back['Default']['events'] == back['Idle']['events'] == []
assert back['Start']['events'][0]['name'] == 'OnStart'
assert back['Start']['events'][0]['seconds'] == 0.13333334028720856
receipt = {'version': 1, 'status': 'PASS_SAVED_SOURCE_ONLY',
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(),
    'input_bindings': bindings, 'parent_source_driver_sha256': sha(source_runner.read_bytes()),
    'source_contract_receipt_sha256': sha((ROOT / 'source-contract-receipt087.json').read_bytes()),
    'results': summaries, 'independent_front_comparisons': front_comparisons,
    'parent_front_control_saved_verified': True,
    'front_control_local_file_saved_mtime_utc': control_mtime.isoformat(),
    'front_control_local_saved_file_precedes_Back_start': True,
    'Back_source_candidate_count': 2, 'Back_source_candidates': candidates,
    'Back_other_named_records': ['Default', 'Idle', 'Start'],
    'Back_Die_or_Skill2_records_inferred_from_Front': False,
    'current_resource_bytes_git_blob_SHA256_rechecked_without_parsing': True,
    'official_bundle_factory_driver_bytes_still_exact': True,
    'observed_parent_fresh_full_reader_calls': 2, 'observed_parent_reader_errors': 0,
    'historical_visible_error_lower_bound': 1, 'historical_total_attempts': None,
    'historical_reader_identity': None, 'historical_error_root_cause_established': False,
    'reviewer_fresh_full_reader_calls': 0, 'reviewer_application_API_helper_formatter_test_Qt_Wine_calls': 0,
    'runtime_binding_verified': False, 'EOF_consumption_verified': False,
    'atlas_texture_geometry_render_verified': False,
    'scope': 'Exact fixed-resource official-reader return and saved source metadata; no product numeric update or native clock assertion.'}
(ROOT / 'saved-source-result-review087.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'source_review': info(ROOT / 'saved-source-result-review087.json'),
                  'Front_control_records': 9, 'Back_candidates': 2,
                  'reviewer_fresh_parse_calls': 0}, ensure_ascii=False))
