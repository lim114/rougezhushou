from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from types import ModuleType
from hashlib import sha256
import sys,json,time
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent,QCoreApplication,Qt
from rouge import app as current,expansion_view,public_node_statistics,public_archive
old=ModuleType('rouge._before_deferred_app');old.__package__='rouge';old.__file__=str(R/'rouge/app.py')
exec(compile((R/'research/deferred-reference-review-20261031/before-app.py').read_bytes(),'<own-before-app>','exec'),old.__dict__)
old_view=ModuleType('rouge._before_deferred_view');old_view.__package__='rouge';old_view.__file__=str(R/'rouge/expansion_view.py')
exec(compile((R/'research/deferred-reference-review-20261031/before-expansion_view.py').read_bytes(),'<own-before-view>','exec'),old_view.__dict__)
gui=QApplication([]);calls=[];new_panel=expansion_view.ExpansionUpdatePanel;backend=current.DesktopBackend
def forbidden(*a,**k):calls.append(True);raise AssertionError('No external operations')
def construct(mode,inspect=True):
    owner=old if mode=='before'else current
    with TemporaryDirectory(prefix='rouge-deferred-bench-')as folder,ExitStack()as stack:
        root=Path(folder)
        for module in(current,old):
            for key,value in {'ROOT':root,'SETTINGS':root/'settings.json','OPERATOR_STATE':root/'operators.json','RUN_STATE':root/'run.json'}.items():stack.enter_context(patch.object(module,key,value))
            stack.enter_context(patch.object(module,'DesktopBackend',lambda _path,callback:backend(root/'chat',callback)))
            stack.enter_context(patch.object(module,'list_game_windows',return_value=[]))
        for name in('connect','capture','next_frame'):stack.enter_context(patch.object(current.GameCapture,name,side_effect=forbidden))
        for name in('start','request'):stack.enter_context(patch.object(backend,name,side_effect=forbidden))
        for module in(current,old):
            for name in('stream_chat','read_key'):stack.enter_context(patch.object(module,name,side_effect=forbidden))
        for module in(public_node_statistics,public_archive):stack.enter_context(patch.object(module,'fetch',side_effect=forbidden))
        stack.enter_context(patch.object(expansion_view,'ExpansionUpdatePanel',old_view.ExpansionUpdatePanel if mode=='before'else new_panel))
        start=time.perf_counter();window=owner.MainWindow();startup=(time.perf_counter()-start)*1000
        row={'mode':mode,'startup_ms':startup,'initial_directory_counts':{n:p.entries.count()for n,p in window.common_reference_panels.items()},'lookups':[]}
        if inspect:
            for category in window.common_reference_categories:
                start=time.perf_counter();p=window.reference_panel(category,activate=False);elapsed=(time.perf_counter()-start)*1000
                values=[(p.entries.item(i).text(),p.entries.item(i).data(Qt.ItemDataRole.UserRole))for i in range(p.entries.count())]
                payload=json.dumps(values,ensure_ascii=False,separators=(',',':')).encode('utf8')
                row['lookups'].append({'category':category,'milliseconds':elapsed,'count':len(values),'ordered_public_entries_sha256':sha256(payload).hexdigest()})
        window.close();window.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);gui.processEvents()
        return row
construct('after')
order=('before','after')if int(sys.argv[1])%2==0 else('after','before')
rows=[construct(mode)for mode in order]
by={r['mode']:r for r in rows};strip=lambda v:[{k:x for k,x in r.items()if k!='milliseconds'}for r in v['lookups']]
assert strip(by['before'])==strip(by['after'])
assert all(v==0 for v in by['after']['initial_directory_counts'].values())
assert not calls
output=Path(sys.argv[2]);output.write_text(json.dumps({'passed':True,'rows':rows,'external_attempts':0,'scope':'Unprofiled same-process paired construction after one warm-up. Fresh empty temporary states; first explicit lookups include deferred work. Excludes interpreter/import startup, private real run and all game/FPS claims.'},indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'startup_before_ms':by['before']['startup_ms'],'startup_after_ms':by['after']['startup_ms']}),flush=True)
