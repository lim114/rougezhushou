from pathlib import Path
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os,sys,json,unittest,subprocess
r=Path.cwd();sys.path.insert(0,str(r))
out=r/'verification/maintenance/hidden-view-sync-20261103'
if len(sys.argv)==1:
    with(out/'checks-stdout.txt').open('wb')as a,(out/'checks-stderr.txt').open('wb')as b:
        child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],stdout=a,stderr=b);code=child.wait()
    (out/'checks-process.json').write_text(json.dumps({'actual_PID':child.pid,'actual_exit':code},indent=2)+'\n','utf8',newline='\n')
    (out/'checks-source.py').write_bytes(Path(__file__).read_bytes())
    print((out/'checks-stderr.txt').read_text('utf8')[-1600:]);raise SystemExit(code)
os.environ['QT_QPA_PLATFORM']='offscreen'
import rouge.app as app
with TemporaryDirectory()as folder,ExitStack()as stack:
    # Older history-view fixtures already isolate run/settings/chat; isolate
    # their shared ROOT too, so notes/hotkey/config never use the real profile.
    stack.enter_context(patch.object(app,'ROOT',Path(folder)))
    modules=['tests.test_sampling_view_refresh','tests.test_node_resource_view','tests.test_node_map_navigation',
             'tests.test_node_history_workflow','tests.test_inventory_layout_review','tests.test_current_sync_ui',
             'tests.test_sampling_flow','tests.test_new_run_capture_view_112']
    result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    raise SystemExit(0 if result.wasSuccessful()else 1)
