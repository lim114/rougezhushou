from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/sections/306-necessary-attempt1';OUT.mkdir()
selectors=['tests.test_enemy_form_reference_306','tests.test_enemy_form_view_306','tests.test_cloud_index_sync','tests.test_player_battle_information_286','tests.test_player_information_view_286','tests.test_auxiliary_enemy_mechanisms']
names=set(json.loads((ROOT/'research/p3-enemy-form-306/source-manifest.json').read_bytes())['runtime_files'])
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'research/p3-enemy-form-306').iterdir() if p.is_file())
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'rouge').glob('*.py'))
names.update(s.replace('.','/')+'.py' for s in selectors)
names.update(['scripts/update_cloud_index.py','scripts/build_enemy_form_reference_306.py'])
def bound():return {n:sha256((ROOT/n).read_bytes()).hexdigest() for n in sorted(names)}
before=bound();env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1')
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*selectors];start=datetime.now(timezone.utc).isoformat()
with (OUT/'stdout.txt').open('xb') as stdout,(OUT/'stderr.txt').open('xb') as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=p.wait()
after=bound();err=(OUT/'stderr.txt').read_text('utf8',errors='replace');m=re.search(r'Ran (\d+) tests? in ([\d.]+)s',err)
receipt={'section':306,'kind':'actual_necessary_offscreen_behavior_checks','selectors':selectors,'argv':argv,'retained_popen_pid':p.pid,'actual_observed_exit':code,'exit_code':code,'methods_ran':int(m[1]) if m else None,'seconds':float(m[2]) if m else None,'start_utc':start,'finish_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'passed':code==0 and m is not None and before==after,'full_validation_rerun':False,'native_windows_visible_or_game_chat_validation_claimed':False,'QT_QPA_PLATFORM':'offscreen'}
(OUT/'process.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes());(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii')
print(json.dumps({k:v for k,v in receipt.items() if not k.startswith('source_sha')},ensure_ascii=False))
if not receipt['passed']:print(err[-6500:])
raise SystemExit(0 if receipt['passed'] else 1)
