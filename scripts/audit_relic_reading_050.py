"""Audit packaged inventory references and isolated state proof boundaries.

This script does not capture a window, write user configuration, send chat,
or infer an unseen inventory/recipient from a counter or historical count.
"""
import ast
import hashlib
import io
import importlib.util
import json
import sys
import time
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.catalog import catalog, tactical_tools
from rouge.recognition import ScreenReader
from rouge.relic_recognition import artwork_families, reference_entries
from rouge.relics import mechanics
from rouge.run_config import config_data


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', default='audit')
    parser.add_argument('--samples', action='store_true')
    parser.add_argument('--before-source', help='Replay tests against an explicitly named public RunState backup.')
    args = parser.parse_args()
    output = ROOT / '.cache/research/p1-recognition-050'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for entry in reference_entries():
        path = ROOT / 'rouge/data' / entry['file']
        blob = path.read_bytes()
        pixels = cv2.imdecode(np.frombuffer(blob, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        digest = hashlib.sha1(b'blob ' + str(len(blob)).encode('ascii') + b'\0' + blob).hexdigest()
        assert hashlib.sha256(blob).hexdigest() == entry['sha256'], entry['id']
        assert digest == entry['git_blob_sha1'], entry['id']
        assert pixels is not None and pixels.ndim == 3 and pixels.shape[2] == 4, entry['id']
        records.append({'id': entry['id'], 'file': entry['file'], 'sha256': entry['sha256'],
                        'git_blob_sha1': digest, 'shape': list(pixels.shape)})
    direct = {entry['id'] for entry in reference_entries()}
    relics = set(catalog()['relics'])
    equivalent = set(artwork_families()) - direct
    missing = sorted(relics - direct - equivalent)
    assert not missing
    bindings = [{'id': bid, 'name': entry['name'], 'icon_relic_id': entry['relic_id'],
                 'reference_present': entry['relic_id'] in direct}
                for bid, entry in mechanics()['char_buffs'].items()]
    assert all(entry['reference_present'] for entry in bindings)
    source_paths = ['rouge/run_state.py', 'rouge/run_recognition.py', 'rouge/relic_recognition.py',
                    'rouge/recognition.py', 'rouge/resource_recognition.py', 'rouge/app.py',
                    'rouge/data/relic-icon-receipt.json', 'rouge/data/tactical-icon-receipt.json',
                    'rouge/data/relic-reference-equivalence.json', 'rouge/data/run-config.json',
                    'tests/test_relic_reading_050.py', 'scripts/audit_relic_reading_050.py']
    source_hashes = {path: sha(ROOT / path) for path in source_paths if (ROOT / path).exists()}
    # Record what the existing reader actually emits, without claiming a
    # missing parser merely because one screenshot lacks a particular field.
    module = ast.parse((ROOT / 'rouge/run_recognition.py').read_text(encoding='utf-8'))
    strings = {node.value for node in ast.walk(module) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    static_seams = {'run_reader_contains_char_buff_ids_field': 'char_buff_ids' in strings,
                    'run_reader_contains_char_buffs_complete_field': 'char_buffs_complete' in strings}
    samples = []
    if args.samples:
        reader = ScreenReader()
        for name in ('run-relic-multicard.png', 'run-relic-multicard-closed.png'):
            path = ROOT / 'samples/native-client' / name
            pixels = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
            started = time.perf_counter()
            result = reader.read(pixels)
            run = result.get('run') or {}
            held = run.get('relics', {})
            samples.append({'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                'page': result.get('page'), 'count': held.get('count'), 'ids': held.get('ids', []),
                'tool_ids': run.get('tactical_tools', {}).get('ids', []),
                'icons': [{key: icon[key] for key in ('id', 'candidates', 'confirmed', 'score') if key in icon}
                          for icon in held.get('icons', [])],
                'cards': held.get('cards', []), 'resource_keys': sorted(run.get('resources', {})),
                'seconds_single_offline_read': time.perf_counter() - started,
                'scope': 'One existing saved page only; not a speed benchmark or full-inventory coverage.'})
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_relic_reading_050')
    if args.before_source:
        before = (ROOT / args.before_source).resolve()
        boundary = (ROOT / '.cache/batch-050-before').resolve()
        assert before.is_relative_to(boundary) and before.name == 'run_state.py'
        spec = importlib.util.spec_from_file_location('rouge.run_state_before_050', before)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import tests.test_relic_reading_050 as test_module
        test_module.RunState = module.RunState
        source_hashes['tested_run_state_backup'] = sha(before)
    tested = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    (output / f'{args.label}-tests.log').write_text(stream.getvalue(), encoding='utf-8')
    payload = {'scope': 'Packaged reference integrity; two optional saved samples; synthetic state-seam regression.',
        'coverage': {'catalog_relics': len(relics), 'independent_original_references': len(direct & relics),
            'equivalent_variants': len(equivalent & relics), 'missing_relic_references': missing,
            'tactical_tools': len(tactical_tools()), 'tool_reference_count': len(direct & set(tactical_tools())),
            'difficulty_groups': len(config_data()['difficulty_upgrade_relic_groups']),
            'independent_variant_artwork_verified': False},
        'reference_records': records, 'char_buff_reference_links': bindings, 'static_seams': static_seams,
        'saved_samples': samples,
        'tests': {'run': tested.testsRun, 'passed': tested.testsRun - len(tested.failures) - len(tested.errors),
            'failures': [{'id': str(test), 'traceback': trace} for test, trace in tested.failures],
            'errors': [{'id': str(test), 'traceback': trace} for test, trace in tested.errors]},
        'source_sha256': source_hashes,
        'limitations': [
            'Reference coverage is not a live accuracy claim for every owned page, tier, scale or occlusion.',
            'Owned card titles/usages corroborate identity, but no page/session inventory version token is read.',
            'Stable visible total count plus historical cross-page IDs cannot prove a simultaneous snapshot.',
            'A current bar missing icons is absence of evidence; contradictory new ambiguous artwork revokes proof.',
            'Layer-count and stable recipient display layout is absent from the saved pages; no parser is invented.',
            'No live sampling, game operation, private-state read, chat request or numeric mechanism edit.']}
    target = output / f'{args.label}.json'
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'file': target.relative_to(ROOT).as_posix(), 'coverage': payload['coverage'],
                      'tests': {key: value for key, value in payload['tests'].items() if key in ('run', 'passed')},
                      'sample_count': len(samples)}, ensure_ascii=True))


if __name__ == '__main__':
    main()
