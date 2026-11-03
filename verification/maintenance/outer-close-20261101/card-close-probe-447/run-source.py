from pathlib import Path
import sys,subprocess,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/outer-close-20261101'
if len(sys.argv)>1:
 from player_ui_verification import run
 from rouge import player_acceptance
 original=player_acceptance.check
 def check(section,window,gui,require):
  original(section,window,gui,require)
  controls=window.compact_window.replay_popup.panel.statistics.card_controls;controls.open_viewer();gui.processEvents();viewer=controls.viewer
  close=viewer.titleBar.closeBtn
  out=B/('card-close-probe-'+str(section))
  (out/'close.json').write_text(json.dumps({'viewer_width':viewer.width(),'close_rect':[close.x(),close.y(),close.width(),close.height()],'mask_bounds':[close.mask().boundingRect().width(),close.mask().boundingRect().height()],'inside_client':viewer.rect().contains(close.geometry())},indent=2)+'\n','utf8')
  viewer.grab().save(str(out/'viewer.png'));close.grab().save(str(out/'close.png'))
  require(viewer.rect().contains(close.geometry()),'outer_close_actual_statistics_viewer_circle_fits_inside_native_client')
 player_acceptance.check=check
 n=int(sys.argv[1]);raise SystemExit(run(n,B/('card-close-probe-'+str(n))/'window.json'))
for n in(447,):
 out=B/('card-close-probe-'+str(n));out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),str(n)],cwd=R,stdout=a,stderr=b);print({'scope':n,'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
 value=json.loads((out/'window.json').read_bytes());print({'scope':n,'actual_exit':code,'checks':value['unique_checks'],'failure':value['failure']},flush=True)
 if code:raise SystemExit(code)
