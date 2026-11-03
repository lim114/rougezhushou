"""Fixed-file extraction only, no product queries, Qt, tests or live writes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scripts.build_expedition_results_297 import _Document,_text,_descendants

GAME='.cache/p3-287-event-research/fixed-game-topic.json'
MAIN='research/p3-stage-context/community-main.html'
CATALOG='rouge/data/node-catalog.json'
RULES={
    '安全的角落':{'event_ids':['community_group_037'],'excluded':[1],'wording':'※该节点不会在第I层出现'},
    '狭路相逢':{'event_ids':['community_group_028','community_group_029'],'excluded':[1,2,6],'wording':'※该节点不会在第I，II，VI层出现。'},
    '失与得':{'event_ids':['community_group_025'],'excluded':[1,6],'wording':'※该节点不会在第I，VI层出现。'},
    '误入奇境':{'event_ids':['community_group_027'],'excluded':[1,2,6],'wording':'※该节点不会在第I，II，VI层出现。'},
    '先行一步':{'event_ids':['community_group_024'],'excluded':[1,5,6],'wording':'※该节点不会在第I，V，VI层出现。'},
}


def pin(path):
    raw=(ROOT/path).read_bytes();return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def main():
    game_raw=(ROOT/GAME).read_bytes()
    assert hashlib.sha256(game_raw).hexdigest()=='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
    game=json.loads(game_raw);detail=game['details']['rogue_6']
    dev=game['customizeData']['rogue_6']['commonDevelopment']
    raw_catalog=json.loads((ROOT/CATALOG).read_bytes())
    doc=_Document((ROOT/MAIN).read_text(encoding='utf8'));selected=[]
    for name,rule in RULES.items():
        headers=[n for n in doc.nodes if n.tag=='ul' and _text(n).strip()=='事件 '+name]
        assert len(headers)==1,(name,len(headers))
        header=headers[0]
        block=next(n for n in doc.nodes if n.order>header.order and n.tag=='dl')
        paragraphs=[_text(n).strip() for n in _descendants(block) if n.tag=='dd']
        assert rule['wording'] in paragraphs,(name,paragraphs)
        type_records={key:value for key,value in detail['nodeTypeData'].items() if value['name']==name}
        assert len(type_records)==1
        events=[e for e in raw_catalog['events'] if e['id'] in rule['event_ids']]
        assert len(events)==len(rule['event_ids']) and all(e['node_types']==[name] for e in events)
        selected.append({'node_type':name,'documented_excluded_main_floors':rule['excluded'],
            'main_header':{'order':header.order,'text':_text(header).strip(),'attributes':header.attrs},
            'main_description_list':{'order':block.order,'text':_text(block).strip(),'paragraphs':paragraphs},
            'primary_node_type_records':type_records,'current_complete_catalog_events':events,
            'scope':'documented natural main-floor candidates only; not observed identity or special-region applicability',
            'actual_server_or_entry_script':None})
    tech={}
    for key in ('rogue_6_outbuff_7','rogue_6_outbuff_9'):
        tech[key]={'development':dev['developments'][key],
                   'native_relic_declaration_if_present':detail['relics'].get(key),
                   'necessary_negative_gate_proven':False,'account_actual_active':None}
    result={'kind':'node-environment-source-evidence-not-product-acceptance','checked_at':datetime.now(timezone.utc).isoformat(),
        'sources':{path:pin(path) for path in (GAME,MAIN,CATALOG,'rouge/data/technology-reference.json',
            'rouge/event_planning.py','rouge/node_catalog.py','tests/test_node_catalog.py')},
        'rules':selected,'technology_enabling_references':tech,
        'source_complete_table_selector':'$.customizeData.rogue_6.commonDevelopment.developments',
        'technology_statement_direction':'Known named enabling references; inactive->impossible is not established here.',
        'production_or_private_writes':False,'Qt_tests_GUI_game_chat_Git_mutation':False}
    output=HERE/'node-environment-source-evidence.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'path':str(output.relative_to(ROOT)),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'rules':[{'node_type':r['node_type'],'event_ids':[e['id'] for e in r['current_complete_catalog_events']],
                  'excluded':r['documented_excluded_main_floors']} for r in selected],
        'tech':tech},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
