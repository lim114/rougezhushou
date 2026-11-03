from pathlib import Path
import subprocess,sys,json
R=Path.cwd();tag=sys.argv[1];out=R/'verification/maintenance/current-enemy-forecast-review-20261031'/tag;out.mkdir(parents=True,exist_ok=False)
source=(R/'verification/maintenance/player-tool-navigation-review-20261031/tests-verified/bootstrap.py').read_text('utf8')
start=source.index('modules=');end=source.index('\nwith TemporaryDirectory',start)
names=['tests.test_current_enemy_forecast_review','tests.test_enemy_overview_review','tests.test_enemy_atlas_review','tests.test_current_enemy_traits_351','tests.test_current_enemy_traits_view_351','tests.test_player_scene_battle_395','tests.test_scene_reader_review','tests.test_player_feature_431']
source=source[:start]+'modules='+repr(names)+source[end:]
source=source.replace("out=R/'verification/maintenance/player-tool-navigation-review-20261031/tests-verified'",'out=R/'+repr(out.relative_to(R).as_posix()))
(out/'bootstrap.py').write_text(source,'utf8');argv=[sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')]
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 child=subprocess.Popen(argv,cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print(json.dumps({'actual_observed_exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure_tail':(out/'stderr.txt').read_text('utf8')[-4500:]if code else None},ensure_ascii=False))
raise SystemExit(code)
