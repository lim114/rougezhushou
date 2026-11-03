from pathlib import Path
import hashlib,shutil,json
r=Path(__file__).resolve().parents[1]
def copy(s,d,h=None):
 if h:assert hashlib.sha256(s.read_bytes()).hexdigest()==h,s
 d.parent.mkdir(parents=True,exist_ok=True);assert not d.exists(),d;shutil.copyfile(s,d)
copy(r/'.cache/section283-main-tests/test_panel_native_main_283.py',r/'tests/test_panel_native_main_283.py','6a74891b29f17653b031bdbdd72dc08c8b2798047cf784e968868cfd8c679dcd')
copy(r/'.cache/section283-source-review/verify_panel_native_window_283.py',r/'scripts/verify_panel_native_window_283.py','61c92b591fd8c97fbc1c05f7426e57f8216ba88e903d1d5afea27d5a47ac3d4e')
p=r/'scripts/verify_full_available.py';s=p.read_text();old="    'tests.test_sp_recovery_attribute_independent_282',";assert s.count(old)==1
p.write_bytes(s.replace(old,old+"\n    'tests.test_panel_native_finalization_283',\n    'tests.test_panel_native_main_283',").encode('utf8'))
prior=json.loads((r/'verification/sections/282-main-window.json').read_bytes());old=json.loads((r/'verification/sections/281-main-window.json').read_bytes())
assert prior['main_pid']==[28876] and old['main_pid']==[3456]
s=(r/'.cache/section282-restart.ps1').read_text().replace('section282','section283').replace('section=282;','section=283;').replace('3456','28876').replace(old['main_started_at'],prior['main_started_at']).replace('verification/sections/282-main-window.json','verification/sections/283-main-window.json').replace('sp_recovery_attribute_reference','panel_native_finalization').replace('SP attributes14/30 and source-qualified timer reconfiguration','source-qualified native panel arithmetic integrated with the current model')
assert '282-main-window' not in s and old['main_started_at'] not in s
(r/'.cache/section283-restart.ps1').write_bytes(s.encode('utf8'))
print('283 exact main10/Windows fixture promoted; old selectors retained')
