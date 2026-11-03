"""Copy the exact reviewed public283 archive plan; no deletes or overwrite."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'rouge/app.py').is_file())
MANIFEST_SHA256 = '8427d2082c0ca498cc098f0e3e19cbff96128c49280cee7446ad6d8e447b6516'
SUMMARY_SHA256 = '84b8ec45016f683f18e113a9027b5cb2c1689217b686534a15ed4590e1bad083'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='Actually copy the reviewed public files; default only prints the plan.')
    args = parser.parse_args()
    manifest_path = HERE/'public-archive-files-283.json'
    summary_path = HERE/'archive-summary-283.json'
    if sha(manifest_path) != MANIFEST_SHA256 or sha(summary_path) != SUMMARY_SHA256:
        raise RuntimeError('Reviewed plan or summary changed; stop before any write.')
    manifest = json.loads(manifest_path.read_bytes())
    destination = (ROOT/manifest['destination_root_relative']).resolve()
    if destination != (ROOT/'verification/sections/283-preparation').resolve():
        raise ValueError('Unexpected archive destination.')
    files = [(ROOT/r['source_relative'],destination/r['destination_relative'],r['sha256'])
             for r in manifest['files']]
    files += [(manifest_path,destination/'public-archive-files-283.json',MANIFEST_SHA256),
              (summary_path,destination/'archive-summary-283.json',SUMMARY_SHA256),
              (Path(__file__).resolve(),destination/'copy_public_preparation_283.py',sha(Path(__file__).resolve()))]
    for source,target,expected in files:
        if not source.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Source leaves this checkout.')
        if not target.resolve().is_relative_to(destination):
            raise ValueError('Destination leaves the reviewed archive.')
        if sha(source) != expected:
            raise RuntimeError('Original source changed: '+str(source))
        if target.exists() and (not target.is_file() or sha(target)!=expected):
            raise FileExistsError('Preserve the different existing original: '+str(target))
    if not args.apply:
        print(json.dumps({'prepared_only':True,'apply_requested':False,'planned_files':len(files),
                          'bytes':sum(s.stat().st_size for s,_,_ in files),'target':str(destination)},ensure_ascii=False))
        return
    copied = 0
    reused = 0
    for source,target,expected in files:
        if target.exists():
            reused += 1
            continue
        if sha(source) != expected:
            raise RuntimeError('Source changed after preflight: '+str(source))
        target.parent.mkdir(parents=True,exist_ok=True)
        # Exclusive-create protects an original appearing after preflight.
        with source.open('rb') as reader,target.open('xb') as writer:
            shutil.copyfileobj(reader,writer)
        if sha(target) != expected:
            raise RuntimeError('Copied bytes did not match: '+str(target))
        copied += 1
    print(json.dumps({'copied':copied,'identical_existing_preserved':reused,
                      'target':str(destination),'deletes':0,'overwrites':0,
                      'not_test_or_windows_execution':True},ensure_ascii=False))

if __name__=='__main__':
    main()
