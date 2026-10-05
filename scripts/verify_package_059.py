"""Build public wheel offline and instantiate both visual asset readers in isolation."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def source_hashes():
    files=[ROOT/'pyproject.toml',Path(__file__),*(ROOT/'rouge').rglob('*.py'),
           *[p for group in ('visual-anchors','page-features')
             for p in (ROOT/'rouge/data'/group).iterdir() if p.is_file()]]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def main():
    started=time.perf_counter();before=source_hashes()
    folder=ROOT/'.cache/package-059'/str(time.time_ns())
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
    assert '-0.59.0-' in wheel.name,wheel.name
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
from importlib.metadata import version
import numpy as np
import rouge
from rouge.page_features import PageFeatureRouter
from rouge.visual_recognition import VisualReader
from rouge.page_ocr import PageOCR
assert Path(rouge.__file__).resolve().is_relative_to(Path.cwd())
assert version('rouge-blackflow-helper')=='0.59.0'
a=PageFeatureRouter(); b=VisualReader(cache_enabled=False)
assert a._plan_cache is None and b.cache_enabled is False
calls=[]
def provider(image):
    calls.append(image.shape)
    return [[[[0.,0.],[4.,0.],[4.,4.],[0.,4.]],'provider',.9]],None
c=PageOCR(provider,cache_enabled=False)
raw,_=c.read(np.zeros((20,30,3),np.uint8),regions=[[2,2,8,8]])
assert len(calls)==1 and calls[0]==(20,30,3) and raw[0][1]=='provider'
assert c.metrics['fallback_reason']=='unsupported_provider'
assert c.metrics['full_frame_input'] and c.metrics['coverage_verified'] is False
print(json.dumps({'installed_path':True,'page_feature_pages':len(a.pages),
    'visual_references':len(b.references),'page_ocr_imported':True,
    'page_ocr_unknown_provider_single_full_fallback':True}))
"""
            probe=subprocess.run([sys.executable,'-c',code],cwd=tmp,env=env,check=True,
                text=True,encoding='utf-8',capture_output=True,timeout=30)
            result=json.loads(probe.stdout)
    after=source_hashes()
    changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
    assert not changed,changed
    receipt={'version':'0.59.0','passed':True,'verified_at':time.time(),
        'wheel':wheel.relative_to(ROOT).as_posix(),'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),
        'assets_checked':len(expected),'isolated_import':result,'offline_build':True,
        'private_runtime_packaged':False,'game_actions':0,'chat_requests':0,
        'source_sha256':before,'source_sha256_after':after,'source_drift':changed,
        'runner_sealed':True,'python_files_checked':len(python_files),
        'elapsed_seconds':time.perf_counter()-started}
    with (ROOT/'PACKAGE_0.59_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'assets_checked':len(expected),'isolated_import':result}))


if __name__=='__main__':main()
