"""Bind documented table structure to unique current game text, never ID prefixes."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
from copy import deepcopy
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-sand-325'
DATA = 'rouge/data/current-sand-reference.json'
CURRENT = 'research/p3-expansion-313/current-topic.json'
TITLES = {'线人': 'informer', '好奇心与死': 'curiosity'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Node:
    def __init__(self, tag, attrs):
        self.tag = tag; self.attrs = dict(attrs); self.children = []; self.parent = None

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node('root', []); self.stack = [self.root]; self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs); node.parent = self.stack[-1]; node.parent.children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]; break

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def plain(text):
    text = (text or '').replace('\\n', '\n').replace('\r', '\n')
    return re.sub(r'<@[^>]+>|</>|<\$[^>]+>', '', text)


def canonical(text):
    return re.sub(r'\s+', '', plain(text))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def build(root=ROOT):
    root = Path(root); receipt = json.loads((root/PACK/'source-receipt.json').read_bytes()); envelope=receipt; receipt=receipt['bwiki']
    document_path = root/receipt['selected_file']; document_raw = document_path.read_bytes()
    if receipt['revision'] != 352356 or sha256(document_raw).hexdigest() != receipt['selected_sha256']:
        raise ValueError('Keep the actual selected revision352356 tables unchanged.')
    if len(document_raw) != receipt['selected_bytes'] or [v['title']for v in receipt['tables']] != list(TITLES):
        raise ValueError('The complete three selected tables are required.')
    current = json.loads((root/CURRENT).read_bytes())['details']
    nodes = list(Document(document_raw.decode('utf8')).root.walk())
    events = []; scenes = {}; choices = {}; originals = {'scenes': {}, 'choices': {}, 'items': {}, 'stages': {}}
    for title, event_id in TITLES.items():
        heads = [n for n in nodes if n.tag == 'h3' and n.attrs.get('id') == title]
        if len(heads) != 1:
            raise ValueError('One exact document heading required: ' + title)
        table = next(n for n in nodes[nodes.index(heads[0])+1:] if n.tag == 'table')
        rows = []
        for node in table.walk():
            if node.tag != 'tr': continue
            ancestor = node.parent
            while ancestor is not None and ancestor.tag != 'table': ancestor = ancestor.parent
            if ancestor is table:
                rows.append([c for c in node.children if isinstance(c, Node) and c.tag in ('td', 'th')])
        entry = None; selected_scene = None; pending = None; event_scenes = []; event_choices = []
        for ri, row in enumerate(rows):
            for ci, cell in enumerate(row):
                text = canonical(cell.text())
                locator = {'document': receipt['selected_file'], 'heading': title, 'row': ri, 'cell': ci,
                           'cell_text_sha256': sha256(cell.text().encode('utf8')).hexdigest(),
                           'cell_attributes': deepcopy(cell.attrs)}
                if not text or text == '主选项': continue
                if re.fullmatch('选项[一二三]', text):
                    if entry is None: raise ValueError('Document option precedes its entrance scene.')
                    selected_scene = entry; pending = None; continue
                if cell.tag == 'th':
                    matches = [key for key, value in current['choiceScenes'].items()
                               if value['title'] == title and canonical(value['description']) == text]
                    if len(matches) != 1: raise ValueError('Scene text is absent or ambiguous: ' + title)
                    sid = matches[0]
                    if sid in scenes: raise ValueError('A documented scene was repeated.')
                    if pending is not None and current['choices'][pending]['nextSceneId'] != sid:
                        raise ValueError('Document narrative contradicts exact nextSceneId.')
                    pending = None; selected_scene = sid
                    if entry is None: entry = sid
                    scenes[sid] = {'id': sid, 'event_id': event_id, 'choice_ids': [], 'source': locator}
                    originals['scenes'][sid] = deepcopy(current['choiceScenes'][sid]); event_scenes.append(sid)
                    continue
                candidates = [key for key, value in current['choices'].items()
                              if value.get('title') and text.startswith(canonical(value['title']) + canonical(value.get('description')))]
                if len(candidates) != 1 or selected_scene is None:
                    raise ValueError('Choice text is absent or ambiguous: ' + title)
                cid = candidates[0]; original = current['choices'][cid]
                if cid in choices: raise ValueError('Choice belongs to more than one documented scene.')
                target = original['nextSceneId']; stage_ids = []
                item_id = (original.get('displayData') or {}).get('itemId')
                if item_id is not None and item_id not in current['items']:
                    raise ValueError('Named item is absent from this exact current source.')
                choices[cid] = {'id': cid, 'event_id': event_id, 'scene_id': selected_scene,
                                'next_scene_id': target, 'stage_ids': stage_ids, 'item_id': item_id, 'source': locator}
                scenes[selected_scene]['choice_ids'].append(cid); event_choices.append(cid)
                originals['choices'][cid] = deepcopy(original)
                if item_id is not None: originals['items'][item_id] = deepcopy(current['items'][item_id])
                for sid in stage_ids: originals['stages'][sid] = deepcopy(current['stages'][sid])
                pending = cid if target is not None else None
        if pending is not None: raise ValueError('Document ends before a declared next scene.')
        if any(choices[c]['next_scene_id'] is not None and choices[c]['next_scene_id'] not in event_scenes for c in event_choices):
            raise ValueError('A documented branch leaves its exact event scope.')
        events.append({'id': event_id, 'title': title, 'entry_scene_id': entry,
                       'scene_ids': event_scenes, 'choice_ids': event_choices})
    for name in ('沙盘α','沙盘β'):
        ids=[k for k,v in current['items'].items()if v['name']==name and v['type']=='RELIC']
        if len(ids)!=1:raise ValueError('Unique exact current sand relic required.')
        originals['items'][ids[0]]=deepcopy(current['items'][ids[0]])
    prts=envelope['prts'];raw=(root/prts['selected_file']).read_bytes()
    if prts['revision']!=433770 or len(raw)!=prts['selected_bytes']or sha256(raw).hexdigest()!=prts['selected_sha256']:raise ValueError('Exact independent documented conditions required.')
    text=canonical(Document(raw.decode()).root.text())
    for phrase in('第Ⅱ层到第Ⅳ层','第Ⅴ层','2个为好奇心与死','1个为窥视箱中','同时持有两个','未标记时','消耗50源石锭','解锁本结局的相关选项和收藏品'):
        if phrase not in text:raise ValueError('Keep exact independent condition evidence.')
    if (len(events),len(scenes),len(choices),len(originals['items']),len(originals['stages']))!=(2,7,5,4,0):raise ValueError('Preserve two whole tables, all seven scenes/five choices and four original item records.')
    rewards={'choice_ro6_bomb1_1':{'kind':'named_relic','item_id':'rogue_6_relic_final_1','quantity':None,'pool':None},'choice_ro6_bomb1_2':{'kind':'加工品','item_id':None,'quantity':1,'quality':'珍贵','pool':None},'choice_ro6_end1_2':{'kind':'收藏品','item_id':None,'quantity':1,'pool':None}}
    for cid,row in choices.items():row['reward']=rewards.get(cid);row['cost_gold']=50 if cid=='choice_ro6_end1_1'else None
    if canonical(originals['choices']['choice_ro6_bomb1_1']['description'])!='获得沙盘α，让探索开启不同的方向':raise ValueError('Keep explicitly named reward, no default quantity.')
    old=json.loads((root/'research/p3-expansion-313/baseline-topic.json').read_bytes())['details']
    comparison={g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in rows.items()}for g,rows in originals.items()}
    result = {'schema': 'current_sand_325_v1', 'game_commit': 'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',
              'events': events, 'scenes': scenes, 'choices': choices, 'originals': originals,
              'source': envelope, 'complete_selected_record_comparison_to_baseline':comparison, 'complete_documented_tables': True, 'complete_game_option_pool': False,
              'original_game_parent_choice_script_restored': False, 'generation_prerequisites_restored': False,
              'actual_server_verified': False, 'actual_received': None, 'run_state_updated': False}
    data = encoded(result)
    names = [CURRENT, 'research/p3-expansion-313/baseline-topic.json', PACK+'/source-receipt.json', receipt['selected_file'], prts['selected_file']]
    files = {n: {'sha256': sha256((root/n).read_bytes()).hexdigest(), 'bytes': (root/n).stat().st_size} for n in names}
    files[DATA] = {'sha256': sha256(data).hexdigest(), 'bytes': len(data)}
    manifest = encoded({'schema': 'current_sand_325_manifest_v1', 'game_commit': result['game_commit'],
                        'files': files, 'current_version_packet_required': True})
    return data, manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    data, manifest = build()
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir/'current-sand-reference.json').write_bytes(data)
        (args.output_dir/'runtime-manifest.json').write_bytes(manifest)
    if args.check:
        assert (ROOT/DATA).read_bytes() == data and (ROOT/PACK/'runtime-manifest.json').read_bytes() == manifest
    print(json.dumps({'events': 2, 'scenes': 7, 'choices': 5, 'manifest_sha256': sha256(manifest).hexdigest()}))
