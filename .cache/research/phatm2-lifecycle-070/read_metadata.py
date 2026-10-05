"""Read native lifecycle metadata from original files without executing game code."""
from pathlib import Path
import hashlib, json, struct

OUT = Path(__file__).resolve().parent
RESEARCH = OUT.parent
reader = RESEARCH / 'p1-native-runtime-054/read_metadata_static.py'
s = {'__file__': str(reader), '__name__': '_file_metadata'}
exec(compile(reader.read_text(encoding='utf-8').split('selected=[]\n')[0], str(reader), 'exec'), s)
mapping = json.loads((RESEARCH / 'p1-native-mapping-054/script.json').read_text(encoding='utf-8'))['ScriptMethod']
by_index = {m['metadata_method_index']: m for m in mapping}
params = s['records']('parameters', 'IIi')
wanted = {
    'Torappu.Battle.Ability', 'Torappu.Battle.AbilityStandard',
    'Torappu.Battle.BasicSkill', 'Torappu.Battle.NextAttackOrCombatSkill',
    'Torappu.Battle.ReplacementSkill', 'Torappu.Battle.ReplacementSkillFixed',
    'Torappu.Battle.Abilities.EasyToStartAbility',
    'Torappu.Battle.Abilities.AbstractAnimatedAbility',
    'Torappu.Battle.Abilities.AbstractBasicAttack',
    'Torappu.Battle.Abilities.MultiMeleeAttack',
    'Torappu.Battle.Character', 'Torappu.Battle.AbilityStandard+<_DoCast>d__85',
    'Torappu.AbnormalFlag', 'Torappu.PeriodicTimer',
    'Torappu.Battle.AbilityStandard+Event', 'Torappu.Battle.Entity+Event',
    'Torappu.Battle.Character+States+AttackState',
    'Torappu.Battle.AsyncUtil+<WaitForFixedSeconds>d__5',
}
selected = []
for ti, td in enumerate(s['types']):
    name = s['type_def_name'](ti)
    enum = bool(td[24] & 2)
    keep = name in wanted or name.startswith('Torappu.Battle.Abilities.EasyToStartAbility+') or (
        enum and any(x in name for x in ['AbilityEvent', 'FinishReason', 'ResetCooldown', 'StandardEvent']))
    if not keep:
        continue
    fp = s['reg']['fields'][ti]
    offsets = struct.unpack_from('<' + str(td[18]) + 'i', s['binary'], s['offset'](fp)) if fp and td[18] else []
    fields = [{'name': s['string'](s['fields'][fi][0]), 'type': s['typename'](s['fields'][fi][1]),
               'offset': offsets[j] if offsets else None, 'default': s['default_value'](fi)}
              for j, fi in enumerate(range(td[8], td[8] + td[18]))]
    methods = []
    for mi in range(td[9], td[9] + td[16]):
        m = s['methods'][mi]
        row = {'name': name + '$$' + s['string'](m[0]), 'metadata_method_index': mi,
               'token': hex(m[5]), 'slot': m[8], 'return_type': s['typename'](m[2]),
               'parameters': [{'name': s['string'](params[pi][0]), 'type': s['typename'](params[pi][2])}
                              for pi in range(m[3], m[3] + m[9])]}
        if mi in by_index:
            row['address'] = hex(by_index[mi]['Address'])
        methods.append(row)
    slots = []
    for slot in range(td[21]):
        encoded = s['vtable'][td[14] + slot][0]
        kind, index = encoded >> 29, (encoded & 0x1ffffffe) >> 1
        row = {'slot': slot, 'usage_type': kind, 'decoded_index': index}
        if kind == 3:
            m = s['methods'][index]
            row['method'] = s['type_def_name'](m[1]) + '$$' + s['string'](m[0])
        slots.append(row)
    selected.append({'name': name, 'type_index': ti, 'enum': enum, 'fields': fields,
                     'methods': methods, 'vtable': slots})
assert wanted <= {row['name'] for row in selected}
out = {'source_game_dll_sha256': hashlib.sha256(s['binary']).hexdigest(),
       'source_metadata_sha256': hashlib.sha256(s['meta']).hexdigest(),
       'selected': selected, 'dll_executed': False, 'process_memory_read': False}
(OUT / 'lifecycle-metadata.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'metadata_types': len(selected), 'game_code_executed': False}))
