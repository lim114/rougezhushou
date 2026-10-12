"""Bind explicit leading ownership clauses; never reconstruct a source scene."""
from html.parser import HTMLParser
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CURRENT_SHA='e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8'

class Node:
    def __init__(self,tag='',attrs=()):self.tag=tag;self.attrs=dict(attrs);self.children=[];self.parts=[]
    def text(self):return ''.join(self.parts).strip()

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

def walk(node):
    yield node
    for child in node.children:yield from walk(child)

def has_class(node,name):return name in node.attrs.get('class','').split()

def plain(text):return re.sub(r'<[^>]*>','',text or '')

def top_level(text):
    depth=0;result=[]
    for char in plain(text):
        if char in '(（':depth+=1
        elif char in ')）':depth=max(depth-1,0)
        elif not depth:result.append(char)
    return ''.join(result)

def normalized_identity(text):return re.sub(r'^持有零件','持有',top_level(text))

def build(root=ROOT):
    root=Path(root);directory=root/'research/p3-choice-held'
    body=(directory/'current-events.html').read_bytes()
    assert hashlib.sha256(body).hexdigest()==CURRENT_SHA
    text=body.decode('utf8');assert '"wgRevisionId":440271' in text
    assert 'https://creativecommons.org/licenses/by-nc-sa/4.0/' in text
    catalog=json.loads((root/'rouge/data/node-catalog.json').read_text(encoding='utf8'))
    original=json.loads((root/'rouge/data/node-events.json').read_text(encoding='utf8'))
    primary=json.loads((directory/'original-choice-source.json').read_text(encoding='utf8'))
    item_reference=json.loads((root/'rouge/data/event-planning-reference.json').read_text(encoding='utf8'))
    assert primary['game_table_sha256']==original['source']['game_data']['sha256']
    assert primary['game_commit']==original['source']['commit']
    records=primary['choice_records'];assert len(records)==6
    original_rows={};names={}
    for identity,item in primary['item_records'].items():
        assert item_reference['source_item_names'][identity]['name']==item['name']
        assert item_reference['source_item_names'][identity]['type']==item['type']
        assert [key for key,value in item_reference['source_item_names'].items() if value['name']==item['name']]==[identity]
        names.setdefault(item['name'],[]).append(identity)
    for identity,record in records.items():
        known=original['choices'][identity]
        assert all(known[k]==v for k,v in record.items() if k in known)
        description=plain(record['description']);match=re.fullmatch(r'持有([^，]+)，(.+)',description)
        assert match
        name=match.group(1);ids=names[name];assert len(ids)==1
        original_rows[identity]={'record_id':identity,'description':record['description'],
            'source_text':'持有'+name,'required_item_name':name,'required_item_id':ids[0],
            'required_item_type':primary['item_records'][ids[0]]['type'],
            'source_selector':'$.details.rogue_6.choices.'+identity+'.description',
            'raw_record':record,'holding_is_consumption':False,'actual_consumed':None,
            'source_scene_link_verified':False,'next_scene_used_to_infer_source':False}
    parser=Parser();parser.feed(text)
    groups=[g for g in walk(parser.root) if has_class(g,'IS-event-data')]
    assert len(groups)==len(catalog['events'])==38
    rows={};counts={'groups':len(groups),'scenes':0,'choices':0,'top_level_owned_positions':0}
    nested=[]
    for gi,group in enumerate(groups):
        event=catalog['events'][gi];scenes=[s for s in group.children if has_class(s,'scene')]
        assert len(scenes)==len(event['scenes']);counts['scenes']+=len(scenes)
        for si,scene in enumerate(scenes):
            known_scene=event['scenes'][si];choices=[c for c in scene.children if has_class(c,'choose')]
            assert scene.attrs.get('data-name')==event['title'];assert len(choices)==len(known_scene['choices'])
            counts['choices']+=len(choices)
            for ci,choice in enumerate(choices):
                known=known_scene['choices'][ci]
                assert choice.attrs.get('data-title','')==known['title']
                description=''.join(c.text() for c in choice.children if has_class(c,'desc1'))
                assert description==known['description']
                if not description.startswith('持有'):
                    if '持有' in description:nested.append(known['key'])
                    continue
                assert ''.join(c.text() for c in scene.children if has_class(c,'sceneText'))==known_scene['description']
                match=re.match(r'^持有(?:零件)?([^，]+)，',description);assert match
                name=match.group(1);ids=names[name];assert len(ids)==1
                matches=[key for key,record in records.items() if record['title']==known['title']
                    and normalized_identity(record['description'])==normalized_identity(description)]
                assert matches
                rows[known['key']]={'choice_key':known['key'],'event_id':event['id'],'event_title':event['title'],
                    'scene_key':known_scene['key'],'choice_title':known['title'],'description':description,
                    'required_item_name':name,'required_item_id':ids[0],
                    'source_text':match.group(0).rstrip('，'),'required_item_type':primary['item_records'][ids[0]]['type'],
                    'community_attributes':choice.attrs,'original_content_reference_ids':matches,
                    'identity_relation':'literal_title_and_top_level_result_text_only',
                    'normalization':'Strip rich-text tags and parenthetical relic effects; leading 零件 is a category label.',
                    'source_scene_link_verified':False,'holding_is_consumption':False,'actual_consumed':None,
                    'primary_source_records':[original_rows[key] for key in matches]}
                counts['top_level_owned_positions']+=1
    assert counts=={'groups':38,'scenes':190,'choices':233,'top_level_owned_positions':5}
    assert len(nested)==1 and nested==['community_group_021:scene:0:choice:0']
    return {'schema_version':1,'sources':{
        'fixed_event_catalog':catalog['sources']['cached_community_catalog'],
        'current_event_document':{'url':'https://m.prts.wiki/w/沉沦者的黑流树海/事件一览',
            'revision':'440271','sha256':CURRENT_SHA,'whole_html_downloaded':True,
            'file':'research/p3-choice-held/current-events.html','license':'CC BY-NC-SA 4.0'},
        'original_game':original['source']['game_data']|{'commit':primary['game_commit']}},
        'counts':counts,'community_choices':rows,'original_choices':original_rows,
        'nested_effect_references_not_used_as_requirements':nested,
        'limits':['持有只证实具名物品门槛，不证明消耗、显示概率或实际服务器可选性。',
            '同值原选项文字不补来源场景；nextSceneId从未用于倒推源入口。',
            '仅五个明示顶部持有条件在两份文档相同；不声称整份当前服务器规则完成。',
            '收藏品与支援道具完整度不能证明零件缺失；生产输入只覆盖明确原ID范围。']}

if __name__=='__main__':
    data=build()
    (ROOT/'rouge/data/choice-held-reference.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'research/p3-choice-held/source-receipt.json').write_text(json.dumps({
        'sources':data['sources'],'counts':data['counts'],'original_owned_choices':len(data['original_choices']),
        'entry_unknowns_not_removed':{'scenes':25,'choices':57},
        'limits':data['limits'],'raw_markup_color_used_as_consumption_proof':False,
        'game_license':'Original game text and data remain Hypergryph copyright; factual extraction only.',
        'current_document_license':'CC BY-NC-SA 4.0, footer verified on captured full revision440271 body.'
    },ensure_ascii=False,indent=2)+'\n',encoding='utf8')
