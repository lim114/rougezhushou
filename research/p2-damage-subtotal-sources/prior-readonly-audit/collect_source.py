"""Targeted reuse and hash verification of public receipts and pinned raw tables."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / 'frozen'
REPO = Path('/workspace/rougezhushou')
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
expected = {
    'character_table': '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
    'skill_table': '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca',
}
tables = {}
receipt = {'public_code_head': '15e0fa455aad05d27303428299d24d15db4c572c',
    'source_repository': 'Kengxxiao/ArknightsGameData', 'source_commit': COMMIT,
    'source_mode': 'Reuse previously pinned public raw files; fresh local SHA256 check, no new binary/game access',
    'tables': {}}
for name, wanted in expected.items():
    path = REPO / '.cache/p2-s1-binding' / (name + '.json')
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    assert actual == wanted, name
    receipt['tables'][name] = {'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/' +
        COMMIT + '/zh_CN/gamedata/excel/' + name + '.json', 'reused_local_path': str(path),
        'bytes': len(raw), 'sha256': actual, 'sha256_matched': True}
    tables[name] = json.loads(raw)

char = tables['character_table']['char_1042_phatm2']
talents = [next(c for c in talent['candidates']
    if c['unlockCondition']['phase'] == 'PHASE_2' and c['requiredPotentialRank'] == 0)
    for talent in char['talents']]
receipt['selectors'] = {
    'skill_table.skchr_phatm2_1.levels[9]': tables['skill_table']['skchr_phatm2_1']['levels'][9],
    'character_table.char_1042_phatm2.talents[0].candidates[PHASE_2,potentialRank=0]': talents[0],
    'character_table.char_1042_phatm2.talents[1].candidates[PHASE_2,potentialRank=0]': talents[1],
}
receipt['reused_receipts'] = {}
for name in ('research/p2-s1-binding/source-receipt.json',
             'research/p2-incoming-clock/source-receipt.json',
             'research/p2-amiya-phase-reference/NOTE.md',
             'research/p2-healing-subtotal-scaling/NOTE.md',
             '.cache/research/phatm2-s1-069/REPORT.md',
             '.cache/research/phatm2-first-event-070/REPORT.md',
             '.cache/research/phatm2-damage-070/REPORT.md',
             '.cache/research/phatm2-damage-070/native-proof.json',
             '.cache/research/phatm2-damage-070/s1-unmove-template.json'):
    raw = (FROZEN / name).read_bytes()
    receipt['reused_receipts'][name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
old = json.loads((FROZEN / 'research/p2-s1-binding/source-receipt.json').read_text())
for name, wanted in old['reused_evidence_sha256'].items():
    assert receipt['reused_receipts'][name]['sha256'] == wanted, name

receipt['source_supports'] = [
    'S1 two 1.5-ATK magic strikes; binding neural multiplier 1.8 for 3 seconds is conditional on target buff',
    'E2 attack talent direct neural buildup is 30% attack, independent of damage-taken modifier',
    'E2 incoming talent is 70 neural buildup per within-range target normal attack; a count alone is not timestamps',
    'Public empty relic selection contains no River source; this is independently shown by request and resolution',
    'Existing native receipts support original relative action reference, not a complete current actual schedule',
]
receipt['source_does_not_support'] = [
    'Current native first binding attachment, refresh order, actual burst event times or hotfix equivalence',
    'Any new actual burst count or total, skill end, recharge, or cycle inferred from the source parameters',
    'A numerical damage/healing defect based solely on the wrong report source note',
]
receipt['candidate'] = {'kind': 'report_source_misattribution_only',
    'code_location': 'rouge/reporting.py:692-704',
    'public_cases': ['wine_s1_explicit_empty_relics', 'wine_s2_incoming_no_river'],
    'one_shared_branch': True, 'actual_aggregate_still_unknown': True}
(ROOT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'tables_hash_matched': list(expected), 'selectors': len(receipt['selectors']),
    'reused_receipts': len(receipt['reused_receipts']), 'report_candidates': 1}, ensure_ascii=False))
