"""Derive six stable base-one source records from the sealed original packet."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'research/p2-relic-damage-composition-current'
OUTPUT = ROOT / 'rouge/data/relic-order-precision-source.json'
IDS = tuple('rogue_6_relic_legacy_' + str(i) for i in range(5, 11))


def build():
    receipt = json.loads((EVIDENCE / 'receipt.json').read_text(encoding='utf-8'))
    for name, expected in receipt['artifact_sha256'].items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == expected, name
    raw = json.loads((EVIDENCE / 'fixed-raw-sources.json').read_text(encoding='utf-8'))
    bindings = json.loads((EVIDENCE / 'prefab-binding.json').read_text(encoding='utf-8'))
    templates = json.loads((EVIDENCE / 'current-templates.json').read_text(encoding='utf-8'))
    names = json.loads((ROOT / 'rouge/data/relic-mechanics.json').read_text(encoding='utf-8'))['relics']
    assert raw['source_commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
    assert bindings['base_version'] == templates['base_version'] == receipt['base_version']
    records = []
    for identity in IDS:
        source = raw['selected'][identity]
        assert len(source['buffs']) == 1 and source['buffs'][0]['key'] == 'global_buff_stack_base_one'
        board = {r['key']: r for r in source['buffs'][0]['blackboard']}
        group = board['key']['valueStr']
        assert group in ('enemy_damage_scale[phy]', 'enemy_damage_scale[mag]')
        family = 'physical' if group.endswith('[phy]') else 'magic'
        prefab = next(r for r in bindings['selected'] if r['asset_path'].endswith('/' + group + '.prefab'))
        buff = next(o['data']['_buffs'][0] for o in prefab['objects'] if '_buffs' in o['data'])
        template = next(r for r in templates['selected'] if r['templateKey'] == buff['templateKey'])
        actions = json.loads(template['eventToActions']['_items'][0]['value']['SerializedState'])
        assert template['eventToActions']['_items'][0]['key'] == 10
        assert len(actions) == 1 and actions[0]['$type'] == 'Torappu.Battle.Action.Nodes+DamageScale'
        assert actions[0]['_filterDamageType'] and actions[0]['_damageMask'] == ('PHYSICAL' if family == 'physical' else 'MAGICAL')
        assert not any(actions[0][k] for k in ('_isOneMinus', '_isStackable', '_isValidStackCnt'))
        records.append({'relic_id': identity, 'name': names[identity]['name'],
            'source_buff_key': source['buffs'][0]['key'], 'prefab_group': group,
            'damage_family': family, 'damage_mask': actions[0]['_damageMask'],
            'parameter': board['damage_scale']['value'], 'template_key': buff['templateKey'],
            'raw_selector': 'selected.' + identity + '.buffs[0].blackboard.damage_scale'})
    return {'schema_version': 1, 'source_commit': raw['source_commit'],
        'original_table_sha256': raw['source_sha256'], 'native_base_version': receipt['base_version'],
        'game_dll_sha256': receipt['game_dll_sha256'], 'metadata_sha256': receipt['metadata_sha256'],
        'source_evidence': 'research/p2-relic-damage-composition-current/receipt.json',
        'records': records,
        'processing_rule': 'same exact prefabGroup only: float32(float32(old + incoming) - float32(1)); first group record is copied, not merged with implicit1',
        'runtime_acquisition_to_processing_order_verified': False,
        'runtime_binding_verified': False, 'current_hotfix_equivalence_proven': False,
        'source_artifact_sha256': {name: receipt['artifact_sha256'][name] for name in
            ('fixed-raw-sources.json', 'prefab-binding.json', 'current-templates.json', 'native-proof.json', 'selected-metadata.json')}}


if __name__ == '__main__':
    content = (json.dumps(build(), ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    OUTPUT.write_bytes(content)
    print(json.dumps({'path': str(OUTPUT.relative_to(ROOT)), 'sha256': hashlib.sha256(content).hexdigest()}))
