from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'305-window-tooldeps'))
import ctypes,json,subprocess,time,psutil
import win32gui,win32process,win32con
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/380-main-window.json'


def _verified_full380():
    from pathlib import Path as _Path
    from hashlib import sha256 as _sha256
    import json as _json
    import subprocess as _subprocess
    def _read(name):
        path=ROOT/name
        assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve()),name
        return _json.loads(path.read_bytes())
    def _sha(name):return _sha256((ROOT/name).read_bytes()).hexdigest()
    f=_read('verification/full-380/summary.json')
    assert f['after_section']==380 and f['available_checks_passed']is True and f['scope_not_reduced']is True
    assert f['actual_root_controller_exit']==0 and f['single_available_scope_execution_all_green']is True
    assert f['current_worktree_validation_authority']is True and f['source_drift']==[]
    assert f['complete_repository_validation']is False and all(f[k]is False for k in('P3_complete','P2_complete','P1_complete'))
    assert f['native_windows_game_chat_verified']is False and f['historical_original_Windows_verified']is False
    freeze=f['source_freeze'];assert freeze.startswith('verification/full-380/source-freeze-attempt')and freeze.endswith('.json')
    assert _sha(freeze)==f['source_freeze_sha256']
    d=_read(freeze)
    assert d['section']==380 and d['root_declared']is True and d['parent_commit']==f['tested_worktree_parent_commit']
    assert d['actual_validation_attempt']==f['actual_validation_attempt']and type(d['actual_validation_attempt'])is int and d['actual_validation_attempt']>=1
    assert len(d['selectors'])==len(set(d['selectors']))==f['maintained_selectors']
    assert len(d['p3_scripts'])==f['native_supplements']and f['actual_required_components']==5+len(d['p3_scripts'])
    assert all(any(int(mode.split('_')[1])==n for mode in d['p3_scripts'])for n in range(286,381))
    for mode in('p3_304','p3_305'):assert d['p3_script_options'][mode]['explicit_current_source_freeze']is True
    assert d['p3_script_options']['p3_312']['visible_ms']==120000
    maps={}
    for group in('source_sha256','legacy_native_source_sha256','supplemental_public_inputs_sha256'):
        for name,pin in d[group].items():
            if name in maps:assert maps[name]==pin,name
            maps[name]=pin
    for name,pin in maps.items():
        path=ROOT/name
        assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())and _sha(name)==pin,name

    _expected_canonical = [{'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/enemydata/enemy_database.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c.json', 'sha256': 'f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c', 'bytes': 15022043, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4-b.json', 'public_path': 'research/p3-auxiliary-mechanisms/level_rogue6_b-4-b.json', 'sha256': 'fc2f7ae7371829259bd445a45704d79f30f84094f8eedbfa74b026fe075c51ea', 'bytes': 202372, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4-b.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292.json', 'sha256': '1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292', 'bytes': 207445, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-5.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf.json', 'sha256': 'aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf', 'bytes': 205518, 'origin_manifests': [{'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-5.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-6.json', 'public_path': 'research/p3-spawn-candidates-299/levels/57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9.json', 'sha256': '57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9', 'bytes': 165191, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-6.json'}]}]
    assert d.get('canonical_local_public_input_bindings') == _expected_canonical
    _canonical_names = {row['local_path'] for row in _expected_canonical}
    assert {(mode,name) for mode,names in d['p3_script_selected_paths'].items() for name in names if name.startswith('.cache/')} == {('p3_369',name) for name in _canonical_names}
    assert d.get('canonical_local_public_input_sha256') == {row['local_path']:row['sha256'] for row in _expected_canonical}
    for row in _expected_canonical:
        assert row['mode']=='p3_369' and row['canonical_script']=='scripts/verify_current_boss_documents_window_369.py'
        for origin in row['origin_manifests']:
            authority=ROOT/origin['path']
            assert authority.is_file()and not authority.is_symlink()and authority.resolve().is_relative_to(ROOT.resolve())
            assert _sha(origin['path'])==origin['sha256']and authority.stat().st_size==origin['bytes']
            assert _read(origin['path'])['build_authority_files'][row['local_path']]=={'sha256':row['sha256'],'bytes':row['bytes']}
            assert origin['json_pointer']=='/build_authority_files/'+row['local_path'].replace('~','~0').replace('/','~1')
        _raws=[]
        for name in(row['local_path'],row['public_path']):
            path=ROOT/name
            assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())
            for parent in path.parents:
                if parent==ROOT:break
                assert not parent.is_symlink()
            raw=path.read_bytes();assert len(raw)==row['bytes']and _sha256(raw).hexdigest()==row['sha256']
            _raws.append(raw)
        assert _raws[0]==_raws[1]
        assert d['supplemental_public_inputs_sha256'][row['public_path']]==row['sha256']
    manifest='verification/full-380/execution-attempt'+str(d['actual_validation_attempt'])+'/archive-manifest.json'
    assert f['archive_manifests_sha256'][manifest]==_sha(manifest)
    archive=_read(manifest)
    assert archive['section']==380 and archive['actual_validation_attempt']==d['actual_validation_attempt']
    assert archive['actual_root_controller_exit']==0 and archive['source_freeze_sha256']==f['source_freeze_sha256']
    assert archive['activation_sha256']==f['activation_sha256']and archive['required_component_positions']==f['actual_required_components']
    assert archive['all_executed_retained_Popen_and_assigned_jobs_terminal']is True
    assert archive['all_original_ordered_components_retained']is True and archive['automated_available_scope_passed']is True
    visual=f['root_PNG_visual_review'];assert visual['file']=='verification/full-380/root-visual-review.json'
    assert _sha(visual['file'])==visual['sha256']and visual['all_reviewed']is True
    pixels=_read(visual['file'])
    assert pixels['section']==380 and pixels['actual_validation_attempt']==d['actual_validation_attempt']
    assert pixels['source_freeze_sha256']==f['source_freeze_sha256']and pixels['archive_manifest_sha256']==_sha(manifest)
    assert pixels['all_reviewed']is True and pixels['pending_actual_view_rows']==0 and pixels['blocking_visual_issues']==[]
    assert visual['image_count']==pixels['image_count']==len(pixels['images'])
    _subprocess.run(['git','merge-base','--is-ancestor',d['parent_commit'],'HEAD'],cwd=ROOT,check=True,stdout=_subprocess.PIPE,stderr=_subprocess.PIPE)
    return f


