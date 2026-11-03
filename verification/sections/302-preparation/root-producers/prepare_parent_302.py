from pathlib import Path
from hashlib import sha256
import ast,json

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.cache/p3-302-parent'
DEST.mkdir(parents=True,exist_ok=True)
name='rouge/node_catalog_view.py'
before=(ROOT/name).read_bytes()
assert sha256(before).hexdigest()=='65420d73c69c275d96b63b14274e7b481b5795ca7053ea9f1b0412027e659bf5'
text=before.decode('utf8')
def replace(old,new):
    global text
    assert text.count(old)==1,old[:60]
    text=text.replace(old,new)
eol='\r\n' if b'\r\n' in before else '\n'
replace('from .named_reward_items_view import NamedRewardItemsPanel'+eol,
        'from .named_reward_items_view import NamedRewardItemsPanel'+eol+
        'from . import ritual_weakening'+eol+'from .ritual_weakening_view import RitualWeakeningPanel'+eol)
replace('        self.named_reward_window=None'+eol,'        self.named_reward_window=None'+eol+'        self.ritual_weakening_window=None'+eol)
replace('        self.named_reward_button.hide();self.named_reward_button.clicked.connect(self.open_named_reward_items)'+eol,
        '        self.named_reward_button.hide();self.named_reward_button.clicked.connect(self.open_named_reward_items)'+eol+
        '        self.ritual_weakening_button=QPushButton("查看仪式条件与首领弱化");rl.addWidget(self.ritual_weakening_button)'+eol+
        '        self.ritual_weakening_button.setToolTip("逐项查阅条件效果，可手动打开相关作战；不代表本局已经提交或生效。")'+eol+
        '        self.ritual_weakening_button.hide();self.ritual_weakening_button.clicked.connect(self.open_ritual_weakening)'+eol)
anchor='        if not entry:text=\'没有符合筛选的资料。不能把资料缺失视为不可能出现。\''+eol
replace(anchor,
        '        ritual_packet=ritual_weakening.event_reference(entry["record"].get("id")) if entry and entry["kind"]=="event" else None'+eol+
        '        ritual=bool(ritual_packet and ritual_packet.get("target") is True)'+eol+
        '        self.ritual_weakening_button.setVisible(ritual)'+eol+
        '        self.ritual_weakening_button.setEnabled(bool(ritual and ritual_packet.get("source_valid") is True))'+eol+
        '        if self.ritual_weakening_window:'+eol+
        '            self.ritual_weakening_window.set_reference(entry["record"]["id"] if ritual else None,scope_key=key if ritual else None)'+eol+anchor)
anchor='    def open_named_reward_items(self):'+eol
method='''    def open_ritual_weakening(self):
        key=self.list.selected_key();entry=next((e for e in self.entries if e["key"]==key),None)
        if not entry or entry["kind"]!="event":return
        identity=entry["record"].get("id");packet=ritual_weakening.event_reference(identity)
        if not packet or packet.get("target") is not True or packet.get("source_valid") is not True:
            self.ritual_weakening_button.setEnabled(False)
            if self.ritual_weakening_window:self.ritual_weakening_window.set_reference(None)
            return
        if self.ritual_weakening_window is None:self.ritual_weakening_window=RitualWeakeningPanel(self)
        self.ritual_weakening_window.set_reference(identity,scope_key=key)
        self.ritual_weakening_window.show();self.ritual_weakening_window.raise_();self.ritual_weakening_window.activateWindow()

'''.replace('\n',eol)
# Use the established actual parent entry API, not an invented method.
assert '        key=self.list.selected_key();entry=next((e for e in self.entries if e["key"]==key),None)'+eol in text
replace(anchor,method+anchor)
ast.parse(text)
out=DEST/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(text.encode('utf8'))
archive=ROOT/'verification/sections/302-preparation/before'/name
archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(before)
(DEST/'parent-patch.json').write_text(json.dumps({'existing_production_file':name,'before_sha256':sha256(before).hexdigest(),'after_sha256':sha256(out.read_bytes()).hexdigest(),'production_not_modified':True},indent=2)+'\n',encoding='utf8')
print(json.dumps({'candidate':str(out),'sha256':sha256(out.read_bytes()).hexdigest(),'existing_parent_api_verified':True}))
