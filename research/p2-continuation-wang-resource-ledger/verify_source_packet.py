"""Re-read public original tables; never read runtime or private state."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument('--original-directory', type=Path, default=root / '.cache' / 'p2-s1-binding')
    args = parser.parse_args()
    packet = json.loads((root / 'rouge' / 'data' / 'p2-wang-resource-source.json').read_text(encoding='utf-8'))
    originals = {}
    for name, info in packet['sources'].items():
        raw = (args.original_directory / (name + '.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest() != info['sha256']:
            raise AssertionError(name + '原始字节与固定提交回执不一致。')
        originals[name] = json.loads(raw)
    operator = originals['character_table'][packet['operator_id']]
    for index, selected in enumerate(packet['talent_candidates']):
        assert selected['raw'] == operator['talents'][0]['candidates'][index]
    count = 0
    for index, selected in enumerate(packet['skills']):
        assert selected['binding_raw'] == operator['skills'][index]
        for rank, selected_level in enumerate(selected['levels']):
            assert selected_level['raw'] == originals['skill_table'][selected['skill_id']]['levels'][rank]
            count += 1
    print(json.dumps({'source_commit': packet['source_commit'], 'primary_byte_hashes_verified': True,
                      'talent_candidates_rechecked': len(packet['talent_candidates']),
                      'skill_levels_rechecked': count,
                      'prts_selected_revision': packet['separate_entity_evidence']['revision_id'],
                      'prts_live_requeried': False, 'current_hotfix_verified': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
