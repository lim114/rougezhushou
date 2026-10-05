"""Read-only static evidence for Deepcolor's default simultaneous token limit.

The installed game is never executed. No process memory or private run state is
read. All generated receipts stay in this investigation directory.
"""
from pathlib import Path
import hashlib, json, mmap, runpy, struct

OUT = Path(__file__).resolve().parent
RESEARCH = OUT.parent
PROJECT = OUT.parents[2]
BASE = Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
SOURCE = 'pkgrps/btl_pfb_tokens_0.ab'
ASSET = 'dyn/battle/prefabs/[uc]tokens/token_10001_deepcl_tentac.prefab'
TOKEN = 'token_10001_deepcl_tentac'


def read_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')


def pp(x):
    if isinstance(x, dict):
        if 'm_FileID' in x and 'm_PathID' in x:
            yield x
        for v in x.values():
            yield from pp(v)
    elif isinstance(x, list):
        for v in x:
            yield from pp(v)


old = read_json(RESEARCH / 'summon-038/evidence.json')
raw_hashes = {}
for name in ['character_table.json', 'battle_equip_table.json']:
    path = PROJECT / '.cache/game-data' / name
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha == old['raw_sources_sha256']['.cache/game-data/' + name]
    raw_hashes[name] = sha
chars = read_json(PROJECT / '.cache/game-data/character_table.json')
equips = read_json(PROJECT / '.cache/game-data/battle_equip_table.json')
base_values = [phase['attributesKeyFrames'][0]['data']['maxDeployCount'] for phase in chars[TOKEN]['phases']]
assert base_values == [1, 1, 1]
talents = chars[TOKEN]['talents'][0]['candidates']
talent_add = [next(bb['value'] for bb in c['blackboard'] if bb['key'] == 'max_deploy_count') for c in talents]
assert talent_add == [1, 2, 3]
module_add = []
for phase in equips['uniequip_002_deepcl']['phases']:
    bb = {x['key']: x['value'] for x in phase['tokenAttributeBlackboard'][TOKEN]}
    assert bb == {'cost': -2, 'max_deploy_count': 3}
    module_add.append({'stage': phase['equipLevel'], 'token_blackboard': bb})

manifest = read_json(BASE / 'hot_update_list.json')
entry = next(x for x in manifest['abInfos'] if x['name'] == SOURCE)
raw = (BASE / SOURCE).read_bytes()
assert len(raw) == entry['abSize'] and len(raw) < 6_000_000
assert hashlib.md5(raw).hexdigest() == entry['md5']
reader = runpy.run_path(str(RESEARCH / 'p1-runtime-source-054/read_unity_stdlib.py'))
_, files = reader['bundle'](raw)
matches = [(name, data) for name, data in files if ASSET.encode() in data]
assert len(matches) == 1
filename, data = matches[0]
v = reader['serialized'](data)
assets = [o for o in v['objects'] if o['class_id'] == 142]
assert len(assets) == 1 and assets[0]['read_exact']
container = next(x for x in assets[0]['data']['m_Container'] if x['first'] == ASSET)
assert container['second']['asset']['m_FileID'] == 0
root_id = container['second']['asset']['m_PathID']
om = {o['path_id']: o for o in v['objects']}
todo, seen, selected = [root_id], set(), []
while todo:
    oid = todo.pop()
    if not oid or oid in seen:
        continue
    seen.add(oid)
    obj = om[oid]
    if obj['class_id'] == 49:
        # Spine binary TextAssets are irrelevant to the count mechanic. The
        # general text reader cannot decode them and they are not used here.
        selected.append({k: obj[k] for k in ['path_id', 'class_id', 'byte_start', 'byte_size', 'type_index']})
        continue
    assert obj['read_exact'], (oid, obj['class_id'])
    selected.append(obj)
    todo.extend(p['m_PathID'] for p in pp(obj.get('data', {})) if p['m_FileID'] == 0)
