"""Derive a complete exact-reference lookup, without evaluating spawn conditions."""
from pathlib import Path
from hashlib import sha256
import argparse, importlib.util, json, sys

BASE = Path(__file__).resolve().parents[1]
SOURCE_ROOT = BASE if (BASE / 'rouge/expansion_reference.py').is_file() else BASE.parents[1]


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def build(root):
    sys.path.insert(0, str(root))
    from rouge import current_battle_reference as battle, current_stage_directory as directory
    spec = importlib.util.spec_from_file_location('rouge.current_enemy_stage_index', BASE / 'rouge/current_enemy_stage_index.py')
    model = importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    current, stages = battle.packet(), directory.packet()
    if current is None or stages is None: raise ValueError('Current complete source chains required')
    data = model.derive(current, stages)
    rows = data['rows']
    if len(data['stages']) != 184 or len(rows) != 2060: raise ValueError('Expected fixed snapshot cardinality changed')
    if len({(r['stage_id'], r['enemy_key']) for r in rows}) != len(rows): raise ValueError('Duplicate exact identity')
    source_paths = [battle.MANIFEST, battle.PACK + '/source-inputs.json', battle.PACK + '/source-selection.json',
                    battle.PACK + '/enemy-images.json', directory.MANIFEST, directory.DATA]
    originals = {}
    for name in source_paths:
        raw = (root / name).read_bytes(); originals[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    notes = {'schema': 'current_enemy_stage_index_370_notes_v1', 'original_sources': originals,
             'coverage': {'stage_configurations': len(data['stages']), 'exact_enemy_references': len(rows),
                          'by_original_tier': {tier: sum(r['tier'] == tier for r in rows) for tier in ('NORMAL', 'ELITE', 'BOSS')},
                          'unknown_tier': sum(r['tier'] is None for r in rows),
                          'not_counted_in_original': sum(r['not_counted'] is True for r in rows),
                          'with_exact_picture_reference': sum(r['portrait'] is not None for r in rows),
                          'without_picture_reference': sum(r['portrait'] is None for r in rows)},
             'selection': 'One row per current stage_id and original enemyDbRefs index; no name or level merging.',
             'identity_rules': ['Only enabled override wrappers modify identity; disabled placeholder values do not classify an entity.',
                                'Reuse current314 exact prefab or exact id portrait references, never name or trimmed-id fallback.',
                                'UseDb=false is not an auxiliary-role classification.',
                                'notCountInTotal=true is a separately filterable documented flag, not a claim of auxiliary role.',
                                'Raw database level is technical metadata, never a player difficulty or a calculated stat panel.'],
             'preexisting_scope': 'Current317 stage-name directory, current314 per-stage exact enemy records and portraits remain unchanged. This adds cross-stage enemy-name/category lookup and exact navigation.',
             'remaining_unknowns': ['Actual spawn eligibility, random choices and actual quantities.',
                                    'All unreferenced script-spawned entities outside the original enemyDbRefs directory.',
                                    'Current server execution and final in-run stat panels.'],
             'new_mechanism_or_probability_added': False}
    blobs = {model.DATA: enc(data), model.NOTES: enc(notes)}
    manifest = {'schema': 'current_enemy_stage_index_370_manifest_v1',
                'source_identities': {'battle': current['identity'], 'stage_directory': stages['source_identity'],
                                      'version': current['version']['source_identity']},
                'files': {name: {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)} for name, raw in blobs.items()}}
    blobs[model.MANIFEST] = enc(manifest)
    return blobs, notes['coverage']


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    parser.add_argument('--output-root', type=Path, default=BASE); parser.add_argument('--check', action='store_true')
    args = parser.parse_args(); blobs, coverage = build(args.source_root.resolve())
    for name, raw in blobs.items():
        target = args.output_root / name
        if args.check:
            if not target.is_file() or target.read_bytes() != raw: raise ValueError('Non-identical derived data: ' + name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    print(json.dumps({'passed': True, 'build_only': True, 'check': args.check,
                      'coverage': coverage, 'manifest_sha256': sha256(blobs['research/p3-current-enemy-stage-index-370/runtime-manifest.json']).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__': main()
