"""Record the mechanism actually read, its scope, and unchanged unknowns."""
import hashlib,json,sys,time
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage
from rouge.relics import mechanics


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def summary(result):
    s=result['estimate']['skill'];stream=result['timing']['streams'][0]
    return {'window_damage':result['total_damage'],'release_frames':stream['release_frames'],
        'impact_frames':stream['impact_frames'],'total_damage':s['total_damage'],
        'phase_damage':s['phase_damage'],'cycle_damage':s['cycle_damage'],
        'initial_seconds':s['initial_seconds'],'recharge_seconds':s['recharge_seconds'],
        'cycle_seconds':s['cycle_seconds']}


def main():
    snapshot=read('.cache/research/impact-037/web-source.json')
    assert '弹道延迟0.8秒后落地' in snapshot['source']
    data=read('.cache/game-data/skill_table.json')['skchr_mcnist_3']
    assert len(data['levels'])==10
    values=data['levels'][-1]['blackboard']
    assert {x['key']:x['value'] for x in values if x['valueStr'] is None}['base_attack_time']==2.3
    # The skill BB is complementary evidence, not the source of the delay.
    assert all('delay' not in x['key'] for level in data['levels'] for x in level['blackboard'])
    before_research='.cache/research/phase-036/evidence.json'
    parent=read(before_research)
    examples=[]
    for scenario in (
        {'operator':'mechanist','skill':3,'base_attack':1000,'window_seconds':.5,
         'timing':{'windup_frames':6,'recovery_frames':9}},
        {'operator':'mechanist','skill':3,'base_attack':1000,
         'timing':{'windup_frames':0,'recovery_frames':0,'start_delay_frames':24}},
        {'operator':'mechanist','skill':3,'base_attack':1000,
         'timing':{'windup_frames':0,'recovery_frames':0,'start_delay_frames':24,
                   'projectile_travel_seconds':35.1}}):
        after=calculate_damage(scenario)
        with patch('rouge.timing.impact_delays',return_value={}):before=calculate_damage(scenario)
        examples.append({'synthetic_offline_preview':True,'scenario':scenario,
                         'before':summary(before),'after':summary(after)})
    receipt={'version':'0.37.0','verified_at':time.time(),'checked_date':'2026-10-04',
        'standing_instruction_file':'AGENTS.md','source_commit':mechanics()['commit'],
        'mechanism_change':'main mechanist S3 projectile receives documented 0.8-second impact delay',
        'recognition_change':'none',
        'source_page':snapshot['page_url'],'source_snapshot':'.cache/research/impact-037/web-source.json',
        'source_snapshot_sha256':digest('.cache/research/impact-037/web-source.json'),
        'source_revision_pinned':False,
        'revision_fetch_limits':['requests is not installed in the project runtime; no package was installed.',
            'The read-only MediaWiki API request failed with SSLEOFError; no revision number is claimed.',
            'The mechanism was read via the web tool and its returned content was saved locally.'],
        'raw_skill_source':'.cache/game-data/skill_table.json',
        'raw_skill_source_sha256':digest('.cache/game-data/skill_table.json'),
        'source_revision_of_game_data':parent['source_commit'],
        'raw_s3_values':values,'delay_not_in_skill_blackboard':True,
        'established':['The S3 main cross projectile lands 0.8 seconds after being thrown.',
            'It is thrown at the target tile center; collision area and aerial targets are described.',
            'The structural summon charge is a different projectile; no matching fixed impact time is established.'],
        'implementation':['Add24 frames after main release in the30Hz model; explicit extra travel is additive.',
            'Do not change releases, attack cadence, skill duration, initial SP or recharge.',
            'Keep late impacts in cast attribution but filter them by phase, observation window and this cycle.',
            'A fixed-delay metric appears only on mechanist S3 in frame mode.',
            'No normal-attack, token, other-skill or legacy continuous-mode delay is inferred.'],
        'preview_examples':examples,
        'inherited_unknowns':parent['unknowns'],'inherited_evidence':before_research,
        'inherited_evidence_sha256':digest(before_research),
        'remaining_specific_unknowns':['Actual first-three windup/recovery and skin/template bindings remain unverified.',
            'Main-projectile attack snapshot and target movement through the cross area are not newly verified.',
            'Summon charge hit time, conditional module packet scope and prior-cycle projectile steady-state are not simulated.'],
        'private_state_used':False,'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0}
    path=ROOT/'.cache/research/impact-037/evidence.json'
    path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'source_snapshot_verified':True,'raw_ranks_checked':10,
        'offline_examples':len(examples),'source_revision_pinned':False}),flush=True)


if __name__=='__main__':main()
