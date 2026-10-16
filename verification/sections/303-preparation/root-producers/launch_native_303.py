from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
necessary=json.loads((ROOT/'verification/sections/303-necessary-first/process.json').read_bytes())
assert necessary['exit_code']==0 and necessary['source_unchanged'] and not necessary['timed_out']
folder=ROOT/'.cache/p3-303-native-window/root-launch';folder.mkdir(exist_ok=False)
argv=[sys.executable,'-B','-X','utf8','.cache/p3-303-native-window/run_section_303_window.py','--execute','--attempt','1',
      '--expected-parent','c2b78e4aa4136fe739067b5ccf9d13b595142320',
      '--native-source-sha256','06a2856aec1bc7e6d927b8a480022620749e0d0983862780c1220c752e5d8d63','--visible-ms','60000']
with (folder/'stdout.txt').open('xb') as stdout,(folder/'stderr.txt').open('xb') as stderr:
    process=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True,
         creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP)
record={'section':303,'kind':'actual_background_helper_launch_not_acceptance','at_utc':datetime.now(timezone.utc).isoformat(),
        'launcher_pid':process.pid,'argv':argv,'live_immediately_after_launch':process.poll() is None,
        'stdin_DEVNULL_and_stdout_stderr_exact_files_and_close_fds':True,'console_hidden':True,
        'native_or_product_pass_claimed':False}
(folder/'launch.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'section':303,'launcher_pid':process.pid,'launched':record['live_immediately_after_launch'],'native_result_pending':True}))
