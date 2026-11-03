from pathlib import Path
import subprocess,sys,json,os
R=Path.cwd();B=R/'verification/sections/447-presentation-card/density-matrix'
if len(sys.argv)>1:
 sys.path[:0]=[str(R)];from PySide6.QtWidgets import QApplication
 from PySide6.QtCore import QEvent
 from PySide6.QtGui import QColor
 from rouge.reference_image import ReferenceImage
 from tests.test_battle_reader_review import image_bytes
 q=QApplication([]);assert q.platformName()=='windows';label=ReferenceImage();label.set_data(image_bytes(),'未取得原图');label.show();source=label.original.cacheKey();rows=[]
 for w,h in[(90,100),(301,151),(700,180),(1200,400)]:
  label.resize(w,h);q.processEvents();q.sendEvent(label,QEvent(QEvent.Type.DevicePixelRatioChange));pix=label.pixmap();ratio=label.devicePixelRatioF();size=pix.deviceIndependentSize();image=pix.toImage();assert pix.devicePixelRatioF()==ratio;assert size.width()<=label.contentsRect().width()+.5/ratio and size.height()<=label.contentsRect().height()+.5/ratio;assert image.pixelColor(0,image.height()//2)==QColor('red')and image.pixelColor(image.width()-1,image.height()//2)==QColor('blue');assert source==label.original.cacheKey();rows.append({'actual_widget_size':[label.width(),label.height()],'actual_DPR':ratio,'physical_image_size':[pix.width(),pix.height()],'logical_image_size':[size.width(),size.height()]})
 label.close();(B/(sys.argv[1]+'.json')).write_text(json.dumps({'passed':True,'QT_SCALE_FACTOR':os.environ['QT_SCALE_FACTOR'],'qpa':q.platformName(),'rows':rows,'real_cross_monitor_game_test':False},indent=2)+'\n','utf8');raise SystemExit(0)
B.mkdir(exist_ok=False)
for factor in('0.75','1','1.25','2'):
 env=dict(os.environ);env['QT_SCALE_FACTOR']=factor
 with(B/(factor+'-stdout.txt')).open('xb')as a,(B/(factor+'-stderr.txt')).open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),factor],cwd=R,env=env,stdout=a,stderr=b);code=p.wait()
 (B/(factor+'-process.json')).write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');print({'factor':factor,'actual_exit':code},flush=True)
 if code:raise SystemExit(code)
(B/'run-source.py').write_bytes(Path(__file__).read_bytes())
