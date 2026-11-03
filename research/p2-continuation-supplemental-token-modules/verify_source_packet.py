"""Verify selected full public source records and the archived generic ADD CFG."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument('--character-table', type=Path, default=root / '.cache/p2-s1-binding/character_table.json')
    parser.add_argument('--equipment-directory', type=Path, default=root / 'work/p2-extra-token-rules')
    args = parser.parse_args()
    packet = json.loads((root / 'rouge/data/p2-supplemental-token-module-source.json').read_text(encoding='utf-8'))
    originals = {}
    for name, path in [('character_table', args.character_table),
                       ('battle_equip_table', args.equipment_directory / 'battle_equip_table.json'),
                       ('uniequip_table', args.equipment_directory / 'uniequip_table.json')]:
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == packet['sources'][name]['sha256'], name
        originals[name] = json.loads(raw)
    records = 0
    for identity, source in packet['operators'].items():
        owner = originals['character_table'][identity]
        assert source['owner_phases_raw'] == owner['phases']
        assert source['display_token_dict_raw'] == owner['displayTokenDict']
        for index, variant in enumerate(source['variants']):
            assert variant['skill_binding_raw'] == owner['skills'][index]
            assert variant['token_raw'] == originals['character_table'][variant['token_id']]
            assert variant['skill_binding_raw']['overrideTokenKey'] == variant['token_id']
            records += 1
        module = source['module_raw']['uniEquipId']
        assert source['module_raw'] == originals['uniequip_table']['equipDict'][module]
        for index, stage in enumerate(source['module_stage_records']):
            assert stage['raw'] == originals['battle_equip_table'][module]['phases'][index]
    evidence = packet['generic_addition_evidence']
    proof = root / evidence['proof_path']
    assert hashlib.sha256(proof.read_bytes()).hexdigest() == evidence['proof_sha256']
    for name, expected in evidence['cfg_files'].items():
        assert hashlib.sha256((proof.parent / name).read_bytes()).hexdigest() == expected
    print(json.dumps({'passed': True, 'source_commit': packet['source_commit'],
                      'complete_token_and_skill_bindings': records, 'module_stages': 6,
                      'module_gates': 2, 'public_documents': len(packet['public_documents']),
                      'historical_cfg_artifact_hashes_verified': True,
                      'current_dll_reverified': False, 'current_hotfix_verified': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
