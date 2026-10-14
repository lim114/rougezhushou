"""Read-only276 draft probes; preserve source and complete synthetic IO."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import rouge
rouge.__path__.insert(0,str(ROOT/'.cache/section276-draft/rouge'))
from rouge import sp_initialization_reference as module
HERE=Path(__file__).resolve().parent
raw=Path(module.__file__).read_bytes()
sha=hashlib.sha256(raw).hexdigest()
if sha!='c2c7286da513ed549bea7e8e6752a08ec2f0b52f7117e8958349ada95226f648':
    raise RuntimeError('The first-reviewed core changed before sealing.')
snapshot=HERE/'core-before.py'
if snapshot.exists():raise RuntimeError('Do not overwrite original core.')
snapshot.write_bytes(raw)
cases=[]
def save(name,payload,reason):
    output=module.sp_initialization_reference(deepcopy(payload))
    cases.append({'name':name,'input':payload,'actual_output':output,'source_reason':reason})
p=module.public_example();p['actions']=p['actions'][:1]
p['actions'][0]['timer_allocate_normally']=None
save('unknown timer allocation retains false final pointer existence',p,
     'Constructor66753 normal allocation/constructor/assignment can produce exists=True; exception path can retainFalse. PrefixFalse may be preserved, finalFalse is not common to both paths.')
p=module.public_example();p['actions']=[p['actions'][1]]
p['state']['timer']={'exists':True,'period_raw':4294967296,'remaining_raw':4294967296}
p['actions'][0]['first_max_read']['cost_decode']['normal']=None
save('unknown cost return marks later capacity calls false',p,
     'SpData32849 has charges decode/IMUL/encoder after normally returned first decode; unknown first normal can continue or throw. Only false normal guarantees later callsFalse.')
p=module.public_example();p['actions']=[p['actions'][1]]
p['actions'][0]['first_max_read']['ordinary_native_path']=None
save('unknown capacity path marks all capacity calls false',p,
     'Neither ordinary versus hotfix eligibility nor future calls are proved when path qualifier isNone; omitted modeled stages are distinct from confirmed never-called.')
p=module.public_example();p['actions']=p['actions'][:1]
p['actions'][0]['timer_allocate_normally']=None
later=deepcopy(p['actions'][0]);later['id']='第二个未qualified构造';later['timer_allocate_normally']=True
p['actions'].append(later)
save('subsequent conditionally invoked constructor retains false pointer existence',p,
     'After unknown first normal, second construct may be invoked and installTrue timer; known oldFalse is not a final common value.')
report={'scope':'Synthetic file-only first review findings; no product edits, DLL execution, game/memory/chat or window use.',
        'core_sha256':sha,'source_valid':module.source_data() is not None,'cases':cases,
        'core_unchanged_during_probes':Path(module.__file__).read_bytes()==raw}
out=HERE/'original-probes.json'
if out.exists():raise RuntimeError('Do not overwrite original probe receipt.')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_valid':report['source_valid'],'cases':len(cases),'core_sha256':sha,
 'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'unchanged':report['core_unchanged_during_probes']}))
