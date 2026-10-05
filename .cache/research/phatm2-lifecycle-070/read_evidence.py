"""Reproduce lifecycle CFGs on request and verify every instruction against original PE.

Only this research directory is written. GameAssembly.dll is read as bytes, never
loaded, executed, or attached to a process. No runtime/private state is inspected.
"""
from pathlib import Path
import argparse, hashlib, json, runpy, subprocess, sys

OUT = Path(__file__).resolve().parent
RESEARCH = OUT.parent
p = argparse.ArgumentParser()
p.add_argument('--extract', action='store_true')
args = p.parse_args()
manifest = json.loads((OUT / 'reproduction-manifest.json').read_text(encoding='utf-8'))
if args.extract:
    tool = RESEARCH / 'p1-native-cost-054/extract_cfg.py'
    for row in manifest['cfgs']:
        command = [sys.executable, str(tool), '--output', '../phatm2-lifecycle-070/' + row['stem']]
        for method in row['methods']:
            command.extend(['--address', method['address']])
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
runpy.run_path(str(OUT / 'read_metadata.py'))
metadata = json.loads((OUT / 'lifecycle-metadata.json').read_text(encoding='utf-8'))
game = Path('D:/Hypergryph Launcher/games/Arknights/GameAssembly.dll').read_bytes()
assert hashlib.sha256(game).hexdigest() == metadata['source_game_dll_sha256'] == '6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce'
proof = []
for row in manifest['cfgs']:
    data = json.loads((OUT / (row['stem'] + '.json')).read_text(encoding='utf-8'))
    for method in data['methods']:
        assert method['cfg_bounded_traversal_finished'] and not method['limits']
        for ins in method['instructions']:
            off = int(ins['physical_offset'], 16)
            actual = bytes.fromhex(ins['bytes'])
            assert game[off:off + len(actual)] == actual, ins['address']
        entry = next(m for m in row['methods'] if int(m['address'], 16) == method['method']['Address'])
        proof.append({'cfg': row['stem'] + '.json', 'method': entry['name'], 'address': entry['address'],
                      'instructions': method['instruction_count'],
                      'reachable_bytes_sha256': method['reachable_bytes_sha256'], 'complete': True})
old = RESEARCH / 'phatm2-s1-069'
reused = ['skill-prefabs.json', 'reproduced-metadata.json', 'scale-cast-cfg.json',
          'skill-end-cfg.json', 'multi-cfg.json', 'wait-cfg.json']
references = []
for name in reused:
    raw = (old / name).read_bytes()
    data = json.loads(raw)
    references.append({'file': '../phatm2-s1-069/' + name, 'sha256': hashlib.sha256(raw).hexdigest()})
    for method in data.get('methods', []):
        assert method['cfg_bounded_traversal_finished'] and not method['limits']
        for ins in method['instructions']:
            off = int(ins['physical_offset'], 16)
            actual = bytes.fromhex(ins['bytes'])
            assert game[off:off + len(actual)] == actual
prefabs = json.loads((old / 'skill-prefabs.json').read_text(encoding='utf-8'))
prefab = next(row for row in prefabs['selected_prefabs'] if row['asset_path'].endswith('/skchr_phatm2_1.prefab'))
objects = {o['path_id']: o for o in prefab['objects']}
skill = objects[-7067969616294705369]['data']
attack = objects[1442620349020702503]['data']
for name in ['_allowSpRecoveryWhenAffecting', '_earlySkillFinishAtAttackFinished', '_useEscapeTime']:
    assert skill[name] == 0
assert attack['_resetCdStrategy'] == 1 and attack['_minPostDelay'] == 0
selected = {row['name']: row for row in metadata['selected']}
def slot(typename, index):
    return next(row['method'] for row in selected[typename]['vtable'] if row['slot'] == index)
assert slot('Torappu.Battle.ReplacementSkillFixed', 79) == 'Torappu.Battle.ReplacementSkill$$OnCastFinish'
assert slot('Torappu.Battle.ReplacementSkillFixed', 68) == 'Torappu.Battle.NextAttackOrCombatSkill$$OnAfterAttack'
assert slot('Torappu.Battle.Abilities.MultiMeleeAttack', 53) == 'Torappu.Battle.Abilities.MultiMeleeAttack$$OnCastEnd'
assert slot('Torappu.Battle.Abilities.MultiMeleeAttack', 43) == 'Torappu.Battle.AbilityStandard$$CleanupForNextCast'
assert slot('Torappu.Battle.Abilities.MultiMeleeAttack', 79) == 'Torappu.Battle.Abilities.EasyToStartAbility$$OnWaitForPostDelay'
assert slot('Torappu.Battle.ReplacementSkillFixed', 85) == 'Torappu.Battle.ReplacementSkill$$CancelAfterAttack'
assert slot('Torappu.Battle.ReplacementSkillFixed', 78) == 'Torappu.Battle.BasicSkill$$UpdateSpRecovery'
assert slot('Torappu.Battle.BasicSkill', 43) == 'Torappu.Battle.BasicSkill$$get_isUsedUp'

