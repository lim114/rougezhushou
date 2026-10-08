"""Bounded private-core compatibility, separately counted from public matrix."""
import copy,gzip,hashlib,json,sys
from pathlib import Path
from matrix_plan import typed,json_value
OUT=Path(__file__).resolve().parent


def main():
 package=sys.argv[1];sys.path.insert(0,str(OUT/package));assert package in ('baseline','draft')
 from rouge.catalog import catalog
 from rouge.damage import _prepare_damage,_evaluate_damage_once
 from rouge.estimate import format_estimate
 from rouge.reporting import format_report
 rows=[];catalog_before=typed(catalog());prepares=cores=texts=0
 for j,(skill,continuous,value,expect) in enumerate(((2,True,'false','same'),(3,False,'false','same'),
                                                   (3,True,'false','changed'),(3,True,0,'same'))):
  original={'operator':'char_4182_oblvns','skill':skill,'base_attack':975,'window_seconds':13,
            'level':60,'module_id':'uniequip_002_oblvns','module_level':2,'continuous_attacks':continuous,
            'ranged_attack':value,'_oblvns_ranged_attack_consumed':True,'_wine_phase_frame':91}
  original_before=typed(original);prepared=_prepare_damage(copy.deepcopy(original));prepares+=1
  prepared_before_clones=typed(prepared)
  for phase in (0,7):
   isolated=copy.deepcopy(prepared);row={'index':len(rows)+1,'case':j,'expect':expect,
      'input':json_value(original),'input_typed':original_before,'phase_argument':phase,
      'prepared_before':typed(isolated)}
   cores+=1
   try:result=_evaluate_damage_once(isolated,wine_phase=phase)
   except Exception as error:row.update(outcome='error',error_type=type(error).__name__,error_message=str(error))
   else:
    row.update(outcome='accepted',result=result,result_typed=typed(result),reports={
      'estimate':format_estimate(result),'user':format_report(result),'technical':format_report(result,technical=True)})
    texts+=3
   row['prepared_after']=typed(isolated);row['original_caller_unchanged']=typed(original)==original_before
   row['catalog_unchanged']=typed(catalog())==catalog_before
   assert row['original_caller_unchanged'] and row['catalog_unchanged'];rows.append(row)
  assert typed(prepared)==prepared_before_clones
 data=json.dumps(rows,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
 path=OUT/(package+'-isolated-cores.json.gz')
 with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as stream:stream.write(data)
 summary={'passed':True,'package':package,'fresh_public_calls':0,'explicit_prepare_helper_calls':prepares,
    'explicit_core_helper_calls':cores,'formatter_calls':texts,'catalog_isolation_cache_reads':9,
    'saved_rows':len(rows),'gzip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'gzip_bytes':path.stat().st_size,
    'decoded_sha256':hashlib.sha256(data).hexdigest(),'decoded_bytes':len(data),
    'scope':'Internal isolated core phase-argument compatibility only; no public nondeployment phase envelope or native/game tick validation.',
    'prepared_clone_after_mutation_compared_to_old':True,'Qt':0,'Wine':0}
 with (OUT/(package+'-isolated-cores-summary.json')).open('x',encoding='utf-8') as f:json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(summary))


if __name__=='__main__':main()
