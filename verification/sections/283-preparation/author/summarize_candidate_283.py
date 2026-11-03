"""Read selected source bytes freshly and record investigation-only coverage."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
reader=ROOT/'.cache/research/p2-native-current-263/read_metadata_static.py'
ns={'__file__':str(reader)}
exec(compile(reader.read_text(encoding='utf8').split('selected=[]\n')[0],str(reader),'exec'),ns)
sha=lambda b:hashlib.sha256(b).hexdigest()
expected=('583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5',
          'd3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f')
assert (sha(ns['binary']),sha(ns['meta']))==expected
records=[];spans=[];ins={};artifacts={}
for name in ('common-panel-native-candidate.json','panel-writer-helper-candidate.json'):
    raw=(HERE/name).read_bytes();artifacts[name]=sha(raw)
    data=json.loads(raw)
    assert (data['dll_sha256'],data['metadata_sha256'])==expected
    for m in data['methods']:
        for i in m['instructions']:
            o=int(i['physical_offset'],0);b=bytes.fromhex(i['bytes']);assert ns['binary'][o:o+len(b)]==b
            assert ins.setdefault(i['address'],b)==b
            spans.append({'source':'dll','physical_offset':o,'raw_hex':b.hex()})
            for r in i.get('rip_data',[]):
                o=ns['offset'](int(r['address'],16));b=bytes.fromhex(r['bytes8']);assert ns['binary'][o:o+len(b)]==b
                spans.append({'source':'dll','physical_offset':o,'raw_hex':b.hex()})
        records.append({'index':m['method'].get('metadata_method_index'),'name':m['method']['Name'],
                        'address':hex(m['method']['Address']),'selected_instruction_count':m['instruction_count'],
                        'reachable_bytes_sha256':m['reachable_bytes_sha256'],
                        'whole_dynamic_callgraph_closed':False,'limits':m['limits']})
metadata=json.loads((HERE/'common-panel-field-attributes-283.json').read_bytes())
for r in metadata['fields']:
    o=r['physical_offset'];b=bytes.fromhex(r['raw_hex']);assert ns['meta'][o:o+len(b)]==b
    spans.append({'source':'metadata','physical_offset':o,'raw_hex':b.hex()})
for relative in ('rouge/catalog.py','rouge/relic_attributes.py','rouge/attribute_limits.py','rouge/estimate.py',
                 'rouge/operator_engine.py','rouge/calibration.py','rouge/relic_panel_diagnostics.py',
                 'rouge/recovery_attributes.py','rouge/sp_recovery_attribute_reference.py',
                 'research/p2-panel-levels/README.md'):
    artifacts[relative]=sha((ROOT/relative).read_bytes())
report={'status':'investigation_only','dll_sha256':expected[0],'metadata_sha256':expected[1],
        'selected_records':records,'unique_instructions':len(ins),'selected_byte_spans_fresh_checked':len(spans),
        'byte_spans':spans,'artifacts_sha256':artifacts,'whole_panel_mechanism_closed':False,
        'production_modified':False,'section283_started_or_complete':False,
        'file_only':True,'game_dll_executed':False,'process_memory_read':False,'chat_sent':False,
        'actual_runtime_inventory_clock_hotfix_unknown':True}
(HERE/'candidate-source-inventory-283.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:report[k] for k in ('status','unique_instructions','selected_byte_spans_fresh_checked','whole_panel_mechanism_closed','section283_started_or_complete')}))
