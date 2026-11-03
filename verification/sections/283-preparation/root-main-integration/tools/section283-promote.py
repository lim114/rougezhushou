from pathlib import Path
import hashlib,json,shutil,subprocess
r=Path(__file__).resolve().parents[1]
assert subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()=='8ae63bf9e5eb39be22bc5f706cf6f75e35c691f2'
src=r/'.cache/section283-preparation'
def copy(s,d,h=None):
 if h:assert hashlib.sha256(s.read_bytes()).hexdigest()==h,s
 d.parent.mkdir(parents=True,exist_ok=True);assert not d.exists(),d;shutil.copyfile(s,d)
packet='research/p2-panel-native-finalization-283'
m=json.loads((src/packet/'source-manifest.json').read_bytes())
for p,d in m['files'].items():
 if not p.startswith(packet+'/') and p!='rouge/panel_native_precision.py':assert hashlib.sha256((r/p).read_bytes()).hexdigest()==d,p
copy(src/'rouge/panel_native_finalization.py',r/'rouge/panel_native_finalization.py','536875942fe6222f7ab3d995fffc4d2ae31f043a6f67e3616cc5c39a1cd68190')
copy(r/'.cache/section283-numeric/rouge/panel_native_precision.py',r/'rouge/panel_native_precision.py','878347f7f5d69d09535f1bf0aec409068c68a3cdcf54812091c7deb96be838fc')
for s in (src/packet).rglob('*'):
 if s.is_file():copy(s,r/packet/s.relative_to(src/packet))
copy(r/'.cache/section283-independent-tests/test_panel_native_finalization_283.py',r/'tests/test_panel_native_finalization_283.py','ac49ebd594b6e0403bf27994c6f021985b22ceb5b427be1bd0d241eb52936f01')
print('283 corrected parent, fixed numeric, public packet and exact38 tests promoted; no completion claim')
