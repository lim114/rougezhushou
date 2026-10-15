"""Explicitly authorized three-file promotion and real targeted check recorder."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
EXPECTED={
 'rouge/calibration.py':'72fa76dcb8592b7eb539ddc4d9440cb84e92449d30795b3de9bf9b81f0006691',
 'rouge/offline_tools_view.py':'05de5293607b57114b20f9a228882ec2a771cd0b1606e4d215518c4680e2d3e4',
}
PINS=list(EXPECTED)+['tests/test_extended_calibration_285.py','rouge/operator_engine.py',
    'rouge/panel_native_bridge.py','rouge/panel_native_finalization.py','rouge/panel_native_precision.py']

def digest(path):return sha256(path.read_bytes()).hexdigest()

def main():
    mode=sys.argv[1]
    if mode=='promote':
        before=HERE/'production-before';before.mkdir(exist_ok=False)
        for rel,expected in EXPECTED.items():
            assert digest(ROOT/rel)==expected,rel
            target=before/rel;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/rel).read_bytes())
        assert not (ROOT/'tests/test_extended_calibration_285.py').exists()
        for rel in EXPECTED:(ROOT/rel).write_bytes((HERE/'draft'/rel).read_bytes())
        (ROOT/'tests/test_extended_calibration_285.py').write_bytes((HERE/'test_extended_calibration_285.py').read_bytes())
        print(json.dumps({'promoted':{rel:digest(ROOT/rel) for rel in PINS[:3]}},indent=2))
        return
    output=HERE/mode;output.mkdir(exist_ok=False)
    before={rel:digest(ROOT/rel) for rel in PINS}
    for rel in PINS:
        target=output/'executed-source'/rel;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/rel).read_bytes())
    command=[str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-m','unittest','tests.test_extended_calibration_285','-v']
    env={**os.environ,'QT_QPA_PLATFORM':'offscreen'}
    start=datetime.now(timezone.utc).isoformat()
    with (output/'stdout.txt').open('wb') as stdout,(output/'stderr.txt').open('wb') as stderr:
        process=subprocess.run(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=240)
    after={rel:digest(ROOT/rel) for rel in PINS}
    receipt={'kind':'SECTION_285_ACTUAL_NECESSARY_TARGETED_CHECKS','started_at':start,
        'finished_at':datetime.now(timezone.utc).isoformat(),'command':command,
        'actual_exit_code':process.returncode,'source_before_sha256':before,'source_after_sha256':after,
        'sources_unchanged':before==after,'stdout_sha256':digest(output/'stdout.txt'),
        'stderr_sha256':digest(output/'stderr.txt'),
        'scope':'Adapter/main-result copy/import contracts, not 78 new numerical or native/game checks.'}
    (output/'process.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2));print((output/'stderr.txt').read_text(encoding='utf-8'))
    raise SystemExit(process.returncode)

if __name__=='__main__':main()
