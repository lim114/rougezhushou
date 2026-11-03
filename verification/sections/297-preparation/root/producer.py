from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/p3-297-expedition-root'
assert not BASE.exists();(BASE/'rouge').mkdir(parents=True)
def patch_file(name,changes):
 raw=(ROOT/name).read_bytes();s=raw.decode().replace('\r\n','\n')
 for old,new in changes:
  assert s.count(old)==1,(name,old[:75]);s=s.replace(old,new,1)
 out=BASE/name;out.parent.mkdir(exist_ok=True,parents=True);out.write_bytes(s.replace('\n','\r\n').encode())
 return {'before':sha256(raw).hexdigest(),'after':sha256(out.read_bytes()).hexdigest()}
node=patch_file('rouge/node_catalog_view.py',[
 ('from . import documented_choice_items\n','from . import documented_choice_items\nfrom . import expedition_results\nfrom .expedition_results_view import ExpeditionResultsPanel\n'),
 ('        self.documented_item_window=None\n','        self.documented_item_window=None\n        self.expedition_window=None\n'),
 ('        self.documented_item_button.hide();self.documented_item_button.clicked.connect(self.open_documented_items)\n',
  '        self.documented_item_button.hide();self.documented_item_button.clicked.connect(self.open_documented_items)\n'
  '        self.expedition_button=QPushButton("查看派出、归来与休息结果");rl.addWidget(self.expedition_button)\n'
  '        self.expedition_button.hide();self.expedition_button.clicked.connect(self.open_expedition_results)\n'),
 ("        if not entry:text='没有符合筛选的资料。不能把资料缺失视为不可能出现。'\n",
  "        expedition=bool(entry and entry['kind']=='event' and entry['record'].get('id')==expedition_results.EVENT)\n"
  '        self.expedition_button.setVisible(expedition)\n'
  '        expedition_packet=expedition_results.event_reference(expedition_results.EVENT) if expedition else None\n'
  "        self.expedition_button.setEnabled(bool(expedition_packet and expedition_packet.get('source_valid')))\n"
  '        if self.expedition_window:\n'
  '            self.expedition_window.set_reference(expedition_results.EVENT if expedition else None,scope_key=key if expedition else None)\n'
  "        if not entry:text='没有符合筛选的资料。不能把资料缺失视为不可能出现。'\n"),
 ('    def open_resting_results(self):\n',
  '    def open_expedition_results(self):\n'
  "        key=self.list.selected_key();entry=next((e for e in self.entries if e['key']==key),None)\n"
  "        if not entry or entry['kind']!='event' or entry['record'].get('id')!=expedition_results.EVENT:return\n"
  '        packet=expedition_results.event_reference(expedition_results.EVENT)\n'
  "        if not packet or not packet.get('source_valid'):\n"
  '            if self.expedition_window:self.expedition_window.set_reference(None)\n'
  '            return\n'
  '        if self.expedition_window is None:self.expedition_window=ExpeditionResultsPanel(self)\n'
  '        self.expedition_window.set_reference(expedition_results.EVENT,scope_key=key)\n'
  '        self.expedition_window.show();self.expedition_window.raise_();self.expedition_window.activateWindow()\n\n'
  '    def open_resting_results(self):\n')])
helper='''def _expedition_choice_lines(reference):
    """Show known phases without applying a resource or a run action."""
    dispatch=reference.get('dispatch_reference')
    if not dispatch:
        return ['选择时（资料）：获得2希望；不派出干员。']
    lines=[f'派出期间：{dispatch["operator_count_reference"]}名干员暂时不能编入队伍。',
           '归来时点：原文为本区域结束、进入新区域；社区资料称下一层开始。特殊区域是否相同仍未确认。']
    item=reference.get('documented_return_item')
    if item:
        amounts='、'.join(str(r['quantity_reference'])+RESOURCES[r['resource']]
                         for r in reference['return_resource_references'])
        lines+=['归来时（资料）：'+amounts+'和'+_plain(item['name'])+'；不是派出时立即获得。',
                '进阶结果：这种源头探索不会使派出的干员进阶。',
                '可在下方派出结果入口中手动查看归来藏品的图标、用途与完整说明。',
                '科技“喙”与源头“仅获得”的关系尚未核验，不额外加算随机加工品。']
    else:
        lines+=['归来物资的具体内容、数量，以及是否进阶：尚未确认。']
    return lines


'''
player=patch_file('rouge/player_node_information.py',[
 ('import re\n','import re\nimport json\n'),
 ('from . import event_planning\n','from . import event_planning\nfrom . import expedition_results\n'),
 ('def _function_lines(record, context):\n',helper+'def _function_lines(record, context):\n'),
 ("    numbers = {scene['key']: number for number, scene in enumerate(scenes, 1)}\n",
  "    numbers = {scene['key']: number for number, scene in enumerate(scenes, 1)}\n"
  '    expedition=expedition_results.event_reference(event_id)\n'
  "    if expedition and expedition.get('source_valid'):\n"
  '        # Bind the actual reading graph as well as the fresh on-disk source.\n'
  "        original=json.dumps(expedition['expected_event']['scenes'],sort_keys=True,ensure_ascii=False,allow_nan=False)\n"
  '        current=json.dumps(scenes,sort_keys=True,ensure_ascii=False,allow_nan=False)\n'
  "        if current!=original:expedition={'source_valid':False}\n"
  "    expedition_rows={(r['scene_key'],r['choice_key']):r for r in expedition['rows']} if expedition and expedition.get('source_valid') else {}\n"
  "    expedition_note=expedition.get('return_explanatory_reference') if expedition and expedition.get('source_valid') else None\n"
  '    if expedition and not expedition.get("source_valid"):\n'
  "        lines.append('派出与归来资料暂时无法核对；保留原文，奖励时点和实际领取仍待确认。')\n"),
 ("            row = resources[choice['key']]\n",
  "            row = resources[choice['key']]\n"
  "            expedition_row=expedition_rows.get((scene['key'],choice['key']))\n"
  "            if expedition_note and (scene['key'],choice['key'])==(expedition_note['scene_key'],expedition_note['choice_key']):\n"
  "                lines+=['','【探索源头的归来说明】',_plain(choice.get('description')),\n"
  "                        '归来时（资料）：2希望和怦然信标；该干员不会进阶。',\n"
  "                        '这段是归来结果说明，不是另一个可点击的选择，也不是派出时的即时收益。']\n"
  '                continue\n'),
 ("            for reference in row['resource_references']:\n                lines.extend(_resource_lines(reference))\n            if not row['resource_references']:\n",
  '            if expedition_row:\n'
  '                lines.extend(_expedition_choice_lines(expedition_row))\n'
  '            else:\n'
  "                for reference in row['resource_references']:\n                    lines.extend(_resource_lines(reference))\n"
  "            if not row['resource_references'] and not expedition_row:\n")])
(BASE/'HANDOFF.json').write_bytes((json.dumps({'kind':'ROOT_INTEGRATION_CANDIDATE_NOT_EXECUTED','section':297,
 'existing_production_changes':{'rouge/node_catalog_view.py':node,'rouge/player_node_information.py':player},
 'production_changed':False,'Qt_tests_or_Git_executed':False},ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'root_candidate':str(BASE),'changes':[node,player],'production_changed':False}))
