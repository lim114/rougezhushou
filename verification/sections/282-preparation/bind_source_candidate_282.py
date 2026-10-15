"""Bind the 282 proposal's selected file evidence; not a functional section pass."""
import hashlib,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
reader=ROOT/'.cache/research/p2-native-current-263/read_metadata_static.py'
ns={'__file__':str(reader)}
exec(compile(reader.read_text(encoding='utf8').split('selected=[]\n')[0],str(reader),'exec'),ns)
sha=lambda raw:hashlib.sha256(raw).hexdigest()
expected={'dll':'583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5',
          'metadata':'d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f'}
assert sha(ns['binary'])==expected['dll'] and sha(ns['meta'])==expected['metadata']
artifacts={};methods={};byte_spans=[]
def read(relative):
    raw=(ROOT/relative).read_bytes();artifacts[relative]=sha(raw);return json.loads(raw)
def select(relative,wanted):
    data=read(relative)
    assert data['dll_sha256']==expected['dll'] and data['metadata_sha256']==expected['metadata']
    for m in data['methods']:
        mi=m['method'].get('metadata_method_index')
        if mi in wanted:
            methods[mi]={'origin':relative,**m}
def bind(source,offset,raw,label):
    off=int(offset,0) if isinstance(offset,str) else offset
    original=ns['binary'] if source=='dll' else ns['meta']
    assert original[off:off+len(raw)]==raw,(source,off,label)
    byte_spans.append({'source':source,'physical_offset':off,'raw_hex':raw.hex(),'label':label})
select('.cache/section282-preparation/attribute-notification-candidate.json',{64290,64291,66477,66699,66750,76035})
select('.cache/section282-preparation/attribute-notification-extra.json',{77706})
select('.cache/section282-preparation/attribute-data-candidate.json',{64269,64276,66409})
select('research/p2-recovery-attributes-273/source-proof.json',{64295,64296,64297,30777,30781})
# Init is already published; select the bounded slot0/overwrite/subscribe prefix,
# not a claim that all subsequent Init virtual callbacks have been closed.
select('research/p2-sp-initialization-276/source-proof.json',{66624})
assert 66624 in methods
init=methods[66624]
init['original_full_method_metrics']={k:init[k] for k in ('instruction_count','reachable_instruction_bytes','reachable_bytes_sha256','cfg_bounded_traversal_finished','limits','edges')}
init['instructions']=[i for i in init['instructions'] if 0x1806f5328<=int(i['address'],16)<=0x1806f54a3]
prefix_bytes=b''.join(bytes.fromhex(i['bytes']) for i in init['instructions'])
init['instruction_count']=len(init['instructions'])
init['reachable_instruction_bytes']=len(prefix_bytes)
init['reachable_bytes_sha256']=sha(prefix_bytes)
prefix_addresses={i['address'] for i in init['instructions']}
init['edges']=[e for e in init['edges'] if e['from'] in prefix_addresses]
init['selected_prefix_instruction_count']=len(init['instructions'])
init['selected_prefix_bytes_sha256']=sha(prefix_bytes)
init['scope']='SP slot0/raw14/dirty delegate construction prefix only; later Init is not traversed here'
init['cfg_bounded_traversal_finished']=False
init['whole_method_claim']=False
new_instructions={}
for mi,m in methods.items():
    for i in m['instructions']:
        raw=bytes.fromhex(i['bytes']);bind('dll',i['physical_offset'],raw,m['method']['Name']+'@'+i['address'])
        assert new_instructions.setdefault(i['address'],raw)==raw
        for rip in i.get('rip_data',[]):bind('dll',ns['offset'](int(rip['address'],16)),bytes.fromhex(rip['bytes8']),'RIP '+rip['address'])
    # Explicitly retain unclosed computed jumps: extractor queue completion does
    # not prove all switch targets or dynamic callback/dispatch targets.
    m['indirect_edges_not_traversed']=[e for e in m['edges'] if e['kind'] in ('indirect_jump','indirect_call')]
