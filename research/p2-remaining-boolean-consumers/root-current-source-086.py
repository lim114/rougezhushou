"""Root post-integration source/registration check; no project imports or calls."""
import argparse,ast,hashlib,json,subprocess
from pathlib import Path


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
 parser.add_argument('--repo',default='/workspace/rougezhushou');args=parser.parse_args()
 root=Path(args.repo);packet=Path(__file__).resolve().parent
 frozen=json.loads((packet/'current-baseline-freeze.json').read_bytes())
 reviewed=json.loads((packet/'review-freeze86.json').read_bytes())
 assert subprocess.check_output(['git','-C',str(root),'branch','--show-current']).decode().strip()=='codex/p2-development'
 expected={r['path']:r for r in reviewed['files']}
 products=[]
 for name,row in expected.items():
  data=(root/name).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
  if name.startswith('rouge/'):
   assert b'\r\n' in data and b'\n' not in data.replace(b'\r\n',b''),name
  else:assert b'\r\n' not in data
  ast.parse(data.decode('utf-8'));products.append({'path':name,'bytes':len(data),'sha256':row['sha256']})
 unchanged=0
 for row in frozen['files']:
  if row['path'] in expected or row['path']=='scripts/verify_cloud.py':continue
  data=(root/row['path']).read_bytes()
  assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
  unchanged+=1
 assert unchanged==720
 registry=(root/'scripts/verify_cloud.py').read_text(encoding='utf-8')
 assert any(isinstance(n,ast.Constant) and n.value=='tests.test_remaining_boolean_condition_text_input'
            for n in ast.walk(ast.parse(registry)))
 engine=(root/'rouge/operator_engine.py').read_text(encoding='utf-8')
 damage=(root/'rouge/damage.py').read_text(encoding='utf-8')
 assert 'self.ranged_attack_condition_consumed=False' in engine
 assert 'self.ranged_attack_condition_consumed=not ranged_overridden or normal is not None' in engine
 assert '_oblvns_ranged_attack_consumed' not in engine+damage
 assert "def calculate_extended(scenario,attributes):return Combat(scenario,attributes).calculate()" in engine
 assert damage.index("result['report']=build_report(scenario,result)")<damage.index('conditions={')
 for old in ('enemy_is_boss','enemy_in_neural_break','haruka_repeat','near_previous_deployment'):
  assert old in damage
 output={'passed':True,'section':86,'base_commit':frozen['base_commit'],'current_products':products,
     'other_base_source_files_exact':unchanged,'registry_contains_new_module':True,
     'ranged_per_core_object_state':True,'caller_public_or_scenario_marker_added':False,
     'new_API_calls':0,'new_project_helper_calls':0,'raw240rank_12module_source_audit_repeated':False,
     'original_source_binding_evidence':'Original 28 source attachments and 17 independent source attachments reused at their original commits/counts.',
     'source_qualifiers_and_old_error_limits':'See NOTE.md and sealed independent source/product review; current hash binding preserves reviewed implementation.'}
 with Path(args.output).open('x',encoding='utf-8') as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'passed':True,'section':86,'other_base_sources':unchanged,'new_API_calls':0}))


if __name__=='__main__':main()
