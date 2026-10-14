"""Independent file-byte source review; no game-code execution or state reads."""
from pathlib import Path
import hashlib,json,mmap,struct

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'.cache/research/p2-skill-data-modifiers-278'
OUTPUT=Path(__file__).resolve().parent
files=('skill-data-modifier-first-278.json','rounding-native-helpers-278.json',
       'skill-data-modifier-dependencies-278.json','targeted-type-metadata-278.json',
       'intel-arithmetic-source.json','intel-sdm-vol1-dec2024.pdf')
artifacts={name:hashlib.sha256((INPUT/name).read_bytes()).hexdigest() for name in files}
selected=[]
for name,indices in ((files[0],{85326,85329,85835}),(files[1],None),(files[2],{84880,84998})):
    document=json.loads((INPUT/name).read_text(encoding='utf-8'))
    for method in document['methods']:
        if indices is None or method['method'].get('metadata_method_index') in indices:
            selected.append(method)
instructions={i['address']:i for m in selected for i in m['instructions']}
dll_path=Path(r'D:\Hypergryph Launcher\games\Arknights\GameAssembly.dll')
with dll_path.open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as binary:
    dll_hash=hashlib.sha256(binary).hexdigest()
    if dll_hash!='583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5':
        raise RuntimeError('Primary DLL SHA changed.')
    pe=struct.unpack_from('<I',binary,0x3c)[0]
    section_count=struct.unpack_from('<H',binary,pe+6)[0]
    optional_size=struct.unpack_from('<H',binary,pe+20)[0]
    table=pe+24+optional_size
    sections=[]
    for k in range(section_count):
        at=table+40*k
        virtual_size,rva,raw_size,offset=struct.unpack_from('<IIII',binary,at+8)
        sections.append((rva,max(virtual_size,raw_size),offset,raw_size))
    def offset(va):
        relative=va-0x180000000
        for rva,size,at,raw_size in sections:
            if rva<=relative<rva+size and relative-rva<raw_size:return at+relative-rva
        raise RuntimeError('RIP address is not file-backed: '+hex(va))
    spans=[]
    for instruction in instructions.values():
        at=int(instruction['physical_offset'],16);expected=bytes.fromhex(instruction['bytes'])
        if binary[at:at+len(expected)]!=expected:raise RuntimeError('Instruction differs: '+instruction['address'])
        spans.append({'source':'dll','physical_offset':at,'raw_hex':expected.hex(),'label':instruction['address']})
    rip={}
    for instruction in instructions.values():
        for observation in instruction.get('rip_data',[]):
            va=int(observation['address'],16);expected=bytes.fromhex(observation['bytes8'])
            if binary[offset(va):offset(va)+len(expected)]!=expected:raise RuntimeError('RIP data differs: '+hex(va))
            rip[(va,expected)]=True
    for va,expected in rip:
        spans.append({'source':'dll','physical_offset':offset(va),'raw_hex':expected.hex(),'label':'RIP '+hex(va)})
metadata_path=Path(r'D:\Hypergryph Launcher\games\Arknights\Arknights_Data\il2cpp_data\Metadata\global-metadata.dat')
metadata_sha=hashlib.sha256(metadata_path.read_bytes()).hexdigest()
if metadata_sha!='d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f':
    raise RuntimeError('Primary metadata SHA changed.')
