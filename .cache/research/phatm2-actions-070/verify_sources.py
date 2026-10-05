"""Seal the ordinary S1 action dispatch chain without executing game code."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    cfgs = [OUT / (name + '.json') for name in ('action-entry', 'run-actions', 'apply-actions')]
    first = read(cfgs[0]); dll = Path(first['source_game_dll'])
    meta = dll.parent / 'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    dh, mh = sha(dll), sha(meta)
    methods = []; count = 0
    with dll.open('rb') as stream:
        for path in cfgs:
            cfg = read(path)
            assert cfg['dll_sha256'] == dh and cfg['metadata_sha256'] == mh
            for method in cfg['methods']:
                assert method['cfg_bounded_traversal_finished'] and not method['limits']
                methods.append(method)
                for ins in method['instructions']:
                    data = bytes.fromhex(ins['bytes'])
                    stream.seek(int(ins['physical_offset'], 16))
                    assert stream.read(len(data)) == data
                    count += 1
    assert len(methods) == 8 and count == 1330, (len(methods), count)
    instruction = {ins['address']: ins for m in methods for ins in m['instructions']}
    for address, target in (
            ('0x180e909cd', '0x1805e2a90'),
            ('0x181155aae', '0x181155c10'),
            ('0x181155d51', '0x1811550d0'),
            ('0x181155d71', '0x180043e50')):
        assert instruction[address]['mnemonic'] == 'call'
        assert instruction[address]['operands'] == target
    config = read(ROOT / '.cache/research/phatm2-s1-069/skill-prefabs.json')
    actual = next(o for o in config['selected_prefabs'][0]['objects']
                  if o['path_id'] == 1442620349020702503)['data']
    assert actual['_splitDamage'] == 0
    paths = [*cfgs, Path(__file__), OUT / 'REPORT.md',
             ROOT / '.cache/research/phatm2-s1-069/skill-prefabs.json']
    proof = {'passed': True, 'native_methods_verified': len(methods),
             'native_instructions_verified': count, 'dll_sha256': dh,
             'metadata_sha256': mh,
             'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
             'ordinary_split_damage_false_dispatch_verified': True,
             'action_utility_iteration_is_synchronous': True,
             'current_hotfix_equivalence_proven': False, 'game_actions': 0,
             'process_memory_read': False, 'private_state_read': False}
    (OUT / 'proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in proof.items() if k != 'source_sha256'}))


if __name__ == '__main__':
    main()
