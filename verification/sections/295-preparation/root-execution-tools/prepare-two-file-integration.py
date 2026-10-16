from pathlib import Path
from hashlib import sha256
import ast, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge import node_catalog as catalog
from rouge.player_node_information import node_information_text

DEST=ROOT/'.cache/p3-295-root-integration';DEST.mkdir(exist_ok=False)
baseline={'kind':'ACTUAL_PRE295_PUBLIC_QUERY_AND_PLAYER_OUTPUT_NOT_TEST_PASS','events':{},
          'node_catalog_sha256':sha256((ROOT/'rouge/node_catalog.py').read_bytes()).hexdigest()}
for event in catalog.all_events(include_indirect=True)['rows']:
    entry={'kind':'event','record':event}
    text=node_information_text(entry)
    baseline['events'][event['id']]={'reward_options':catalog.event_reward_options(event['id']),
        'player_sha256':sha256(text.encode()).hexdigest()}
(DEST/'pre295-query-baseline.json').write_bytes((json.dumps(baseline,ensure_ascii=False,indent=2)+'\n').encode())

def prepare(name,changes):
    raw=(ROOT/'rouge'/name).read_bytes();ending='\r\n' if b'\r\n' in raw else '\n'
    text=raw.decode().replace('\r\n','\n')
    for old,new in changes:
        assert text.count(old)==1,(name,old[:80],text.count(old))
        text=text.replace(old,new,1)
    after=text.replace('\n',ending).encode();ast.parse(after,filename=name)
    target=DEST/'rouge'/name;target.parent.mkdir(exist_ok=True)
    target.write_bytes(after)
    return {'path':'rouge/'+name,'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha256(after).hexdigest()}

player=prepare('player_node_information.py',[
    ('from . import event_planning\n','from . import event_planning\nfrom .documented_choice_items import event_item_references\n'),
    ("    rewards = {row['choice_id']: row for row in reward_options['rows']}\n",
     "    rewards = {row['choice_id']: row for row in reward_options['rows']}\n"
     "    documented_items = event_item_references(event_id)\n"
     "    item_references = (documented_items or {}).get('items', [])\n"
     "    if documented_items and documented_items.get('status') == 'unknown':\n"
     "        lines.append('补充物品资料暂时无法核对；可继续阅读选项原文，不表示该选项没有物品。')\n"),
    ("            conversion = row.get('ap_conversion_reference')\n",
     "            for reference in item_references:\n"
     "                if (reference.get('event_id') == event_id and reference.get('scene_key') == scene['key']\n"
     "                        and reference.get('choice_key') == choice['key']):\n"
     "                    lines.append('资料写明的物品：' + _plain(reference['name']) + '（收藏品）；数量与本局实际领取尚未确认。')\n"
     "                    lines.append('可通过下方“查看选项中的物品说明”入口阅读图标与用途；这不会选择游戏中的选项。')\n"
     "            conversion = row.get('ap_conversion_reference')\n")])

view=prepare('node_catalog_view.py',[
    ('from .resting_corner_view import RestingCornerPanel\n',
     'from .resting_corner_view import RestingCornerPanel\nfrom .documented_choice_item_view import DocumentedChoiceItemPanel\nfrom . import documented_choice_items\n'),
    ('        self.resting_window=None\n','        self.resting_window=None\n        self.documented_item_window=None\n'),
    ('        self.resting_button.hide();self.resting_button.clicked.connect(self.open_resting_results)\n',
     '        self.resting_button.hide();self.resting_button.clicked.connect(self.open_resting_results)\n'
     '        self.documented_item_button=QPushButton("查看选项中的物品说明");rl.addWidget(self.documented_item_button)\n'
     '        self.documented_item_button.setToolTip("查看该事件资料明确记载的物品；不代表当前筛选的选项或本局领取。")\n'
     '        self.documented_item_button.hide();self.documented_item_button.clicked.connect(self.open_documented_items)\n'),
    ("        if not entry:text='没有符合筛选的资料。不能把资料缺失视为不可能出现。'\n",
     "        documented=bool(entry and entry['kind']=='event' and entry['record'].get('id')==documented_choice_items.EVENT)\n"
     "        self.documented_item_button.setVisible(documented)\n"
     "        item_packet=documented_choice_items.event_item_references(documented_choice_items.EVENT) if documented else None\n"
     "        self.documented_item_button.setEnabled(bool(item_packet and item_packet.get('status')=='documented_reference'))\n"
     "        if self.documented_item_window:\n"
     "            self.documented_item_window.set_reference(documented_choice_items.EVENT if documented else None,scope_key=key if documented else None)\n"
     "        if not entry:text='没有符合筛选的资料。不能把资料缺失视为不可能出现。'\n"),
    ('    def open_resting_results(self):\n',
     "    def open_documented_items(self):\n"
     "        key=self.list.selected_key();entry=next((row for row in self.entries if row['key']==key),None)\n"
     "        if not entry or entry['kind']!='event' or entry['record'].get('id')!=documented_choice_items.EVENT:return\n"
     "        packet=documented_choice_items.event_item_references(documented_choice_items.EVENT)\n"
     "        if not packet or packet.get('status')!='documented_reference':\n"
     "            if self.documented_item_window:self.documented_item_window.set_reference(None)\n"
     "            return\n"
     "        if self.documented_item_window is None:self.documented_item_window=DocumentedChoiceItemPanel(self)\n"
     "        self.documented_item_window.set_reference(documented_choice_items.EVENT,scope_key=key)\n"
     "        self.documented_item_window.show();self.documented_item_window.raise_();self.documented_item_window.activateWindow()\n\n"
     "    def open_resting_results(self):\n")])
handoff={'section':295,'kind':'CACHE_ROOT_TWO_FILE_INTEGRATION_CANDIDATE','files':[player,view],
    'unchanged_node_catalog_and_old_reward_query':True,
    'reason':'Documented item reference is a separate reading API; it must not broaden the typed grant query.',
    'baseline_sha256':sha256((DEST/'pre295-query-baseline.json').read_bytes()).hexdigest(),
    'baseline_event_count':len(baseline['events']),'executed_tests_or_Qt':False}
(DEST/'HANDOFF.json').write_bytes((json.dumps(handoff,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(handoff,ensure_ascii=False))
