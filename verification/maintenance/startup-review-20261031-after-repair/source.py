from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from hashlib import sha256
import sys,json,time,cProfile,pstats
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication
from rouge import app as a
from rouge import public_node_statistics,public_archive
out=R/'verification/maintenance/startup-review-20261031-after-repair';out.mkdir(parents=True,exist_ok=False)
gui=QApplication([]);calls=[]
def forbidden(*args,**kwargs):calls.append(True);raise AssertionError('No real external operation during isolated startup profile')
with TemporaryDirectory(prefix='rouge-startup-review-')as folder,ExitStack()as stack:
    root=Path(folder)
    for key,value in {'ROOT':root,'SETTINGS':root/'settings.json','OPERATOR_STATE':root/'operators.json','RUN_STATE':root/'run.json'}.items():stack.enter_context(patch.object(a,key,value))
    backend=a.DesktopBackend;stack.enter_context(patch.object(a,'DesktopBackend',lambda _path,callback:backend(root/'chat',callback)))
    stack.enter_context(patch.object(a,'list_game_windows',return_value=[]))
    for name in ('connect','capture','next_frame'):stack.enter_context(patch.object(a.GameCapture,name,side_effect=forbidden))
    for name in ('start','request'):stack.enter_context(patch.object(backend,name,side_effect=forbidden))
    for owner,name in ((a,'stream_chat'),(a,'read_key'),(public_node_statistics,'fetch'),(public_archive,'fetch')):stack.enter_context(patch.object(owner,name,side_effect=forbidden))
    profile=cProfile.Profile();started=time.perf_counter();profile.enable();window=a.MainWindow();profile.disable();elapsed=time.perf_counter()-started
    data=pstats.Stats(profile);rows=[]
    for (filename,line,function),(primitive,total,own,cumulative,_)in data.stats.items():
        path=Path(filename)
        if not path.is_absolute()or not path.is_relative_to(R/'rouge'):continue
        rows.append({'file':path.relative_to(R).as_posix(),'line':line,'function':function,'primitive_calls':primitive,'calls':total,'own_seconds':own,'cumulative_seconds':cumulative})
    rows.sort(key=lambda v:v['cumulative_seconds'],reverse=True)
    window.close();gui.processEvents()
result={'isolated_startup_seconds':elapsed,'profiled_not_a_production_latency_benchmark':True,'external_attempts':len(calls),'qpa':gui.platformName(),'source_sha256':sha256((R/'rouge/app.py').read_bytes()).hexdigest(),'functions':rows[:70]}
(out/'profile.json').write_text(json.dumps(result,indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'profiled_seconds':elapsed,'top_project_functions':rows[:18]},indent=2))
