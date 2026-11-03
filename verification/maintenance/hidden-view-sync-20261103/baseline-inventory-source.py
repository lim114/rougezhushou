from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import sys,os,subprocess,json,unittest
r=Path.cwd();sys.path.insert(0,str(r));out=r/'verification/maintenance/hidden-view-sync-20261103'
if len(sys.argv)==1:
 with(out/'baseline-inventory-stdout.txt').open('wb')as a,(out/'baseline-inventory-stderr.txt').open('wb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],stdout=a,stderr=b);code=p.wait()
 (out/'baseline-inventory-process.json').write_text(json.dumps({'actual_PID':p.pid,'actual_exit':code,'baseline_commit':'d06efce62ba746599fd1c7375949b888dd86f182'},indent=2)+'\n','utf8',newline='\n')
 (out/'baseline-inventory-source.py').write_bytes(Path(__file__).read_bytes())
 print((out/'baseline-inventory-stderr.txt').read_text('utf8')[-300:]);raise SystemExit(0 if code==1 else 2)
os.environ['QT_QPA_PLATFORM']='offscreen'
module=ModuleType('rouge._inventory_before_hidden');module.__package__='rouge';module.__file__=str(r/'rouge/player_inventory.py')
source=subprocess.check_output(['git','show','d06efce62ba746599fd1c7375949b888dd86f182:rouge/player_inventory.py'])
exec(compile(source,module.__file__,'exec'),module.__dict__)
from tests import test_inventory_layout_review as tests
with patch.object(tests,'InventoryPanel',module.InventoryPanel):
 result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(tests))
 raise SystemExit(0 if result.wasSuccessful()else 1)
