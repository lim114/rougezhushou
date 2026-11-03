"""Build two fixed document-content reward links without network or game I/O."""
import argparse
from copy import deepcopy
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACKET = 'research/p3-event-named-rewards-289'
TARGET = 'community_group_007'
PINNED = {
    PACKET+'/bwiki-investigation.html':'26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908',
    PACKET+'/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
    PACKET+'/original-records.json':'37c22789a5a025a2c2304b7c41a23e9b0a09891bc56a82ba0deffd733f07d4c0',
    'rouge/data/node-catalog.json':'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
    'rouge/data/node-reward-reference.json':'f1cd64daf20efec4e1af1f751c43ca90c43cf99f51def59116edc32362e3800e',
}


class _Node:
    def __init__(self, tag, attrs, order):
        self.tag, self.attrs, self.order, self.children = tag, dict(attrs), order, []


class _Document(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = [_Node('root', [], -1)]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs, len(self.nodes))
        self.nodes.append(node)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _text(node):
    if isinstance(node, str):
        return node
    return ''.join(_text(child)+('\n' if isinstance(child,_Node) and child.tag in ('br','p','li') else '')
                   for child in node.children)


def _descendants(node, tag):
    for child in node.children:
        if isinstance(child, _Node):
            if child.tag == tag:
                yield child
            yield from _descendants(child, tag)


def _plain_game(value):
    return re.sub(r'<[@$][^<>]*>|</>', '', unescape(value or '')).strip()


def _bytes_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')


