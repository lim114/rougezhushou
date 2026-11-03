import copy
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PACKET=Path('/workspace/.continuation/p2-gummy-back-parser-source087')
BASE='9ef5a469673502754db3be320a8eece9a7fd18d4'
REL=Path('rouge/data/original-animation-references.json')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def serialize(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode('utf-8')
old_raw=(ROOT/'baseline'/REL).read_bytes()
old=json.loads(old_raw)
assert serialize(old)==old_raw, 'Baseline JSON must round-trip byte exactly before an additive change'
source_path=PACKET/'parse-Back-result.json'
source_raw=source_path.read_bytes()
source=json.loads(source_raw)
manifest=json.loads((PACKET/'public-artifacts-manifest087.json').read_text())
entry=next(x for x in manifest['files'] if x['source_path']==str(source_path))
assert len(source_raw)==entry['bytes'] and sha(source_raw)==entry['sha256']
assert source['orientation']=='Back' and source['skeleton']['spine_version']=='3.8.99'
assert source['resource']['sha256']=='09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2'
assert source['resource']['git_blob_sha1']=='473df5c69d7e3552f6937f749bd42dd9e974ca01'
assert source['resource']['bytes']==32563
assert [a['name'] for a in source['animations']]==['Attack','Default','Idle','Skill','Start']

# Existing build_original_animation_048.py policy, independently source checked.
# This is representation normalization only, not a new gameplay frame rule.
def frames(seconds):
    value=float(seconds)*30
    normalized=round(value) if abs(value-round(value))<=1e-5 else value
    return {'seconds':float(seconds),'raw_frames_30hz':value,
            'strict_ceil_frames_30hz':math.ceil(value),
            'representation_normalized_frames_30hz':normalized,
            'ceil_frames_30hz':math.ceil(normalized)}
records=[]
for animation in source['animations']:
    name=animation['name']
    events=[{'name':e['name'],**frames(e['seconds'])} for e in animation['events']]
    duration=frames(animation['duration_seconds'])
    on_attack=[e for e in events if e['name']=='OnAttack']
    reasons=[]
    if len(on_attack)!=1:reasons.append('not exactly one OnAttack event')
    elif not 0<on_attack[0]['seconds']<duration['seconds']:reasons.append('OnAttack must be strictly inside positive animation duration')
    if not ('Attack' in name or name.startswith('Skill')):reasons.append('not a named attack or skill animation')
    if 'Loop' in name:reasons.append('loop named animation requires separate lifecycle binding')
    if 'Begin' in name or 'End' in name or 'Restart' in name:reasons.append('transition animation requires separate lifecycle binding')
    if len(events)!=1:reasons.append('multiple or absent named events require separate binding')
    rec={'id':f'char_196_sunbr:Back:{name}','orientation':'Back','skin':'original','animation':name,
         'spine_version':source['skeleton']['spine_version'],'duration':duration,'events':events,
         'selectable_as_conventional_reference':not reasons,'unverified_reasons':reasons,
         'runtime_binding_verified':False,'source':{'url':source['resource']['source_url'],
         'sha256':source['resource']['sha256'],'git_blob':source['resource']['git_blob_sha1'],'bytes':source['resource']['bytes']}}
    if not reasons:
        windup=on_attack[0]['ceil_frames_30hz'];total=duration['ceil_frames_30hz']
        rec['preview']={'windup_frames':windup,'recovery_frames':total-windup,'animation_frames':total}
    records.append(rec)
new=copy.deepcopy(old)
profile=new['operators']['char_196_sunbr']
assert profile['missing_sources']==[{'orientation':'Back','reason':'Error: boneData cannot be null.'}]
assert len(profile['records'])==9 and all(r['orientation']=='Front' for r in profile['records'])
profile['records'].extend(records)
profile['missing_sources']=[]
all_records=[r for p in new['operators'].values() for r in p['records']]
new['counts']={'operators':len(new['operators']),'source_skeletons':old['counts']['source_skeletons'],
    'animations':len(all_records),'selectable_references':sum(r['selectable_as_conventional_reference'] for r in all_records),
    'unverified_or_transition_references':sum(not r['selectable_as_conventional_reference'] for r in all_records),
    'missing_skeletons':sum(len(p['missing_sources']) for p in new['operators'].values())}
assert new['counts']=={'operators':32,'source_skeletons':64,'animations':928,'selectable_references':162,'unverified_or_transition_references':766,'missing_skeletons':0}
assert len({r['source']['url'] for r in all_records})==64
new['source_additions']=[{
    'operator':'char_196_sunbr','orientation':'Back','record_ids':[r['id'] for r in records],
    'source_commit':old['source_commit'],'source_sha256':source['resource']['sha256'],
    'git_blob':source['resource']['git_blob_sha1'],'bytes':source['resource']['bytes'],
    'source_packet_manifest_sha256':sha((PACKET/'public-artifacts-manifest087.json').read_bytes()),
    'extraction_sha256':sha(source_raw),'official_reader_commit':'8b4844bd4b193ba9e54487ed397a777993cbad56',
    'official_reader_bundle_sha256':source['official_bundle_sha256'],
    'runtime_binding_inferred':False,
    'scope':'Newly reacquired source metadata only. Historical parser identity/root cause, exact EOF, rendering, native skill/normal/skin binding and lifecycle clocks remain unknown.'}]
assert new['selection_derivation']==old['selection_derivation']
new_raw=serialize(new)
byte_records=[]
for op,p in old['operators'].items():
    target=new['operators'][op]
    assert target['records'][:len(p['records'])]==p['records']
    if op!='char_196_sunbr':assert target==p
    for rec in p['records']:
        block='\r\n'.join('        '+line for line in json.dumps(rec,ensure_ascii=False,indent=2).splitlines()).encode()
        assert old_raw.count(block)==1 and new_raw.count(block)==1,rec['id']
        byte_records.append({'id':rec['id'],'bytes':len(block),'sha256':sha(block)})
assert len(byte_records)==923
out=ROOT/'draft'/REL
out.write_bytes(new_raw)
(ROOT/'added-Back-records.json').write_text(json.dumps({'version':1,'records':records},ensure_ascii=False,indent=2)+'\n')
(ROOT/'old-923-record-byte-preservation.json').write_text(json.dumps({'version':1,'record_count':923,'original_record_blocks_exactly_preserved':True,'records':byte_records},indent=2)+'\n')
receipt={'version':1,'baseline_commit':BASE,'target':str(REL),'old_bytes':len(old_raw),'old_sha256':sha(old_raw),'new_bytes':len(new_raw),'new_sha256':sha(new_raw),
    'source_packet_manifest_sha256':sha((PACKET/'public-artifacts-manifest087.json').read_bytes()),'extraction':entry,
    'old_records_byte_and_semantic_preserved':923,'added_records':5,'new_counts':new['counts'],'line_endings':'CRLF preserved',
    'historical_selection_derivation_unchanged':True,'source_skeleton_parser_calls':0,'application_or_helper_calls':0,'network_calls':0}
(ROOT/'data-generation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'added_records':5,'old_record_blocks_preserved':923,'counts':new['counts'],'new_sha256':sha(new_raw)}))
