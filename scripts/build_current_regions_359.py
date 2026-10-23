"""Build the cache or formal source package; no tests or game integration."""
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
    spec = importlib.util.spec_from_file_location('rouge.current_region_reference', module_file)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    current = json.loads((source_root / model.TOPIC).read_bytes())
    receipt = json.loads((source_root / model.DOCUMENT_RECEIPT).read_bytes())
    raw = (source_root / model.DOCUMENT).read_bytes()
    if sha256(raw).hexdigest() != receipt['community_sha256'] or len(raw) != receipt['community_bytes']:
        raise ValueError('Existing original document does not match its receipt')
    excerpts = model.document_excerpts(raw.decode('utf8'))
    data = model.derive_data(current, excerpts, receipt)
    old = json.loads((source_root / 'rouge/data/exploration-reference.json').read_bytes())
    current_ids = {r['id'] for r in data['rows']}
    old_ids = set(old['zones'])
    notes = {'section': 359, 'scope': 'Current exact-region entry grants, document corroboration and exhaustion conditions',
             'new_capability': 'Exact 27-zone grant rows plus current wing description, separately corroborated regional document amounts and ordinary-page targets',
             'already_existing_scope_not_recounted': ['189 old 26-region goals and exhaustion budget',
                                                      '196 portal transitions and temporary item retention'],
             'old_region_count': len(old_ids), 'current_region_count': len(current_ids),
             'new_current_ids': sorted(current_ids - old_ids),
             'old_budget_source': 'rouge/data/exploration-reference.json',
             'old_budget_sha256_at_preparation': sha256((source_root / 'rouge/data/exploration-reference.json').read_bytes()).hexdigest(),
             'old_budget_replaced': False, 'new_html_acquired': False,
             'document_revision': 433770, 'current_server_verified': False,
             'source_keys': ['details.zones', 'modules.gridZone.zoneMissionBannerData',
                             'modules.gridZone.scrapSideBarStepZeroHintBannerData',
                             'details.gameConst.portalZones', 'details.relics.rogue_6_feature_ap_1',
                             'customizeData.commonDevelopment.developments.rogue_6_outbuff_37'],
             'limits': ['Grant parameters do not prove runtime attachment or current final action points',
                        'Shared Chinese name is not independent variant proof',
                        'No actual destination, execution, inventory or run update',
                        'No order of payment, rewards and exhaustion inferred'],
             'license': receipt['license']}
    output = {model.DATA: enc(data), model.EXCERPTS: enc(excerpts), model.NOTES: enc(notes)}
    files = {}
    for name in sorted(set(output) | {model.TOPIC, model.DOCUMENT, model.DOCUMENT_RECEIPT}):
        content = output.get(name)
        if content is None:
            content = (source_root / name).read_bytes()
        files[name] = {'sha256': sha256(content).hexdigest(), 'bytes': len(content)}
    output[model.MANIFEST] = enc({'schema': 'current_region_359_manifest_v1',
                                'game_commit': model.version.NEW_COMMIT, 'files': files})
    return model, output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument('--source-root', type=Path, default=root)
    parser.add_argument('--output-root', type=Path, default=root)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    model, output = build(args.source_root.resolve(), root / 'rouge/current_region_reference.py')
    for name, content in output.items():
        path = args.output_root / name
        if args.check:
            if path.read_bytes() != content:
                raise ValueError('Build differs: ' + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    digest = sha256(output[model.MANIFEST]).hexdigest()
    if args.check and digest != model.MANIFEST_SHA256:
        raise ValueError('Manifest pin differs')
    print(json.dumps({'regions': 27, 'portal_returns': 19, 'entry_grant_records': 27,
                      'first_region_wings_reference': True, 'manifest_sha256': digest}))
