"""Root-only check after integrating section 81; does not run calculations."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--repository', type=Path, default=Path('/workspace/rougezhushou'))
parser.add_argument('--original-topic', type=Path,
                    default=Path('/workspace/.continuation/p2-after-055-audit/relic-scope/roguelike_topic_table.json'))
parser.add_argument('--output', type=Path)
args = parser.parse_args()
root = args.repository
sha = lambda data: hashlib.sha256(data).hexdigest()
branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip()
assert branch == 'codex/p2-development'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
original = args.original_topic.read_bytes()
assert sha(original) == 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
topic = json.loads(original)['details']['rogue_6']
engine = (root / 'rouge/relics.py').read_bytes()
assert sha(engine) == '79f5f607a247fbe366651c63ee951215a518e6a597868cd65e4212d16564e5d3'
assert engine.count(b'\r\n') == engine.count(b'\n')
model = (root / 'rouge/data/relic-mechanics.json').read_bytes()
assert sha(model) == '6ee8d52cbaffdb0ec79a1ab44689e0bd1ef43364f6ddb3b2e4f2c80afbfe6f47'
mechanics = json.loads(model)
selectors = []
for number in (81, 82, 83):
    key = 'rogue_6_relic_legacy_' + str(number)
    current = mechanics['relics'][key]
    assert current['raw_buffs'] == topic['relics'][key]['buffs']
    assert current['relic_params'] == topic['relicParams'][key]
    assert all(effect['stacking'] == 'unverified' for effect in current['effects'])
    selectors.append(key)
test = (root / 'tests/test_relic_warning_order.py').read_bytes()
assert sha(test) == 'f5efb87f04bc14031faa4185a897b777740682028e07461ac397c1d6ded5c1a7'
assert '"tests.test_relic_warning_order"' in (root / 'scripts/verify_cloud.py').read_text()
receipt = {'passed': True, 'section': 81, 'branch': branch, 'current_head_before_section_commit': head,
           'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
           'original_topic': {'path': str(args.original_topic), 'bytes': len(original), 'sha256': sha(original)},
           'current_relics_sha256': sha(engine), 'current_mechanics_sha256': sha(model),
           'current_test_sha256': sha(test), 'new_test_registered': True,
           'original_selectors_exact': selectors, 'crlf_preserved': True,
           'numeric_model_changed': False, 'native_stacking_verified': False,
           'calculate_damage_calls': 0, 'gui_executed': False, 'wine_executed': False}
if args.output:
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
        f.write('\n')
print(json.dumps(receipt, ensure_ascii=False))