intel=json.loads((INPUT/'intel-arithmetic-source.json').read_text(encoding='utf-8'))
if artifacts['intel-sdm-vol1-dec2024.pdf']!=intel['sha256']:raise RuntimeError('Intel cached PDF differs.')
report={'scope':'278 preparation source facts only, not a product implementation or completed section.',
        'file_only':True,'game_dll_executed':False,'game_process_memory_read':False,
        'source_artifacts_sha256':artifacts,'dll_sha256':dll_hash,'metadata_sha256':metadata_sha,
        'selected_methods':selected,'selected_method_count':len(selected),
        'unique_instruction_count':len(instructions),'fresh_raw_byte_spans':spans,
        'fresh_raw_byte_span_count':len(spans),'fresh_primary_bytes_matched':True,
        'official_intel_source':{'url':intel['url'],'sha256':intel['sha256'],
          'reviewed_sections':['4.8.4/4.8.4.1/4.8.4.2','10.2.3.1–10.2.3.4'],
          'online_primary_text_checked':True,'game_current_MXCSR_proven':False},
        'facts':[
          {'method':85326,'fact':'Independently decodedInt32 spCost ->CVTDQ2PS ->MULSS with independent TryGetFloat result ->raw unnamed helper18059e290 ->Int32 encoder ->20-byte spCost copy. TryGetFloat false skips; absent skillData skips. No Entity.UpdateSpData or numeric nonnegative clamp appears.'},
          {'method':85329,'fact':'Same source field/prefix but ADDSS. Each call rounds separately before protected encoding. No common combined modifier expression or cost floor is proved.'},
          {'method':85835,'fact':'GetFloat result, not TryGetFloat fallback. CVTDQ2PS/MULSS ->Single widened toDouble ->inline sign/fraction/parity/floor/ceil path ->CVTTSD2SI32 ->encoder ->20-byte spCost copy. No minimum0/1 clamp appears.'},
          {'helper':'0x18059e290','metadata_identity':None,'fact':'Raw observed helper converts Single toDouble. Modf-like helper tests fractional +/-0.5; integral parity selects unchanged even or +/-1 odd. Other positive/negative values use floor(x+0.5)/ceil(x-0.5). Returned safe-domain value is tie-to-even, not a metadata-named Unity.Mathf.RoundToInt.'},
          {'method':84998,'fact':'Independent first data.spData/cost decode ->low32 signedIMUL by Int32 _spScale ->encoder ->20-byte copy ->owner read ->second independent data read ->data and raw-owner NULL checks ->Entity.UpdateSpData(secondData.spData,onlyUpdateSpCost=true). No Single/percentage/scale-count arithmetic here.'},
          {'method':84880,'fact':'Independent first data read then Int32 cost encoder BEFORE first spData nullcheck; after20-byte copy, modifyType true reads second data and writes spType. First owner is tested by independent Unity truthiness; valid result then reads second owner and third data before raw NULL checks and Entity.UpdateSpData(thirdData.spData,onlyUpdateSpCost=!modifyType).'}],
        'recommended_closed_group':[
          'Independent per-source cost/pre-encoder reference for CdMul/CdAdd/CostMul; require typed cost/Single bits/read normality/native path, and independently qualified floating operation results or exact finite arithmetic subdomain.',
          'Raw unnamed Single-round helper: only finite qualified safe-domain conversion to signed32; no invented helper metadata identity. Keep NaN/infinity/out-of-range/exception state unknown.',
          'SpScale low32 IMUL and direct typed replacement in ModifySpData; separate encoding/copy/instance qualifications and source-accurate future-callUnknown versus confirmed skipped calls.',
          'Display independent UpdateSpData argument links to276 only when data/owner identity and absence of intervening changes are qualified. Do not overwrite existing reads or infer protected roundtrip.'],
        'numeric_domain':{
          'integer_input':'signed32; CVTDQ2PS need exact representability or independently declared result bits and operation normality. MAX32 is not exactly Single.',
          'single_operation':'MULSS/ADDSS depend on MXCSR RC for inexact results; FTZ/DAZ and exception masks matter. Do not use host Python round-nearest as actual game state.',
          'final_helper':'Given finite normal Single (or independently qualified widening), helper normality and signed32 rounded result domain, rounding integer is nearest/even. Restrict denormal widening unless DAZ or final-operation qualification is independently proved.',
          'negative_values':'Source contains no nonnegative clamp; negative supported typed inputs remain negative if safe/qualified.',
          'wrap':'SpScale integer product is low32 signed wrap, not saturation.'},
        'public_conditional_literals_not_native_execution':[
          {'cost':3,'operand_bits':'0x3fc00000','operation':'multiply','exact_single':4.5,'encoder_input':4},
          {'cost':-3,'operand_bits':'0x3fc00000','operation':'multiply','exact_single':-4.5,'encoder_input':-4},
          {'cost':10,'operand_bits':'0x3d4ccccd','operation':'multiply','conditions':{'RC_nearest':'Single0.5 ->helper0','RC_upward':'Single0.5000000596046448 ->helper1'},'actual_game_RC':None},
          {'cost':16777217,'operand_bits':'0x3f800000','operation':'multiply','conditions':{'RC_nearest':'Int32->Single16777216 ->helper16777216','RC_upward':'Int32->Single16777218 ->helper16777218'},'actual_game_RC':None},
          {'input_cost':2147483647,'scale':2,'signed32_imul_argument':-2}],
        'remaining_unknown':[
          'Actual attached relic/rune, call order, concrete metadata/blackboard keys and live callbacks.',
          'Actual MXCSR RC/DAZ/FTZ/masks, protected keys, encoder payload and later independently decoded spCost.',
          'Actual Entity/SkillData/SpData identities and three-data/two-owner observational equality.',
          'Actual SP/payment/activation/recovery clock/full-cycle totals; source-local field input is not actual cost settlement.']}
out=OUTPUT/'cost-source-review.json'
if out.exists():raise RuntimeError('Do not overwrite original source review.')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'methods':len(selected),'unique_instructions':len(instructions),'fresh_spans':len(spans),
 'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'game_dll_executed':False,'game_process_memory_read':False}))
