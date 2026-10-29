"""Final-batch read-only preparation; never closes an existing window."""
from pathlib import Path
from hashlib import sha256
import json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
from player_ui_verification import source_hashes
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==409
full=json.loads((R/'verification/full-410/summary.json').read_bytes())
assert full['available_checks_passed'] and full['scope_not_reduced'] and full['actual_root_controller_exit']==0
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
output=R/'.cache/runtime410-before.json';assert not output.exists()
output.write_text(json.dumps({'private':{n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files},'source':source_hashes(),'no_windows_closed_by_preparation':True}), 'utf8')
print('Final410 runtime guard prepared; private fingerprints retained only in local cache.')
