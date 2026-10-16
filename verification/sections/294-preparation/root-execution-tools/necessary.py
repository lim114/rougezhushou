from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/sys.argv[1];DEST.mkdir(parents=True,exist_ok=False)
modules=['tests.test_direct_landmark_294','tests.test_direct_landmark_mapping',
 'tests.test_direct_landmark_extension','tests.test_map_direct_continuation',
 'tests.test_direct_landmark_288','tests.test_player_tile_information_288']
paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
paths|={ROOT/('tests/'+m.split('.')[-1]+'.py') for m in modules}
paths|={ROOT/'scripts/verify_direct_map_window_294.py',ROOT/'scripts/extend_direct_landmark_294.py'}
for packet in ('p3-map-direct-checkpoints-294','p3-map-direct-road-288','p3-map-direct-continuation',
               'p3-direct-ground-expanded','p3-direct-ground-current'):
    paths|={p for p in (ROOT/'research'/packet).rglob('*') if p.is_file()}
stage_data=json.loads((ROOT/'rouge/data/battle-previews.json').read_bytes())['stages']
for sid in ('ro6_n_3_2','ro6_e_3_2','ro6_t_5','ro6_e_t_5'):
    paths.add(ROOT/'rouge/data'/stage_data[sid]['image']['file'])
assert all(p.is_file() and not p.is_symlink() for p in paths)
def hashes():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
before=hashes();start=datetime.now(timezone.utc).isoformat()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*modules]
with (DEST/'stdout.txt').open('xb') as out,(DEST/'stderr.txt').open('xb') as err:
    result=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=err,timeout=300,
        env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1'))
after=hashes()
row={'section':294,'kind':'necessary_change_related_tests_not_full_suite','argv':argv,'modules':modules,
 'source_commit_before':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),'exit_code':result.returncode,
 'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,
 'game_sampling_verified':False,'chat_verified':False,'full_scope_reduced':False,'full_suite_rerun':False}
(DEST/'process.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'section':294,'actual_exit':result.returncode,'source_unchanged':before==after,'receipt':str(DEST/'process.json')}))
raise SystemExit(result.returncode if before==after else 97)
