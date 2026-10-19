from pathlib import Path
from hashlib import sha256
import subprocess,sys,os,json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/313-diagnostic-attempt1';out.mkdir()
for name in('rouge/expansion_reference.py','rouge/expansion_view.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py'):
 p=out/'before-fix'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
argv=[sys.executable,'-B','-X','utf8','-X','faulthandler','-m','unittest','-v','tests.test_expansion_view_313.ExpansionView313Tests.test_real_source_loss_clears_text_picture_link_and_selection_recovery_is_manual']
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=dict(os.environ,QT_QPA_PLATFORM='offscreen'));code=p.wait()
report={'kind':'isolated_original_failure_diagnostic_not_acceptance','section':313,'argv':argv,'actual_child_pid':p.pid,'actual_exit':code,'no_game_chat_or_private_state_used':True,'original_sources_archived_before_repair':True}
(out/'process.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());(out/'execution-diagnostic.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(report));print((out/'stderr.txt').read_text('utf8',errors='replace')[-6500:])
