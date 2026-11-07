from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from rouge import current_spawn_candidates as model
from rouge.current_spawn_candidates_view import CurrentSpawnCandidatesPanel


class CandidateBoundaryRetentionTests(TestCase):
    def test_each_pinned_file_corruption_rejected(self):
        root=Path(__file__).resolve().parents[1]
        names=[model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']]
        with TemporaryDirectory() as temporary:
            target=Path(temporary)
            for name in names:
                path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((root/name).read_bytes())
            with patch.object(model.battle.version,'_file',side_effect=lambda name:target/name):
                self.assertIsNotNone(model._packet())
                for name in names:
                    with self.subTest(name=name):
                        path=target/name;raw=path.read_bytes();path.write_bytes(raw+b' ')
                        self.assertIsNone(model._packet());path.write_bytes(raw)

    def test_declared_relations_must_match_projection(self):
        packet=model._packet();packet['inventory']['stages']['ro6_n_1_1']['relations']=[]
        with patch.object(model,'_packet',return_value=packet):
            self.assertIsNone(model.stage_reference('ro6_n_1_1'))

    def test_public_bad_inputs_do_not_read_sources(self):
        with patch.object(model,'_packet') as packet:
            for stage,origin in [(None,None),([],None),('ro6_n_1_1',False)]:
                self.assertIsNone(model.stage_reference(stage,origin))
            for result,relation,key in [(None,'g','0'),({},None,'0'),({},'g',False)]:
                self.assertIsNone(model.resolve_member(result,relation,key))
            self.assertIsNone(model.resolve_member({},'g','0'))
        packet.assert_not_called()


class CandidateDisplayRetentionTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.reference=model.stage_reference('ro6_n_1_1')

    def setUp(self):
        self.query=patch.object(model,'stage_reference',return_value=deepcopy(self.reference));self.query.start();self.addCleanup(self.query.stop)
        self.panel=CurrentSpawnCandidatesPanel('ro6_n_1_1');self.addCleanup(self.panel.close)

    def test_missing_and_bad_image_clear_old_picture_without_clearing_text(self):
        member={'action_type':'SPAWN','enemy_candidates':[{'portrait':{'file':'test'}}]}
        self.panel.player.setPlainText('keep useful text')
        for raw in (None,b'not png'):
            with self.subTest(raw=raw),patch.object(model.battle,'picture_bytes',return_value=raw):
                self.panel.portrait.setPixmap(QPixmap(4,4))
                self.panel._show_portrait(member)
                self.assertTrue(self.panel.portrait.pixmap().isNull())
                self.assertIn('图片无法核对',self.panel.portrait.text())
                self.assertEqual(self.panel.player.toPlainText(),'keep useful text')
        for member in (None,{'action_type':'EMPTY'}, {'action_type':'SPAWN','enemy_candidates':[]},
                       {'action_type':'SPAWN','enemy_candidates':[{'portrait':None}]},
                       {'action_type':'SPAWN','enemy_candidates':[{'portrait':{}},{'portrait':{'other':1}}]}):
            with patch.object(model.battle,'picture_bytes') as read:
                self.panel._show_portrait(member)
                read.assert_not_called();self.assertTrue(self.panel.portrait.isHidden())

    def test_failed_position_clears_once_and_emits_no_jump(self):
        relation=self.reference['groups'][0];member=relation['members'][0]
        invalidated=[];jumps=[]
        self.panel.sourceInvalidated.connect(lambda:invalidated.append(True))
        self.panel.actionPositionRequested.connect(jumps.append)
        with patch.object(self.panel,'_selected',return_value=(relation,member)),patch.object(model,'position_reference',return_value=None):
            self.assertFalse(self.panel.follow_position())
        self.assertEqual(invalidated,[True]);self.assertEqual(jumps,[])
        self.assertIsNone(self.panel.result);self.assertFalse(self.panel.position_button.isEnabled())
        self.panel.clear_reference();self.assertEqual(invalidated,[True])
