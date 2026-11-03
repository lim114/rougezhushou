from pathlib import Path
from hashlib import sha256
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from rouge import app as a
from player_ui_verification import run
out=R/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
original=a.MainWindow.closeEvent;images=[]
def close(self,event):
    for name,pixmap in getattr(self,'player_inventory_mode_images',{}).items():
        p=out/(name+'.png');assert pixmap.save(str(p));images.append({'file':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest()})
    original(self,event)
from unittest.mock import patch
with patch.object(a.MainWindow,'closeEvent',close):code=run(446,out/'window.json')
(out/'extra-images.json').write_text(json.dumps(images,ensure_ascii=False,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
raise SystemExit(code)
