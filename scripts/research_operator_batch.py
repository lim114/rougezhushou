"""Read public reference pages, preserving URL, timestamp and digest. No login."""
import concurrent.futures
import gzip
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '.cache' / 'research' / 'mechanics'
DEST.mkdir(parents=True, exist_ok=True)
chars = json.loads((ROOT / '.cache/game-data/character_table.json').read_text(encoding='utf-8'))
chars.update(json.loads((ROOT / '.cache/game-data/char_patch_table.json').read_text(encoding='utf-8'))['patchChars'])
ids = ['char_1052_kalts2', 'char_1045_svash2', 'char_4230_mcnist', 'char_151_myrtle',
       'char_4228_closur', 'char_1050_chen3', 'char_4182_oblvns', 'char_002_amiya',
       'char_196_sunbr', 'char_1044_hsgma2', 'char_2025_shu', 'char_1035_wisdel',
       'char_1048_orchd2', 'char_133_mm', 'char_1046_sbell2', 'char_328_cammou',
       'char_1038_whitw2', 'char_298_susuro', 'char_1042_phatm2', 'char_4202_haruka',
       'char_110_deepcl', 'char_2027_wang', 'char_1041_angel2', 'char_1029_yato2',
       'char_4087_ines', 'char_206_gnosis', 'char_4107_vrdant', 'char_1015_aglna2',
       'char_4204_mantra', 'char_437_mizuki']

def fetch(cid):
    name = chars[cid]['name']
    url = 'https://prts.wiki/w/' + urllib.parse.quote(name)
    target = DEST / (cid + '.html')
    try:
        if not target.exists():
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
            data = urllib.request.urlopen(request, timeout=20).read()
            if data[:2] == b'\x1f\x8b':
                data = gzip.decompress(data)
            target.write_bytes(data)
        return {'id': cid, 'name': name, 'url': url, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'status': 'downloaded'}
    except Exception as exc:
        return {'id': cid, 'name': name, 'url': url, 'status': 'failed', 'error': str(exc)}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        entries = list(executor.map(fetch, ids))
    receipt = {'retrieved_at': time.time(), 'sources': entries}
    (DEST / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'downloaded': sum(e['status'] == 'downloaded' for e in entries), 'failed': [e['name'] for e in entries if e['status'] != 'downloaded']}, ensure_ascii=False))
