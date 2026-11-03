"""Only parse original metadata/PE bytes; never load the target assembly."""
from pathlib import Path
import json
import struct

BASE = Path(__file__).resolve().parent
reader = BASE.parent / 'research/p2-native-current-263/read_metadata_static.py'
ns = {'__file__': str(reader)}
exec(compile(reader.read_text(encoding='utf8').split('selected=[]\n')[0], str(reader), 'exec'), ns)
parameters = ns['records']('parameters', 'Iii')
wanted = {
    'System.Type', 'System.RuntimeType', 'System.Reflection.FieldInfo',
    'System.Reflection.RuntimeFieldInfo', 'Torappu.AttributeMetaAttribute',
    'Torappu.Battle.Roguelike.RoguelikeBattleManager',
    'CodeStage.AntiCheat.ObscuredTypes.ObscuredInt',
    'CodeStage.AntiCheat.ObscuredTypes.ObscuredFloat',
}
out = []
for ti, td in enumerate(ns['types']):
    name = ns['type_def_name'](ti)
    if name not in wanted:
        continue
    fp = ns['reg']['fields'][ti]
    offsets = struct.unpack_from('<' + str(td[19]) + 'i', ns['binary'], ns['offset'](fp)) if fp and td[19] else []
    fields = [
        {'name': ns['string'](ns['fields'][fi][0]), 'index': fi,
         'type': ns['typename'](ns['fields'][fi][1]), 'offset': offsets[j] if offsets else None}
        for j, fi in enumerate(range(td[8], td[8] + td[19]))
    ]
    methods = []
    for mi in range(td[9], td[9] + td[17]):
        m = ns['methods'][mi]
        mn = ns['string'](m[0])
        if name.startswith('System.') and mn not in ['get_FieldType', 'SetValue', 'IsAssignableFrom', 'GetTypeFromHandle', 'op_Equality', 'GetValue']:
            continue
        if name.startswith('CodeStage.') and mn not in ['op_Implicit', '.ctor', 'InternalDecrypt', 'Decrypt']:
            continue
        if name.startswith('Torappu.') and mn not in ['.ctor', 'GetRange', '_ApplyFinalAttributes']:
            continue
        methods.append({
            'index': mi, 'name': mn, 'return_type': ns['typename'](m[2]),
            'slot': m[8], 'flags': hex(m[6]),
            'parameters': [
                {'name': ns['string'](x[0]), 'type': ns['typename'](x[2])}
                for x in parameters[m[3]:m[3] + m[9]]
            ],
        })
    out.append({'name': name, 'type_index': ti, 'fields': fields, 'methods': methods})
(BASE / 'routing-metadata-283.json').write_text(json.dumps(out, indent=2), encoding='utf8')
for row in out:
    print(row['name'])
    print(row['fields'] if row['name'].startswith('Torappu.') else [])
    print(*row['methods'], sep='\n')
