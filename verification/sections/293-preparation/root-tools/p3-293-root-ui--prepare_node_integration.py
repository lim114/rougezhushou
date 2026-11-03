from pathlib import Path
from hashlib import sha256
import ast,difflib,json
root=Path(__file__).resolve().parents[2]
original=(root/'rouge/node_catalog_view.py').read_bytes()
assert sha256(original).hexdigest()=='61c65384c2f9420cf43d134497406cdec0f65d85c507ae8da88403e639ac5791'
newline='\r\n' if original.count(b'\r\n')==original.count(b'\n') else '\n'
text=original.decode().replace('\r\n','\n')
changes=[(
 'from .seed_cultivation_view import SeedCultivationPanel\n',
 'from .seed_cultivation_view import SeedCultivationPanel\nfrom .resting_corner_view import RestingCornerPanel\n'),(
 '        self.seed_window=None;self.seed_origin_key=None\n',
 '        self.seed_window=None;self.seed_origin_key=None\n        self.resting_window=None\n'),(
 '        self.seed_button.hide();self.seed_button.clicked.connect(self.open_seed_cultivation)\n',
 '        self.seed_button.hide();self.seed_button.clicked.connect(self.open_seed_cultivation)\n'
 '        self.resting_button=QPushButton("查看随机选择的后续资料");rl.addWidget(self.resting_button)\n'
 '        self.resting_button.hide();self.resting_button.clicked.connect(self.open_resting_results)\n'),(
 '        if seed and self.seed_window and self.seed_origin_key==key:self.seed_window.set_context(self._event_context())\n',
 '        if seed and self.seed_window and self.seed_origin_key==key:self.seed_window.set_context(self._event_context())\n'
 "        resting=bool(entry and entry['kind']=='event' and entry['record'].get('id')=='community_group_023')\n"
 '        self.resting_button.setVisible(resting)\n'
 '        if self.resting_window:\n'
 "            self.resting_window.set_reference('community_group_023' if resting else None,scope_key=key if resting else None)\n"),(
 '    def open_seed_cultivation(self):\n',
 '    def open_resting_results(self):\n'
 "        key=self.list.selected_key();entry=next((row for row in self.entries if row['key']==key),None)\n"
 "        if not entry or entry['kind']!='event' or entry['record'].get('id')!='community_group_023':return\n"
 '        if self.resting_window is None:self.resting_window=RestingCornerPanel(self)\n'
 "        self.resting_window.set_reference('community_group_023',self.event_choice_filter.currentData(),scope_key=key)\n"
 '        self.resting_window.show();self.resting_window.raise_();self.resting_window.activateWindow()\n\n'
 '    def open_seed_cultivation(self):\n')]
for old,new in changes:
    assert text.count(old)==1,old
    text=text.replace(old,new,1)
dest=Path(__file__).resolve().parent/'rouge/node_catalog_view.py'
candidate=text.replace('\n',newline).encode('utf8')
dest.write_bytes(candidate);ast.parse(candidate)
ui=dest.with_name('resting_corner_view.py');ast.parse(ui.read_bytes())
diff=''.join(difflib.unified_diff(original.decode().splitlines(True),candidate.decode().splitlines(True),
 fromfile='a/rouge/node_catalog_view.py',tofile='b/rouge/node_catalog_view.py'))
dest.parent.parent.joinpath('node_catalog_view.py.diff').write_bytes(diff.encode('utf8'))
row={'scope':'cache only; no Qt/tests or production writes','before':sha256(original).hexdigest(),
 'candidate_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in (dest,ui)},'AST_only':True}
dest.parent.parent.joinpath('UI_HANDOFF.json').write_bytes((json.dumps(row,indent=2)+'\n').encode('utf8'))
print(json.dumps(row))
