from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_ritual_reference as model,player_reference_links as links
from rouge.current_ritual_view import CurrentRitualPanel


class MaterialKindBoundaryTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_fixed_sources_use_exact_three_supported_kinds(self):
        source=model.packet()
        self.assertIsNotNone(source)
        self.assertEqual({r['kind'] for r in source['data']['acquisitions'].values()},{'event','exchange','battle'})

    def test_shared_host_unknown_kind_raises(self):
        panel=SimpleNamespace(window=lambda:object())
        with patch.object(links,'ReferenceWindow',object):
            with self.assertRaisesRegex(ValueError,'未支持的材料来源类型'):
                links.open_material_source(panel,{'kind':'internal-new-kind'})

    def test_standalone_unknown_kind_raises_and_does_not_open_child(self):
        panel=CurrentRitualPanel('ritual','scene_ro6_end3_1','choice_ro6_end3_3')
        self.addCleanup(panel.close)
        with patch.object(panel,'_recheck',return_value=True),patch.object(model,'acquisition_reference',return_value={'kind':'internal-new-kind'}):
            with self.assertRaisesRegex(ValueError,'未支持的材料来源类型'):panel.open_material()
        self.assertIsNone(panel.material_dialog)
