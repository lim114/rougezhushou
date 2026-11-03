"""Independent bounded scenarios; freeze inputs before product execution."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
PARENT = Path('/workspace/.continuation/p2-amiya-trait-scale-080')
OP = 'char_1037_amiya3'
MODULE = 'uniequip_002_amiya3'


def sha(data): return hashlib.sha256(data).hexdigest()


def save(name, value):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


original = json.loads((PARENT / 'freeze-receipt.json').read_text())
assert original['baseline_commit'] == '4b1e4d1f0bd9c60bc87523d6ac05c61f77f2a52b'
source = {}
for rel, entry in original['files'].items():
    before = (PARENT / 'baseline' / rel).read_bytes()
    after = (PARENT / 'draft' / rel).read_bytes()
    assert sha(before) == entry['sha256'], rel
    assert rel == 'rouge/operator_engine.py' or before == after, rel
    source[rel] = {'baseline_sha256': sha(before), 'draft_sha256': sha(after)}
assert source['rouge/operator_engine.py']['draft_sha256'] == 'b94d2b83f88c382cc3f46efde4f80f07422728c1c6a76f4eeff8696af62e20e7'
new_test = PARENT / 'draft/tests/test_amiya_module_healing_trait.py'
save('freeze080.json', {'status': 'frozen_before_independent_execution',
                       'parent_baseline_commit': original['baseline_commit'],
                       'parent_source_paths': {kind: str(PARENT / kind) for kind in ('baseline', 'draft')},
                       'public_file_count': len(source), 'sources': source,
                       'new_test': {'path': str(new_test), 'bytes': new_test.stat().st_size,
                                    'sha256': sha(new_test.read_bytes())},
                       'hash_seed_for_all_product_subprocesses': '0',
                       'source_review_sealed_unchanged': True,
                       'preparation_read_error': {'guessed_test_path': 'tests/test_amiya_trait_scale_module.py',
                                                  'stderr': 'cat: /workspace/.continuation/p2-amiya-trait-scale-080/draft/tests/test_amiya_trait_scale_module.py: No such file or directory',
                                                  'correct_path_discovered_before_any_test': str(new_test)}})

cases = []


def add(label, **extra):
    cases.append({'label': label, 'scenario': {'operator': OP, 'skill': 1, 'elite': 2, 'level': 50,
                 'skill_rank': 7, 'base_attack': 1000, 'module_id': MODULE, 'module_level': 1, **extra}})


for mode in ('frames', 'continuous'):
    for elite, level, skill, rank in [(0, 50, 1, 4), (1, 70, 2, 7), (2, 49, 1, 9)]:
        for stage in (1, 2, 3):
            add(f'{mode}-below-gate-e{elite}-s{skill}-m{stage}', timing_mode=mode,
                elite=elite, level=level, skill=skill, skill_rank=rank, module_level=stage)
    for stage in (1, 2, 3):
        add(f'{mode}-exact-gate-s1-r6-m{stage}', timing_mode=mode, skill_rank=6, module_level=stage)
    add(f'{mode}-cap-s2-r9-m3', timing_mode=mode, level=80, skill=2, skill_rank=9, module_level=3)
    for skill in (1, 2):
        for stage in (0, 3):
            add(f'{mode}-absent-id-stage{stage}-s{skill}', timing_mode=mode,
                skill=skill, module_id=None, module_level=stage)
    variants = [
        ('s1-zero-atk-p6', {'skill_rank': 1, 'module_level': 2, 'potential': 6, 'base_attack': 0}),
        ('s2-zero-atk-p6', {'skill': 2, 'potential': 6, 'base_attack': 0}),
        ('s1-hundred-recipients', {'module_level': 3, 'potential': 6, 'healing_targets': 100, 'window_seconds': 7.25}),
        ('s2-hundred-recipients', {'skill': 2, 'skill_rank': 9, 'module_level': 2, 'amiya_hit_targets': 5, 'healing_targets': 100, 'window_seconds': 7.25}),
        ('s2-zero-window', {'skill': 2, 'window_seconds': 0}),
        ('s2-zero-recipients', {'skill': 2, 'healing_targets': 0}),
        ('s2-zero-hostile-life', {'skill': 2, 'timing': {'target_disappears_seconds': 0}}),
        ('s2-short-positive-life', {'skill': 2, 'window_seconds': .08, 'timing': {'target_disappears_seconds': .08}}),
        ('s1-zero-window', {'window_seconds': 0}),
        ('s1-zero-recipients', {'healing_targets': 0}),
        ('s1-zero-hostile-life', {'timing': {'target_disappears_seconds': 0}}),
        ('s2-empty-target-windows', {'skill': 2, 'timing': {'target_windows': []}}),
        ('s1-empty-target-windows', {'timing': {'target_windows': []}}),
        ('s2-after-resistance-modifier', {'skill': 2, 'skill_rank': 6, 'enemy_resistance': 57, 'effects': [{'kind': 'damage_taken', 'damage_type': 'magic', 'value': .27}]}),
        ('s1-max-resistance', {'enemy_resistance': 100}),
        ('s2-single-heal-factor', {'skill': 2, 'skill_rank': 9, 'enemy_resistance': 40, 'module_level': 3, 'relic_ids': ['rogue_6_relic_legacy_81']}),
        ('s1-single-heal-factor', {'potential': 6, 'module_level': 2, 'relic_ids': ['rogue_6_relic_legacy_81']}),
        ('s2-unknown-multiple-heal-factors', {'skill': 2, 'relic_ids': ['rogue_6_relic_legacy_81', 'rogue_6_relic_legacy_82']}),
        ('s1-unknown-multiple-heal-factors', {'relic_ids': ['rogue_6_relic_legacy_81', 'rogue_6_relic_legacy_82']}),
    ]
    for label, extra in variants:
        add(mode + '-' + label, timing_mode=mode, **extra)

for label, extra in [
    ('module-stage-zero-error', {'module_level': 0}),
    ('module-stage-four-error', {'module_level': 4}),
    ('module-stage-bool-error', {'module_level': True}),
    ('module-stage-string-error', {'module_level': '1'}),
    ('wrong-form-module-error', {'module_id': 'uniequip_002_amiya2'}),
    ('missing-module-stage-error', {'module_level': None}),
    ('locked-s2-error', {'elite': 0, 'level': 1, 'skill': 2, 'skill_rank': 1}),
    ('invalid-module-before-locked-s2-error', {'elite': 0, 'level': 1, 'skill': 2, 'skill_rank': 1, 'module_level': 0}),
    ('recipients-bool-error', {'healing_targets': True}),
    ('level-zero-error', {'level': 0}),
]:
    add(label, **extra)
keys = [json.dumps(case['scenario'], ensure_ascii=False, sort_keys=True) for case in cases]
assert len(keys) == len(set(keys)), 'duplicate scenarios'
assert len(cases) == 82
save('cases080.json', cases)
print(json.dumps({'public_files_frozen': len(source), 'independent_pairs': len(cases), 'product_calls_so_far': 0}))
