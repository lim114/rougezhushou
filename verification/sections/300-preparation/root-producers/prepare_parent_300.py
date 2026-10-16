from pathlib import Path
from hashlib import sha256
import ast, json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.cache/p3-300-parent'
original = (ROOT/'rouge/node_catalog_view.py').read_bytes()
assert sha256(original).hexdigest() == 'c6a7f25e00644c1ec1f6b6a2ad6517b29977207f32558be65ebc22957018f4bf'
source = original.decode('utf8').replace('\r\n', '\n')
replacements = [
 ('from .expedition_results_view import ExpeditionResultsPanel\n',
  'from .expedition_results_view import ExpeditionResultsPanel\nfrom . import future_region_effects\nfrom .future_region_effects_view import FutureRegionEffectsPanel\n'),
 ('        self.expedition_window=None\n',
  '        self.expedition_window=None\n        self.future_region_window=None\n'),
 ('        self.expedition_button.hide();self.expedition_button.clicked.connect(self.open_expedition_results)\n',
  '        self.expedition_button.hide();self.expedition_button.clicked.connect(self.open_expedition_results)\n'
  '        self.future_region_button=QPushButton("查看下一地区的影响");rl.addWidget(self.future_region_button)\n'
  '        self.future_region_button.setToolTip("分开查看两个选项记载的后续效果；不表示本局已选择或下一地区一定生效。")\n'
  '        self.future_region_button.hide();self.future_region_button.clicked.connect(self.open_future_region_effects)\n'),
 ('        if not entry:text=\'没有符合筛选的资料。不能把资料缺失视为不可能出现。\'\n',
  '        future=bool(entry and entry["kind"]=="event" and entry["record"].get("id")==future_region_effects.EVENT)\n'
  '        self.future_region_button.setVisible(future)\n'
  '        future_context=self._event_context(entry["record"]) if future else {}\n'
  '        future_packet=future_region_effects.event_reference(future_region_effects.EVENT,\n'
  '            mode=future_context.get("exploration_mode"),difficulty=future_context.get("difficulty")) if future else None\n'
  '        self.future_region_button.setEnabled(bool(future_packet and future_packet.get("source_valid")))\n'
  '        if self.future_region_window:\n'
  '            self.future_region_window.set_reference(future_region_effects.EVENT if future else None,\n'
  '                mode=future_context.get("exploration_mode"),difficulty=future_context.get("difficulty"),\n'
  '                scope_key=key if future else None)\n'
  '        if not entry:text=\'没有符合筛选的资料。不能把资料缺失视为不可能出现。\'\n'),
 ('    def open_expedition_results(self):\n',
  '    def open_future_region_effects(self):\n'
  '        key=self.list.selected_key();entry=next((e for e in self.entries if e["key"]==key),None)\n'
  '        if not entry or entry["kind"]!="event" or entry["record"].get("id")!=future_region_effects.EVENT:return\n'
  '        context=self._event_context(entry["record"])\n'
  '        packet=future_region_effects.event_reference(future_region_effects.EVENT,\n'
  '            mode=context.get("exploration_mode"),difficulty=context.get("difficulty"))\n'
  '        if not packet or packet.get("source_valid") is not True:\n'
  '            self.future_region_button.setEnabled(False)\n'
  '            if self.future_region_window:self.future_region_window.set_reference(None)\n'
  '            return\n'
  '        if self.future_region_window is None:self.future_region_window=FutureRegionEffectsPanel(self)\n'
  '        self.future_region_window.set_reference(future_region_effects.EVENT,\n'
  '            mode=context.get("exploration_mode"),difficulty=context.get("difficulty"),scope_key=key)\n'
  '        self.future_region_window.show();self.future_region_window.raise_();self.future_region_window.activateWindow()\n\n'
  '    def open_expedition_results(self):\n')]
for before, after in replacements:
    assert source.count(before) == 1, before
    source = source.replace(before, after)
ast.parse(source)
target = OUT/'rouge/node_catalog_view.py'
target.parent.mkdir(parents=True, exist_ok=True)
assert not target.exists()
raw = source.replace('\n','\r\n').encode('utf8') if b'\r\n' in original else source.encode('utf8')
target.write_bytes(raw)
print(json.dumps({'draft':str(target.relative_to(ROOT)),'sha256':sha256(raw).hexdigest(),
                  'existing_source_sha256':sha256(original).hexdigest(),'production_modified':False}))
