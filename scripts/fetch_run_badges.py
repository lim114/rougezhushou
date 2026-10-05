"""Download publicly documented squad reference icons with provenance hashes."""
import concurrent.futures
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'https://prts.wiki/w/沉沦者的黑流树海'


def get(url):
    with urllib.request.urlopen(urllib.request.Request(
            urllib.parse.quote(url, safe=':/?=&%'), headers={'User-Agent': 'rouge-run-badge-references'}),
            timeout=30) as response:
        return response.read()


def main():
    cached = ROOT / '.cache/run-badge-page.html'
    page = cached.read_bytes() if cached.exists() else get(PAGE)
    text = page.decode('utf-8')
    data_path = ROOT / 'rouge/data/run-config.json'
    data = json.loads(data_path.read_text(encoding='utf-8'))
    folder = ROOT / 'rouge/data/run-badges'
    folder.mkdir(exist_ok=True)
    mapping = []
    for key, squad in data['squads'].items():
        matches = set()
        for row in re.findall(r'<td[^>]*>(.*?)</td>', text, re.S):
            label = html.unescape(re.sub('<[^>]*>', '', row)).strip()
            if not label.endswith(squad['name']):
                continue
            images = re.findall(r'<img[^>]*src="([^"]+)"', row)
            if images:
                src = html.unescape(images[-1]).split('?')[0]
                original = re.sub(r'/thumb(/[^/]+/[^/]+/[^/]+)\/[^/]+$', r'\1', src)
                matches.add(original)
        if len(matches) != 1:
            raise ValueError(f'Ambiguous documented image for {squad["name"]}: {matches}')
        mapping.append({'id': key, 'normal_id': squad['normalBandId'], 'name': squad['name'],
                        'documentation_image': next(iter(matches)),
                        'url': f'https://static.closure.wiki/v3/rogueliketopic/rogue_6/initreliciconpic/{squad["iconId"]}.webp',
                        'file': f'run-badges/{key}.webp'})

    def download(record):
        payload = get(record['url'])
        if not (payload.startswith(b'RIFF') and payload[8:12] == b'WEBP'):
            raise ValueError('Reference is not a WebP')
        (ROOT / 'rouge/data' / record['file']).write_bytes(payload)
        return {**record, 'sha256': hashlib.sha256(payload).hexdigest()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(download, mapping))
    receipt = {'source_page': PAGE, 'source_page_sha256': hashlib.sha256(page).hexdigest(),
               'image_mapping_page': 'https://closure.wiki/integrated-strategies-7',
               'game_mapping_sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
               'icons': records,
               'stage_policy': 'One documented image is used for each squad type; image alone does not verify upgrade effects.',
               'notice': 'Game artwork belongs to Hypergryph. Research/testing references; see licenses/GAME-ICON-NOTICE.md.'}
    (ROOT / 'rouge/data/run-badge-receipt.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(records)} squad icons downloaded and hashed')


if __name__ == '__main__':
    main()
