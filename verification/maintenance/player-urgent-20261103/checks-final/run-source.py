from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
r=Path.cwd();out=r/'verification/maintenance/player-urgent-20261103/checks-final'
paths=['rouge/branch_choice.py','rouge/current_enemy_spawns_view.py','rouge/current_battle_view.py','rouge/player_compact.py','rouge/player_game_binding.py','rouge/player_toolbar.py','rouge/player_toolbar_acceptance.py','tests/test_player_toolbar_412.py','tests/test_player_urgent_experience.py','tests/test_owned_window_follow_review.py','tests/test_branch_choices_046.py','tests/test_current_enemy_forecast_review.py','tests/test_current_battle_view_314.py','scripts/verify_player_urgent_experience.py']
pins=lambda:{p:sha256((r/p).read_bytes()).hexdigest()for p in paths}
before=pins();cmd=[sys.executable,'-B','-X','utf8','-m','unittest','-v','tests.test_player_toolbar_412','tests.test_player_urgent_experience','tests.test_owned_window_follow_review','tests.test_branch_choices_046','tests.test_current_enemy_forecast_review','tests.test_current_battle_view_314']
with(out/'stdout.txt').open('wb')as a,(out/'stderr.txt').open('wb')as b:
 c=subprocess.Popen(cmd,stdout=a,stderr=b);code=c.wait()
after=pins();result={'actual_retained_PID':c.pid,'actual_observed_exit':code,'command':cmd[4:],'source_sha256_before':before,'source_sha256_after':after,'source_drift':before!=after,'full_suite':False};(out/'process.json').write_text(json.dumps(result,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code,'source_unchanged':before==after});print((out/'stderr.txt').read_text('utf8')[-900:]);assert code==0 and before==after
