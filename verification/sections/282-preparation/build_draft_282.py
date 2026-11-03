"""Create only the owned 282 isolated prototype/public-source packet."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
packet=HERE/'research/p2-sp-recovery-attributes-282';packet.mkdir(parents=True,exist_ok=True)
(HERE/'rouge/data').mkdir(parents=True,exist_ok=True)
(HERE/'rouge/__init__.py').write_text('',encoding='utf8')
files={}
def copy(relative):
    raw=(ROOT/relative).read_bytes();target=HERE/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    files[relative]=sha(raw)
for name in ('recovery_attributes.py','sp_recovery_clock.py','regeneration_clock.py','mechanist_explosion_math.py',
             'skill_sp_increment_reference.py','catalog.py','shield_source_inventory.py'):
    copy('rouge/'+name)
for file in ('recovery-attribute-source.json','sp-recovery-clock-source.json','regeneration-clock-source.json'):
    relative='rouge/data/'+file;copy(relative)
    for key in json.loads((ROOT/relative).read_bytes())['source_artifacts_sha256']:
        copy(key)
# All current public279 guard files are pinned too, without traversing historical
# cache/private source paths mentioned in old provenance proof bodies.
for p in sorted((ROOT/'research/p2-skill-sp-increments-279').iterdir()):
    if p.is_file():copy(p.relative_to(ROOT).as_posix())
proof=(HERE/'source-candidate-proof-282.json').read_bytes();(packet/'source-proof.json').write_bytes(proof)
for name in ('SCHEMA.md','DESIGN.md'):
    raw=(HERE/name).read_bytes();(packet/name).write_bytes(raw)
    files['research/p2-sp-recovery-attributes-282/'+name]=sha(raw)

Q=1<<32
def reading(i,attr,value,*,dirty=False):
    c={'inventory_complete':True,'enumeration_normal':True,'modifiers':[],
       'raw_read':{'normal':True,'raw':value},'range_read':{'normal':True,'override':False,'metadata_range_matches':True,'lower_raw':None,'upper_raw':None},
       'cache_store_normal':True}
    return {'id':i,'attribute':attr,'ordinary_native_path':True,'attributes_exist':True,'dirty':dirty,
            'decoded_cache':{'normal':True,'raw':value},'calculation':c if dirty else None}
def ptr(i,*,array=False,length=40):
    p={'id':i,'normal':True,'exists':True,'identity':None}
    if array:p['length']=length
    return p
readings=[reading('init.refresh14',14,7*Q,dirty=True),reading('new14',14,2*Q,dirty=True),reading('new30',30,Q,dirty=True),
          reading('can14',14,Q),reading('can30',30,Q),reading('ratio-over-one',30,3*Q,dirty=True),reading('negative14',14,-Q,dirty=True)]
rates=[]
for i,prefix in (('new-rate','new'),('can-rate','can')):
    rates.append({'id':i,'ordinary_native_path':True,'first_attributes_getter_normal':True,'second_attributes_getter_normal':True,
        'flat_read_id':prefix+'14','ratio_read_id':prefix+'30','same_entity':True,'unchanged_to_point':True,'multiply_normally':True})
init={'id':'slot0-into-raw14','ordinary_native_path':True,'attributes_read':ptr('initial.attributes'),
      'sp_data_read':ptr('initial.spData'),'increments_read':ptr('initial.increments',array=True,length=4),
      'slot0_read':{'id':'initial.slot0','normal':True,'bits':0x3fc00000},'single_conversion_normally':True,
      'raw_array_read':ptr('initial.raw-array',array=True),'raw_encoder_normally':True,'raw_store_normally':True,
      'mark_dirty_returns_normally':True,'refresh_read_id':'init.refresh14','refresh_same_attributes':True,'refresh_unchanged_to_point':True}
drain={'id':'independent-OnTick-zero','kind':'tick','ordinary_native_path':True,'delta_raw':0,'enabled':False,
       'gate_stop':{'exists':True,'normal':True,'value':False},'full_read':{'normal':True,'value':False},
       'recovery':{'ordinary_native_path':True,'force':False,'stop_read':{'exists':True,'normal':True,'value':False},
                   'sp_read':{'exists':True,'normal':True,'raw':0},'setter_returns_normally':True}}
notify={'id':'dirty30-newrate-not-eligibility','attribute':30,'old_value_raw':99*Q,'ordinary_native_path':True,'entity_exists':True,
        'controller_read':ptr('notification.controller'),'new_rate_id':'new-rate','can_recover_rate_id':'can-rate',
        'ordinary_controller_update_path':True,'controller_matches_clock':True,'precise_timer_identity':True,
        'no_intervening_timer_changes':True,'timer':{'exists':True,'period_raw':Q,'remaining_raw':3*Q//4},'drain':drain}
example={'readings':readings,'rate_reads':rates,'initializations':[init],'notifications':[notify]}
raw=(json.dumps(example,ensure_ascii=False,indent=2)+'\n').encode('utf8');(packet/'public-example.json').write_bytes(raw)
files['research/p2-sp-recovery-attributes-282/public-example.json']=sha(raw)
primary=json.loads(proof)
manifest={'schema_version':1,'dll_sha256':primary['dll_sha256'],'metadata_sha256':primary['metadata_sha256'],
          'files_sha256':dict(sorted(files.items())),'proof_method_scope':'16 selected records, not16new whole methods',
          'inherited_full_proof_audit_repeated':False}
raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8');(packet/'source_manifest.json').write_bytes(raw)
template=(HERE/'core_template.py').read_text(encoding='utf8')
core=template.replace('__PROOF_SHA__',sha(proof)).replace('__MANIFEST_SHA__',sha(raw))
(HERE/'rouge/sp_recovery_attribute_reference.py').write_text(core,encoding='utf8')
receipt={'core_sha256':sha((HERE/'rouge/sp_recovery_attribute_reference.py').read_bytes()),'proof_sha256':sha(proof),'manifest_sha256':sha(raw),
         'bound_files':len(files),'owned_cache_only':True,'section282_complete':False}
(HERE/'draft-build-282.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(receipt))