all_methods = {}
for row in manifest['cfgs']:
    for method in json.loads((OUT / (row['stem'] + '.json')).read_text(encoding='utf-8'))['methods']:
        all_methods[method['method']['Address']] = method
def require_instruction(method, at, mnemonic, operands):
    ins = next(i for i in all_methods[method]['instructions'] if int(i['address'], 16) == at)
    assert (ins['mnemonic'], ins['operands']) == (mnemonic, operands), ins

# Verify the actual override chain; MultiMeleeAttack is not directly EasyToStartAbility.
require_instruction(0x180e912a0, 0x180e912ea, 'call', '0x180e7b8d0')
require_instruction(0x180e7b8d0, 0x180e7b931, 'jmp', '0x180ec7dc0')
require_instruction(0x180ec7dc0, 0x180ec7e41, 'call', '0x180ed3620')
# FinishIfNot: cleanup, OnCastEnd, constant finish callback, then once callback.
require_instruction(0x1805e9020, 0x1805e90ef, 'call', 'rax')
require_instruction(0x1805e9020, 0x1805e9118, 'call', 'rax')
require_instruction(0x1805e9020, 0x1805e91db, 'call', 'r10')
require_instruction(0x1805e9020, 0x1805e91fe, 'call', 'r10')
# CancelAfterAttack's true branch invokes UpdateSpRecovery in the same callback.
require_instruction(0x180963650, 0x1809636ef, 'call', 'r10')
require_instruction(0x180963650, 0x18096370d, 'mov', 'rax, qword ptr [rdx + 0x618]')
require_instruction(0x180963650, 0x18096371b, 'call', 'rax')
# The copy uses SetRemainingTime, which clamps only above the raw timer period.
require_instruction(0x1805ea7d0, 0x1805ea88e, 'mov', 'rdx, qword ptr [rdx + 0x18]')
require_instruction(0x1805ea7d0, 0x1805ea8a4, 'jmp', '0x181f140f0')
require_instruction(0x181f140f0, 0x181f14143, 'call', '0x186316760')
require_instruction(0x181f140f0, 0x181f1414d, 'mov', 'qword ptr [rsi + 0x18], rax')
result = {'source_game_dll_sha256': metadata['source_game_dll_sha256'],
          'source_metadata_sha256': metadata['source_metadata_sha256'],
          'base_version': prefabs['base_version'], 'source_skill_bundle_sha256': prefabs['source_sha256'],
          'actual_prefab': prefab['asset_path'], 'skill_component': -7067969616294705369,
          'attack_component': 1442620349020702503,
          'actual_flags': {name: skill[name] for name in ['_allowSpRecoveryWhenAffecting', '_earlySkillFinishAtAttackFinished', '_useEscapeTime']},
          'actual_attack_flags': {name: attack[name] for name in ['_resetCdStrategy', '_escapeTime', '_minPostDelay']},
          'new_cfgs': proof, 'reused_evidence': references,
          'instruction_count': sum(row['instructions'] for row in proof),
          'all_instruction_bytes_match_original_file': True,
          'semantic_native_checks': ['actual S1 flags and HALF_FRAME strategy',
              'actual virtual overrides', 'MultiMeleeAttack to EasyToStartAbility end chain',
              'cleanup and callback order', 'same callback UpdateSpRecovery after cancellation',
              'ClearReplacement copy setter clamps by original timer period'],
          'established_scope': ['actual serialized lifecycle flags',
              'native post-delay requests at least one fixed wait step',
              'normal end cleanup and callback ordering',
              'HALF_FRAME strategy acts on replacement cooldown before raw cooldown copy',
              'SP modifier update occurs in normal completion callback',
              'raw attack readiness can be checked in completion callback'],
          'remaining_unknown': ['live XLua hot-update equivalence',
              'nested coroutine and external SP scheduling observation frame',
              'global first-hit phase and absolute full-skill duration without binding',
              'interrupted, target-dead, transformed-skin and externally-modified paths'],
          'native_default_path_only': True, 'hot_update_equivalence_verified': False,
          'dll_executed': False, 'process_memory_read': False, 'private_files_read': False,
          'production_files_changed': False}
(OUT / 'proof.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'methods': len(proof), 'instructions': result['instruction_count'], 'verified': True}, ensure_ascii=False))
