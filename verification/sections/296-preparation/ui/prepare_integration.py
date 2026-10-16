from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def prepare(name,changes):
    raw=(ROOT/'rouge'/name).read_bytes();ending='\r\n' if b'\r\n' in raw else '\n'
    text=raw.decode().replace('\r\n','\n')
    for old,new in changes:
        assert text.count(old)==1,(name,old[:70],text.count(old))
        text=text.replace(old,new,1)
    after=text.replace('\n',ending).encode();ast.parse(after,filename=name)
    target=HERE/'rouge'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(after)
    return {'path':'rouge/'+name,'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha256(after).hexdigest()}

battle=prepare('battle_view.py',[
 ('from .highland_top_view import HighlandTopDialog\n','from .highland_top_view import HighlandTopDialog\nfrom .battle_entry_reference_view import BattleEntryReferencePanel,entry_packet\n'),
 ('class BattlePreviewPanel(QWidget):\n    stageSelected=Signal(object)\n','class BattlePreviewPanel(QWidget):\n    stageSelected=Signal(object)\n    entryEventSelected=Signal(object)\n'),
 ('        self.branch_toggle=QCheckBox(\'展开特殊出怪条件与位置\');layout.addWidget(self.branch_toggle)\n',
  '        self.entry_reference_button=QPushButton("查看对应节点与进入方式资料");layout.addWidget(self.entry_reference_button)\n'
  '        self.entry_reference_button.hide();self.entry_reference_window=None\n'
  '        self.entry_reference_button.clicked.connect(self.open_entry_references)\n'
  '        self.branch_toggle=QCheckBox(\'展开特殊出怪条件与位置\');layout.addWidget(self.branch_toggle)\n'),
 ('    def open_highland_top(self):\n',
  '''    def _refresh_entry_reference(self):
        try:packet=entry_packet(self.current_stage)
        except (OSError,ValueError,KeyError,TypeError):packet=None
        self.entry_reference_button.setVisible(packet is not None)
        self.entry_reference_button.setEnabled(bool(packet and packet['result'].get('status')=='documented_reference'))
        if self.entry_reference_window:self.entry_reference_window.set_stage(self.current_stage)

    def open_entry_references(self):
        try:packet=entry_packet(self.current_stage)
        except (OSError,ValueError,KeyError,TypeError):packet=None
        if not packet or packet['result'].get('status')!='documented_reference':
            if self.entry_reference_window:self.entry_reference_window.set_stage(None)
            return False
        if self.entry_reference_window is None:
            self.entry_reference_window=BattleEntryReferencePanel(self)
            self.entry_reference_window.eventReferenceSelected.connect(self._request_entry_event)
        self.entry_reference_window.set_stage(self.current_stage)
        self.entry_reference_window.show();self.entry_reference_window.raise_();self.entry_reference_window.activateWindow()
        return True

    def _request_entry_event(self,token):
        from .battle_event_references import resolve_stage_event_reference
        row=resolve_stage_event_reference(self.current_stage,token)
        if not row:return False
        self.entryEventSelected.emit(copy.deepcopy(row['token']));return True

    def open_highland_top(self):
'''),
 ('    def render_rows(self,*_):\n        stage=battle_data()[\'stages\'].get(self.current_stage)\n',
  '    def render_rows(self,*_):\n        self._refresh_entry_reference()\n        stage=battle_data()[\'stages\'].get(self.current_stage)\n')])

app=prepare('app.py',[
 ('        self.battle_preview.stageSelected.connect(self.select_battle_stage)\n',
  '        self.battle_preview.stageSelected.connect(self.select_battle_stage)\n'
  '        self.battle_preview.entryEventSelected.connect(self.show_battle_event_reference)\n'),
 ('    def show_source_catalog_event(self,event_id):\n',
  '''    def show_battle_event_reference(self,token):
        from .battle_event_references import resolve_stage_event_reference
        stage_id=self.battle_preview.current_stage
        if not resolve_stage_event_reference(stage_id,token):return False
        if not self.node_catalog.open_battle_event_reference(stage_id,token):return False
        self.centralWidget().setCurrentWidget(self.node_catalog)
        if self.battle_preview.entry_reference_window:self.battle_preview.entry_reference_window.hide()
        return True

    def show_source_catalog_event(self,event_id):
''')])

node=prepare('node_catalog_view.py',[
 ('    def open_original_destination(self):\n',
  '''    def open_battle_event_reference(self,stage_id,token):
        from .battle_event_references import resolve_stage_event_reference
        reference=resolve_stage_event_reference(stage_id,token)
        if not reference:return False
        event_id=reference['event_id']
        event=next((e for e in catalog.all_events(include_indirect=True)['rows'] if e['id']==event_id),None)
        if event is None:return False
        details=catalog.event_details(event_id)
        scene=next((s for s in details['rows'] if s['key']==reference['scene_key']),None)
        if not scene or not any(c['key']==reference['choice_key'] for c in scene['choices']):return False
        self.show_directory()
        for control,value in ((self.kind,'event'),(self.floor,None),(self.node_type,None)):
            index=control.findData(value)
            if index<0:return False
            control.setCurrentIndex(index)
        self.search.setText(event['title']);self.refresh()
        index=next((i for i,e in enumerate(self.entries) if e['kind']=='event' and e['record']['id']==event_id),None)
        if index is None:return False
        self.list.setCurrentRow(index)
        for control,value in ((self.event_scene_filter,reference['scene_key']),
                              (self.event_choice_filter,reference['choice_key'])):
            index=control.findData(value)
            if index<0:return False
            control.setCurrentIndex(index)
        self.context_label.setText('从固定战斗手动查阅对应的完整事件选项；这只是资料对应，不表示本局已进入或已选择。')
        return True

    def open_original_destination(self):
''')])

player=prepare('player_node_information.py',[
 ('from .documented_choice_items import event_item_references\n',
  'from .documented_choice_items import event_item_references\nfrom .stage_entry_reference import stage_entry_reference\n'),
 ("    base = stage_base_rewards(stage_id)\n",
  "    entry_reference = stage_entry_reference(stage_id)\n"
  "    if entry_reference is not None:\n"
  "        reward_heading = lines[-2:]; lines = lines[:-2]\n"
  "        if entry_reference.get('status') == 'documented_reference':\n"
  "            floors = '、'.join(str(r['main_floor_reference']) for r in entry_reference['rows'] if type(r['main_floor_reference']) is int)\n"
  "            lines.extend(['', '【资料记录的关联入口】', '原始资料列出第' + floors + '层普通作战上的关联标记，另有原资料称为“假层”的单独记录。',\n"
  "                '可在战斗预览中点击“查看对应节点与进入方式资料”，阅读完整标记及相关藏品说明。',\n"
  "                '这不保证本局出现；假层不归到某个主层或秘境，实际标记位置和全部进入方式仍未确认。'])\n"
  "        else:\n"
  "            lines.append('补充进入方式资料暂时无法核对；保留关卡原说明，不把资料失效当作没有入口。')\n"
  "        lines.extend(['', *reward_heading])\n"
  "    base = stage_base_rewards(stage_id)\n")])

view=(HERE/'battle_entry_reference_view.py').read_bytes();ast.parse(view)
result={'section':296,'kind':'CACHE_UI_AND_FOUR_EXISTING_FILE_INTEGRATION_CANDIDATE',
        'files':[battle,app,node,player],
        'new_view':{'path':'rouge/battle_entry_reference_view.py','sha256':sha256(view).hexdigest(),'bytes':len(view)},
        'Qt_or_product_tests_executed':False,'old_qualification_sources_untouched':True}
(HERE/'HANDOFF.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result))
