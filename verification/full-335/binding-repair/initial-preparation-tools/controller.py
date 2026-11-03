from pathlib import Path
import sys,tempfile,uuid,os,json
from common import ROOT,BASE,PIN,guard
sys.path.insert(0,str(ROOT/'.cache/full335-prep'))
from execution335 import execute_observed,terminal_job_record,checkpoint
from full335_common import write_new,now
assert guard();container=Path(tempfile.gettempdir())/('rouge-full335-binding-recheck1-'+uuid.uuid4().hex);container.mkdir();write_new(BASE/'once.json',{'container':str(container),'controller_pid':os.getpid(),'automatic_retry_allowed':False})
r={'section':335,'status':'running','root_controller_pid':os.getpid(),'source_freeze_sha256':PIN,'components':[]};write_new(container/'orchestration.json',r)
for mode in ('p3_304','p3_305'):
 guard();folder=container/mode;folder.mkdir();child=[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'child.py'),mode,str(folder/'actual')];argv=[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(ROOT/'.cache/full335-prep/supervisor335.py'),'--status',str(folder/'supervisor.json'),'--timeout','300','--',*child]
 observed=execute_observed(argv,folder,timeout=390);terminal,details=terminal_job_record(folder,observed);row={'mode':mode,**details,'terminal':terminal};r['components'].append(row);checkpoint(container/'orchestration.json',r);assert terminal,'No duplicate execution after uncertain job';guard()
r['status']='all_required_components_terminal';r['passed']=all(x['child_primary_exit']==x['supervisor_exit']==0 and not x['timed_out']and x['owned_job_no_live_execution_verified']for x in r['components']);checkpoint(container/'orchestration.json',r);print(json.dumps({'recheck_terminal':True,'passed':r['passed'],'container':str(container)}),flush=True);raise SystemExit(0 if r['passed']else 1)
