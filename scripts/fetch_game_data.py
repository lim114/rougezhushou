"""Fetch a pinned community game-data snapshot; never fetch account data."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache' / 'game-data'
REPO = 'Kengxxiao/ArknightsGameData'
FILES = ['character_table', 'skill_table', 'uniequip_table', 'battle_equip_table', 'roguelike_topic_table']

def download(url):
    with urlopen(Request(url, headers={'User-Agent': 'rouge-development'}), timeout=90) as response:
        return response.read()

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    receipt_path = CACHE / 'receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else {'repository': REPO, 'commit': json.loads(download(f'https://api.github.com/repos/{REPO}/commits/master'))['sha'], 'files': {}}
    for name in FILES:
        target = CACHE / f'{name}.json'
        source = f'https://raw.githubusercontent.com/{REPO}/{receipt["commit"]}/zh_CN/gamedata/excel/{name}.json'
        if not target.exists():
            payload = download(source)
            json.loads(payload)
            target.write_bytes(payload)
        payload = target.read_bytes()
        receipt['files'][name] = {'url': source, 'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload)}
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{name}: {len(payload)} bytes', flush=True)
    print('Pinned commit:', receipt['commit'])

if __name__ == '__main__':
    main()
