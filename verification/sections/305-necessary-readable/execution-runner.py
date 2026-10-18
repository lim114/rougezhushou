from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/sections/305-necessary-readable'
assert not OUT.exists()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='89606d703dc121d26f869723e1bb7d1d356a913e'
OUT.mkdir(parents=True)
selectors=['tests.test_relic_exchange_flow_305','tests.test_relic_exchange_flow_view_305',
 'tests.test_event_planning','tests.test_event_preview_filters_292','tests.test_scrap_exchange_planning']
manifest=json.loads((ROOT/'research/p3-relic-exchange-305/source-manifest.json').read_bytes())
names=set(manifest['runtime_files'])
names.add(manifest['complete_primary_build_pin']['file'])
names.update(row['file'] for row in manifest['build_source_documents'])
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'rouge').glob('*.py'))
names.update(s.replace('.','/')+'.py' for s in selectors)
names.update(['scripts/build_relic_exchange_flow_305.py','research/p3-relic-exchange-305/source-manifest.json'])
def bound():return {name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)}
before=bound()
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1')
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*selectors]
start=datetime.now(timezone.utc).isoformat()
with (OUT/'stdout.txt').open('xb') as stdout,(OUT/'stderr.txt').open('xb') as stderr:
    result=subprocess.run(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env)
after=bound()
stderr=(OUT/'stderr.txt').read_text(encoding='utf8',errors='replace')
match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',stderr)
receipt={'section':305,'kind':'actual_necessary_unit_and_offscreen_Qt_behavior_checks',
 'argv':argv,'selectors':selectors,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),
 'exit_code':result.returncode,'methods_ran':int(match[1]) if match else None,'seconds':float(match[2]) if match else None,
 'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,
 'passed':result.returncode==0 and match is not None and before==after,
 'native_windows_visible_or_game_chat_validation_claimed':False,
 'QT_QPA_PLATFORM':'offscreen','full_validation_rerun':False}
(OUT/'process.json').write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode())
(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256_before','source_sha256_after')},ensure_ascii=False))
if not receipt['passed']:
    print(stderr[-6500:])
raise SystemExit(0 if receipt['passed'] else 1)
