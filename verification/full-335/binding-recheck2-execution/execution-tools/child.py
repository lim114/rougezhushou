import sys,os,runpy,json,traceback
from pathlib import Path
from common import ROOT,BASE,FREEZE,PIN,guard,sha
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
data=guard();mode=sys.argv[1];out=Path(sys.argv[2]);assert mode in ('p3_304','p3_305')and not out.exists()and not out.is_relative_to(ROOT);out.mkdir()
target=ROOT/data['p3_scripts'][mode];argv=[str(target),'--receipt',str(out/'window.json'),'--visible-ms','60000','--source-freeze',FREEZE];sys.argv=argv;error=None;cleanup_error=None;code=None;after_error=None
try:
 try:runpy.run_path(str(target),run_name='__main__');code=0
 except SystemExit as e:code=e.code if type(e.code)is int else 0 if e.code is None else 1
 except BaseException as e:error={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};code=1
finally:
 try:
  from qt_verification_cleanup import shutdown_verification_qt
  cleanup=shutdown_verification_qt()
 except BaseException as e:cleanup_error=str(e)
try:guard()
except BaseException as e:after_error=str(e)
raw=json.loads((out/'window.json').read_bytes())if(out/'window.json').is_file()else None
passed=code==0 and error is None and cleanup_error is None and after_error is None and raw is not None and raw.get('passed')is True
r={'section':335,'mode':mode,'actual_argv':argv,'actual_fixture_exit':code,'fixture_exception':error,'qt_cleanup_error':cleanup_error,'source_guard_exception_after':after_error,'source_freeze':FREEZE,'source_freeze_sha256':PIN,'actual_receipt_sha256':sha(out/'window.json')if raw is not None else None,'component_automated_passed':passed,'full_suite_rerun':False,'original_failed_component_preserved':True}
(out/'recheck-source-closure.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'mode':mode,'passed':passed,'actual_exit':code}),flush=True);raise SystemExit(0 if passed else 1)
