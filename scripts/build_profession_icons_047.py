"""Download audited PRTS profession icons; subsequent builds use cached evidence.

This script reads pinned public game data and writes only its new resource and
research outputs. It does not inspect runtime state or operate the game.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/research/professions-047'
DATA = ROOT / 'rouge/data'
GAME_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
API = 'https://prts.wiki/api.php'
PROFESSIONS = {
    'pioneer': ('先锋', 'char_123_fang'),
    'warrior': ('近卫', 'char_208_melan'),
    'tank': ('重装', 'char_500_noirc'),
    'sniper': ('狙击', 'char_124_kroos'),
    'caster': ('术师', 'char_121_lava'),
    'medic': ('医疗', 'char_120_hibisc'),
    'support': ('辅助', 'char_278_orchid'),
    'special': ('特种', 'char_237_gravel'),
}


def digest(raw: bytes, algorithm: str = 'sha256') -> str:
    return hashlib.new(algorithm, raw).hexdigest()


def fetch(url: str) -> bytes:
    if not url.startswith(('https://prts.wiki/', 'https://media.prts.wiki/')):
        raise ValueError('Unexpected evidence or media host')
    request = Request(url, headers={
        'User-Agent': 'RougeBlackflowHelper/0.47 (public reference icon audit)',
    })
    with urlopen(request, timeout=35) as response:
        if response.status != 200:
            raise ValueError(f'HTTP {response.status}')
        return response.read()


def cached_query(filename: str, parameters: dict, refresh: bool) -> tuple[dict, str]:
    url = API + '?' + urlencode(parameters)
    target = CACHE / filename
    if refresh or not target.exists():
        raw = fetch(url)
        parsed = json.loads(raw)
        if 'error' in parsed:
            raise ValueError(parsed['error'])
        target.write_bytes(raw)
    return json.loads(target.read_text(encoding='utf-8')), url


def build(refresh: bool = False) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    assets = DATA / 'profession-icons'
    assets.mkdir(parents=True, exist_ok=True)
    game_receipt = json.loads((ROOT / '.cache/game-data/receipt.json').read_text(encoding='utf-8'))
    if game_receipt['commit'] != GAME_COMMIT:
        raise ValueError('Pinned game data commit changed; audit before rebuilding')
    character_raw = (ROOT / '.cache/game-data/character_table.json').read_bytes()
    expected = game_receipt['files']['character_table']
    if digest(character_raw) != expected['sha256'] or len(character_raw) != expected['bytes']:
        raise ValueError('Pinned character table failed integrity check')
    characters = json.loads(character_raw)
    example_names = []
    for key, (_, identity) in PROFESSIONS.items():
        example = characters[identity]
        if example['profession'] != key.upper():
            raise ValueError(f'Unexpected profession for {identity}')
        example_names.append(example['name'])

    image_evidence, image_query = cached_query('imageinfo.json', {
        'action': 'query',
        'titles': '|'.join('File:图标 职业 ' + label + '.png' for label, _ in PROFESSIONS.values()),
        'prop': 'imageinfo|revisions',
        'iiprop': 'url|size|sha1|timestamp|mime',
        'rvprop': 'ids|timestamp',
        'format': 'json', 'formatversion': '2',
    }, refresh)
    correspondence, correspondence_query = cached_query('correspondence.json', {
        'action': 'query', 'titles': '|'.join(example_names),
        'prop': 'categories|revisions', 'cllimit': 'max',
        'rvprop': 'ids|timestamp', 'format': 'json', 'formatversion': '2',
    }, refresh)
    image_pages = {p['title']: p for p in image_evidence['query']['pages']}
    character_pages = {p['title']: p for p in correspondence['query']['pages']}
    records = {}
    for key, (label, identity) in PROFESSIONS.items():
        name = characters[identity]['name']
        character_page = character_pages[name]
        if '分类:' + label + '干员' not in [c['title'] for c in character_page.get('categories', ())]:
            raise ValueError(f'Chinese profession correspondence not established for {identity}')
        page = image_pages['文件:图标 职业 ' + label + '.png']
        information = page['imageinfo'][0]
        if information['mime'] != 'image/png' or not re.fullmatch('[0-9a-f]{40}', information['sha1']):
            raise ValueError('Unexpected image format or SHA-1 representation')
        target = assets / (key + '.png')
        raw = target.read_bytes() if target.exists() else b''
        if len(raw) != information['size'] or digest(raw, 'sha1') != information['sha1']:
            raw = fetch(information['url'])
        if len(raw) != information['size'] or digest(raw, 'sha1') != information['sha1']:
            raise ValueError(f'Remote image integrity check failed: {key}')
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != 'PNG' or image.size != (information['width'], information['height']):
                raise ValueError(f'Remote image dimensions changed: {key}')
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            alpha = image.convert('RGBA').getchannel('A')
            transparency = alpha.getextrema()[0] < 255
        target.write_bytes(raw)
        character_revision = character_page['revisions'][0]
        image_revision = page['revisions'][0]
        records[key] = {
            'label': label, 'game_profession': key.upper(),
            'file': 'profession-icons/' + key + '.png',
            'url': information['url'], 'source_page': information['descriptionurl'],
            'source_page_id': page['pageid'], 'source_revision_id': image_revision['revid'],
            'source_revision_timestamp': image_revision['timestamp'],
            'image_timestamp': information['timestamp'],
            'sha1': digest(raw, 'sha1'), 'sha256': digest(raw), 'bytes': len(raw),
            'width': information['width'], 'height': information['height'],
            'transparent': transparency,
            'correspondence': {
                'operator_id': identity, 'operator_name': name,
                'game_profession': characters[identity]['profession'],
                'prts_category': '分类:' + label + '干员',
                'source_page': 'https://prts.wiki/w/' + quote(name),
                'source_revision_id': character_revision['revid'],
                'source_revision_timestamp': character_revision['timestamp'],
                'game_source': expected['url'],
            },
        }
    manifest = {
        'version': '0.47',
        'purpose': '八职业选择与干员身份展示；不参与任何数值计算',
        'copyright': '明日方舟职业图标版权归鹰角网络所有；图片来源为 PRTS Wiki 对应职业文件页。',
        'image_api': image_query, 'correspondence_api': correspondence_query,
        'game_commit': GAME_COMMIT,
        'character_table_sha256': digest(character_raw),
        'professions': records,
        'evidence': {
            'imageinfo': {'file': '.cache/research/professions-047/imageinfo.json',
                          'sha256': digest((CACHE / 'imageinfo.json').read_bytes())},
            'correspondence': {'file': '.cache/research/professions-047/correspondence.json',
                               'sha256': digest((CACHE / 'correspondence.json').read_bytes())},
        },
    }
    (DATA / 'profession-icons.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    receipt = {
        'version': '0.47', 'professions_verified': len(records),
        'image_bytes': sum(record['bytes'] for record in records.values()),
        'all_image_sha1_matched_api': True,
        'all_chinese_labels_matched_game_enum_and_prts_category': True,
        'all_png_dimensions_matched_api': True,
        'all_images_have_transparency': all(record['transparent'] for record in records.values()),
        'files': {record['file']: record['sha256'] for record in records.values()},
        'manifest_sha256': digest((DATA / 'profession-icons.json').read_bytes()),
        'unknowns': [],
        'scope': '仅职业图标与中文职业对应，不核验职业伤害机制。',
    }
    (CACHE / 'build-receipt.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-evidence', action='store_true',
                        help='Refetch PRTS evidence; normal builds reuse audited local evidence')
    arguments = parser.parse_args()
    result = build(arguments.refresh_evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
