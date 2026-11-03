"""Verify public originals and create fresh, consumer-compatible source indexes.

This does not download, edit original bytes, rebuild historical goldens, parse OCR,
or claim the new indexes are historical download receipts. Run without --write
first; all sources are verified before any of the three authorized writes.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re

GAME_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
RESOURCE_COMMIT = 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd'
TABLE_NAMES = {'character_table', 'skill_table', 'uniequip_table',
               'battle_equip_table', 'roguelike_topic_table'}
SOURCE_PINS = {
    'rouge/data/catalog.json': '061079249952deda98d6b391f577cec7fa2c67a018599155df1ea11d2205a01b',
    'rouge/data/battle-previews.json': 'f0155647af8766eb2f01e84295f85b7300264fc49b40ffc82e89800837d274f3',
    'rouge/data/original-animation-references.json': '390deaa49bb353cface07b555c65a970b15a7ff1b58002008664e7872793ef53',
}
TARGETS = ('.cache/game-data/receipt.json',
           '.cache/research/battle-039/image-receipt.json',
           '.cache/research/timing-048/skeleton-downloads.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(root, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Source/index path escapes public root: ' + str(relative))
    target = root / p
    if any(part.is_symlink() for part in (target, *target.parents)
           if part != root.parent):
        raise ValueError('Symlink is not a pinned public original: ' + str(relative))
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Source/index path escapes public root: ' + str(relative))
    return target


def verify_bytes(root, relative, descriptor, git_blob_key=None, dimensions=False):
    raw = safe_path(root, relative).read_bytes()
    if sha(raw) != descriptor['sha256'] or len(raw) != descriptor['bytes']:
        raise ValueError('Public original SHA/size mismatch: ' + relative)
    if git_blob_key:
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if blob != descriptor[git_blob_key]:
            raise ValueError('Public original Git blob mismatch: ' + relative)
    if dimensions:
        from PIL import Image
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != 'PNG' or image.size != (descriptor['width'], descriptor['height']):
                raise ValueError('Public image dimensions/format mismatch: ' + relative)
            image.verify()
    return {'path': relative, 'sha256': sha(raw), 'bytes': len(raw)}


def build_indexes(root, checked_at_utc=None, source_pins=None):
    """Return proposed indexes plus an audit after verifying every original.

    source_pins is supplied only by isolated fixture tests; CLI always uses the
    committed fixed source hashes above, never caller-provided source metadata.
    """
    root = Path(root).resolve()
    pins = SOURCE_PINS if source_pins is None else source_pins
    documents = {}
    for relative, expected in pins.items():
        raw = safe_path(root, relative).read_bytes()
        if sha(raw) != expected:
            raise ValueError('Fixed source descriptor changed: ' + relative)
        documents[relative] = json.loads(raw)
    if set(documents) != set(SOURCE_PINS):
        raise ValueError('All three fixed public source descriptors are required')
    checked = checked_at_utc or datetime.now(timezone.utc).isoformat()
    stamp = datetime.fromisoformat(checked.replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
        raise ValueError('Fresh check date must be UTC')
    fresh = {'index_type': 'fresh_public_source_index', 'checked_at_utc': checked,
             'historical_download_recreated': False, 'historical_golden_generated': False,
             'private_samples_used': False, 'network_download_performed': False}
    catalog = documents['rouge/data/catalog.json']['source']
    if catalog['commit'] != GAME_COMMIT or set(catalog['files']) != TABLE_NAMES:
        raise ValueError('Fixed five-table source scope/commit changed')
    verified = []
    for name, descriptor in sorted(catalog['files'].items()):
        expected_url = ('https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'
                        + GAME_COMMIT + '/zh_CN/gamedata/excel/' + name + '.json')
        if descriptor['url'] != expected_url:
            raise ValueError('Table URL differs from exact pinned public source')
        verified.append(verify_bytes(root, '.cache/game-data/' + name + '.json', descriptor))
    table_index = dict(fresh, repository=catalog['repository'], commit=GAME_COMMIT,
                       files=copy.deepcopy(catalog['files']), source_descriptor_sha256=pins)
    battle = documents['rouge/data/battle-previews.json']
    if (battle['source']['game_commit'] != GAME_COMMIT or
            battle['source']['resource_commit'] != RESOURCE_COMMIT or len(battle['stages']) != 105):
        raise ValueError('Fixed battle image scope/commits changed')
    images = {}; seen_images = {}
    for sid, stage in sorted(battle['stages'].items()):
        image = stage['image']
        name = Path(image['file']).name
        if image['file'] != 'battle-maps/' + name or image['url'] != (
                'https://raw.githubusercontent.com/fexli/ArknightsResource/'
                + RESOURCE_COMMIT + '/mapreview/' + name):
            raise ValueError('Battle image URL/file differs from exact original')
        if image['file'] in seen_images and seen_images[image['file']] != image:
            raise ValueError('Same public bitmap has conflicting source descriptors')
        if image['file'] not in seen_images:
            verified.append(verify_bytes(root, 'rouge/data/' + image['file'], image,
                                         'source_blob_sha1', True))
            seen_images[image['file']] = image
        images[sid] = copy.deepcopy(image)
    image_index = dict(fresh, game_commit=GAME_COMMIT, resource_commit=RESOURCE_COMMIT,
                       images=images, source_descriptor_sha256=pins)
    animation = documents['rouge/data/original-animation-references.json']
    if animation['source_commit'] != RESOURCE_COMMIT or animation['counts']['source_skeletons'] != 64:
        raise ValueError('Fixed skeleton scope/commit changed')
    sources = {}
    for profile in animation['operators'].values():
        profile_id = profile['id']
        if not re.fullmatch(r'char_[a-zA-Z0-9_]+', profile_id):
            raise ValueError('Invalid public profile ID')
        for record in profile['records']:
            orientation = record['orientation']
            if orientation not in ('Front', 'Back'):
                raise ValueError('Invalid pinned skeleton orientation')
            source = record['source']
            expected_url = ('https://raw.githubusercontent.com/fexli/ArknightsResource/'
                            + RESOURCE_COMMIT + '/spine/' + profile_id + '/' + profile_id
                            + '/' + orientation + '/' + profile_id + '.skel')
            if source['url'] != expected_url:
                raise ValueError('Skeleton URL differs from exact profile/orientation')
            item = dict(file=profile_id + '-' + orientation + '.skel', **source)
            if source['url'] in sources and sources[source['url']] != item:
                raise ValueError('Same skeleton has conflicting source descriptors')
            sources[source['url']] = item
    if len(sources) != 64:
        raise ValueError('All exact 64 original skeletons are required')
    skeleton_index = []
    for _, item in sorted(sources.items()):
        verified.append(verify_bytes(root, '.cache/research/timing-048/' + item['file'], item, 'git_blob'))
        skeleton_index.append(dict(copy.deepcopy(item), **fresh,
                                   source_descriptor_sha256=pins['rouge/data/original-animation-references.json']))
    indexes = dict(zip(TARGETS, (table_index, image_index, skeleton_index)))
    audit = dict(fresh, fixed_source_descriptor_sha256=pins, verified_public_originals=verified,
                 counts={'tables': 5, 'battle_stage_ids': 105, 'battle_image_files': len(seen_images),
                         'unique_battle_image_sha256': len({i['sha256'] for i in seen_images.values()}),
                         'original_skeletons': 64, 'verified_original_files': len(verified)},
                 original_sources_modified=False, original_tests_or_assertions_modified=False,
                 actual_game_or_native_windows_verified=False,
                 index_sha256={p: sha(encoded(v)) for p, v in indexes.items()})
    return indexes, audit


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def create_indexes(root, indexes):
    """Create only the allowlisted absent indexes; never replace old receipts."""
    if set(indexes) != set(TARGETS):
        raise ValueError('Only the three authorized source indexes may be created')
    destinations = [(safe_path(Path(root).resolve(), p), encoded(v)) for p, v in indexes.items()]
    if any(p.exists() for p, _ in destinations):
        raise FileExistsError('Existing source indexes are preserved; use verification mode')
    created = []
    try:
        for p, raw in destinations:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as f:
                created.append(p)
                f.write(raw)
    except BaseException:
        for p in created:
            p.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--verify-existing', action='store_true')
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    if args.receipt.exists():
        raise FileExistsError('Existing audit receipt is preserved')
    date = None
    if args.verify_existing:
        date = json.loads(safe_path(args.root.resolve(), TARGETS[0]).read_bytes())['checked_at_utc']
    indexes, audit = build_indexes(args.root, date)
    if args.write:
        create_indexes(args.root, indexes)
    if args.verify_existing:
        for relative, index in indexes.items():
            if safe_path(args.root.resolve(), relative).read_bytes() != encoded(index):
                raise ValueError('Current source index differs from verified fresh source scope: ' + relative)
    audit.update(indexes_created=args.write, existing_indexes_verified=args.verify_existing,
                 verification_complete=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open('xb') as f:
        f.write(encoded(audit))
    print(json.dumps({'verification_complete': True, 'indexes_created': args.write,
                      'counts': audit['counts'], 'receipt': str(args.receipt)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
