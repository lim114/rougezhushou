from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];mode=sys.argv[1];out=R/'verification/sections/459-viewport'/'native-final'
if len(sys.argv)==2:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,mode,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_reference_window.py','rouge/player_inline_notes.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtWidgets import QScrollArea,QWidget,QVBoxLayout,QLabel,QPushButton
 from rouge.player_reference_window import ToolPage
 from rouge.player_reference_notes import note_for
 from rouge.player_notes import content_key
 from unittest.mock import patch
 mode=sys.argv[1];before=deepcopy(window.run.state);notes=window.player_notes;notes.autosave.setChecked(False)
 old_init=ToolPage.__init__
 def wrapped(page,title,content,parent,**kwargs):
  old_init(page,title,content,parent,**kwargs);body=page.layout();body.removeWidget(content);page.body_scroll=QScrollArea();page.body_scroll.setWidgetResizable(True);page.body_scroll.setFrameShape(QScrollArea.Shape.NoFrame);page.body_scroll.setWidget(content);body.addWidget(page.body_scroll,1)
 manager=patch.object(ToolPage,'__init__',old_init)
 records=[];images=[]
 with manager:
  window.show_compact();c=window.compact_window
  for timer in window.findChildren(QTimer):timer.stop()
  def observe(name,page):
   gui.processEvents();QTest.qWait(180);gui.processEvents();host=c.reference_window;p=getattr(page,'panel',None);row={'name':name,'preferred':[page.preferred_size.width(),page.preferred_size.height()],'actual':[host.width(),host.height()],'root_has_hfw':host.layout().hasHeightForWidth(),'root_hfw':host.layout().totalHeightForWidth(host.width()),'page_hfw':page.heightForWidth(page.width()),'panel_size':[p.width(),p.height()]if p else None}
   if mode=='scroll':row.update(scroll_range=page.body_scroll.verticalScrollBar().maximum(),viewport_size=[page.body_scroll.viewport().width(),page.body_scroll.viewport().height()])
   if name.startswith('notes'):row.update(card_y=p.card.y(),stack_height=p.stack.height(),text_height=notes.editor.viewport().height(),min_text_height=notes.editor.fontMetrics().lineSpacing()*4)
   require(row['actual']==row['preferred'],name+'_requested_size_retained');require(page.body_scroll.viewport().height()>=120,name+'_body_readable');row['titlebar']={'size':[host.titleBar.width(),host.titleBar.height()],'hint':[host.titleBar.sizeHint().width(),host.titleBar.sizeHint().height()],'minimum_hint':[host.titleBar.minimumSizeHint().width(),host.titleBar.minimumSizeHint().height()],'hfw':host.titleBar.heightForWidth(host.width()),'headers_size':[host.headers.width(),host.headers.height()],'headers_hint':[host.headers.sizeHint().width(),host.headers.sizeHint().height()],'current_header_hint':[host.headers.currentWidget().sizeHint().width(),host.headers.currentWidget().sizeHint().height()],'all_header_hints':[[host.headers.widget(i).windowTitle(),host.headers.widget(i).sizeHint().height()]for i in range(host.headers.count())]};records.append(row)
   if name.startswith('notes'):
    path=out/(name+'.png');require(host.grab().save(str(path)),name+'_snapshot');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  for name,action,slot in [('map',c.open_map,'map_popup'),('notes-empty',c.open_recent_notes,'recent_notes_popup'),('library',c.open_note_library,'note_library_page'),('inventory',c.open_inventory,'inventory_popup'),('history',c.open_replay,'replay_popup'),('team',c.open_team,'team_popup'),('scene',c.open_scene_battle,'scene_popup'),('settings',lambda:c.present(c.settings_popup),'settings_popup'),('overview',lambda:c.present(c.overview_popup),'overview_popup')]:
   require(action(),'open_'+name);observe(name,getattr(c,slot))
  content=note_for('stages','ro6_n_1_2');key=content_key(content);notes.store.save(key,'\n'.join('公开笔记正文 '+str(i)for i in range(160)),notes.store.read(key)[1]);require(c.open_saved_note(content),'open_note_editor');observe('notes-edit',c.recent_notes_popup);c.recent_notes_popup.panel.request_edit();observe('notes-read',c.recent_notes_popup)
  widget=QWidget();layout=QVBoxLayout(widget);label=QLabel('完整长说明 '*450);label.setWordWrap(True);layout.addWidget(label);last=QPushButton('最后一项');layout.addWidget(last);page=ToolPage('长内容测试',widget,c);page.resize(600,250);require(c.present(page),'open_wrapped_content');observe('long-label',page)
  if mode=='scroll':page.body_scroll.ensureWidgetVisible(last);gui.processEvents();records[-1]['last_visible_rect']=[last.mapTo(page.body_scroll.viewport(),last.rect().topLeft()).y(),last.mapTo(page.body_scroll.viewport(),last.rect().bottomRight()).y()]
  require(records[-1]['last_visible_rect'][0]>=0 and records[-1]['last_visible_rect'][1]<page.body_scroll.viewport().height(),'long_content_last_control_reachable');require(window.run.state==before,'current_run_unchanged');require(not errors,'no_Qt_slot_errors');window.player_validation_target=c.reference_window
 (out/'observations.json').write_text(json.dumps({'mode':mode,'records':records,'investigation_only':False},ensure_ascii=False,indent=2)+'\n','utf8');(out/'images.json').write_text(json.dumps({'images':images,'public_temporary_notes_only':True},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(459,out/'window.json'))