type_indices = {o['type_index'] for o in selected}
prefab = dict(source_name=SOURCE, source_bytes=len(raw), source_md5=entry['md5'],
              source_sha256=hashlib.sha256(raw).hexdigest(), base_version=manifest['versionId'],
              asset_path=ASSET, root_id=root_id, object_count_source=len(v['objects']), objects=selected,
              types=[{'index': i, 'class_id': t['class_id'], 'old_type_hash': t['old_type_hash'],
                      'script_id': t.get('script_id')} for i, t in enumerate(v['types']) if i in type_indices],
              external_refs=v['externals'])
save('token-group-prefabs.json', prefab)

tpk = read_json(RESEARCH / 'p1-native-runtime-054/monoscripts-public-tpk-055.json')
hash_types = {}
for src in tpk['sources']:
    for obj in src['monoscripts']:
        d = obj['data']
        h = bytes(d['m_PropertiesHash']['bytes[' + str(i) + ']'] for i in range(16)).hex()
        hash_types.setdefault(h, set()).add(d['m_Namespace'] + '.' + d['m_ClassName'])
type_map = {t['index']: t for t in prefab['types']}
buff = next(o for o in selected if o['path_id'] == 2100531260680023828)
talent = next(o for o in selected if o['path_id'] == -6104297881906401516)
assert hash_types[type_map[buff['type_index']]['old_type_hash']] == {'Torappu.Battle.Abilities.PassiveBuffAbility'}
assert hash_types[type_map[talent['type_index']]['old_type_hash']] == {'Torappu.Battle.Talent'}
assert buff['data']['m_GameObject'] == talent['data']['m_GameObject']
game_object = om[buff['data']['m_GameObject']['m_PathID']]
assert game_object['data']['m_Name'] == '1'
assert talent['data']['_attachInDummy'] == 1
assert buff['data']['_attachPassiveBuffsOnDummy'] == 1
assert buff['data']['_selector']['m_PathID'] == 0
buffdata = buff['data']['_buffs'][0]
assert buffdata['buffKey'] == 'tentac_t_1' and buffdata['templateKey'] == 'empty'
assert buffdata['maxStackCnt'] == 1 and buffdata['disableOverride'] == 1
assert buffdata['attributes']['attributeModifiers'] == [
    {'attributeType': 16, 'formulaItem': 0, 'value': 0.0, 'loadFromBlackboard': 1, 'fetchBaseValueFromSourceEntity': 0}]

# Read native field offsets/vtables from the current source metadata. Running
# only the original reader's definition prefix does not rewrite its receipts.
meta_script = RESEARCH / 'p1-native-runtime-054/read_metadata_static.py'
scope = {'__file__': str(meta_script)}
exec(meta_script.read_text(encoding='utf8').split('selected=[]\n')[0], scope)
targets = {'Torappu.Battle.Deck+TokenCard', 'Torappu.Battle.Deck+Card', 'Torappu.AttributeType',
           'Torappu.AttributeModifierData+AttributeModifier+FormulaItemType',
           'Torappu.BattleEquipPerLevelPack', 'Torappu.AttributesCalculator+Input',
           'Torappu.Battle.BattleCharacterData'}
metadata = []
for ti, td in enumerate(scope['types']):
    name = scope['type_def_name'](ti)
    if name not in targets:
        continue
    fp = scope['reg']['fields'][ti]
    offsets = struct.unpack_from('<' + str(td[18]) + 'i', scope['binary'], scope['offset'](fp)) if fp else [0] * td[18]
    fs = []
    for i, fi in enumerate(range(td[8], td[8] + td[18])):
        f = scope['fields'][fi]
        fs.append({'name': scope['string'](f[0]), 'type': scope['typename'](f[1]),
                   'offset': offsets[i], 'default': scope['default_value'](fi)})
    vs = []
    for slot in range(td[21]):
        encoded = scope['vtable'][td[14] + slot][0]
        kind, idx = encoded >> 29, (encoded & 0x1ffffffe) >> 1
        if kind == 3 and idx < len(scope['methods']):
            m = scope['methods'][idx]
            vs.append({'slot': slot, 'method': scope['type_def_name'](m[1]) + '$$' + scope['string'](m[0])})
    metadata.append({'name': name, 'metadata_type_index': ti, 'fields': fs, 'vtable': vs})
