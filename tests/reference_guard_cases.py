"""Shared read-only public cases; no GUI, run state, network or private inputs."""
from pathlib import Path
from unittest.mock import patch
import json
from rouge import choice_recruitment_results as recruit,current_reward_reference as current,event_named_reward_links as links,moving_reward_reference as moving,peace_guardian_results as peace,resting_corner_results as resting,stage_entry_reference as entry,node_catalog as catalog,node_rewards
from rouge import current_event_directory,current_event_resources,current_event_item_uses
from tests.test_runtime_reference_review import outputs,battle,items,ritual

MODELS=[(recruit,'recruitment'),(current,'current-rewards'),(links,'event-named-links'),(moving,'moving-rewards'),(peace,'peace-guardian'),(resting,'resting-corner'),(entry,'stage-entry')]


def packets():return {m.__name__:(m.packet()if m is current else m.source_data())for m,_ in MODELS}


def cases():
    result={};data=packets();assert all(v is not None for v in data.values())
    result['source_packets']=data
    event=catalog._event(recruit.EVENT);result['recruitment']=[recruit.choice_reference(recruit.EVENT,event['scenes'][0]['choices'][1])]
    event=catalog._event(peace.EVENT);scene=event['scenes'][1];result['peace']=[peace.choice_result_reference(event,scene,scene['choices'][0])]
    result['event_named_links']=[links.event_named_reward_links(catalog._event(links.TARGET),node_rewards._reference()['event_rewards'])]
    result['resting']=[resting.resting_result_cards(resting.EVENT)]
    for card in data[resting.__name__]['cards']:
        for branch in card['branches']:result['resting'].append(resting.resting_result_scene(resting.EVENT,card['choice_key'],branch['branch_id']))
    result['stage_entry']=[entry.stage_entry_reference(entry.STAGE_ID)]
    result['moving']=[moving.moving_reward_rule([{'raw':{'id':moving.ENTITY,'useDb':True,'level':g,'overwrittenData':None}}])for g in [0,1,2,3,False]]+[moving.moving_reward_rule([])]
    ref=data[current.__name__];result['current_rewards']=[]
    with patch.object(current,'packet',return_value=ref):
        for sid in ref['current']['version']['current']['details']['stages']:result['current_rewards'].append(current.stage_rewards(sid))
    result['previously_restored']=sum((outputs(m)for m in [battle,items,ritual]),[])
    result['dependent_directory']=[m.packet()for m in [current_event_directory,current_event_resources,current_event_item_uses]]
    return result


def normalize(value,record):
    text=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
    for key in record['old_bindings']:
        for field in ['path','sha256']:text=text.replace(record['new_bindings'][key][field],record['old_bindings'][key][field])
    return text.encode('utf8')


def builder_reads(root,record):
    paths=set()
    for row in record['old_bindings'].values():
        manifest=json.loads((root/row['path']).read_bytes());paths.update(n for n in manifest.get('runtime_files',manifest['files'])if n.endswith('.py'))
    counts={p:0 for p in paths};original=Path.read_bytes
    def read(path):
        if path.is_relative_to(root):
            name=path.relative_to(root).as_posix()
            if name in counts:counts[name]+=1
        return original(path)
    with patch.object(Path,'read_bytes',read):assert all(packets().values())
    return counts
