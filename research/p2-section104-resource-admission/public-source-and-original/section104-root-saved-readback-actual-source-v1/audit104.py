"""Root-only pure saved readback: no project, Qt, API or test execution."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

from native_evidence import assert_native_equal, read_record, source_map


HELPER = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
RUNNER = '24f6e00bf52d6a08e40e5da2c66eb45848311c75235434217b06f8c9fb42bbe1'
GOLD_RECEIPT = '86e88039636ec70a366917fb5a1ce8d6d426dc71b176242424a85dec0e6da3eb'
CANDIDATE_RECEIPT = '290949a8d5759a8021f681f2b3e5235ade24cb76d6e57eb0adbf9dd55d08e80a'
GOLD_GUARD = '5c049bc888fc892dca0219a1a328ffceea03105be05130d9cd4e537165e406d9'
CANDIDATE_GUARD = 'f43683207776aa862406d5525012112e9a18d313b76df70a448c2d243c2b7225'
VISUAL = '46b50f83c3501a22f2c150ed3806937a6750dc3d50208923c495de3052737c64'
CORE = 'a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
HEALTHY = ('healthy-zero', 'healthy-positive-update', 'healthy-unread-positive',
           'healthy-float-unconsumed', 'healthy-null-unconsumed', 'healthy-bool-unconsumed',
           'healthy-text-unconsumed', 'healthy-unused-opaque-alias', 'healthy-actual-IO-memory')
BAD = ('bad-no-old-missing-both', 'bad-old-null-missing-both', 'bad-old-positive-missing-both',
       'bad-null-record-with-peer-and-config', 'bad-container-null', 'bad-container-list',
       'bad-record-list', 'bad-unknown-counter-with-good-gold', 'bad-read-after-actual-IO-memory')
KEEP = {'healthy-zero', 'healthy-unread-positive', 'bad-no-old-missing-both',
        'bad-old-null-missing-both', 'bad-old-positive-missing-both',
        'bad-container-null', 'bad-container-list', 'bad-record-list'}
STABLE = KEEP | {'healthy-unused-opaque-alias'}
IO = {'healthy-actual-IO-memory', 'bad-read-after-actual-IO-memory'}
MARKER = b'public-resource104-nonempty-temporary'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_json(path, expected):
    path = Path(path)
    assert not path.is_symlink()
    raw = path.read_bytes()
    assert sha(raw) == expected, str(path)
    return json.loads(raw), {'path': str(path), 'bytes': len(raw), 'sha256': expected}


def same(left, right, label):
    assert_native_equal(left, right, label)


def json_native(raw):
    assert type(raw) is bytes
    return json.loads(raw.decode('utf-8'))


def missing(value):
    assert value == {'exists': False, 'kind': None, 'bytes': None}


def main():
    parser = argparse.ArgumentParser()
    for name in ('root', 'gold', 'gold-primary', 'candidate', 'candidate-primary',
                 'gold-guard', 'guard', 'runner', 'visual', 'out'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--related')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.out).resolve()
    assert not output.exists() and output != root and root not in output.parents
    assert output.parent.is_dir()
    artifact = Path(__file__).resolve().parent
    assert artifact != root and root not in artifact.parents
    assert sha((artifact / 'native_evidence.py').read_bytes()) == HELPER
    started = time.perf_counter()
    active = {'phase': 'bindings', 'case': None, 'record': None}
    report = {'kind': 'ROOT_ACTUAL_104_PURE_SAVED_READBACK', 'passed': False,
              'workflow_complete': False, 'audit_Source_sha256': sha(Path(__file__).read_bytes()),
              'native_helper_sha256': HELPER, 'decoded_records': [], 'snapshot_checks': [],
              'restart_checks': [], 'healthy_Gold_points': [], 'PNG_checks': [],
              'project_API_formatter_numeric_Qt_tests_Wine_Git_executed': False,
              'new_probe_or_API_execution': False, 'saved_inputs_written': False,
              'native_windows_verified': False, 'natural_OCR_producer_verified': False,
              'reset_measured_by_104_window_or_saved': False,
              'reset_coverage_note': 'No reset calls in these Saved records. Separate maintained99/related test coverage must be assessed from its actual receipt, not inferred from 104 window or this audit.',
              'numeric_scope': 'Complete original returned subgraphs and native callers linked to saved snapshots; no numerical recomputation.',
              'text_scope': 'All three saved full texts at all54 snapshots, GUI/default equality, estimate/default equality, and18 complete healthy Gold snapshot comparisons; no formatter re-execution.',
              'restart_scope': '27 actual close/direct RunState reload records. This audit does not open a second MainWindow or preserve live aliases through JSON.'}
    current = None
    additional = None
    input_bindings = {}
    try:
        guard, binding = pinned_json(args.guard, CANDIDATE_GUARD)
        input_bindings['candidate_guard'] = binding
        old_guard, binding = pinned_json(args.gold_guard, GOLD_GUARD)
        input_bindings['Gold_guard'] = binding
        current = guard['source_sha256']
        old = old_guard['source_sha256']
        additional = guard['source_additional_sha256']
        assert len(current) == 748 and len(old) == 747
        assert additional == old_guard['source_additional_sha256'] == {'CORE_0.70_VERIFICATION.json': CORE}
        assert set(current) - set(old) == {'tests/test_resource_observation_104.py'} and not set(old) - set(current)
        assert {name for name in old if old[name] != current[name]} == {'rouge/run_state.py', 'scripts/verify_cloud.py'}
        report['source_before'] = source_map(root)
        assert report['source_before'] == current
        report['source_additional_before'] = {name: sha((root / name).read_bytes()) for name in additional}
        assert report['source_additional_before'] == additional
        assert sha(Path(args.runner).read_bytes()) == RUNNER
        report['runner_sha256'] = RUNNER
        datasets = {}
        for phase, directory, primary, digest, expected, count, calls, guard_digest in (
            ('gold', args.gold, args.gold_primary, GOLD_RECEIPT, old, 117, 90, GOLD_GUARD),
            ('candidate', args.candidate, args.candidate_primary, CANDIDATE_RECEIPT,
             current, 238, 183, CANDIDATE_GUARD)):
            active.update(phase=phase, case=None, record=None)
            directory = Path(directory).resolve()
            assert directory != root and root not in directory.parents
            primary_raw = Path(primary).read_bytes()
            assert primary_raw == b'0\n'
            input_bindings[phase + '_primary'] = {'path': str(primary), 'bytes': len(primary_raw), 'sha256': sha(primary_raw)}
            receipt, binding = pinned_json(directory / 'receipt.json', digest)
            input_bindings[phase + '_receipt'] = binding
            assert receipt['kind'] == 'ROOT_ACTUAL_104_REAL_MAINWINDOW' and receipt['phase'] == phase
            assert receipt['passed'] is True and receipt['workflow_complete'] is True
            assert receipt['runner_sha256'] == RUNNER and receipt['native_helper_sha256'] == HELPER
            assert receipt['source_guard_sha256'] == guard_digest
            assert receipt['source_before'] == receipt['source_after'] == expected and receipt['source_drift'] == []
            assert receipt['source_additional_before'] == receipt['source_additional_after'] == additional
            assert receipt['Qt_errors'] == [] and receipt['deadline_seconds'] == 450
            assert 0 < receipt['elapsed_seconds'] < 450
            for key in ('native_windows_verified', 'natural_OCR_producer_verified', 'private_state_access', 'game_chat_sampling_executed'):
                assert receipt[key] is False
            identities = list(HEALTHY) if phase == 'gold' else list(HEALTHY + BAD)
            assert [row['id'] for row in receipt['rows']] == identities
            assert len(receipt['records']) == count and receipt['calculate_call_count'] == calls
            if phase == 'candidate':
                assert receipt['actual_gold_receipt_sha256'] == GOLD_RECEIPT
            values = {}
            metadata_by_path = {}
            nearest = {}
            predecessor = {}
            kinds = Counter()
            record_dir = directory / 'records'
            assert not record_dir.is_symlink()
            assert set(path.name for path in record_dir.iterdir()) == {m['path'] for m in receipt['records']}
            for sequence, metadata in enumerate(receipt['records'], 1):
                active.update(record=metadata['path'], case=metadata['case'])
                assert metadata['path'] == '%06d.pickle.gz' % sequence
                assert metadata['case'] in identities and metadata['path'] not in values
                value = read_record(record_dir, metadata)
                for key in ('kind', 'case', 'phase'):
                    assert value[key] == metadata[key]
                kinds[value['kind']] += 1
                values[metadata['path']] = value
                metadata_by_path[metadata['path']] = metadata
                if value['kind'] == 'actual_calculate_result':
                    same(value['before'], value['after'], 'Original actual calculator retained complete native caller')
                    assert type(value['result']) is dict
                    nearest[value['case']] = metadata['path']
                elif value['kind'] in ('actual_initial_snapshot', 'actual_post_snapshot'):
                    assert value['case'] in nearest
                    predecessor[metadata['path']] = nearest[value['case']]
                else:
                    assert value['kind'] in ('actual_restart', 'actual_post_IO_unread')
                report['decoded_records'].append({'dataset': phase, **metadata, 'read_record_hash_and_safe_native_decode_verified': True})
            assert kinds['actual_calculate_result'] == calls
            assert kinds['actual_initial_snapshot'] == kinds['actual_post_snapshot'] == kinds['actual_restart'] == len(identities)
            assert kinds['actual_post_IO_unread'] == (0 if phase == 'gold' else 1)
            assert sum(kinds.values()) == count
            datasets[phase] = {'receipt': receipt, 'values': values, 'metadata': metadata_by_path,
                               'predecessor': predecessor, 'directory': directory, 'kinds': dict(kinds)}

        for phase, data in datasets.items():
            for row in data['receipt']['rows']:
                identity = row['id']
                active.update(phase=phase, case=identity, record=None)
                assert row['constructor_returned'] is True
                before = data['values'][row['before']['path']]
                after = data['values'][row['after']['path']]
                restart = data['values'][row['restart']['path']]
                for key, value, wanted in (('before', before, 'actual_initial_snapshot'),
                                           ('after', after, 'actual_post_snapshot'),
                                           ('restart', restart, 'actual_restart')):
                    assert row[key] == data['metadata'][row[key]['path']]
                    assert value['case'] == identity and value['kind'] == wanted
                for metadata, snapshot in ((row['before'], before), (row['after'], after)):
                    active['record'] = metadata['path']
                    original = data['values'][data['predecessor'][metadata['path']]]
                    view = snapshot['view']
                    # Each subgraph is complete. The wrapper froze the caller
                    # before saving the returned graph, so no artificial cross-
                    # domain caller/result alias comparison is assembled here.
                    same(view['calculation_caller'], original['before'], 'Snapshot linked to original retained caller')
                    same(view['damage_result']['scenario'], original['before']['args'][0], 'Actual scenario equals full original scenario argument')
                    same(view['damage_result']['result'], original['result'], 'Snapshot equals complete actual original returned graph')
                    assert view['damage_result']['scenario']['operator'] == 'mechanist'
                    assert view['damage_result']['scenario']['skill'] == 3
                    texts = view['three_texts']
                    assert list(texts) == ['estimate', 'default', 'technical']
                    assert all(type(text) is str and text for text in texts.values())
                    assert texts['estimate'] == texts['default']
                    assert view['displayed_damage'] == texts['default'].replace(chr(160), ' ')
                    assert type(view['summary']) is str and view['summary']
                    same(view['resource_view'], snapshot['durable']['run']['resources'], 'Basic resources full native view equals raw resource facts')
                    report['snapshot_checks'].append({'dataset': phase, 'case': identity,
                        'record': metadata['path'], 'original_calculate_record': data['predecessor'][metadata['path']],
                        'complete_result_and_caller_subgraphs_verified': True,
                        'three_saved_full_text_sha256': {key: sha(text.encode('utf-8')) for key, text in texts.items()}})
                prior = before['durable']['run']['resources']
                resources = after['durable']['run']['resources']
                if identity in KEEP:
                    same(resources, prior, 'Unread resource preserves every old fact and original time')
                if identity in STABLE:
                    same(after['view']['damage_result'], before['view']['damage_result'], 'Unread or metadata-only complete real math unchanged')
                    same(after['view']['three_texts'], before['view']['three_texts'], 'Unread or metadata-only three full reports unchanged')
                if identity == 'bad-no-old-missing-both':
                    assert resources == {} and '源石锭/零件数尚未确认' in after['view']['summary']
                if identity == 'healthy-zero':
                    for key in ('gold', 'parts_count'):
                        assert type(resources[key]['value']) is int and resources[key]['value'] == 0
                        assert resources[key]['captured_at'] == 1000.0
                if identity == 'healthy-unread-positive':
                    assert after['view']['damage_result']['result']['estimate']['base_stats']['attack_speed'] == 135
                if identity.startswith('healthy-') and identity.endswith('-unconsumed'):
                    scenario = after['view']['damage_result']['scenario']
                    assert scenario['relic_ids'] == [] and scenario['relic_context'] == {}
                    typed = {'healthy-float-unconsumed': (float, 8.0), 'healthy-null-unconsumed': (type(None), None),
                             'healthy-bool-unconsumed': (bool, False), 'healthy-text-unconsumed': (str, '9')}
                    kind, value = typed[identity]
                    assert type(resources['gold']['value']) is kind
                    same(resources['gold']['value'], value, 'Complete legacy value type retained')
                    assert resources['gold']['captured_at'] == 1001.0
                if identity == 'bad-null-record-with-peer-and-config':
                    same(resources['gold'], prior['gold'], 'Bad gold keeps original complete fact/time')
                    assert resources['parts_count']['value'] == 4 and resources['parts_count']['capacity'] == 12
                    assert resources['parts_count']['captured_at'] == 1001.0
                    assert after['durable']['run']['config']['difficulty'] == {
                        'value': 2, 'source': 'public-peer104', 'captured_at': 1001.0}
                if identity in ('healthy-positive-update', 'bad-unknown-counter-with-good-gold') or identity in IO:
                    assert type(resources['gold']['value']) is int and resources['gold']['value'] == 26
                    assert resources['gold']['captured_at'] == 1001.0
                if identity == 'bad-unknown-counter-with-good-gold':
                    assert 'public-unknown-counter104' not in resources
                same(after['disks']['account'], before['disks']['account'], 'Run-only action keeps original account bytes')
                missing(before['disks']['run_tmp'])
                missing(before['disks']['account_tmp'])
                missing(after['disks']['account_tmp'])
                same(restart['disks'], after['disks'], 'Actual close and direct reload preserve entire observed disk phase')
                same(restart['live_before_close'], after['durable'], 'Close retained original complete live state')
                same(restart['caller_before'], restart['caller_after'], 'Original observation caller retained through close/restart')
                assert restart['state']['id'] == before['durable']['run']['id']
                if identity in IO:
                    assert after['durable']['run_save_issue'] == '本局记录保存未完成'
                    assert '仅在当前运行有效' in after['view']['summary']
                    same(after['disks']['run'], before['disks']['run'], 'IO failure leaves original older run bytes')
                    temporary = after['disks']['run_tmp']
                    assert temporary == {'exists': True, 'kind': 'directory',
                                         'children': ['public-marker'], 'marker': MARKER}
                    same(restart['state'], before['durable']['run'], 'Actual IO reload restores complete older loaded disk graph')
                    same(restart['resource_view'], prior, 'Actual IO restart has only older confirmed resources')
                    assert '仅在当前运行有效' not in restart['summary']
                    if identity == 'bad-read-after-actual-IO-memory':
                        follow = data['values'][row['post_IO_unread']['path']]
                        assert row['post_IO_unread'] == data['metadata'][row['post_IO_unread']['path']]
                        same(follow['caller_before'], follow['caller_after'], 'Bad post-IO caller retained')
                        same(follow['durable'], after['durable'], 'Bad post-IO observation keeps final live fact/time/terminal issue')
                        same(follow['disks'], after['disks'], 'Bad post-IO observation preserves older disk and real marker directory')
                        assert follow['caller_after'][1] == 1002.0
                    oracle = 'Full older loaded public disk graph; unsaved memory not persisted'
                else:
                    assert after['durable']['run_save_issue'] is None
                    missing(after['disks']['run_tmp'])
                    persisted = json_native(after['disks']['run']['bytes'])
                    same(restart['state'], persisted, 'Complete actual saved JSON graph restored')
                    same(restart['resource_view'], persisted['resources'], 'Restored resource view respects original JSON policy')
                    assert restart['summary'] == after['view']['summary']
                    oracle = 'Full persisted JSON graph; no live alias preservation claim'
                if identity == 'healthy-unused-opaque-alias':
                    resource = resources['gold']
                    assert resource['public_left'] is resource['public_right']
                    restored = restart['state']['resources']['gold']
                    assert restored['public_left'] is not restored['public_right']
                    same(restored['public_left'], resource['public_left'], 'JSON keeps opaque metadata values/float bits')
                    caller = restart['caller_after'][0]
                    shared = caller['resources']['gold']['public_left']
                    assert shared is caller['resources']['gold']['public_right']
                    assert shared is caller['public_opaque']['left'] is caller['public_opaque']['right']
                    cycle = caller['public_opaque']['unused_cycle']
                    assert cycle[0] is cycle
                    same(after['durable']['run']['public_opaque'], before['durable']['run']['public_opaque'],
                         'Unused caller opaque cycle does not overwrite saved opaque state')
                report['restart_checks'].append({'dataset': phase, 'case': identity, 'record': row['restart']['path'],
                                                 'oracle': oracle, 'actual_close_direct_RunState_verified': True})

        gold_rows = {row['id']: row for row in datasets['gold']['receipt']['rows']}
        for row in datasets['candidate']['receipt']['rows']:
            if row['id'] not in gold_rows:
                continue
            assert row['complete_healthy_native_initial_post_and_three_texts_equal_Gold'] is True
            for key in ('before', 'after'):
                original = datasets['gold']['values'][gold_rows[row['id']][key]['path']]
                candidate = datasets['candidate']['values'][row[key]['path']]
                same({name: candidate[name] for name in ('view', 'durable', 'disks')},
                     {name: original[name] for name in ('view', 'durable', 'disks')},
                     'Complete healthy initial/post actual Gold graph and all three full texts')
                report['healthy_Gold_points'].append({'case': row['id'], 'point': key,
                                                     'complete_native_Gold_equal': True})

        active.update(phase='actual-PNG-ledger', case=None, record=None)
        visual, binding = pinned_json(args.visual, VISUAL)
        input_bindings['actual_visual_ledger'] = binding
        assert visual['passed'] is True and visual['workflow_complete'] is True
        assert visual['native_windows_game_chat_verified'] is False
        pngs = datasets['candidate']['receipt']['pngs']
        assert len(pngs) == len(visual['pngs']) == 4 and datasets['gold']['receipt']['pngs'] == []
        for png, viewed in zip(pngs, visual['pngs']):
            assert {key: viewed[key] for key in png} == png
            assert viewed['actually_viewed'] is True and type(viewed['visual_observation']) is str and viewed['visual_observation']
            assert Path(png['file']).name == png['file']
            path = datasets['candidate']['directory'] / png['file']
            assert not path.is_symlink()
            raw = path.read_bytes()
            assert len(raw) == png['bytes'] and sha(raw) == png['sha256'] and raw.startswith(b'\x89PNG\r\n\x1a\n')
            report['PNG_checks'].append({**png, 'actual_Root_view_ledger_bound': True})
        if args.related:
            path = Path(args.related)
            raw = path.read_bytes()
            json.loads(raw)
            input_bindings['separate_related_receipt'] = {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw),
                'scope': 'Pointer only. No reset leaf PASS inferred from aggregate221 result.'}
        assert len(report['decoded_records']) == 355
        assert len(report['snapshot_checks']) == 54 and len(report['healthy_Gold_points']) == 18
        assert len(report['restart_checks']) == 27 and len(report['PNG_checks']) == 4
        report.update(passed=True, workflow_complete=True, decoded_record_count=355,
                      original_calculate_caller_records_checked=273, complete_saved_snapshots_checked=54,
                      three_saved_full_texts_checked=162, healthy_Gold_points_checked=18,
                      actual_close_direct_RunState_records_checked=27,
                      candidate_actual_IO_disk_cases_checked=2, Gold_actual_IO_baseline_checked=1)
    except BaseException as error:
        report['failure'] = {'active': dict(active), 'type': type(error).__name__, 'message': str(error),
                             'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}
    finally:
        report['bindings'] = input_bindings
        if current is not None:
            report['source_after'] = source_map(root)
            report['source_drift'] = [name for name in set(current) | set(report['source_after'])
                                      if current.get(name) != report['source_after'].get(name)]
            report['source_additional_after'] = {name: sha((root / name).read_bytes()) for name in additional}
            if report['source_drift'] or report['source_additional_after'] != additional:
                report.update(passed=False, workflow_complete=False)
        report['elapsed_seconds'] = time.perf_counter() - started
        with output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'decoded_records': len(report['decoded_records']),
                      'snapshots': len(report['snapshot_checks']), 'restarts': len(report['restart_checks']),
                      'healthy_Gold_points': len(report['healthy_Gold_points'])}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
