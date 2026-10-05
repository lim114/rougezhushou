"""Verify positive natural-SP sources and the medical-only prefab selector."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / '.cache/research/sp-attributes-066'
BASE = Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def component(bundle, name):
    prefab = next(p for p in bundle['selected_prefabs'] if p['asset_path'].endswith('/' + name + '.prefab'))
    rows = [o['data'] for o in prefab['objects'] if o['class_id'] == 114]
    assert len(rows) == 1
    return rows[0]


def main():
    paths = [DIR / name for name in ('globals-prefabs.json', 'abilities-prefabs.json',
        'global-selector-cfg.json', 'sp-application-cfg.json', 'sp-helpers-cfg.json',
        'target-metadata.json', 'read_target_metadata.py', 'read_globals.py', 'read_abilities.py')]
    paths += [ROOT / name for name in (
        '.cache/research/attribute-boundaries-065/native-proof.json',
        '.cache/research/p1-native-runtime-054/metadata-native-fields.json',
        '.cache/research/p1-native-runtime-054/read_metadata_static.py',
        '.cache/research/p1-native-runtime-054/blackboard-timers.json',
        '.cache/research/p1-native-runtime-054/relic-integration-summary.json',
        '.cache/research/p1-runtime-source-054/read_unity_stdlib.py',
        '.cache/research/p1-native-cost-054/extract_cfg.py',
        '.cache/game-data/roguelike_topic_table.json',
        'scripts/build_relic_mechanics.py', 'rouge/data/relic-mechanics.json')]
    paths.append(Path(__file__))
    previous = read(paths[9])
    assert previous['passed']
    for source, digest in previous['source_sha256'].items():
        assert sha(ROOT / source) == digest, source
    globals_, abilities = [read(DIR / name) for name in ('globals-prefabs.json','abilities-prefabs.json')]
    manifest = read(BASE / 'hot_update_list.json')
    for bundle in (globals_, abilities):
        raw = (BASE / bundle['source_name']).read_bytes()
        entry = next(x for x in manifest['abInfos'] if x['name'] == bundle['source_name'])
        assert manifest['versionId'] == bundle['base_version'] == '26-08-16-14-00-43_415873'
        assert len(raw) == bundle['source_bytes'] == entry['abSize']
        assert hashlib.md5(raw).hexdigest() == bundle['source_md5'] == entry['md5']
        assert hashlib.sha256(raw).hexdigest() == bundle['source_sha256']
        assert all(s['object_count'] == s['read_exact_count'] for s in bundle['parse_stats'])
    medic = component(globals_, 'modify_sp_recover[medic]')
    normal = component(globals_, 'modify_sp_recover[normal]')
    cookie = component(abilities, 'rogue_6_sp_recover')
    assert medic['_options']['enableAdvancedOptions'] == 1 and medic['_options']['professionMask'] == 8
    assert normal['_options']['enableAdvancedOptions'] == 0
    for source in (medic, normal, cookie):
        buff = source['_buffs'][0]
        assert len(source['_buffs']) == 1 and buff['templateKey'] == 'empty'
        assert buff['lifeTimeType'] == 2
        assert buff['attributes']['attributeModifiers'] == [{'attributeType':14, 'formulaItem':0,
            'value':0.0, 'loadFromBlackboard':1, 'fetchBaseValueFromSourceEntity':0}]
    assert medic['_buffs'][0]['disableOverride'] == cookie['_buffs'][0]['disableOverride'] == 1
    assert normal['_buffs'][0]['disableOverride'] == 0
    metadata = read(DIR / 'target-metadata.json')
    assert next(f['default']['value'] for f in metadata['Torappu.ProfessionCategory'] if f['field']=='MEDIC') == 8
    assert next(f['offset'] for f in metadata['Torappu.Battle.TargetOptions'] if f['field']=='professionMask') == 48
    fields = read(ROOT / '.cache/research/p1-native-runtime-054/metadata-native-fields.json')
    formula = next(t for t in fields['selected'] if t['name']=='Torappu.AttributeModifierData+AttributeModifier+FormulaItemType')
    assert next(f['default']['value'] for f in formula['fields'] if f['name']=='ADDITION') == 0
    cfgs = [read(DIR / name) for name in ('global-selector-cfg.json','sp-application-cfg.json','sp-helpers-cfg.json')]
    dll = Path(cfgs[0]['source_game_dll'])
    meta = dll.parent / 'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    dll_hash, meta_hash = sha(dll), sha(meta)
    methods = []
    for cfg in cfgs:
        assert cfg['dll_sha256'] == previous['dll_sha256'] == dll_hash
        assert cfg['metadata_sha256'] == previous['metadata_sha256'] == meta_hash
        methods.extend(cfg['methods'])
    with dll.open('rb') as stream:
        for method in methods:
            assert method['cfg_bounded_traversal_finished'] and not method['limits']
            for row in method['instructions']:
                stream.seek(int(row['physical_offset'],16))
                assert stream.read(len(bytes.fromhex(row['bytes']))).hex() == row['bytes']
    instructions = {x['address']:x for m in methods for x in m['instructions']}
    checks = {'0x1809e5653':('mov','edi, dword ptr [rbx + 0x20]'),
              '0x1809e566a':('mov','edx, dword ptr [rax + 0x70]'),
              '0x1809e5675':('call','0x180acf230'),
              '0x180acf295':('and','ebx, edi'), '0x180acf297':('cmp','ebx, edi'),
              '0x180acf299':('sete','al'), '0x180cf6c41':('call','0x18230e2c0')}
    for addr, expected in checks.items():
        assert (instructions[addr]['mnemonic'],instructions[addr]['operands']) == expected
    topic = ROOT / '.cache/game-data/roguelike_topic_table.json'
    assert sha(topic) == 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
    data = read(topic)['details']['rogue_6']
    inventory = []
    for group in ('relics','charBuffData'):
        for rid, relic in data[group].items():
            for buff in relic['buffs']:
                board = {x['key']:x['valueStr'] if x.get('valueStr') is not None else x['value'] for x in buff['blackboard']}
                if any('sp_recover' in key for key in board):
                    inventory.append({'id':rid,'source_group':group,'key':buff['key'],'blackboard':board})
    expected = {'rogue_6_relic_legacy_2':.2, 'rogue_6_relic_legacy_3':.35,
                'rogue_6_relic_legacy_4':.5, 'rogue_6_relic_legacy_74':.3, 'rogue_6_from_relic_15':.8}
    assert len(inventory) == 6
    for rid, value in expected.items():
        row = next(x for x in inventory if x['id']==rid)
        assert row['blackboard']['sp_recovery_per_sec'] == value
    assert {x['id'] for x in inventory} == set(expected) | {'rogue_6_relic_fight_15'}
    path = 'rouge/data/relic-mechanics.json'
    old = read(ROOT / '.cache/batch-066-before' / path)
    current = read(ROOT / path)
    assert old['relics']['rogue_6_relic_legacy_74']['effects'][0]['profession'] == ''
    old['relics']['rogue_6_relic_legacy_74']['effects'][0]['profession'] = 'medic'
    assert old == current, 'Only the verified medical selector may change in production data.'
    assert (DIR / 'generated-final-mechanics.json').read_bytes() == (ROOT / path).read_bytes()
    result = {'passed':True, 'dll_sha256':dll_hash,'metadata_sha256':meta_hash,
        'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        'methods_checked':len(methods), 'instructions_checked':sum(m['instruction_count'] for m in methods),
        'natural_sp_inventory':inventory, 'active_additive_sources_checked':5,
        'medical_profession_mask':8, 'medical_selector_corrected':True,
        'only_production_data_change':'relics/rogue_6_relic_legacy_74/effects/0/profession',
        'combat_hp_source_reference_only':True, 'generic_sp_ratio_or_negative_implementation_added':False,
        'current_hotfix_equivalence_proven':False, 'new_live_panel_acceptance':False,
        'file_only':True,'dll_executed':False,'process_memory_read':False}
    (DIR / 'native-proof.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','natural_sp_inventory')}))


if __name__ == '__main__': main()
