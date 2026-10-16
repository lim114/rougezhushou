"""Pure-file source inventory for a possible P3 scope, not a test."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scripts.build_expedition_results_297 import _Document, _text

PATHS = ['rouge/data/node-catalog.json','rouge/data/event-planning-reference.json',
         'rouge/data/battle-node-pools.json','rouge/data/original-entry-reference.json',
         'research/p3-stage-context/community-main.html',
         'research/p3-choice-recruitment-290/prts-events-440271.html',
         '.cache/p3-287-event-research/fixed-game-topic.json']


def pin(name):
    raw=(ROOT/name).read_bytes()
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def main():
    pins={name:pin(name) for name in PATHS}
    data=json.loads((ROOT/PATHS[0]).read_bytes())
    plans=json.loads((ROOT/PATHS[1]).read_bytes())
    pools=json.loads((ROOT/PATHS[2]).read_bytes())
    entries=json.loads((ROOT/PATHS[3]).read_bytes())
    doc=_Document((ROOT/PATHS[4]).read_text(encoding='utf8'))
    main_excerpts=[]
    for node in doc.nodes:
        text=_text(node).strip() if node.tag in ('li','dd') else ''
        if any(term in text for term in ('该节点不会在','无法在先行一步中被选择','临时中介所',
                                       '相关加成后','不持有【怦然信标】')):
            main_excerpts.append({'tag':node.tag,'order':node.order,'text':text})
    events=[{'id':e['id'],'title':e['title'],'node_types':e['node_types'],'floors':e['floors'],
             'natural':e['natural'],'natural_reason':e['natural_reason'],
             'conditions':[{'scene_key':s['key'],'choice_key':c['key'],'title':c['title'],
                            'conditional':c['conditional']} for s in e['scenes'] for c in s['choices'] if c['conditional']]}
            for e in data['events']]
    unknown=[{'kind':'scene',**s} for s in data['unmapped_original_scenes']]+[
             {'kind':'choice',**c} for c in data['unmapped_original_choices']]
    result={'kind':'existing-gap-source-inventory-not-product-acceptance',
        'checked_at':datetime.now(timezone.utc).isoformat(),'source_pins':pins,
        'events':events,'node_function_sources':pools['node_functions'],
        'main_excerpts':main_excerpts,'unmapped_originals':unknown,
        'original_entry_record_ids':list(entries['records']),
        'remaining_unknown_counts':data['completeness'],'planning_reference_counts':plans['counts'],
        'Qt_test_game_chat_private_Git_mutation':False}
    target=HERE/'existing-event-gap-inventory.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'events':len(events),'function_types':[n['node_type'] for n in pools['node_functions']],
        'main_excerpt_count':len(main_excerpts),'unmapped':len(unknown),
        'non_encounter_events':[e for e in events if e['node_types']!=['不期而遇']]},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
