from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,sys,tempfile,uuid
R=Path(__file__).resolve().parents[2];B=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.cache/full350-attempt2'))
from full350_common import bound,sha,write_new
P=json.loads((B/'profile.json').read_bytes());parent=P['parent_commit'];freeze=P['root_freeze_sha256'];activation=P['activation_sha256']
def stamp():return datetime.now(timezone.utc).isoformat()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def coordinator():
 from run_full350_controller import observed_step
 bound(parent,freeze,activation)
 assert sha(B/'component_child350_recheck.py')==P['child_sha256']
 prior=json.loads((R/'verification/full-350/execution-attempt2/orchestration.json').read_bytes())
 assert prior['status']=='all_required_components_terminal' and [x['component']for x in prior['review_failures']]==['p3_312']
 destination=Path(tempfile.gettempdir())/('rouge-full350-312-recheck-'+uuid.uuid4().hex)
 assert not destination.exists();destination.mkdir()
 write_new(B/'once.json',{'section':350,'container':str(destination),'profile_sha256':sha(B/'profile.json'),'automatic_retry':False})
 write_new(destination/'authority.json',{'section':350,'controller_fixture_pid':os.getpid(),'root':str(R),'parent_commit':parent,'root_freeze_sha256':freeze,'activation_sha256':activation,'profile_sha256':sha(B/'profile.json'),'runner_sha256':sha(Path(__file__)),'child_sha256':P['child_sha256'],'created_at':stamp()})
 argv=[str(R/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(B/'component_child350_recheck.py'),'--mode','p3_312','--out',str(destination/'p3_312/actual'),'--expected-parent-commit',parent,'--freeze-sha256',freeze,'--activation-sha256',activation]
 row=observed_step(destination,'p3_312',argv,300,390,parent,freeze,activation)
 write_new(destination/'result.json',{'section':350,'row':row,'original60s_pass_claimed':False,'normal_latency_improvement_claimed':False,'passed':row['child_primary_exit']==row['supervisor_exit']==0})
 return row['supervisor_exit']
if '--coordinator' in sys.argv:raise SystemExit(coordinator())
bound(parent,freeze,activation)
folder=B/'root-launch';folder.mkdir()
argv=[str(R/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(Path(__file__)),'--coordinator']
with (folder/'stdout.txt').open('xb')as out,(folder/'stderr.txt').open('xb')as err:
 p=subprocess.Popen(argv,cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
 record={'section':350,'status':'running','argv':argv,'controller_pid':p.pid,'root_wrapper_pid':os.getpid(),'owned_popen_retained':True,'actual_observed_exit':None,'runner_sha256_at_launch':sha(Path(__file__)),'profile_sha256':sha(B/'profile.json'),'started_at':stamp()}
 write(folder/'controller-process.json',record)
 code=p.wait()
 (folder/'process.exit').write_text(str(code)+'\n',encoding='ascii')
 record.update(status='completed',actual_observed_exit=code,finished_at=stamp(),exit_observed_directly_from_retained_popen=True)
 write(folder/'controller-process.json',record)
raise SystemExit(code)