_verified_full380()

assert not OUT.exists()
def read(n):return json.loads((ROOT/n).read_bytes())
def digest(p):return sha256(p.read_bytes()).hexdigest()
n=read('verification/sections/380-necessary-attempt1/process.json');w=read('verification/sections/380-native-attempt1/actual/window.json')
assert n['passed']and w['passed']and w['qt_exit_code']==0
for name,h in w['source_sha256_after'].items():assert digest(ROOT/name)==h,name
private=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json']
def fingerprint():return{n:digest(ROOT/n)if(ROOT/n).is_file()else None for n in private}
def windows():
 rows=[]
 def visit(h,_):
  if '黑流树海助手'in win32gui.GetWindowText(h):
   rows.append({'hwnd':h,'pid':win32process.GetWindowThreadProcessId(h)[1],'title':win32gui.GetWindowText(h),'visible':bool(win32gui.IsWindowVisible(h)),'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h)),'minimized':bool(win32gui.IsIconic(h))})
 win32gui.EnumWindows(visit,None);return rows
def owned(row):
 p=psutil.Process(row['pid']);return Path(p.cwd()).resolve()==ROOT.resolve()and any('rouge.app'in arg for arg in p.cmdline())
before=fingerprint();old=windows();assert len(old)<=1 and all(owned(r)for r in old),'Review existing exact app; do not duplicate or close unrelated windows.'
for row in old:
 win32gui.PostMessage(row['hwnd'],win32con.WM_CLOSE,0,0);deadline=time.monotonic()+15
 while win32gui.IsWindow(row['hwnd'])and time.monotonic()<deadline:time.sleep(.1)
 assert not win32gui.IsWindow(row['hwnd']),'App did not close normally; no forced termination.'
assert not windows()
p=subprocess.Popen([str(ROOT/'.venv/Scripts/pythonw.exe'),'-B','-m','rouge.app'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
deadline=time.monotonic()+35
while time.monotonic()<deadline:
 rows=windows()
 if len(rows)==1 and rows[0]['visible']and rows[0]['responding']:break
 time.sleep(.25)
assert len(rows)==1 and rows[0]['visible']and rows[0]['responding']and owned(rows[0])
h=rows[0]['hwnd'];win32gui.ShowWindow(h,win32con.SW_RESTORE)
try:win32gui.SetForegroundWindow(h)
except Exception:pass
after=fingerprint();result={'section':380,'passed':before==after,'window_visible_and_responsive':True,'launcher_pid':p.pid,'visible_windows':rows,'closed_previous_exact_project_windows':old,'private_state_five_paths_unchanged':before==after,'private_entire_normal_close_and_start_interval_unchanged':before==after,'private_path_comparison_count':5,'private_contents_parsed_copied_or_restored':False,'private_hashes_published':False,'source_sha256':w['source_sha256_after'],'full_validation_this_changed_source_rerun':True,'current_full_receipt':'verification/full-380/summary.json','at_utc':datetime.now(timezone.utc).isoformat()}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items()if k!='source_sha256'},ensure_ascii=False));raise SystemExit(0 if result['passed']else 1)
