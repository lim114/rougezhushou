from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
cache=ROOT/'.cache/research/p2-native-current-263/sp-precise-preparation-274.json'
raw=cache.read_bytes();assert hashlib.sha256(raw).hexdigest()=='aac95f6a6c284868d25d73a89fc126f27ba827609dae327938d7b0f280bf7557'
d=json.loads(raw)
for p,h in d['source_artifacts_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
primary={'dll':Path('D:/Hypergryph Launcher/games/Arknights/GameAssembly.dll').read_bytes(),
 'metadata':Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()}
assert hashlib.sha256(primary['dll']).hexdigest()==d['dll_sha256']
assert hashlib.sha256(primary['metadata']).hexdigest()==d['metadata_sha256']
for s in d['byte_spans']:
 b=bytes.fromhex(s['raw_hex']);o=s['physical_offset'];assert primary[s['source']][o:o+len(b)]==b,s['label']
instructions={}
for m in d['methods']:
 assert m['cfg_bounded_traversal_finished'] and not m['limits']
 for i in m['instructions']:
  b=bytes.fromhex(i['bytes']);o=i['physical_offset'];assert primary['dll'][o:o+len(b)]==b
  assert instructions.setdefault(i['address'],b)==b
assert len(instructions)==2252 and len(d['methods'])==50 and len(d['byte_spans'])==3518
out=ROOT/'research/p2-sp-recovery-clock-274';out.mkdir(parents=True,exist_ok=True);(out/'source-proof.json').write_bytes(raw)
bindings=['research/p2-sp-recovery-clock-274/source-proof.json','rouge/mechanist_explosion_math.py',
 'rouge/regeneration_clock.py','rouge/data/regeneration-clock-source.json']
manifest={'scope':'Source-bound natural SP Precise batch ticks and independent request/rate declarations; not actual SP/timer/skill acceptance',
 'source_artifacts_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in bindings},
 'primary_source_sha256':{'dll':d['dll_sha256'],'metadata':d['metadata_sha256']},
 'facts':d['facts'],'supported_division_subdomain':d['supported_division_subdomain'],'public_literal_reference':d['public_literal_reference'],
 'actual_state_unknown':d['remaining_unknown'],'method_count':50,'unique_instruction_count':2252,'source_span_count':3518,
 'file_only':True,'game_dll_executed':False,'process_memory_read':False,'hotfix_equivalence_proven':False}
mp=ROOT/'rouge/data/sp-recovery-clock-source.json';mp.write_bytes((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print({'source_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'methods':50,'instructions':2252,'spans':3518,'preparation_artifacts':len(d['source_artifacts_sha256'])})
