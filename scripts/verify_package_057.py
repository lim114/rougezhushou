"""Build public wheel offline and instantiate both visual asset readers in isolation."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    started=time.perf_counter()
    folder=ROOT/'.cache/package-057'/str(time.time_ns())
    folder.mkdir(parents=True)
    # Build from a fresh public-only staging directory. Package discovery must
    # not walk this workspace's large research/venv trees or use old build/lib.
    with tempfile.TemporaryDirectory(prefix='public-build-',dir=folder) as staged:
        source=Path(staged).resolve();assert source.is_relative_to(folder.resolve())
        shutil.copy2(ROOT/'pyproject.toml',source/'pyproject.toml')
        shutil.copytree(ROOT/'rouge',source/'rouge',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        with (folder/'build.log').open('x',encoding='utf-8') as stream:
            subprocess.run([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation',
                '--no-index','--wheel-dir',str(folder),str(source)],cwd=source,stdout=stream,
                stderr=subprocess.STDOUT,check=True,timeout=180)
    wheels=list(folder.glob('*.whl'));assert len(wheels)==1
    wheel=wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        names=archive.namelist()
        assert not any('.local/' in n or 'local-settings' in n or 'samples/' in n or '.cache/' in n for n in names)
        expected=[p.relative_to(ROOT).as_posix() for group in ('visual-anchors','page-features')
                  for p in (ROOT/'rouge/data'/group).iterdir() if p.is_file()]
        python_files=[p.relative_to(ROOT).as_posix() for p in (ROOT/'rouge').rglob('*.py')]
        checked=expected+python_files
        assert all(n in names for n in checked),sorted(set(checked)-set(names))
        for name in checked:
            assert archive.read(name)==(ROOT/name).read_bytes(),name
        with tempfile.TemporaryDirectory() as tmp:
            archive.extractall(tmp)
            env=dict(os.environ,PYTHONPATH=tmp,PYTHONIOENCODING='utf-8')
            code="""import json
from pathlib import Path
import rouge
from rouge.page_features import PageFeatureRouter
from rouge.visual_recognition import VisualReader
assert Path(rouge.__file__).resolve().is_relative_to(Path.cwd())
a=PageFeatureRouter(); b=VisualReader(cache_enabled=False)
assert a._plan_cache is None and b.cache_enabled is False
print(json.dumps({'installed_path':True,'page_feature_pages':len(a.pages),'visual_references':len(b.references)}))
"""
            probe=subprocess.run([sys.executable,'-c',code],cwd=tmp,env=env,check=True,
                text=True,encoding='utf-8',capture_output=True,timeout=30)
            result=json.loads(probe.stdout)
    receipt={'version':'0.57.0','passed':True,'verified_at':time.time(),
        'wheel':wheel.relative_to(ROOT).as_posix(),'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),
        'assets_checked':len(expected),'isolated_import':result,'offline_build':True,
        'private_runtime_packaged':False,'game_actions':0,'chat_requests':0,
        'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                         for n in ['pyproject.toml','scripts/verify_package_057.py',*checked]},
        'elapsed_seconds':time.perf_counter()-started}
    with (ROOT/'PACKAGE_0.57_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'assets_checked':len(expected),'isolated_import':result}))


if __name__=='__main__':main()
