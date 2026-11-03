"""Build exact old-catalogue to current-reader reference links, never run identity."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,importlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-node-readers-332';DATA='rouge/data/current-node-readers.json';LEGACY='rouge/data/node-catalog.json'
PROVIDERS=[('rest','current_rest_travel','current-rest-travel.json'),('shop','current_unattended_shop','current-unattended-shop.json'),('resources','current_resource_events','current-resource-events.json'),('lake','current_lake','current-lake.json'),('encounters','current_encounters','current-encounters.json'),('sand','current_sand_reference','current-sand-reference.json'),('ritual','current_ritual_reference','current-ritual-reference.json'),('box','box_event_reference','box-event-reference.json'),('document','documented_event_flows','documented-event-flows.json')]
SUMMARY_KEYS=('id','title','node_types','floors','natural','natural_reason','entry')

def build(root=ROOT):
    root=Path(root);legacy=json.loads((root/LEGACY).read_bytes())['events'];selected={};current_sources={};unrepresented=[]
    for kind,module,file in PROVIDERS:
        data=json.loads((root/'rouge/data'/file).read_bytes());events=data.get('events')or[data['event']];events=list(events.values())if isinstance(events,dict)else events
        provider=importlib.import_module('rouge.'+module)
        for e in events:
            title=e['title']
            if title in selected:continue
            selected[title]=True;reference=provider.reference(e['id'])
            if reference is None or reference['event']!=e:raise ValueError('Current reader source must already be valid and equal the complete saved event.')
            originals={k:v for k,v in data['originals']['scenes'].items()if v['title']==title};rows=[old for old in legacy if old['title']==title]
            if not rows:unrepresented.append({'title':title,'reader':kind,'reason':'No existing event catalogue row; do not invent a row or map entry.'});continue
            current_sources[kind]={'module':module,'manifest':provider.MANIFEST,'manifest_sha256':provider.MANIFEST_SHA256,'data':provider.DATA}
            for old in rows:
                links=[{'legacy_scene_key':scene['key'],'current_original_scene_id':sid,'basis':'exact_original_scene_id_title_and_canonical_complete_narrative'}for scene in old['scenes']for sid in scene['game_scene_ids']if sid in originals and canonical(scene['description'])==canonical(originals[sid]['description'])]
                if not links:raise ValueError('A same title alone must never create a reader link.')
                key=old['id'];record={'legacy_event_id':key,'title':title,'expected_legacy_event':deepcopy(old),'expected_summary':{k:deepcopy(old[k])for k in SUMMARY_KEYS},'reader':kind,'current_event_id':e['id'],'current_event':deepcopy(e),'current_original_scenes':deepcopy(originals),'current_source_identity':json.loads(json.dumps(reference['source_identity'])),'exact_scene_links':links,'mapping_mode':'event_reference_only','actual_same_game_version':None,'actual_scene':None,'actual_choice':None,'run_updated':False}
                selected[key]=record
    bindings={k:v for k,v in selected.items()if type(v)is dict};counts={'catalogue_groups':len(bindings),'current_event_titles':len({r['title']for r in bindings.values()}),'reader_types':len(current_sources),'exact_scene_links':sum(len(r['exact_scene_links'])for r in bindings.values()),'unsupported_new_event_titles':len(unrepresented)}
    if counts!={'catalogue_groups':25,'current_event_titles':23,'reader_types':8,'exact_scene_links':116,'unsupported_new_event_titles':3}:raise ValueError('Reader coverage changed; audit before admission: '+str(counts))
    data={'schema':'current_node_readers_332_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','bindings':bindings,'current_sources':current_sources,'unsupported_new_events':unrepresented,'counts':counts,'actual_node_identity_restored':False,'actual_same_version':None,'run_updated':False,'all_source_events_bound':False};blob=encoded(data);ledger={'section':332,'kind':'integration_of_existing_verified_documents_no_new_mechanism','legacy_file':LEGACY,'legacy_bytes':len((root/LEGACY).read_bytes()),'legacy_sha256':sha256((root/LEGACY).read_bytes()).hexdigest(),'current_sources':current_sources,'same_title_alone_admitted':False,'reader_opens_event_overview_not_inferred_current_phase':True,'historical_and_current_map_context_not_applied_to_calculation':True};ledger_blob=encoded(ledger);files={LEGACY:{'bytes':len((root/LEGACY).read_bytes()),'sha256':sha256((root/LEGACY).read_bytes()).hexdigest()},DATA:{'bytes':len(blob),'sha256':sha256(blob).hexdigest()},PACK+'/source-ledger.json':{'bytes':len(ledger_blob),'sha256':sha256(ledger_blob).hexdigest()}};return blob,ledger_blob,encoded({'schema':'current_node_readers_332_manifest_v1','game_commit':data['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,l,m=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-node-readers.json').write_bytes(d);(args.output_dir/'source-ledger.json').write_bytes(l);(args.output_dir/'runtime-manifest.json').write_bytes(m)
    if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'source-ledger.json').read_bytes()==l and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
