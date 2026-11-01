from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtTest import QTest
from PySide6.QtCore import QRectF
from rouge.player_map_reader import make_reader
app=QApplication([]);o=QWidget();d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开原图'},o);d.show();rows=[]
for width,height in[(800,340),(640,360),(1040,600),(800,340)]:
 d.resize(width,height);QTest.qWait(40);p=d.panel;v=p.overview_scroll.viewport();m=p.map_image;pix=m.pixmap();size=pix.deviceIndependentSize();rect=QRectF(m.rect().center().x()-size.width()/2,m.rect().center().y()-size.height()/2,size.width(),size.height());origin=m.mapTo(v,rect.topLeft().toPoint());visible=v.rect().contains(origin)and v.rect().contains(origin+rect.size().toSize().toPoint());rows.append({'requested':[width,height],'actual':[d.width(),d.height()],'viewport':[v.width(),v.height()],'map_widget':[m.width(),m.height()],'rendered_pixmap':[size.width(),size.height()],'full_rendered_map_in_viewport':visible,'section_minimum':p.map_section.minimumSizeHint().height(),'image_item_minimum':p.map_section.content().layout().itemAt(0).minimumSize().height(),'position_button_minimum':p.position_button.minimumSizeHint().height()})
d.close();o.close();(R/'verification/maintenance/map-thumbnail-fit-20261101/before-geometry.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');print(json.dumps(rows))
