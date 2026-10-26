"""Derive current event lookup from existing verified readers, not guessed parents."""
from pathlib import Path
from hashlib import sha256
import argparse, importlib.util, json, sys
BASE = Path(__file__).resolve().parents[1]


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def build(root):
    sys.path.insert(0, str(root))
    from rouge import node_catalog, current_node_readers, expansion_reference as version
    spec = importlib.util.spec_from_file_location('rouge.current_event_directory', BASE / 'rouge/current_event_directory.py')
    model = importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    catalogue = node_catalog.all_events(include_indirect=True)['rows']
    bindings = {e['id']: current_node_readers.binding_for(e) for e in catalogue}
    mods = model.providers(); data = model.derive(catalogue, bindings, mods)
    sources = set()
    for key, m in mods.items():
        sources.update((m.DATA, m.MANIFEST, 'rouge/' + model.PROVIDERS[key] + '.py'))
    sources.update(('rouge/expansion_reference.py', 'rouge/node_catalog.py', 'rouge/current_node_readers.py',
                    version.MANIFEST, current_node_readers.MANIFEST, 'rouge/data/node-events.json', 'rouge/data/original-entry-reference.json'))
    pending = list(sources); visited = set()
    while pending:
        path = pending.pop()
        if path in visited: continue
        visited.add(path)
        if not path.endswith('.json') or 'manifest' not in Path(path).name: continue
        manifest = json.loads((root / path).read_bytes())
        if type(manifest.get('files')) is not dict: raise ValueError('Unsupported upstream manifest requires explicit adapter: ' + path)
        for child in manifest['files']:
            if child not in sources: sources.add(child); pending.append(child)
    source_pins = {}
    for path in sorted(sources):
        raw = (root / path).read_bytes(); source_pins[path] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    notes = {'schema': 'current_event_directory_372_notes_v1', 'game_commit': version.NEW_COMMIT,
             'original_sources': source_pins,
             'provider_source_identities': {key: json.loads(json.dumps(m.packet()['source_identity'])) for key, m in mods.items()},
             'provider_data_files': {key: m.DATA for key, m in mods.items()},
             'version_source_identity': version.MANIFEST_SHA256,
             'coverage': {'current_event_readers': len(data['rows']), 'old_catalogue_groups_retained': len(catalogue),
                          'dialogue_choice_occurrences': sum(len(r['entries']) for r in data['rows']),
                          'classified_current_events': sum(bool(r['node_types']) for r in data['rows']),
                          'unclassified_current_events': sum(not r['node_types'] for r in data['rows'])},
             'existing_coverage': 'The old catalogue has 38 groups and individual current readers; this adds one current search/filter and exact dialogue-choice navigation. It does not add an unverified hidden event or generation rule.',
             'sources_reused': ['Current exact event provider manifests and their already downloaded fixed source receipts; no new server script claim.',
                                'Node-type grouping is the old fixed public catalogue classification, never proof of current node eligibility.'],
             'targeted_web_recheck': {'url': 'https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录',
                                     'observed_update_label': '2026-10-18',
                                     'new_html_snapshot_downloaded': False,
                                     'use': 'Only a new public lead; no newer page body replaces pinned old reader evidence.'},
             'mapping_rules': ['Keep each (reader,event_id) distinct and all dialogue-choice occurrences; same choice in different phases is separate.',
                               'Three old 三重身 picture groups share one verified current reader; all three group records stay in its metadata.',
                               'Unclassified events remain unclassified, rather than assumed to be 不期而遇.',
                               'Topics are literal wording or an existing documented battle link, not sufficient or necessary server conditions.',
                               'Missing a topic does not mean free, unconditional or impossible.'],
             'unknowns': ['Complete hidden event table, server eligibility and actual current phase.',
                          'Actual menu, grants, costs and random outcomes.'],
             'new_mechanism_added': False, 'private_or_game_data_used': False}
    blobs = {model.DATA: enc(data), model.NOTES: enc(notes)}
    old = (root / 'rouge/data/node-catalog.json').read_bytes()
    pins = {**source_pins, 'rouge/data/node-catalog.json': {'sha256': sha256(old).hexdigest(), 'bytes': len(old)},
            **{name: {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)} for name, raw in blobs.items()}}
    blobs[model.MANIFEST] = enc({'schema': 'current_event_directory_372_manifest_v1', 'game_commit': version.NEW_COMMIT, 'files': pins})
    return blobs, notes['coverage']


def main():
    p = argparse.ArgumentParser(); p.add_argument('--source-root', type=Path, default=Path.cwd())
    p.add_argument('--output-root', type=Path, default=BASE); p.add_argument('--check', action='store_true')
    args = p.parse_args(); blobs, coverage = build(args.source_root.resolve())
    for name, raw in blobs.items():
        target = args.output_root / name
        if args.check:
            if not target.is_file() or target.read_bytes() != raw: raise ValueError('Non-identical derived source: ' + name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    print(json.dumps({'passed': True, 'build_only': True, 'check': args.check, 'coverage': coverage,
                      'manifest_sha256': sha256(blobs['research/p3-current-event-directory-372/runtime-manifest.json']).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__': main()
