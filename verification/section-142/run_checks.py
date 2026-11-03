"""Necessary checks for the changed shared layer and run/UI consumers."""
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['PYTHONUTF8']='1'
result=subprocess.run([sys.executable,'-m','unittest',
    'tests.test_supplemental_battle_142','tests.test_supplemental_battle_view_142',
    'tests.test_supplemental_run_141','tests.test_supplemental_run_view_141',
    'tests.test_supplemental_skills_136','tests.test_supplemental_skills_137',
    'tests.test_supplemental_skills_138','tests.test_cultivation_comparison_140','-q'],
    cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
log=result.stdout+result.stderr
(Path(__file__).parent/'tests.txt').write_bytes(log.encode('utf-8'))
print(log)
sys.exit(result.returncode)
