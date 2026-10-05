"""Extract field offsets and profession constants from files, never game memory."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
reader = OUT.parent / 'p1-native-runtime-054/read_metadata_static.py'
scope = {'__file__': str(reader)}
exec(compile(reader.read_text(encoding='utf-8').split('selected=[]\n')[0], str(reader), 'exec'), scope)
result = {}
for ti, td in enumerate(scope['types']):
    name = scope['type_def_name'](ti)
    if name not in ('Torappu.Battle.TargetOptions', 'Torappu.ProfessionCategory'):
        continue
    pointer = scope['reg']['fields'][ti]
    offsets = scope['struct'].unpack_from('<' + str(td[18]) + 'i', scope['binary'], scope['offset'](pointer))
    result[name] = [{'field': scope['string'](scope['fields'][fi][0]),
                     'offset': offsets[j], 'default': scope['default_value'](fi)}
                    for j, fi in enumerate(range(td[8], td[8] + td[18]))]
path = OUT / 'target-metadata.json'
if path.exists():
    assert json.loads(path.read_bytes()) == result
else:
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'metadata_matches': True, 'selected_types': len(result)}))
