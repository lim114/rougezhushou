from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,unquote
import json,hashlib,re

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT

class Node:
    def __init__(self,tag='',attrs=None):self.tag=tag;self.attrs=dict(attrs or []);self.children=[];self.parts=[]
    def text(self):return ''.join(self.parts).strip()
def walk(node):
    yield node
    for child in node.children:yield from walk(child)
def classes(node,cls):return cls in node.attrs.get('class','').split()
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.root=Node();self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        node=Node(tag,attrs);self.stack[-1].children.append(node)
        if tag not in ('link','br','img','hr','meta','input','wbr','area','base','embed','source','track','col','param'):
            self.stack.append(node)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,text):
        if self.stack[-1].tag not in ('script','style'):
            for node in self.stack:node.parts.append(text)

html_path=ROOT/'.cache/research/events-0.19/prts-events.html';raw=html_path.read_bytes()
catalog=json.loads((ROOT/'rouge/data/node-catalog.json').read_text(encoding='utf8'))
topicraw=(ROOT/'.cache/game-data/roguelike_topic_table.json').read_bytes();detail=json.loads(topicraw)['details']['rogue_6']
parser=Parser();parser.feed(raw.decode('utf8'))
groups=[n for n in walk(parser.root) if classes(n,'IS-event-data')]
assert len(groups)==len(catalog['events'])==38
records=[];all_original_choices={};counts={'groups':len(groups),'scenes':0,'choices':0,'battle_choices':0,'stage_page_anchors':0}
for gi,group in enumerate(groups):
    event=catalog['events'][gi];scenes=[n for n in group.children if classes(n,'scene')]
    assert len(scenes)==len(event['scenes'])
    for si,scene in enumerate(scenes):
        counts['scenes']+=1;known_scene=event['scenes'][si]
        assert scene.attrs.get('data-name')==event['title']
        choices=[n for n in scene.children if classes(n,'choose')]
        assert len(choices)==len(known_scene['choices'])
        for ci,choice in enumerate(choices):
            counts['choices']+=1;known=known_scene['choices'][ci]
            assert choice.attrs.get('data-title','')==known['title']
            links=[]
            for anchor in walk(choice):
                if anchor.tag!='a' or not anchor.attrs.get('href'):continue
                title=anchor.attrs.get('title') or unquote(anchor.attrs['href']).rsplit('/',1)[-1].replace('_',' ')
                if not title.startswith('ISW-'):continue
                code,sep,name=title.partition(' ')
                if not sep:continue
                matches=[{'stage_id':key,'name':stage['name'],'code':stage['code'],'difficulty':stage['difficulty'],
                          'level_id':stage['levelId'],'is_boss_parameter':stage['isBoss'],
                          'source_selector':'$.details.rogue_6.stages.'+key}
                         for key,stage in detail['stages'].items() if stage['code']==code and stage['name']==name]
                links.append({'title':title,'href':urljoin('https://prts.wiki',anchor.attrs['href']),
                              'anchor_text':anchor.text(),'stage_records':matches})
                counts['stage_page_anchors']+=1
            battle=choice.attrs.get('data-icon')=='battle'
            if battle:counts['battle_choices']+=1
            if links or battle:
                records.append({'event_id':event['id'],'event_title':event['title'],'scene_key':known_scene['key'],
                                'choice_key':known['key'],'choice_title':known['title'],'description':known['description'],
                                'conditional_text':known['conditional'],'attributes':choice.attrs,'stage_page_links':links,
                                'game_choice_ids':known['game_choice_ids'],'battle_icon':battle,
                                'community_choice_to_page_verified':bool(links),'actual_stage_instance_verified':False})
            for key in known['game_choice_ids']:
                all_original_choices[key]={k:detail['choices'][key][k] for k in ('id','title','description','lockedCoverDesc',
                    'type','nextSceneId','displayData','isHiddenChoice','forceShowWhenOnlyLeave')}

assert counts['scenes']==190 and counts['choices']==233
source={'url':catalog['sources']['cached_community_catalog']['url'],'revision':'427904',
        'sha256':hashlib.sha256(raw).hexdigest(),'scope':'exact fixed event DOM; current online page separately read'}
assert source['sha256']==catalog['sources']['cached_community_catalog']['sha256']
game_source={'url':'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json',
             'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','sha256':hashlib.sha256(topicraw).hexdigest()}
names={}
for key,item in detail['items'].items():names.setdefault(item['name'],[]).append(key)
for key,item in detail['relics'].items():
    if item.get('name'):names.setdefault(item['name'],[]).append(key)
name_ids={name:list(dict.fromkeys(ids)) for name,ids in names.items()}
data={'schema_version':1,'sources':{'event_catalog_dom':source,'original_game':game_source},'counts':counts,
      'battle_links':records,'original_choices':all_original_choices,
      'named_required_items':{name:name_ids.get(name,[]) for name in ('笼控器','怦然信标','沙盘α','沙盘β','植浆','犬植浆')},
      'limits':['事件页面链接只证实社区选项到关卡页面，不证明服务器场景脚本。',
                '同名同关卡文件原ID全部保留，不从ID前缀猜当前实例。',
                '原choices无battleInfo/stageID，nextSceneId只证实目标场景，不推出作战。']}
data['resource_item_ids']={key:detail['gameConst'].get(field) for key,field in {'hp':'hpItemId','max_hp':'maxHpItemId','gold':'goldItemId','hope':'populationItemId','shield':'shieldItemId'}.items()}
ap_ids=[key for key,item in detail['items'].items() if item['name']=='行动力']
assert len(ap_ids)==1
data['resource_item_ids']['ap']=ap_ids[0]
scrap_types=json.loads(topicraw)['modules']['rogue_6']['scrap']['scrapItemToType']
data['source_item_names']={key:{'name':item['name'],'type':item['type'],'scrap_category':scrap_types.get(key)} for key,item in detail['items'].items()}
(OUT/'rouge/data/event-planning-reference.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
receipt={'sources':data['sources'],'counts':counts,'scene_choice_binding':'Full source DOM group/scene/choice ordinals match all existing 38/190/233 catalog rows.',
         'original_choice_fields':list(next(iter(detail['choices'].values())).keys()),
         'stage_binding':'Exact wiki code+name then all original stage IDs/level files; ambiguous IDs retained.',
         'current_online_read':'2026-10-12 web open directly verified red-moss prerequisite, gold>50 condition and linked battles; fixed bytes remain revision427904.',
         'license_status':'Source license not newly verified; small factual parameter and link-reference extraction.',
         'unknowns':data['limits']}
(OUT/'research/p3-event-qualification/source-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(counts));print(json.dumps(data['named_required_items'],ensure_ascii=False))
