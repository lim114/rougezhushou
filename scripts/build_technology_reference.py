"""Extract topic 6 display records from the pinned original table."""
import argparse
import hashlib
import json
from pathlib import Path

COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
SHA256 = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'


def build(source):
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('主题原表与已核验固定版本不符。')
    records = json.loads(raw)['customizeData']['rogue_6']['commonDevelopment']
    return {'topic': 'rogue_6', 'source': {
        'commit': COMMIT, 'sha256': SHA256,
        'url': f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json',
        'selector': '$.customizeData.rogue_6.commonDevelopment'}, **records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parents[1]/'rouge/data/technology-reference.json')
    args = parser.parse_args()
    args.output.write_text(json.dumps(build(args.source), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
