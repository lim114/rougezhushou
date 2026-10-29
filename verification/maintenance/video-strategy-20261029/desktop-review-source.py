from pathlib import Path
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1];out=R/'verification/maintenance/video-strategy-20261029'
failure={'attempt':1,'actual_tool_command_exit':1,
    'original_stderr':'Traceback (most recent call last):\n  File "C:\\Users\\李娜\\Desktop\\lcn\\rouge\\.cache\\strategy_test_window_20261029.py", line 43, in <module>\n    assert found and all(r[\'responding\']for r in found)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError\n',
    'original_stdout_empty':True,'passed':False,
    'later_snapshot_showed_window':True,'exact_initial_failure_cause_proven':False,
    'initial_startup_private_hash_comparison_completed':False,
    'no_restart_or_duplicate_window_for_recheck':True}
(out/'test-window-attempt1-failure.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n','utf8')
p=out/'test-window.json';data=json.loads(p.read_bytes());assert data['visible_owned_windows']and not data['opened_if_absent']
data.update(desktop_visual_review_claimed=True,actual_windows_mcp_snapshot_called=True,
    root_actually_viewed_live_surface=True,blocking_visible_issues=False,
    private_guard_scope='read-only later recheck interval only; not original startup interval',
    initial_attempt_failed=True,desktop_image_or_private_item_values_saved_or_published=False,
    native_owned_window_scope='Win32 PID and HWND check; screenshot UI tree supplied no ownership',
    visual_proves_game_accuracy_or_new_function=False,
    at_UTC=datetime.now(timezone.utc).isoformat())
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
(out/'desktop-review-source.py').write_bytes(Path(__file__).read_bytes())
print('Actual desktop review and initial failed observation preserved, no private screenshot copied.')
