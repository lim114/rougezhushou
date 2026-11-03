"""Prepare deterministic public investment reference files; does not run tests."""
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import json
import sys


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def build(source_root, module_file):
    sys.path.insert(0, str(source_root))
    spec = importlib.util.spec_from_file_location('rouge.current_bank_reference', module_file)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    current = json.loads((source_root / model.TOPIC).read_bytes())
    receipt = json.loads((source_root / model.DOCUMENT_RECEIPT).read_bytes())
    raw_document = (source_root / model.DOCUMENT).read_bytes()
    if (sha256(raw_document).hexdigest() != receipt['community_sha256']
            or len(raw_document) != receipt['community_bytes']):
        raise ValueError('Existing pinned original failed its own receipt')
    fragment = model.document_fragment(raw_document.decode('utf8'))
    data = model.derive_data(current['details'], fragment, receipt)
    notes = {
        'section': 356, 'scope': 'Five investment unlock thresholds, explicit counter conflict, exact named collectible reference',
        'current_game_source': model.TOPIC, 'game_commit': model.version.NEW_COMMIT,
        'original_document': model.DOCUMENT, 'document_receipt': model.DOCUMENT_RECEIPT,
        'document_revision': 433770, 'document_reused_from_existing_archive': True,
        'new_html_acquired': False, 'current_server_verified': False,
        'item_binding_basis': data['item_binding']['basis'],
        'counter_evidence': 'Pinned document explicitly distinguishes total historical investment from balance. TOTAL_SUM alone is not used as translated-mechanism proof.',
        'conflict_preserved': 'Current item unlockCondDesc still says peak balance 250. This is not silently rewritten or marked server-resolved.',
        'limits': ['No actual account or run state', 'No investment/withdrawal operation',
                   'No direct grant, inventory update or complete drop pool',
                   'No inferred 50-threshold battle target', 'No final shop slot total'],
        'license': receipt['license'],
    }
    output = {model.DATA: enc(data), model.NOTES: enc(notes), model.EXCERPT: fragment.encode('utf8')}
    names = set(output) | {model.TOPIC, model.DOCUMENT, model.DOCUMENT_RECEIPT, model.ICON}
    files = {}
    for name in sorted(names):
        raw = output.get(name)
        if raw is None:
            raw = (source_root / name).read_bytes()
        files[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    output[model.MANIFEST] = enc({'schema': 'current_bank_356_manifest_v1',
                                'game_commit': model.version.NEW_COMMIT, 'files': files})
    return model, output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument('--source-root', type=Path, default=root)
    parser.add_argument('--output-root', type=Path, default=root)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    model_file = root / 'rouge/current_bank_reference.py'
    model, output = build(args.source_root.resolve(), model_file)
    for name, raw in output.items():
        path = args.output_root / name
        if args.check:
            if path.read_bytes() != raw:
                raise ValueError('Build differs: ' + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    digest = sha256(output[model.MANIFEST]).hexdigest()
    if args.check and digest != model.MANIFEST_SHA256:
        raise ValueError('Manifest pin differs')
    print(json.dumps({'bank_rewards': 5, 'exact_named_item': model.ITEM_ID,
                      'counter_conflict_preserved': True, 'manifest_sha256': digest}))
