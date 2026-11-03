from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1]
before=(ROOT/'rouge/node_catalog_view.py').read_bytes()
assert sha256(before).hexdigest()=='2e51d99f86bff9ca85e49db63493dc80ed488f815577defaa2db141c2dce123c'
source=before.decode('utf8').replace('\r\n','\n')
changes=[
 ('from .future_region_effects_view import FutureRegionEffectsPanel\n',
  'from .future_region_effects_view import FutureRegionEffectsPanel\nfrom . import named_reward_items\nfrom .named_reward_items_view import NamedRewardItemsPanel\n'),
 ('        self.future_region_window=None\n',
  '        self.future_region_window=None\n        self.named_reward_window=None\n'),
 ('        self.future_region_button.hide();self.future_region_button.clicked.connect(self.open_future_region_effects)\n',
  '        self.future_region_button.hide();self.future_region_button.clicked.connect(self.open_future_region_effects)\n'
  '        self.named_reward_button=QPushButton("查看具名奖励图文");rl.addWidget(self.named_reward_button)\n'
  '        self.named_reward_button.setToolTip("按具体选项查阅物品图标与完整说明；不代表本局已领取或生效。")\n'
  '        self.named_reward_button.hide();self.named_reward_button.clicked.connect(self.open_named_reward_items)\n'),
 ('        if not entry:text=\'没有符合筛选的资料。不能把资料缺失视为不可能出现。\'\n',
  '        named_packet=named_reward_items.event_reference(entry["record"].get("id")) if entry and entry["kind"]=="event" else None\n'
  '        named=bool(named_packet and named_packet.get("target") is True)\n'
  '        self.named_reward_button.setVisible(named)\n'
  '        self.named_reward_button.setEnabled(bool(named and named_packet.get("source_valid") is True))\n'
  '        if self.named_reward_window:\n'
  '            self.named_reward_window.set_reference(entry["record"]["id"] if named else None,scope_key=key if named else None)\n'
  '        if not entry:text=\'没有符合筛选的资料。不能把资料缺失视为不可能出现。\'\n'),
 ('    def open_future_region_effects(self):\n',
  '    def open_named_reward_items(self):\n'
  '        key=self.list.selected_key();entry=next((e for e in self.entries if e["key"]==key),None)\n'
  '        if not entry or entry["kind"]!="event":return\n'
  '        identity=entry["record"].get("id");packet=named_reward_items.event_reference(identity)\n'
  '        if not packet or packet.get("target") is not True or packet.get("source_valid") is not True:\n'
  '            self.named_reward_button.setEnabled(False)\n'
  '            if self.named_reward_window:self.named_reward_window.set_reference(None)\n'
  '            return\n'
  '        if self.named_reward_window is None:self.named_reward_window=NamedRewardItemsPanel(self)\n'
  '        self.named_reward_window.set_reference(identity,scope_key=key)\n'
  '        self.named_reward_window.show();self.named_reward_window.raise_();self.named_reward_window.activateWindow()\n\n'
  '    def open_future_region_effects(self):\n')]
for old,new in changes:
    assert source.count(old)==1,old
    source=source.replace(old,new)
ast.parse(source)
raw=source.replace('\n','\r\n').encode('utf8') if b'\r\n' in before else source.encode('utf8')
out=ROOT/'.cache/p3-301-parent/rouge/node_catalog_view.py';out.parent.mkdir(parents=True,exist_ok=True)
assert not out.exists();out.write_bytes(raw)
print(json.dumps({'draft':out.relative_to(ROOT).as_posix(),'sha256':sha256(raw).hexdigest(),'production_modified':False}))
