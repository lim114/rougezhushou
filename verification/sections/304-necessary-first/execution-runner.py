from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/sections/304-necessary-first'
assert not OUT.exists()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='93ef6815b261d3b5f9ab58262f4825fd7b22d537'
OUT.mkdir(parents=True)
selectors=['tests.test_curiosity_node_rules_304','tests.test_curiosity_node_rules_view_304',
 'tests.test_event_planning','tests.test_event_preview_filters_292','tests.test_ritual_weakening_integration_302']
manifest=json.loads((ROOT/'research/p3-curiosity-node-rules-304/source-manifest.json').read_bytes())
names=set(manifest['files'])
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'rouge').glob('*.py'))
names.update(s.replace('.','/')+'.py' for s in selectors)
names.update(['scripts/build_curiosity_node_rules_304.py','research/p3-curiosity-node-rules-304/source-manifest.json'])
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
receipt={'section':304,'kind':'actual_necessary_unit_and_offscreen_Qt_behavior_checks',
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
