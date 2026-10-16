"""Targeted pure-file keyword context; no product/runtime interpretation."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
source = ROOT / '.cache/p3-287-event-research/fixed-game-topic.json'
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
data = json.loads(raw)['details']['rogue_6']
hits = []


def walk(value, path, parent):
    if isinstance(value, dict):
        for key, item in value.items():
            walk(item, path + [str(key)], value)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk(item, path + [str(index)], value)
    elif isinstance(value, str) and any(word in value for word in ('先行一步', '归来时', 'expedition', '喙')):
        hits.append({'path': path, 'value': value, 'parent': parent})


walk(data, [], None)
result = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'hits': hits,
          'keyword_matches_not_activation_script': True, 'research_only': True}
destination = HERE / 'primary-expedition-keyword-context.json'
with destination.open('x', encoding='utf8') as stream:
    stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'count': len(hits), 'output_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                  'paths_and_values': [{'path': h['path'], 'value': h['value']} for h in hits]}, ensure_ascii=False))
