from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication
from rouge.player_notes import NoteStore,NotesDialog,content_key
from rouge.player_recent_notes import RecentNotesPanel
from rouge.run_state import RunState
qt=QApplication([]);out=R/'verification/maintenance/notes-reader-review-20261031';out.mkdir(parents=True)
with TemporaryDirectory()as folder:
 run=RunState(Path(folder)/'run.json');store=NoteStore(Path(folder)/'notes');context={'kind':'battle','title':'隔离场景','variant_id':'normal'};key=content_key(context)
 store.save(key,'第一份本机笔记',store.read(key)[1]);run.state['last_node_content']=context
 panel=RecentNotesPanel(run,store);panel.follow.setChecked(False);run.reset(save=False);panel.refresh(force=True)
 reset_bug=panel.context==context and '第一份'in panel.preview.toPlainText()
 editor=NotesDialog(store.folder);editor.set_context(context);store.path(key).write_text('外部软件更新后的内容','utf8');editor.set_context(context)
 reopen_bug=editor.editor.toPlainText()=='第一份本机笔记'
 run.state['last_node_content']=context;panel.follow.setChecked(True);read_calls=[]
 with patch.object(store,'read',wraps=store.read)as reading:
  panel.select_context({'kind':'event','title':'另一隔离场景'});read_calls=reading.call_count
 result={'baseline_commit':'a7f437e534cffd13df7d4a9e55defb10f32f9a72','actual_RunState_reset_retains_old_paused_context':reset_bug,'clean_same_note_reopen_ignores_external_change':reopen_bug,'manual_context_selection_reads':read_calls,'private_files_used':False,'game_or_chat_called':False}
 (out/'before-reproduction.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');(out/'reproduction-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,ensure_ascii=False))
 panel.close();editor.close()
