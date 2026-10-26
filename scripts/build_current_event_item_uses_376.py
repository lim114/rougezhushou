"""Compile exact role verbs and unique full item names from pinned event text."""
from pathlib import Path
from hashlib import sha256
import argparse, importlib.util, json, sys
BASE = Path(__file__).resolve().parents[1]


def enc(value): return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def build(root):
    sys.path.insert(0, str(root)); from rouge import current_event_directory as directory, expansion_reference as version
    spec = importlib.util.spec_from_file_location('rouge.current_event_item_uses', BASE / 'rouge/current_event_item_uses.py')
    model = importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    reference = directory.packet(); current = version.packet()
    if reference is None or current is None: raise ValueError('Verified catalogue and current item records required')
    data = model.derive(reference, current['current']['details'])
    if len(data['rows']) != 12 or len({r['item_id'] for r in data['rows']}) != 7: raise ValueError('Fixed literal coverage changed')
    sources = (directory.DATA, directory.MANIFEST, 'rouge/current_event_directory.py', version.PACK + '/current-topic.json')
    notes = {'schema': 'current_event_item_uses_376_notes_v1',
             'source_directory_identity': json.loads(json.dumps(reference['source_identity'])),
             'coverage': {'named_use_records': 12, 'named_items': 7, 'event_documents': len({r['event_id'] for r in data['rows']}),
                          'roles': {role: sum(r['role'] == role for r in data['rows']) for role, _ in model.ROLES}},
             'evidence': 'Each relation requires an explicit 持有/交出/消耗 verb immediately followed by one unique complete current item name in an exact already verified event description. Display hints alone are not proof.',
             'unknowns': ['Exact quantities not separately written in these descriptions, complete use and acquisition pools, actual inventory, actual eligibility and application.',
                          'Random generic processed/natural materials are not reclassified as these seven named items.'],
             'preexisting_scope': 'Separate event readers and some named acquisition pages already exist. This adds cross-event reverse lookup by item and role and links to exact dialogue and existing acquisition sources.',
             'new_mechanism_or_probability_added': False, 'private_data_used': False}
    blobs = {model.DATA: enc(data), model.NOTES: enc(notes)}
    pins = {n: {'sha256': sha256((root / n).read_bytes()).hexdigest(), 'bytes': (root / n).stat().st_size} for n in sources}
    pins.update({n: {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)} for n, raw in blobs.items()})
    blobs[model.MANIFEST] = enc({'schema': 'current_event_item_uses_376_manifest_v1', 'files': pins})
    return blobs, notes['coverage']


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--source-root', type=Path, default=Path.cwd()); parser.add_argument('--output-root', type=Path, default=BASE); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    blobs, coverage = build(args.source_root.resolve())
    for name, raw in blobs.items():
        target = args.output_root / name
        if args.check:
            if not target.is_file() or target.read_bytes() != raw: raise ValueError('Non-identical derived source: ' + name)
        else: target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    print(json.dumps({'passed': True, 'check': args.check, 'build_only': True, 'coverage': coverage,
                      'manifest_sha256': sha256(blobs['research/p3-current-event-item-uses-376/runtime-manifest.json']).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__': main()
