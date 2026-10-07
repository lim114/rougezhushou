"""Independent public-source closure; never reads run/game state."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = Path('/workspace/.continuation/p2-after-055-audit/relic-scope')
FROZEN = AUDIT / 'frozen'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

freeze = json.loads((AUDIT/'freeze.json').read_text())
manifest = freeze['public_source_hashes']
drift = [rel for rel, expected in manifest.items() if sha(FROZEN/rel) != expected]
assert not drift, drift
original = AUDIT / 'roguelike_topic_table.json'
expected_raw_sha = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
assert original.stat().st_size == 17943244
assert sha(original) == expected_raw_sha
topic = json.loads(original.read_text())
game = topic['details']['rogue_6']
rid = 'rogue_6_relic_cargo_10'
usage = game['items'][rid]['usage']
assert usage == '应急助力节点中招募所需源石锭-50%，应急干员的生命值、攻击力和防御力+40%'
buff = game['relics'][rid]['buffs'][1]
assert buff['key'] == 'global_buff_normal'
assert buff['blackboard'][0]['valueStr'] == 'rogue_6_relic_employ'
values = {b['key']:b['value'] for b in buff['blackboard'][1:]}
assert values == {'atk':.4, 'def':.4, 'max_hp':.4}
mechanics = json.loads((FROZEN/'rouge/data/relic-mechanics.json').read_text())
conditions = []
def walk(node, path):
    if isinstance(node, dict):
        if node.get('condition') == 'emergency_hire':
            conditions.append({'selector':path, 'effect':node})
        for key, child in node.items(): walk(child, path+'.'+key)
    elif isinstance(node,list):
        for i,child in enumerate(node): walk(child, path+f'[{i}]')
walk(mechanics, 'relic-mechanics')
assert len(conditions) == 3
assert [c['selector'] for c in conditions] == [f'relic-mechanics.relics.{rid}.effects[{i}]' for i in range(3)]
assert {c['effect']['kind']:c['effect']['value'] for c in conditions} == {'attack_pct':.4,'defense_pct':.4,'hp_pct':.4}
contracts = json.loads((AUDIT/'source-contracts.json').read_text())
producer_lines = {}
for rel, entry in contracts.items():
    path=FROZEN/rel
    assert sha(path)==entry['sha256']
    lines=path.read_text().splitlines()
    for point in entry['matching_lines']:
        assert lines[point['line']-1].strip()==point['text']
    producer_lines[rel]=entry
policy=json.loads((AUDIT/'policy-override.json').read_text())
receipt={
    'baseline_head':freeze['baseline_head'],
    'review_scope':'Read-only frozen public game/source closure; no fresh network request or private/game reads',
    'frozen_public_files_checked':len(manifest), 'frozen_source_drift':drift,
    'pinned_original_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
    'pinned_original_path':str(original),'pinned_original_sha256':sha(original),'pinned_original_bytes':original.stat().st_size,
    'usage_selector':f'roguelike_topic_table.details.rogue_6.items.{rid}.usage','usage':usage,
    'buff_selector':f'roguelike_topic_table.details.rogue_6.relics.{rid}.buffs[1]','buff':buff,
    'emergency_condition_selectors':conditions,
    'public_source_contracts':producer_lines,
    'legal_public_identity_values':['non_emergency','emergency_hire'],
    'active_input_policy':policy,
    'superseded_audit_recommendation':'Original source-receipt ValueError recommendation is historical only; policy-override.json and NOTE override are active.',
    'native_attachment_proven':False, 'hotfix_equivalence_proven':False,
    'new_timing_or_stacking_claim':False,
    'findings':[], 'source_review_passed':True,
}
(HERE/'source-review.json').write_text(json.dumps(receipt, ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'source_review_passed':True,'frozen_public_files_checked':len(manifest),'source_drift':drift,'conditions':len(conditions),'native_attachment_proven':False},ensure_ascii=False))
