"""Compile the explicit-quantity event lookup from the fixed current catalogue."""
from pathlib import Path
from hashlib import sha256
import argparse, importlib.util, json, sys
BASE = Path(__file__).resolve().parents[1]


def enc(value): return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def build(root):
    sys.path.insert(0, str(root)); from rouge import current_event_directory as directory
    spec = importlib.util.spec_from_file_location('rouge.current_event_resources', BASE / 'rouge/current_event_resources.py')
    model = importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    reference = directory.packet()
    if reference is None: raise ValueError('The complete verified current event catalogue is required')
    data = model.derive(reference)
    sources = (directory.DATA, directory.MANIFEST, 'rouge/current_event_directory.py')
    notes = {'schema': 'current_event_resources_374_notes_v1',
             'source_directory_identity': json.loads(json.dumps(reference['source_identity'])),
             'coverage': {'event_documents': data['source_event_count'], 'source_occurrences': data['source_occurrence_count'],
                          'explicit_change_records': len(data['rows']), 'explicit_resource_parts': sum(len(r['effects']) for r in data['rows']),
                          'source_event_documents_with_explicit_quantity': len({r['event_id'] for r in data['rows']})},
             'source_rule': 'Only literal original description quantities already preserved by current event readers. The directory preserves exact source memberships and existing qualifiers. No body-only or hidden result is inferred.',
             'classification_rules': ['Current HP, maximum HP and shield are separate.', 'Half and all are retained as original rules; no rounding, minimum or actual quantity is guessed.',
                                      'All AP converted to equal hope is separately listed with unknown actual quantity, not added to a guessed net.',
                                      'Fixed reward quantities name only a class; no hidden pool or quality distribution is invented.',
                                      'Filtering by one gain never removes the other known costs from the selected entry.',
                                      'The same choice in different phases is still a separate source occurrence; alternative rewards are never summed.'],
             'preexisting_scope': 'Individual event resource descriptions already exist. This adds cross-event numeric resource and cost lookup with exact return to existing full context.',
             'unknowns': ['All hidden or body-only quantities, complete reward pools, full current server conditions, actual payment and grants.'],
             'new_game_mechanism_or_probability_added': False, 'private_data_used': False}
    blobs = {model.DATA: enc(data), model.NOTES: enc(notes)}
    pins = {n: {'sha256': sha256((root / n).read_bytes()).hexdigest(), 'bytes': (root / n).stat().st_size} for n in sources}
    pins.update({n: {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)} for n, raw in blobs.items()})
    blobs[model.MANIFEST] = enc({'schema': 'current_event_resources_374_manifest_v1', 'files': pins})
    return blobs, notes['coverage']


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--source-root', type=Path, default=Path.cwd())
    parser.add_argument('--output-root', type=Path, default=BASE); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    blobs, coverage = build(args.source_root.resolve())
    for name, raw in blobs.items():
        target = args.output_root / name
        if args.check:
            if not target.is_file() or target.read_bytes() != raw: raise ValueError('Non-identical derived source: ' + name)
        else: target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    print(json.dumps({'passed': True, 'check': args.check, 'build_only': True, 'coverage': coverage,
                      'manifest_sha256': sha256(blobs['research/p3-current-event-resources-374/runtime-manifest.json']).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__': main()
