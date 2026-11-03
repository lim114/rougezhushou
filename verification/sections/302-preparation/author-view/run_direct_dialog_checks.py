"""Isolated cache-only offscreen dialog run; no MainWindow or private inputs."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
from datetime import datetime, timezone
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
VIEW='rouge/ritual_weakening_view.py'
TEST='tests/test_ritual_weakening_view_302.py'
CORE='rouge/ritual_weakening.py'
DATA='rouge/data/ritual-weakening.json'
MANIFEST='research/p3-ritual-weakening-302/source-manifest.json'

CHILD='''from pathlib import Path
import importlib.util,json,sys,unittest
root,original,receipt=map(Path,sys.argv[1:4])
sys.path.insert(0,str(root))
import rouge
rouge.__path__.append(str(original/'rouge'))
from rouge import ritual_weakening as model
from rouge import ritual_weakening_view as view
assert model.ROOT==root,(model.ROOT,root)
assert Path(model.__file__).resolve()==root/'rouge/ritual_weakening.py'
assert Path(view.__file__).resolve()==root/'rouge/ritual_weakening_view.py'
spec=importlib.util.spec_from_file_location('isolated_ritual_weakening_view_302',root/'tests/test_ritual_weakening_view_302.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.loadTestsFromModule(module)
result=unittest.TextTestRunner(verbosity=2).run(suite)
not_loaded={name:name not in sys.modules for name in ('rouge.app','rouge.capture','rouge.capture_windows','rouge.desktop_chat')}
assert all(not_loaded.values()),not_loaded
receipt.write_text(json.dumps({'kind':'cache-direct-dialog-offscreen-checks-not-product-or-native-acceptance',
 'model_import':str(Path(model.__file__).resolve()),'view_import':str(Path(view.__file__).resolve()),
 'public_source_ROOT':str(model.ROOT),'QPA_platform':__import__('os').environ.get('QT_QPA_PLATFORM'),
 'actual_tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
 'skipped':len(result.skipped),'successful':result.wasSuccessful(),
 'excluded_modules_not_loaded':not_loaded},ensure_ascii=False,indent=2)+'\\n',encoding='utf8')
sys.exit(0 if result.wasSuccessful() else 1)
'''

def pin(path):
    raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}

def relative_path(value):
    if type(value) is not str:raise ValueError('Non-string public source path.')
    path=Path(value)
    if path.is_absolute() or '..' in path.parts:raise ValueError('Public path must remain inside its root.')
    if not path.parts or path.parts[0] not in ('research','rouge','scripts','tests'):
        raise ValueError('Unexpected public source path.')
    return path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    backend=args.backend_root.resolve();output=args.output.resolve()
    if output.exists():raise FileExistsError('Preserve original run: output already exists.')
    manifest=json.loads((backend/MANIFEST).read_bytes())
    inputs={}
    for name,expected in manifest['files'].items():
        relative=relative_path(name)
        source=backend/relative
        if not source.is_file():source=ROOT/relative
        actual=pin(source)
        if actual['sha256']!=expected['sha256']:raise ValueError('Public manifest source changed: '+name)
        if 'bytes' in expected and actual['bytes']!=expected['bytes']:raise ValueError('Public source byte count changed: '+name)
        inputs[name]=source
    inputs[MANIFEST]=backend/MANIFEST
    inputs[CORE]=backend/CORE
    inputs[DATA]=backend/DATA
    inputs[VIEW]=HERE/'candidate'/VIEW
    inputs[TEST]=HERE/'candidate'/TEST
    # Existing battle stage grouping asks the isolated catalog for this public table.
    inputs['rouge/data/node-events.json']=ROOT/'rouge/data/node-events.json'
    fallback=('rouge/player_node_information.py','rouge/ui_state.py','rouge/battle_view.py','rouge/battle_preview.py','rouge/view_catalog.py','rouge/branch_choice.py','rouge/run_modifiers.py','rouge/data/battle-previews.json','rouge/data/battle-maps/ro6_b_6.png')
    bound={str(path):pin(path) for path in inputs.values()}
    bound.update({str(ROOT/name):pin(ROOT/name) for name in fallback})
    output.mkdir(parents=True)
    snapshot=output/'source-before';snapshot.mkdir()
    for name,source in inputs.items():
        target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    shutil.copyfile(__file__,output/'runner.py')
    child=output/'child.py';child.write_text(CHILD,encoding='utf8')
    started=datetime.now(timezone.utc).isoformat()
    with TemporaryDirectory(prefix='rouge302-public-dialog-') as temporary:
        isolated=Path(temporary).resolve()
        for name,source in inputs.items():
            target=isolated/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        (isolated/'rouge/__init__.py').write_text('"""Isolated public cache package."""\n',encoding='utf8')
        for name in ('appdata','localappdata','temp'):(isolated/name).mkdir()
        environment=os.environ.copy()
        environment.update(QT_QPA_PLATFORM='offscreen',APPDATA=str(isolated/'appdata'),
                           LOCALAPPDATA=str(isolated/'localappdata'),TEMP=str(isolated/'temp'),TMP=str(isolated/'temp'),
                           PYTHONDONTWRITEBYTECODE='1')
        argv=[sys.executable,'-B','-X','utf8',str(child),str(isolated),str(ROOT),str(output/'actual-result.json')]
        process=subprocess.run(argv,cwd=isolated,env=environment,capture_output=True,timeout=120)
        (output/'stdout').write_bytes(process.stdout);(output/'stderr').write_bytes(process.stderr)
        for name in fallback:
            if pin(ROOT/name)!=bound[str(ROOT/name)]:raise ValueError('Public fallback source changed during run: '+name)
        after={str(path):pin(path) for path in inputs.values()}
        after.update({str(ROOT/name):pin(ROOT/name) for name in fallback})
        receipt={'kind':'cache-only-direct-dialog-process-not-product-or-native-acceptance',
            'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'argv':argv,
            'backend_candidate_root':str(backend),'isolated_public_ROOT':str(isolated),'state_paths_temporary':True,
            'actual_exit':process.returncode,'source_before':bound,'source_after':after,'source_unchanged':bound==after,
            'no_MainWindow_game_chat_private_or_Git':True}
        (output/'process.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(output),'actual_exit':process.returncode,'source_unchanged':bound==after},ensure_ascii=False))
    return process.returncode if bound==after else 2

if __name__=='__main__':raise SystemExit(main())
