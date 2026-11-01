from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/456-tomimi/native-public3'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/tomimi_reference.py','rouge/tomimi_view.py','rouge/data/tomimi-stage-links.json','research/tomimi-456/source-facts.json','tests/test_tomimi_456.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 import time,re,base64
 from unittest.mock import patch
 from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
 from rouge import tomimi_view as tv
 from rouge.player_map_reader import make_reader
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());images=[];observed=[];requests=[];observers=[]
 class Observer(QWebEngineUrlRequestInterceptor):
  def interceptRequest(self,info):requests.append({'url':info.requestUrl().toString(),'method':bytes(info.requestMethod()).decode('ascii')})
 original_profile=tv.QWebEngineProfile
 def profile(parent):
  value=original_profile(parent);observer=Observer(value);value.setUrlRequestInterceptor(observer);observers.append(observer);return value
 def wait_for(condition,timeout=35):
  deadline=time.perf_counter()+timeout
  while not condition():
   if time.perf_counter()>deadline:raise AssertionError('Public web operation timed out')
   gui.processEvents();QTest.qWait(30)
 def evaluate(web,script):
  result=[];web.page().runJavaScript(script,lambda x:result.append(x));wait_for(lambda:bool(result),10);return result[0]
 def runtime_state(code):
  values=iter(base64.urlsafe_b64decode(code+'==='))
  def integer():
   value=0;shift=0
   while True:
    byte=next(values);value|=(byte&127)<<shift
    if not byte&128:return value
    shift+=7
  version,topic,flags,count=integer(),integer(),integer(),integer()
  for _ in range(count):
   relic=integer()
   if relic&1:integer()
  fields={k:integer()for flag,k in[(1,'variation'),(2,'difficulty'),(4,'gold'),(8,'floor'),(16,'index'),(32,'elite')]if flags&flag}
  return {'version':version,'topic':topic,**fields}
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 with patch.object(tv,'QWebEngineProfile',side_effect=profile):
  for sid,level,index,elite in [('ro6_n_1_2','level_rogue6_1-2',0,0),('ro6_e_1_2','level_rogue6_1-2',0,1),('ro6_t_8_c','level_rogue6_t-8-c',2,0),('ro6_b_7_b','level_rogue6_b-7-b',1,0)]:
   root=make_reader('battle',{'id':sid,'title':'公开关卡'},c,historical=True,page_owner=c);root.prepare=root.panel.refresh_reference;require(c.present(root),sid+'_stage_present');p=root.panel;p.tabs.setCurrentIndex(1);local_state=(p.tabs.currentIndex(),p.summary.toPlainText(),deepcopy(p.run_config));require(p.tomimi_button.isVisible()and p.tomimi_button.isEnabled(),sid+'_entry_visible');QTest.mouseClick(p.tomimi_button,Qt.MouseButton.LeftButton);gui.processEvents();page=host.pages.currentWidget();browser=page.panel;web=browser.web
   require(page.source_parent is root and page.window()is host,sid+'_same_main_host');require(p.tomimi_dialog is None,sid+'_no_extra_native_dialog');require(browser.profile.isOffTheRecord(),sid+'_isolated_browser_profile');require(browser.result['level_id']==level and browser.result['variant_index']==index,sid+'_exact_public_binding');wait_for(lambda:browser.status.text()=='tomimi.dev');QTest.qWait(700)
   selector='img[alt="'+level+'"]';script='JSON.stringify({title:document.title,correctMap:!!document.querySelector('+json.dumps(selector)+'),imageLoaded:!!document.querySelector('+json.dumps(selector)+')?.naturalWidth,variants:[...document.querySelectorAll("#stage-variant-selector button")].map(b=>b.getAttribute("aria-pressed"))})';dom=json.loads(evaluate(web,script));require(dom['correctMap']and dom['imageLoaded'],sid+'_actual_map_loaded');require(browser.result['name']in dom['title'],sid+'_actual_stage_title');require(not dom['variants']or dom['variants'][index]=='true',sid+'_actual_variant_selected')
   evaluate(web,"document.getElementById('settings-toggle').click()");QTest.qWait(200);settings=evaluate(web,"document.querySelector('dialog[open]').innerText");match=re.search(r'运行状态代码\s+([A-Za-z0-9_-]+)',settings);require(match is not None,sid+'_actual_settings_opened');state=runtime_state(match.group(1));require(state['version']==1 and state['topic']==5,sid+'_website_decoded_format');require(state.get('index',0)==index and state.get('elite',0)==elite,sid+'_actual_config_and_mode');evaluate(web,"[...document.querySelectorAll('dialog[open] button')].find(b=>b.innerText==='×').click()")
   evaluate(web,'document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});window.rougeReading456="public-reading-marker";');QTest.qWait(250);scroll=evaluate(web,'window.scrollY');save(sid+'-website-map')
   loaded=[];web.loadFinished.connect(lambda value:loaded.append(value));QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is root,sid+'_back_to_local_stage');require(local_state==(p.tabs.currentIndex(),p.summary.toPlainText(),p.run_config),sid+'_local_reading_unchanged');QTest.mouseClick(p.tomimi_button,Qt.MouseButton.LeftButton);gui.processEvents();QTest.qWait(250);require(host.pages.currentWidget()is page,sid+'_same_browser_reused');require(evaluate(web,'window.rougeReading456')=='public-reading-marker'and not loaded,sid+'_reading_retained_without_reload');after=evaluate(web,'window.scrollY');require(abs(after-scroll)<=3,sid+'_scroll_retained')
   observed.append({'stage_id':sid,'level_id':level,'native_entry_hwnd':handle,'native_current_hwnd':int(host.winId()),'native_surface':str(host.windowHandle().surfaceType()),'URL':browser.result['url'],'actual_runtime':state,'actual_DOM':dom,'scroll_before':scroll,'scroll_after':after,'private_run_state_supplied':False})
   if sid=='ro6_b_7_b':
    with patch('rouge.current_battle_reference.stage_reference',return_value=None):
     require(not host.present(page),'missing_parent_source_rejected');gui.processEvents();require(page not in host.history and host.pages.currentWidget()is root and root.panel.result is None,'missing_parent_source_removes_visible_webpage')
   c.present(c.map_popup);host.discard(root,fallback=c.map_popup);gui.processEvents()
 require(not errors,'no_Qt_slot_exceptions');require(not host.linked_pages,'all_web_dependencies_removed');require(window.run.state==before,'temporary_run_unchanged');require(host is c.reference_window,'same_Qt_host_throughout');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'one_visible_reference_window');window.player_validation_target=host
 require(all('PRIVATE_MARKER'not in r['url']for r in requests),'no_private_fixture_marker_sent');require(bool(requests),'actual_public_network_observed')
 (out/'public-web.json').write_text(json.dumps({'cases':observed,'requests':requests,'public_stage_selection_only':True,'private_run_state_supplied':False,'native_handle_note':'Qt upgrades the native surface from raster to Direct3D for the first embedded browser. Same Qt host and one visible reference window are verified; no fixed-HWND requirement inferred.','request_observer_only':True,'request_blocking_or_proxy_changes':False},ensure_ascii=False,indent=2)+'\n','utf8')
 (out/'images.json').write_text(json.dumps({'images':images,'public_web_pages_only':True},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(456,out/'window.json'))

