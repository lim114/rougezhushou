"""Bind the complete exit table and keep each repeated document occurrence distinct."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document, Node, canonical, encoded
ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-exit-339'; DATA = 'rouge/data/current-exit.json'
CURRENT = 'research/p3-expansion-313/current-topic.json'; BASELINE = 'research/p3-expansion-313/baseline-topic.json'
LEGACY = 'rouge/data/node-catalog.json'; TITLE = '险路尽头'

def build(root=ROOT):
    root = Path(root); receipt = json.loads((root/PACK/'source-receipt.json').read_bytes())
    raw = (root/receipt['selected_file']).read_bytes()
    if receipt['revision'] != 352356 or len(raw) != receipt['selected_bytes'] or sha256(raw).hexdigest() != receipt['selected_sha256']:
        raise ValueError('Complete exact document section required')
    current = json.loads((root/CURRENT).read_bytes())['details']; old = json.loads((root/BASELINE).read_bytes())['details']
    tables = [n for n in Document(raw.decode()).root.walk() if n.tag == 'table']
    if len(tables) != 2 or canonical(tables[0].text()) != '调查中': raise ValueError('Keep investigation notice')
    originals = {g: {} for g in ('scenes', 'choices', 'items', 'stages')}; scenes = {}; choices = {}
    narrative_ids = []; entry = None; active = None; branch = False; pending = None; root_persuade = None
    for ri, tr in enumerate(n for n in tables[1].walk() if n.tag == 'tr'):
        for ci, cell in enumerate(n for n in tr.children if isinstance(n, Node) and n.tag in ('th', 'td')):
            text = canonical(cell.text()); loc = {'file': receipt['selected_file'], 'row': ri, 'cell': ci, 'cell_text_sha256': sha256(cell.text().encode()).hexdigest()}
            if not text or text == '主选项': continue
            if text in ('选项一', '选项二', '选项四', '选项五'):
                active = entry; pending = None; continue
            if text == '选项一分支':
                if root_persuade is None: raise ValueError('Branch before documented root choice')
                active = choices[root_persuade]['next_scene_id']; branch = True; pending = None; continue
            if text in ('分支1.1', '分支1.2'): continue
            if cell.tag == 'th':
                hits = [k for k, v in current['choiceScenes'].items() if v['title'] == TITLE and canonical(v['description']) == text]
                if len(hits) != 1: raise ValueError('Narrative must match complete original text')
                sid = hits[0]; originals['scenes'][sid] = deepcopy(current['choiceScenes'][sid]); narrative_ids.append(sid)
                context = 'document:exit-repeat-result' if sid in scenes else sid
                if context in scenes: raise ValueError('Unexpected third narrative occurrence')
                if pending is not None:
                    if choices[pending]['raw_next_scene_id'] != sid: raise ValueError('Documented followup disagrees with original')
                    choices[pending]['next_scene_id'] = context
                scenes[context] = {'id': context, 'raw_scene_id': sid, 'choice_ids': [], 'kind': 'document_narrative', 'source': loc}
                entry = entry or context; active = context; pending = None; continue
            candidates = {k: v for k, v in current['choices'].items() if text == canonical(v['title']+(v.get('description') or ''))
                          and (v['nextSceneId'] is None or current['choiceScenes'].get(v['nextSceneId'], {}).get('title') == TITLE)}
            if not candidates or active is None: raise ValueError('Full documented choice must match current original')
            signature = {(v['title'], v['description'], v['nextSceneId']) for v in candidates.values()}
            if len(signature) != 1: raise ValueError('Do not merge different followups')
            v = next(iter(candidates.values())); gid = 'document-choice:'+sha256((str(ri)+'\0'+str(ci)+'\0'+text).encode()).hexdigest()
            role = {'说服同伴': 'persuade_part', '召集同伴': 'recruit', '离开黑池': 'leave', '帮助倒下的探险家同伴': 'help', '进入下一区域': 'confirm'}[v['title']]
            choices[gid] = {'id': gid, 'title': v['title'], 'description': v['description'], 'scene_id': active,
                            'role': role, 'variant_ids': list(candidates), 'actual_variant_id': None,
                            'next_scene_id': v['nextSceneId'], 'raw_next_scene_id': v['nextSceneId'], 'stage_ids': [],
                            'document_parent_verified': True, 'gold_cost_reference': 10 if role == 'help' else None,
                            'actual_eligible': None, 'actual_received': None, 'source': loc}
            scenes[active]['choice_ids'].append(gid); originals['choices'].update(deepcopy(candidates))
            if role == 'persuade_part' and not branch: root_persuade = gid
            pending = gid if v['nextSceneId'] else None
    if pending is not None or len(choices) != 6 or len(scenes) != 6: raise ValueError('Keep all document occurrences and six choices')
    # These original choices have an explicit destination, but the document does not establish their parent.
    more = {k: v for k, v in current['choices'].items() if k not in originals['choices'] and v['title'] == '说服同伴'
            and v['description'] == '消耗全部行动力，转化为等量希望，进入下一区域'
            and v['nextSceneId'] in originals['scenes']}
    if len(more) != 2: raise ValueError('Exactly two source-only choices required')
    for cid, v in more.items():
        sid = 'original-only:'+cid
        scenes[sid] = {'id': sid, 'raw_scene_id': None, 'choice_ids': [cid], 'kind': 'original_followup_only', 'source': {'file': CURRENT, 'choice': cid}}
        choices[cid] = {'id': cid, 'title': v['title']+'（原件未写加工品，前置未知）', 'description': v['description'],
                        'scene_id': sid, 'role': 'persuade_no_part', 'variant_ids': [cid], 'actual_variant_id': None,
                        'next_scene_id': 'document:exit-repeat-result', 'raw_next_scene_id': v['nextSceneId'], 'stage_ids': [],
                        'document_parent_verified': False, 'gold_cost_reference': None, 'actual_eligible': None, 'actual_received': None,
                        'source': {'file': CURRENT, 'choice': cid}}
        originals['choices'][cid] = deepcopy(v)
    if (len(originals['scenes']), len(originals['choices']), len(choices), len(scenes)) != (5, 8, 8, 8): raise ValueError('Do not drop source variants')
    for c in originals['choices'].values():
        iid = (c.get('displayData') or {}).get('itemId')
        if iid: originals['items'][iid] = deepcopy(current['items'][iid])
    difficulty = next(v for v in current['difficulties'] if v['modeDifficulty'] == 'NORMAL' and v['grade'] == 16)
    if not difficulty['ruleDesc'].startswith('险路尽头不再获得加工品，'): raise ValueError('Difficulty16 rule changed')
    legacy = next(e for e in json.loads((root/LEGACY).read_bytes())['events'] if e['title'] == TITLE)
    links = []
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in originals['scenes']: continue
            before = canonical(s['description']); after = canonical(originals['scenes'][sid]['description'])
            if before != after and before.replace('……', '......') != after: raise ValueError('Legacy full narrative differs')
            links.append({'legacy_scene_key': s['key'], 'current_original_scene_id': sid, 'legacy_complete_description': s['description'],
                          'current_complete_description': originals['scenes'][sid]['description']})
    if len(links) != 4: raise ValueError('Require all four exact legacy narrative links')
    result = {'schema': 'current_exit_339_v1', 'game_commit': 'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',
              'event': {'id': 'exit', 'title': TITLE, 'entry_scene_id': entry, 'scene_ids': list(scenes), 'choice_ids': list(choices)},
              'scenes': scenes, 'choices': choices, 'originals': originals, 'difficulty16': deepcopy(difficulty),
              'complete_document_table': True, 'document_investigation_notice_retained': True, 'complete_game_option_pool': False,
              'actual_eligible': None, 'actual_variant': None, 'run_updated': False, 'source': receipt,
              'catalogue_binding': {'expected_legacy_event': legacy, 'expected_summary': {k: deepcopy(legacy[k]) for k in ('id','title','node_types','floors','natural','natural_reason','entry')},
                                    'exact_scene_links': links, 'current_event_id': 'exit'},
              'complete_selected_record_comparison_to_baseline': {g: {k: old['choiceScenes' if g=='scenes' else g].get(k)==v for k,v in values.items()} for g,values in originals.items()}}
    data = encoded(result); names = [CURRENT, BASELINE, LEGACY, PACK+'/source-receipt.json', PACK+'/source-notes.json', receipt['selected_file']]
    files = {n: {'bytes': len((root/n).read_bytes()), 'sha256': sha256((root/n).read_bytes()).hexdigest()} for n in names}
    files[DATA] = {'bytes': len(data), 'sha256': sha256(data).hexdigest()}
    return data, encoded({'schema': 'current_exit_339_manifest_v1', 'game_commit': result['game_commit'], 'files': files})

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if (ROOT/DATA).read_bytes()!=d or (ROOT/PACK/'runtime-manifest.json').read_bytes()!=m: raise ValueError('Build differs')
    else: (ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    print(json.dumps({'original_scenes':5,'original_choices':8,'document_choices':6,'source_only_choices':2,'reading_contexts':8,'manifest_sha256':sha256(m).hexdigest()}))
