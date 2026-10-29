"""Exact manual reference notes, separate from last-read game scene notes."""
import json
from . import expansion_reference as model

KINDS={'stages':'reference-stage','scenes':'reference-scene'}

def note_for(category,identity):
    if not isinstance(category,str)or category not in KINDS or not isinstance(identity,str)or not identity:return None
    result=model.detail(category,identity)
    if result is None:return None
    row=result['row'];title=row.get('name')
    if not isinstance(title,str)or not title.strip():return None
    key=json.dumps([result['source_identity'],identity],ensure_ascii=True,sort_keys=True,separators=(',',':'))
    return {'kind':KINDS[category],'title':title,'event_id':identity,'variant_id':key}

def reference_target(content):
    if not isinstance(content,dict):return None
    category=next((category for category,kind in KINDS.items()if content.get('kind')==kind),None)
    identity=content.get('event_id');canonical=note_for(category,identity)
    if canonical is None or any(content.get(field)!=canonical[field]for field in('kind','title','event_id','variant_id')):return None
    return category,identity

def sync_note_source(dialog):
    dialog.reference_button.setVisible(reference_target(dialog.content)is not None)

def request_note_source(dialog):
    if reference_target(dialog.content)is not None:dialog.openReference.emit(dict(dialog.content))
    else:dialog.reference_button.hide();dialog.status.setText('原固定资料暂时无法核对；笔记仍保留，未借用同名条目。')

def open_note(window,content):
    if reference_target(content)is None:
        window.player_notes.status.setText('所选固定资料暂时无法核对，未切换已有笔记。');return False
    notes=window.player_notes
    if not notes.set_context(content):notes.show();notes.raise_();return False
    window.show_compact();return window.compact_window.present(notes)

def open_reference(window,content):
    target=reference_target(content)
    if target is None:
        window.player_notes.status.setText('笔记对应的原固定资料暂不可用；笔记仍保留，没有打开同名条目。');return False
    category,identity=target;panel=window.reference_panel(category)
    if panel is None:return False
    panel.search.clear()
    if category=='stages':panel.stage_floor.setCurrentIndex(0);panel.stage_kind.setCurrentIndex(0)
    panel.scope.setCurrentIndex(panel.scope.findData(False));panel.refresh_reference()
    for index in range(panel.entries.count()):
        item=panel.entries.item(index)
        if item.data(__import__('PySide6.QtCore',fromlist=['Qt']).Qt.ItemDataRole.UserRole)==identity:
            panel.entries.setCurrentRow(index)
            if panel.result is None or note_for(category,identity)!=content:return False
            window.show();window.raise_();window.activateWindow();return True
    panel.entries.setCurrentRow(-1);return False

def install(window):
    notes=window.player_notes;notes.openReference.connect(lambda content:open_reference(window,content))
    if window.diagnostic_layout:return
    for panel in window.common_reference_panels.values():
        if not any(category in KINDS for category in panel.allowed_categories):continue
        action=panel.query_menu.menu.addAction('为所选固定资料写笔记');action.setVisible(False);panel.reference_note_action=action
        def context(reader):
            row=(reader.result or{}).get('row',{});return note_for(row.get('category'),row.get('id'))
        def sync(reader=panel,entry=action):entry.setVisible(context(reader)is not None)
        def request(_checked=False,reader=panel):
            content=context(reader)
            if content is not None:open_note(window,content)
        panel.query_menu.menu.aboutToShow.connect(sync);action.triggered.connect(request)

