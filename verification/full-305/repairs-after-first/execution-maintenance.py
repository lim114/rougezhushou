from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast,json,os,subprocess,sys
root=Path(__file__).resolve().parents[1]
def digest(p):return sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
out=root/'verification/full-305/repairs-after-first'
assert json.loads((root/'verification/full-305/first-archive-invocation/process.json').read_bytes())['actual_exit']==0
specs=[('scripts/verify_battle_entry_references_window_296_full305.py','.cache/p3-305-full-failure-triage/native296/candidate/scripts/verify_battle_entry_references_window_296_full305.py','9f770e45c11a8179201c852e24b8f26c80f3ea4523cb8f480f4375d1d2abdec2'),('scripts/verify_curiosity_node_rules_window_304_full305.py','.cache/p3-full305-attempt2-prep-revision2/candidate/scripts/verify_curiosity_node_rules_window_304_full305.py','08501c30f813465667926807809ee7653015851a0cd66e246b4dcdffce091a6a')]
changes=[]
for name,candidate,expected in specs:
 p=root/name;c=root/candidate;assert digest(c)==expected;ast.parse(c.read_bytes());before=None
 if p.exists():
  before=digest(p);q=out/'native-before'/name;q.parent.mkdir(parents=True,exist_ok=True)
  assert not q.exists();q.write_bytes(p.read_bytes())
 else:assert name.endswith('296_full305.py')
 p.write_bytes(c.read_bytes());changes.append({'file':name,'before_sha256':before,'after_sha256':expected,'candidate':candidate})
write(out/'native-promotion.json',{'section':305,'changes':changes,'production_logic_reverted':False,'actual_tests_inferred':False})
names=set(json.loads((root/'verification/full-305/source-freeze.json').read_bytes())['source_sha256'])|{x[0] for x in specs}
def hashes():return {n:digest(root/n) for n in sorted(names)}
before=hashes();dest=out/'necessary';dest.mkdir()
selectors=['tests.test_map_projection_049','tests.test_choice_recruitment_integration_290','tests.test_original_destinations','tests.test_peace_guardian_integration_291','tests.test_batch185_mainwindow','tests.test_resident_reference_signals_291.ResidentReferenceSignal291Tests.test_explicit_view_without_current_selection_never_falls_back_to_old_context']
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*selectors]
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1')
started=datetime.now(timezone.utc).isoformat()
with (dest/'stdout.log').open('xb') as stdout,(dest/'stderr.log').open('xb') as stderr:
 process=subprocess.Popen(argv,cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
 code=process.wait()
after=hashes();value={'section':305,'kind':'source_supported_full305_regression_maintenance_actual_checks','argv':argv,'selectors':selectors,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit_code':code,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'native_window_or_game_chat_claimed':False}
write(dest/'process.json',value);(dest/'process.exit').write_text(str(code)+'\n',encoding='ascii')
(out/'execution-maintenance.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'exit_code':code,'source_unchanged':before==after,'source_count':len(before),'stderr_tail':(dest/'stderr.log').read_text('utf8')[-1800:]},ensure_ascii=False))
raise SystemExit(code if before==after else 1)