def build(root=ROOT):
    """Return output bytes; calling this function does not write any file."""
    root = Path(root)
    blobs = {}
    for relative, expected in PINNED.items():
        raw = (root/relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Fixed public input differs: '+relative)
        blobs[relative] = raw
    bw = blobs[PACKET+'/bwiki-investigation.html'].decode('utf-8')
    for field in ('wgRevisionId','wgCurRevisionId'):
        if re.findall(r'"'+field+r'"\s*:\s*(\d+)', bw) != ['349818']:
            raise ValueError('BWiki revision is not the reviewed complete response.')
    document = _Document(bw)
    headings = [n for n in document.nodes if n.tag in ('h2','h3')]
    indices = [i for i,n in enumerate(headings) if _text(n).replace('[编辑]','').strip() == '沉寂之屋']
    if len(indices) != 1:
        raise ValueError('Document event heading must be unique.')
    index = indices[0]
    end = headings[index+1].order if index+1 < len(headings) else len(document.nodes)
    tables = [n for n in document.nodes if n.tag == 'table' and headings[index].order < n.order < end]
    rows = []
    for table in tables:
        for tr in _descendants(table, 'tr'):
            rows.append([_text(c).strip() for c in tr.children if isinstance(c,_Node) and c.tag in ('td','th')])
    original = json.loads(blobs[PACKET+'/original-records.json'])
    catalog = json.loads(blobs['rouge/data/node-catalog.json'])
    rewards = json.loads(blobs['rouge/data/node-reward-reference.json'])
    event = next(e for e in catalog['events'] if e['id'] == TARGET)
    scene = event['scenes'][0]
    if (event['title'] != '沉寂之屋' or scene['key'] != TARGET+':scene:0'
            or rows[1][0] != scene['description']
            or rows[1][0] != original['choiceScenes']['scene_ro6_normal1_enter']['description']):
        raise ValueError('Full document entry prose differs; title alone cannot link.')
    links = {}
    checked = []
    expected_rewards = {}
    prts = blobs[PACKET+'/prts-events-427904.html'].decode('utf-8')
    for number, (docrow, cid, resource, amount) in enumerate([
        (2,'choice_ro6_normal1_1','hp',2),(4,'choice_ro6_normal1_2','gold',8)]):
        choice = scene['choices'][number]
        raw_choice = original['choices'][cid]
        title, result = rows[docrow][-1].split('\n',1)
        item_id = raw_choice['displayData']['itemId']
        item = original['items'][item_id]
        expected_result = f'消耗{amount}'+('目标生命值' if resource == 'hp' else '源石锭')+'，获得笼控器'
        if (title != raw_choice['title'] or title != choice['title'] or result != expected_result
                or result != _plain_game(raw_choice['description']) or choice['game_choice_ids'] != []
                or raw_choice['displayData']['type'] != 'ITEM' or raw_choice['displayData']['effectHintType'] != 'ITEM'
                or raw_choice['type'] != 'TRADE' or raw_choice['isHiddenChoice'] is not False
                or item_id != 'rogue_6_scrap_G_12' or item['id'] != item_id
                or item['name'] != '笼控器' or item['type'] != 'SCRAP'):
            raise ValueError('Full option result, item pointer or original type differs.')
        expression = r'<div class="choose" [^>]*data-title="'+re.escape(title)+r'"[^>]*><div class="desc1"[^>]*>.*?</div></div>'
        spans = list(re.finditer(expression,prts,re.DOTALL))
        if len(spans) != 1:
            raise ValueError('Exact old PRTS custom option markup must be unique.')
        span = spans[0]
        markup = span.group(0)
        if (unescape(re.sub(r'<[^>]*>','',markup)) != choice['description']
                or not all(name+'="'+value+'"' in markup for name,value in choice['attributes'].items())):
            raise ValueError('Original custom option markup differs from the fixed catalog.')
        reward = rewards['event_rewards'][cid]
        if (reward['choice_id'] != cid or reward['choice_title'] != title or reward['event_title'] != event['title']
                or reward['description'] != result or reward['reward'] != {
                    'item_id':item_id,'name':'笼控器','type':'SCRAP','quantity':None,
                    'quantity_status':'not_serialized_in_display_data'}):
            raise ValueError('Existing complete original reward reference differs.')
        expected_rewards[cid] = deepcopy(reward)
        source_reference = {'document_url':'https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录',
            'document_revision':'349818','document_section':'沉寂之屋','table_row_index':docrow,
            'document_title':title,'document_result':result,
            'original_choice_field':f'$.details.rogue_6.choices.{cid}',
            'original_item_pointer':f'$.details.rogue_6.choices.{cid}.displayData.itemId',
            'original_item_field':f'$.details.rogue_6.items.{item_id}',
            'original_source_sha256':original['source']['sha256'],
            'community_revision':'427904','community_choice_key':choice['key'],
            'original_source_scene_pointer_verified':False,'destination_used_to_infer_origin':False}
        links[choice['key']] = {'original_choice_id':cid,'scene_key':scene['key'],
            'documented_cost_reference':{'resource':resource,'quantity':amount,'actual_payment':None},
            'source_reference':source_reference}
        checked.append({'community_choice_key':choice['key'],'original_choice_id':cid,
            'document_table_row':docrow,'document_full_title':title,'document_full_result':result,
            'community_full_result':choice['description'],'prts_markup':markup,
            'prts_start_byte':len(prts[:span.start()].encode('utf-8')),
            'prts_end_byte':len(prts[:span.end()].encode('utf-8')),
            'prts_span_sha256':hashlib.sha256(markup.encode('utf-8')).hexdigest(),
            'content_match_verified':True,'source_scene_link_verified':False})
    sources = {'original_game':deepcopy(original['source']),
        'bwiki':{'url':'https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录','revision':'349818',
                 'sha256':PINNED[PACKET+'/bwiki-investigation.html'],'visible_content_date':'2026-07-27'},
        'fixed_catalog':deepcopy(catalog['sources']['cached_community_catalog'])}
    data = {'schema_version':1,'event_id':TARGET,'expected_event':deepcopy(event),
        'expected_existing_rewards':expected_rewards,'links':links,'sources':sources,
        'scope':'Document full-content corroboration for existing named SCRAP rewards; no original source-scene script or current execution claim.',
        'source_scene_link_verified':False,'full_reward_pool_known':False,'actual_reward':None,'probability':None}
    extraction = {'schema_version':1,'event_id':TARGET,'document_entry_full_prose':rows[1][0],
        'document_revision':'349818','community_revision':'427904','checked_links':checked,
        'original_origin_gap_reduction_claimed':False,'quantity_inferred':False}
    outputs = {'rouge/data/event-named-reward-links.json':_bytes_json(data),
               PACKET+'/extraction.json':_bytes_json(extraction)}
    files = {}
    for relative in [*PINNED,PACKET+'/README.md',PACKET+'/extract_original_records.py',
                     'scripts/build_event_named_reward_links_289.py',*outputs]:
        raw = outputs.get(relative)
        if raw is None:
            raw = (root/relative).read_bytes()
        files[relative] = {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    outputs[PACKET+'/source-manifest.json'] = _bytes_json({'schema_version':1,'files':files,
        'source_scope':'Archived community documentation and selected pinned original records; not live server or source-scene execution.'})
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    outputs = build()
    for relative, raw in outputs.items():
        target = ROOT/relative
        if args.check:
            if target.read_bytes() != raw:
                raise ValueError('Saved output does not reproduce: '+relative)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:
                stream.write(raw)
    manifest = outputs[PACKET+'/source-manifest.json']
    print(json.dumps({'checked_existing':args.check,'link_count':2,
        'manifest_sha256':hashlib.sha256(manifest).hexdigest(),'server_execution_verified':False}))


if __name__ == '__main__':
    main()