switch=read('.cache/section282-preparation/primary-inventory-282.json')['entity_dirty_switch']
for row in switch:bind('dll',row['physical_offset'],bytes.fromhex(row['raw_hex']),'Entity.OnAttributeDirty switch '+str(row['attribute']))
assert next(r for r in switch if r['attribute']==14)['target']=='0x1806f7701'
parameters=ns['records']('parameters','Iii');metadata=[]
for mi in sorted(methods):
    m=ns['methods'][mi];bind('metadata',ns['header']['methods'][0]+mi*32,struct.pack('<IiiiiI4H',*m),'method '+str(mi))
    params=[]
    for pi in range(m[3],m[3]+m[9]):
        p=parameters[pi];bind('metadata',ns['header']['parameters'][0]+pi*12,struct.pack('<Iii',*p),'param '+str(pi))
        params.append({'name':ns['string'](p[0]),'type':ns['typename'](p[2]),'index':pi})
    metadata.append({'index':mi,'name':ns['type_def_name'](m[1])+'$$'+ns['string'](m[0]),'return_type':ns['typename'](m[2]),'parameters':params,'slot':m[8]})
layouts=[]
wanted={'Torappu.Battle.Attributes':{'m_rawData','m_dataRange','m_overrideDataRange','m_cachedData','m_dirtyMask','onAttributeMarkedDirty'},
        'Torappu.Battle.Entity':{'m_spController'},'Torappu.AttributeType':{'SP_RECOVERY_PER_SEC','SP_RECOVER_RATIO'}}
for ti,td in enumerate(ns['types']):
    name=ns['type_def_name'](ti)
    if name not in wanted:continue
    bind('metadata',ns['header']['typeDefinitions'][0]+ti*92,struct.pack('<IIiiiiiIiiiiiiiii8HII',*td),name+' typedef')
    fields=[];pointer=ns['reg']['fields'][ti]
    for ordinal,fi in enumerate(range(td[8],td[8]+td[19])):
        f=ns['fields'][fi];fname=ns['string'](f[0])
        if fname not in wanted[name]:continue
        bind('metadata',ns['header']['fields'][0]+fi*12,struct.pack('<IiI',*f),name+'.'+fname)
        off=ns['offset'](pointer)+ordinal*4;raw=ns['binary'][off:off+4]
        bind('dll',off,raw,name+'.'+fname+' offset')
        default=ns['default_value'](fi)
        if default and 'raw' in default:bind('metadata',ns['header']['fieldAndParameterDefaultValueData'][0]+default['data_index'],bytes.fromhex(default['raw']),fname+' default')
        fields.append({'index':fi,'name':fname,'type':ns['typename'](f[1]),'offset':struct.unpack('<i',raw)[0],'default':default})
    layouts.append({'type_index':ti,'name':name,'fields':fields})
inherited={}
for relative in ('research/p2-recovery-attributes-273/source-proof.json','research/p2-sp-recovery-clock-274/source-proof.json','research/p2-skill-sp-increments-279/source-proof.json'):
    proof=read(relative);assert proof['dll_sha256']==expected['dll'] and proof['metadata_sha256']==expected['metadata']
    inherited[relative]={'sha256':artifacts[relative],'reused_without_new_full_audit':True}
for row in read('research/p2-sp-recovery-clock-274/source-proof.json')['range_attributes']:
    bind('metadata',row['physical_offset'],bytes.fromhex(row['raw_hex']),row['field']+' AttributeMeta raw')
report={'scope':'282 candidate source and design preparation, not section completion or runtime validation',
        'dll_sha256':expected['dll'],'metadata_sha256':expected['metadata'],'source_artifacts_sha256':artifacts,
        'methods':list(methods.values()),'method_metadata':metadata,'layouts':layouts,'entity_dirty_switch':switch,
        'byte_spans':byte_spans,'unique_instruction_count':len(new_instructions),'selected_method_count':len(methods),
        'byte_span_count':len(byte_spans),'all_selected_spans_rechecked_with_fresh_primary_reads':True,
        'whole_entity_dirty_cfg_closed':False,'SP14_and30_selected_branch_closed':True,
        'inherited_proofs':inherited,'new_independent_full_audit_of_inherited_proofs':False,
        'file_only':True,'game_dll_executed':False,'process_memory_read':False,'current_hotfix_equivalence_proven':False}
out=HERE/'source-candidate-proof-282.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
receipt={'status':'candidate_byte_binding_pass','source_proof_sha256':sha(out.read_bytes()),'methods':len(methods),
         'unique_instructions':len(new_instructions),'byte_spans':len(byte_spans),
         'production_or_tests_changed':False,'section282_complete':False}
(HERE/'source-candidate-readback-282.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(receipt))
