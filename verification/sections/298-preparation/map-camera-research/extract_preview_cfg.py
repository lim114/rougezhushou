"""File-backed bounded x64 CFG only. Target GameAssembly is never executed."""
import argparse,bisect,hashlib,json,mmap,struct,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
RESEARCH=BASE.parents[1]/'.cache/research'
sys.path.insert(0,str(RESEARCH/'p1-runtime-source-054/vendor'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_IMM,X86_OP_MEM,X86_REG_RIP
parser=argparse.ArgumentParser();parser.add_argument('--name',action='append');parser.add_argument('--address',action='append');parser.add_argument('--output',default='initial-cfg');args=parser.parse_args()
mapping=RESEARCH/'p2-native-current-263/script.json'
verification=json.loads((mapping.parent/'mapping-verification.json').read_text(encoding='utf-8'))
methods=json.loads(mapping.read_text(encoding='utf-8'))['ScriptMethod']
supplement=RESEARCH/'p2-native-current-263/supplement-map.json'
if supplement.exists():methods+=json.loads(supplement.read_text(encoding='utf-8'))['ScriptMethod']
helpers=BASE/'helper-map-with-protected.json'
if helpers.exists():methods+=json.loads(helpers.read_text(encoding='utf-8'))['ScriptMethod']
names={}
for m in methods:names.setdefault(m['Address'],[]).append(m['Name'])
DEFAULT=['Torappu.Battle.Entity$$get_cost','Card$$get_cost','ObscuredAttributesSnapshot$$get_cost',
 'Torappu.Battle.Attributes$$GetValueRoundToInt','RuntimeCostModifier$$ApplyFirstPass',
 'RuntimeCostModifier$$TryGetCostDelta','RuntimeCostModifier$$CreateRuntimeModifier',
 'DecklikeRuntimeCostModifier$$TryGetCostDelta','DecklikeRuntimeCostModifier$$Preprocess',
 'Torappu.Battle.DecklikeRuntimeCostTalent$$CreateDecklikeRuntimeCostModifier',
 'Torappu.Battle.DecklikeRuntimeCostTalent$$AssignData',
 'Torappu.Battle.Roguelike.Internal.DCardBuff$$DoPreProcess','Card$$_ApplyAttributeModifier',
 'Card$$UpdateDeckAttributeData','Torappu.Battle.Deck$$_PostProcessDeckLikeRuntimeCostModifiers']
selected=list({(m['Address'],m['metadata_method_index']):m for m in methods if m['Name'] in (args.name or DEFAULT)}.values())
if args.address:
 selected=[] if not args.name else selected
 selected+=[dict(Address=int(a,0),Name='unmapped_'+a,metadata_method_index=None) for a in args.address]
assert selected and len(selected)<=50
game=Path(verification['source_game_dll']);dis=Cs(CS_ARCH_X86,CS_MODE_64);dis.detail=True
with game.open('rb') as file,mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as data:
 dll_sha=hashlib.sha256(data).hexdigest();assert dll_sha==verification['game_dll_sha256']
 base=verification['image_base'];sections=verification['sections']
 def offset(rva):
  for s in sections:
   if s['rva']<=rva<s['rva']+s['raw_size']:return s['offset']+rva-s['rva']
  raise ValueError(('not physically file-backed',hex(rva)))
 def executable(address):
  rva=address-base
  return any(s['rva']<=rva<s['rva']+s['raw_size'] and s['characteristics']&0x20000000 for s in sections)
 pe=struct.unpack_from('<I',data,60)[0];opt=pe+24
 exception_rva,exception_size=struct.unpack_from('<II',data,opt+112+3*8)
 eo=offset(exception_rva);functions=list(struct.iter_unpack('<III',data[eo:eo+exception_size]));starts=[f[0] for f in functions]
 def unwind(address):
  rva=address-base;i=bisect.bisect_right(starts,rva)-1
  if i<0 or not functions[i][0]<=rva<functions[i][1]:return None
  begin,end,info=functions[i];o=offset(info);version_flags,prologue,count,frame=struct.unpack_from('<BBBB',data,o)
  flags=version_flags>>3;trailing=o+4+((count+1)//2)*4
  return {'begin_rva':hex(begin),'end_rva':hex(end),'unwind_rva':hex(info),'version':version_flags&7,
          'flags':flags,'prologue_bytes':prologue,'codes':count,
          'chain_info':[hex(x) for x in struct.unpack_from('<III',data,trailing)] if flags&4 else None}
 records=[]
 for method in selected:
  pending=[method['Address']];seen={};edges=[];limits=[]
  while pending and len(seen)<4000:
   pc=pending.pop()
   while pc not in seen and len(seen)<4000:
    if not executable(pc):limits.append({'address':hex(pc),'reason':'not_file_backed_executable'});break
    o=offset(pc-base);ins=next(dis.disasm(data[o:o+16],pc,count=1),None)
    if ins is None:limits.append({'address':hex(pc),'reason':'undecodable'});break
    row={'address':hex(pc),'rva':hex(pc-base),'physical_offset':hex(o),'bytes':ins.bytes.hex(),
         'mnemonic':ins.mnemonic,'operands':ins.op_str,'pdata':unwind(pc)}
    for op in ins.operands:
     if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
      address=pc+ins.size+op.mem.disp
      try:
       ro=offset(address-base);raw=data[ro:ro+8]
       row.setdefault('rip_data',[]).append({'address':hex(address),'bytes8':raw.hex(),
        'uint32':struct.unpack_from('<I',raw)[0],'float32':struct.unpack_from('<f',raw)[0],
        'uint64':struct.unpack_from('<Q',raw)[0]})
      except (ValueError,struct.error):pass
    target=ins.operands[0].imm if ins.operands and ins.operands[0].type==X86_OP_IMM else None
    if ins.mnemonic.startswith(('call','j')) and target is not None:
     row['target']=hex(target);row['target_symbols']=names.get(target,[])
    seen[pc]=row;nextpc=pc+ins.size
    if ins.mnemonic.startswith('ret') or ins.mnemonic in ('int3','ud2'):break
    if ins.mnemonic=='jmp':
     if target is None:edges.append({'from':hex(pc),'kind':'indirect_jump','target':ins.op_str})
     elif target in names and target!=method['Address']:
      edges.append({'from':hex(pc),'kind':'external_tailcall','to':hex(target),'symbols':names[target]})
     else:edges.append({'from':hex(pc),'kind':'direct_jump','to':hex(target)});pending.append(target)
     break
    if ins.mnemonic.startswith('j'):
     if target is not None:edges.append({'from':hex(pc),'kind':'conditional','to':hex(target)});pending.append(target)
     edges.append({'from':hex(pc),'kind':'fallthrough','to':hex(nextpc)})
     pending.append(nextpc);break
    pc=nextpc
  if pending:limits.append({'reason':'4000_instruction_limit','remaining_entries':[hex(v) for v in pending]})
  instructions=[seen[a] for a in sorted(seen)]
  code=b''.join(bytes.fromhex(i['bytes']) for i in instructions)
  records.append({'method':method,'instructions':instructions,'edges':edges,'limits':limits,
    'instruction_count':len(instructions),'reachable_instruction_bytes':len(code),'reachable_bytes_sha256':hashlib.sha256(code).hexdigest(),
    'cfg_bounded_traversal_finished':not limits,'indirect_call_count':sum(i['mnemonic']=='call' and 'target' not in i for i in instructions)})
 report={'dll_sha256':dll_sha,'metadata_sha256':verification['metadata_sha256'],'mapping_sha256':hashlib.sha256(mapping.read_bytes()).hexdigest(),
 'source_game_dll':str(game),'file_only':True,'game_dll_executed':False,'process_memory_read':False,
 'current_hotfix_equivalence_proven':False,'warning':'Static CFG follows direct native branch continuations, not dynamic calls or current XLua/hotfix overrides.',
 'supplement_mapping_sha256':hashlib.sha256(supplement.read_bytes()).hexdigest() if supplement.exists() else None,
 'methods':records}
 (BASE/(args.output+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
 lines=[]
 for record in records:
  lines.append(record['method']['Name']+' '+hex(record['method']['Address']))
  for i in record['instructions']:
   lines.append(i['address']+' '+i['mnemonic']+' '+i['operands']+(' ; '+','.join(i['target_symbols'][:3])+(' [aliases '+str(len(i['target_symbols']))+']' if len(i['target_symbols'])>3 else '') if i.get('target_symbols') else '')+
    (' DATA '+str(i['rip_data']) if i.get('rip_data') else ''))
  lines.append('EDGES '+json.dumps(record['edges']));lines.append('LIMITS '+json.dumps(record['limits']));lines.append('')
 (BASE/(args.output+'.txt')).write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'methods':[{'name':r['method']['Name'],'instructions':r['instruction_count'],'limits':r['limits']} for r in records]},ensure_ascii=False))
