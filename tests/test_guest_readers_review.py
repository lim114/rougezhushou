"""Three real guest readers preserve all exact source variants and reading states."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
from types import ModuleType
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge.guest_mechanism_view import GuestMechanismPanel,GuestMechanismDialog

ROOT=Path(__file__).resolve().parents[1]
PROFILES={
 'knights':('CurrentGuestKnightsPanel','CurrentGuestKnightsDialog','6e86d5c4a84789f9d1117094384d58f60f74507f34b1f164c725774d0fdbb653'),
 'crystals':('CurrentGuestCrystalsPanel','CurrentGuestCrystalsDialog','b13892c628161b0d4d400bd6c7128336e93483061b08f93d0a32ece8482d4c7f'),
 'material':('CurrentGuestMaterialPanel','CurrentGuestMaterialDialog','1185aec31c12d2e69e3357d162f82a29161424cbd1e60033607b1db0c2c965b0')}
COMPARISONS=[]

def digest(value):return sha256(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf8')).hexdigest()


class GuestReadersReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([]);cls.modules={}
  for name,(_,_,expected)in PROFILES.items():
   raw=(ROOT/('research/guest-readers-review-20261031/before-current-guest-'+name+'-view.py')).read_bytes();assert sha256(raw).hexdigest()==expected
   old=ModuleType('rouge._before_guest_'+name);old.__package__='rouge';exec(compile(raw,'<verified-own-prior-guest-reader>','exec'),old.__dict__)
   cls.modules[name]=(old,import_module('rouge.current_guest_'+name+'_view'))

 def panel(self,name,sid,module=None):
  module=module or self.modules[name][1];p=getattr(module,PROFILES[name][0])(sid);self.addCleanup(p.close);self.addCleanup(p.clear_reference);return p

 def states(self,p,model):
  states=[]
  for key in [None]+[row['key']for row in p.result['rows']]:
   if key is not None:self.assertTrue(p.entities.select_value(key))
   for topic in [None]+[key for key,_ in model.topics(p.result,key)]:
    index=p.topic.findData(topic);self.assertGreaterEqual(index,0);p.topic.setCurrentIndex(index)
    picture=p.portrait.pixmap();image=picture.toImage()if picture and not picture.isNull()else None
    states.append({'key':p.selected_key,'topic':p.topic.currentData(),'player':sha256(p.player.toPlainText().encode('utf8')).hexdigest(),'technical':sha256(p.technical.toPlainText().encode('utf8')).hexdigest(),'topics':[(p.topic.itemText(i),p.topic.itemData(i))for i in range(p.topic.count())],'related':[(p.related.itemText(i),p.related.itemData(i))for i in range(p.related.count())],'portrait':None if image is None else[image.width(),image.height(),sha256(bytes(image.constBits())).hexdigest()],'missing_picture_text':p.portrait.text(),'map_enabled':p.map_button.isEnabled()})
  return states

 def test_all_ten_exact_stage_variants_keep_every_entity_topic_full_reference_and_text(self):
  COMPARISONS.clear()
  self.assertEqual(sum(len(new.model.STAGES)for _,new in self.modules.values()),10)
  for name,(old,new)in self.modules.items():
   for sid in new.model.STAGES:
    outputs=[]
    for module in [old,new]:
     p=self.panel(name,sid,module);self.assertIsNotNone(p.result);states=self.states(p,new.model);outputs.append((deepcopy(p.result),states))
    self.assertEqual(outputs[0],outputs[1],(name,sid))
    COMPARISONS.append({'profile':name,'stage_id':sid,'full_reference_equal':True,'reading_states_compared':len(outputs[1][1]),'reading_state_sha256':digest(outputs[1][1])})

 def test_all_ten_exact_map_targets_and_direct_map_close_behave_like_prior(self):
  for name,(old,new)in self.modules.items():
   for sid in new.model.STAGES:
    maps=[]
    for module in [old,new]:
     p=self.panel(name,sid,module);opened=p.open_map();maps.append(deepcopy(p.map_dialog.panel.result)if opened else None)
     if opened:
      child=p.map_dialog;child.reject();self.assertIsNone(child.panel.result)
    self.assertEqual(maps[0],maps[1],(name,sid))

 def test_shared_implementation_keeps_each_provider_and_dialog_identity(self):
  for name,(_,new)in self.modules.items():
   panel_class,dialog_class,_=PROFILES[name];self.assertTrue(issubclass(getattr(new,panel_class),GuestMechanismPanel));self.assertTrue(issubclass(getattr(new,dialog_class),GuestMechanismDialog))
   d=getattr(new,dialog_class)(new.model.STAGES[0]);self.addCleanup(d.close);self.assertIs(d.panel.model,new.model)
   self.assertEqual(type(d.panel).__name__,panel_class);self.assertEqual(type(d).__name__,dialog_class)
   old_dialog=getattr(self.modules[name][0],dialog_class)(new.model.STAGES[0]);self.addCleanup(old_dialog.close)
   self.assertEqual(d.windowTitle(),old_dialog.windowTitle());self.assertEqual(d.size(),old_dialog.size())

 def test_all_three_keep_reading_selection_on_refresh_and_clear_their_maps_on_source_loss(self):
  for name,(_,new)in self.modules.items():
   p=self.panel(name,new.model.STAGES[0]);p.resize(760,560);p.show();p.entities.select_value(p.result['rows'][0]['key']);p.topic.setCurrentIndex(1);p.tabs.setCurrentIndex(1);self.qt.processEvents()
   cursor=p.technical.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);p.technical.setTextCursor(cursor);before=(p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),cursor.selectedText())
   self.assertTrue(p.refresh_reference());self.assertEqual(before,(p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),p.technical.textCursor().selectedText()))
   self.assertTrue(p.open_map());child=p.map_dialog
   with patch.object(new.model,'reference',return_value=None):self.assertFalse(p.refresh_reference())
   self.assertIsNone(p.result);self.assertIsNone(p.map_dialog);self.assertIsNone(child.panel.result);self.assertFalse(child.isVisible())
   self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected_key)

 def test_each_dialog_close_and_reject_clear_its_owned_reference_and_map(self):
  for name,(_,new)in self.modules.items():
   for method in ['close','reject']:
    d=getattr(new,PROFILES[name][1])(new.model.STAGES[0]);self.addCleanup(d.close);d.show();self.assertTrue(d.panel.open_map());child=d.panel.map_dialog
    getattr(d,method)();self.qt.processEvents();self.assertIsNone(d.panel.result);self.assertIsNone(d.panel.map_dialog);self.assertIsNone(child.panel.result);self.assertFalse(child.isVisible())


if __name__=='__main__':unittest.main()