save('verified-native-fields.json', metadata)
by_type = {t['name']: t for t in metadata}
field = lambda t, n: next(f for f in by_type[t]['fields'] if f['name'] == n)
assert field('Torappu.AttributeType', 'MAX_DEPLOY_COUNT')['default']['value'] == 16
assert field('Torappu.AttributeModifierData+AttributeModifier+FormulaItemType', 'ADDITION')['default']['value'] == 0
assert field('Torappu.Battle.Deck+TokenCard', 'm_spawnedCnt')['offset'] == 0x1d0
assert field('Torappu.Battle.Deck+TokenCard', '<maxDeployCnt>k__BackingField')['offset'] == 0x1e4
assert field('Torappu.Battle.Deck+TokenCard', '<maxDeckStackCnt>k__BackingField')['offset'] == 0x1f8
assert field('Torappu.BattleEquipPerLevelPack', 'tokenAttributeBlackboard')['offset'] == 0x28
assert next(x for x in by_type['Torappu.Battle.Deck+TokenCard']['vtable'] if x['slot'] == 18)['method'].endswith('TokenCard$$get_isMaxDeployed')

cfg_names = ['token-limit-cfg.json', 'token-live-count-cfg.json', 'token-default-cfg.json',
             'token-data-cfg.json', 'convert-internal-cfg.json', 'token-attributes-cfg.json', 'equip-addition-cfg.json']
native = []
dll_sha, meta_sha = hashlib.sha256(scope['binary']).hexdigest(), hashlib.sha256(scope['meta']).hexdigest()
for name in cfg_names:
    cfg = read_json(OUT / name)
    assert cfg['dll_sha256'] == dll_sha and cfg['metadata_sha256'] == meta_sha
    assert cfg['file_only'] and not cfg['game_dll_executed'] and not cfg['process_memory_read']
    for m in cfg['methods']:
        assert m['cfg_bounded_traversal_finished'] and not m['limits']
        for ins in m['instructions']:
            rawins = bytes.fromhex(ins['bytes']); pos = int(ins['physical_offset'], 16)
            assert scope['binary'][pos:pos + len(rawins)] == rawins
        native.append({'name': m['method']['Name'], 'address': hex(m['method']['Address']),
                       'instructions': m['instruction_count'], 'cfg_source': name,
                       'reachable_bytes_sha256': m['reachable_bytes_sha256']})
save('native-proof.json', {'passed': True, 'source_commit': old['source_commit'],
                         'base_version': manifest['versionId'], 'game_dll_sha256': dll_sha,
                         'metadata_sha256': meta_sha, 'raw_sources_sha256': raw_hashes,
                         'token_bundle_sha256': prefab['source_sha256'], 'module_token_attributes': module_add,
                         'base_max_deploy_counts': base_values, 'hidden_talent_additions': talent_add,
                         'default_limits_without_module': [int(a + b) for a, b in zip(base_values, talent_add)],
                         'default_e2_limit_with_unlocked_SUM_Y': 7,
                         'selected_prefab_objects': len(selected), 'verified_methods': native,
                         'instruction_count': sum(m['instructions'] for m in native),
                         'current_hotfix_equivalence_proven': False, 'live_measurement': False,
                         'game_dll_executed': False, 'process_memory_read': False, 'private_files_read': False,
                         'scope': 'compiled base defaults; global placement availability and other max-deploy modifiers are separate'})
print(json.dumps({'passed': True, 'native_methods': len(native), 'instructions': sum(m['instructions'] for m in native),
                  'unmodified_limits': [2, 3, 4], 'e2_SUM_Y_limit': 7}, ensure_ascii=False))
