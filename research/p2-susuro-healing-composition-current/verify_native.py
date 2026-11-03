"""Read-only source-bound healing proof; no native loading or execution."""
from pathlib import Path
import argparse,hashlib,json,mmap,struct

def verify(artifact_dir,game_dir=None):
 root=Path(artifact_dir);read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
 p=read('native-proof.json');meta=read('selected-metadata.json');receipt=read('receipt.json')
 for name,value in receipt['artifact_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==value,name
 for key in ('game_dll_sha256','metadata_sha256'):assert p[key]==meta[key]==receipt[key]
 assert not p['current_hotfix_equivalence_proven'] and not p['game_dll_executed']
 result={'artifact_consistency':True,'native_file_comparison':'unavailable','game_dll_executed':False,
    'process_memory_read':False,'private_state_read':False,'current_hotfix_equivalence_proven':False}
 if game_dir is None:return result
 game=Path(game_dir);metadata=(game/p['metadata_relative']).read_bytes()
 assert hashlib.sha256(metadata).hexdigest()==p['metadata_sha256'],'metadata hash'
 with (game/p['game_dll_relative']).open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as binary:
  assert hashlib.sha256(binary).hexdigest()==p['game_dll_sha256'],'DLL hash'
  pe=struct.unpack_from('<I',binary,60)[0];count=struct.unpack_from('<H',binary,pe+6)[0]
  osize=struct.unpack_from('<H',binary,pe+20)[0];base=struct.unpack_from('<Q',binary,pe+48)[0]
  sections=[struct.unpack_from('<IIII',binary,pe+24+osize+n*40+8)[1:] for n in range(count)]
  def offset(address):
   rva=address-base
   for start,size,pos in sections:
    if start<=rva<start+size:return pos+rva-start
   raise AssertionError(('outside file-backed section',hex(address)))
  checked=set()
  for method in p['methods']:
   assert not method['limits']
   for i in method['instructions']:
    raw=bytes.fromhex(i['bytes']);pos=offset(int(i['address'],0));assert pos==int(i['physical_offset'],0)
    assert binary[pos:pos+len(raw)]==raw,i['address'];checked.add((i['address'],i['bytes']))
  for row in meta['byte_spans']:
   source=binary if row['source']=='dll' else metadata;pos=int(row['physical_offset'],0)
   assert source[pos:pos+row['size']].hex()==row['bytes'],row['reason']
  assert len(checked)==receipt['unique_instruction_checks']
  result.update(native_file_comparison='passed',unique_instruction_checks=len(checked),metadata_and_binding_byte_spans=len(meta['byte_spans']))
 return result

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--artifact-dir',default=str(Path(__file__).resolve().parent))
 parser.add_argument('--game-dir');parser.add_argument('--output');args=parser.parse_args()
 output=json.dumps(verify(args.artifact_dir,args.game_dir),ensure_ascii=False,indent=2)+'\n'
 if args.output:Path(args.output).write_text(output,encoding='utf-8',newline='\n')
 print(output,end='')
