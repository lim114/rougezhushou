"""Check only the accepted box/moving duplicate warning after root repair."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from rouge import node_catalog
from rouge.battle_reward_planning import stage_reward_sources
from rouge.player_node_information import node_information_text


def main():
    original = json.loads((HERE / 'review.json').read_text(encoding='utf-8'))
    old_player_sha = original['source_sha256']['rouge/player_node_information.py']
    current_source = (ROOT / 'rouge/player_node_information.py').read_bytes()
    new_sha = hashlib.sha256(current_source).hexdigest()
    with (HERE / 'finding-resolution-player.py').open('xb') as stream:
        stream.write(current_source)
    stage_id = 'ro6_n_1_1'
    record = next(row for row in node_catalog.battle_candidates(context='all')['rows']
                  if row['id'] == stage_id)
    text = node_information_text({'kind': 'battle', 'record': record})
    source = stage_reward_sources(stage_id)
    warning = ('箱型装置与它召出的移动恶笼草是关联资料；'
               '同一移动敌人的奖励只能算一次，不能各加10源石锭。')
    checks = {
        'root_accepted_specific_warning_present_once': text.count(warning) == 1,
        'default_source_url_absent': 'https://' not in text,
        'default_raw_entity_absent': 'enemy_2152_shezlc' not in text,
        'actual_reward_total_still_unknown': source['actual_reward_total'] is None,
        'core_unchanged_since_original_review': hashlib.sha256(
            (ROOT / 'rouge/moving_reward_reference.py').read_bytes()).hexdigest()
            == original['source_sha256']['rouge/moving_reward_reference.py'],
        'reward_renderer_unchanged_since_original_review': hashlib.sha256(
            (ROOT / 'rouge/battle_reward_planning.py').read_bytes()).hexdigest()
            == original['source_sha256']['rouge/battle_reward_planning.py'],
    }
    result = {'scope': 'One finding-resolution public player-text probe only; not a rerun of original 12 probes / 82 checks.',
              'original_review_player_sha256': old_player_sha,
              'current_player_sha256': new_sha,
              'original_review_bound_to_old_player': True,
              'input_stage_id': stage_id, 'actual_player_text': text,
              'checks': checks, 'failed_check_count': sum(not value for value in checks.values()),
              'game_chat_private_or_window_used': False}
    with (HERE / 'finding-resolution.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
    print(json.dumps({'probe_count': 1, 'check_count': len(checks),
                      'failed_check_count': result['failed_check_count'],
                      'current_player_sha256': new_sha}, ensure_ascii=False))
    raise SystemExit(int(result['failed_check_count'] > 0))


if __name__ == '__main__':
    main()
