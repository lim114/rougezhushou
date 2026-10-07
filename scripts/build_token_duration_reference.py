"""Derive documented token duration parameters from hash-verified game tables."""
import argparse
import hashlib
import json
from pathlib import Path

COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
HASHES = {
    'character_table': '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
    'battle_equip_table': '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460',
    'uniequip_table': 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9',
}
OWNER = 'char_4230_mcnist'
TOKEN = 'token_10069_mcnist_mcgraf'
MODULE = 'uniequip_002_mcnist'


def build_reference(character_path, battle_equip_path, uniequip_path):
    tables = {}
    for name, path in zip(HASHES, (character_path, battle_equip_path, uniequip_path)):
        raw = Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != HASHES[name]:
            raise ValueError(name + ' does not match the pinned SHA-256')
        tables[name] = json.loads(raw)
    characters = tables['character_table']
    owners = characters[OWNER]['talents'][0]['candidates']
    bases = []
    for index, candidate in enumerate(characters[TOKEN]['talents'][0]['candidates']):
        condition = candidate['unlockCondition']
        elite = int(condition['phase'][-1])
        owner = next(c for c in owners if c['unlockCondition'] == condition)
        assert owner['tokenKey'] == TOKEN
        values = {b['key']: b['value'] for b in candidate['blackboard']}
        bases.append({'unlock_elite': elite, 'unlock_level': condition['level'],
            'required_potential_rank': candidate['requiredPotentialRank'],
            'duration_seconds': values['skill@duration'],
            'source_selector': f'character_table.{TOKEN}.talents[0].candidates[{index}]',
            'owner_source_selector': f'character_table.{OWNER}.talents[0].candidates[{owners.index(owner)}]'})
    assert [(b['unlock_elite'], b['unlock_level'], b['duration_seconds']) for b in bases] == [(1, 1, 20), (2, 1, 30)]
    equip = tables['uniequip_table']['equipDict'][MODULE]
    assert (equip['charId'], equip['unlockEvolvePhase'], equip['unlockLevel']) == (OWNER, 'PHASE_2', 60)
    overrides = []
    for phase_index, phase in enumerate(tables['battle_equip_table'][MODULE]['phases']):
        for part_index, part in enumerate(phase['parts']):
            candidates = (part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []
            for index, candidate in enumerate(candidates):
                values = {b['key']: b['value'] for b in candidate['blackboard']}
                if not part.get('isToken') or 'skill@duration' not in values:
                    continue
                assert (part['target'], part['validInMapTag'], candidate['talentIndex'],
                        candidate['unlockCondition'], values['skill@duration'], candidate['upgradeDescription']) == (
                    'TALENT_DATA_ONLY', 'rogue_6', 0, {'phase': 'PHASE_2', 'level': 60}, -1, '持续时间无限')
                overrides.append({'module_level': phase['equipLevel'], 'unlock_elite': 2,
                    'unlock_level': candidate['unlockCondition']['level'],
                    'required_potential_rank': candidate['requiredPotentialRank'],
                    'map_tag': part['validInMapTag'], 'parameter_value': values['skill@duration'],
                    'source_selector': f'battle_equip_table.{MODULE}.phases[{phase_index}].parts[{part_index}].addOrOverrideTalentDataBundle.candidates[{index}]'})
    assert [o['module_level'] for o in overrides] == [2, 3]
    return {'schema_version': 1, 'scope': 'duration_parameter_reference',
        'source_commit': COMMIT,
        'sources': {name: {'sha256': digest, 'url': f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/{name}.json'} for name, digest in HASHES.items()},
        'rules': [{'operator_id': OWNER, 'token_id': TOKEN, 'token_name': characters[TOKEN]['name'],
            'parameter_key': 'skill@duration', 'base_candidates': bases,
            'module_id': MODULE, 'module_source_selector': f'uniequip_table.equipDict.{MODULE}',
            'module_unlock_elite': 2, 'module_unlock_level': equip['unlockLevel'],
            'module_overrides': overrides}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--characters', required=True, type=Path)
    parser.add_argument('--battle-equip', required=True, type=Path)
    parser.add_argument('--uniequip', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    reference = build_reference(args.characters, args.battle_equip, args.uniequip)
    args.output.write_text(json.dumps(reference, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'rules': len(reference['rules']), 'raw_hashes_verified': True}))


if __name__ == '__main__':
    main()
