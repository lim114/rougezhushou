"""Recheck the sealed batch and raise only its pinned, current test window."""
import hashlib,json,sys,time
from pathlib import Path
import win32api,win32con,win32gui,win32process

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify_launch_061 as launch


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    final_path=ROOT/'FINAL_0.61_VERIFICATION.json';final=read(final_path)
    assert final['passed'] and final['version']=='0.61.0'
    for mapping in (final['source_sha256'],final['receipt_sha256']):
        for name,digest in mapping.items():
            path=(ROOT/name).resolve()
            assert path.is_relative_to(ROOT) and '.local' not in path.relative_to(ROOT).parts
            assert sha(path)==digest,name
    app=read(ROOT/'APP_0.61_LAUNCH_VERIFICATION.json')
    before=read(ROOT/app['checkpoint']);live=launch.windows()
    assert len(live)==1 and live[0]['pid']==app['process_id'] and live[0]['title']==launch.TITLE,live
    window=live[0];assert launch.verify_process(window['pid'])==app['process_executable']
    handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,window['pid'])
    try:
        assert win32process.GetProcessTimes(handle)['CreationTime'].timestamp()==app['process_created_at']
    finally:handle.Close()
    assert launch.foreground(window['hwnd']),'Pinned window was raised but foreground not confirmed.'
    live=launch.windows()
    assert len(live)==1 and live[0]['pid']==app['process_id']
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    assert win32gui.GetForegroundWindow()==window['hwnd']
    rect=win32gui.GetWindowRect(window['hwnd'])
    work=win32api.GetMonitorInfo(win32api.MonitorFromWindow(window['hwnd']))['Work']
    assert work[0]<=rect[0]<rect[2]<=work[2] and work[1]<=rect[1]<rect[3]<=work[3]
    after=launch.state();run=read(ROOT/'.local/run-state.json')
    assert before['run_id_hash']==after['run_id_hash']
    prefix=run.get('history',[])[:before['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before['history_prefix_hash']
    assert before['config_hashes']==after['config_hashes']
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    receipt={'version':'0.61.0','passed':True,'verified_at':time.time(),
        'final_receipt':{'path':final_path.relative_to(ROOT).as_posix(),'sha256':sha(final_path)},
        'source_files_checked':len(final['source_sha256']),'evidence_files_checked':len(final['receipt_sha256']),
        'same_pinned_process':True,'process_id':window['pid'],'process_created_at':app['process_created_at'],
        'only_one_project_window':True,'visible_restored_responsive_foreground':True,'within_work_area':True,
        'same_run_preserved':True,'history_prefix_preserved':True,'private_configurations_unchanged':True,
        'history_count_before':before['history_count'],'history_count_after':after['history_count'],
        'configuration_files_checked':len(after['config_hashes']),
        'private_contents_copied':False,'run_state_writes':0,'game_actions':0,'chat_requests':0,
        'automation_1_3_deleted':True}
    path=ROOT/'.cache/launch-061'/f'final-window-{time.time_ns()}.json'
    with path.open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'pid':window['pid'],'receipt':path.relative_to(ROOT).as_posix(),
        'history_count_before':before['history_count'],'history_count_after':after['history_count']}))


if __name__=='__main__':main()
