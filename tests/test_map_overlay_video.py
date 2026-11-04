"""Map overlay's actual controller interface; isolated game pixels and state."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import ast,subprocess,time,unittest
from pathlib import Path
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from rouge.player_game_map import registered_rows,frequency_text,battle_targets
from rouge.public_node_statistics import FrequencyIndex,load
from rouge.map_recognition import map_data
from tests.test_player_feature_424 import fixture
from tests.test_sampling_flow import SamplingFlowTests

def map_fixture():
    reference,current,snapshot=fixture();template=map_data()['templates'][0];nodes=[]
    for n in template['nodes']:
        nodes.append({**deepcopy(n),'center':[.18+n['col']*.15,.25+n['row']*.22],
          'visible':True,'template_type':n['fixed_type'],'observed_type':n['fixed_type']or'未知的诡秘',
          'prediction':{'candidates':['诡意行商','不期而遇','作战']}})
    reference['observation']['map'].update(template_id=template['id'],nodes=nodes,grid={'rows':template['rows']})
    for n in nodes:
        x,y=n['center'];n['label_box']=[[x-.05,y+.035],[x+.05,y+.035],[x+.05,y+.08],[x-.05,y+.08]]
    return reference,current,snapshot

class FrequencyBindingTests(unittest.TestCase):
    def test_duplicate_distance_nodes_share_bucket_but_keep_own_position(self):
        a,_,_=map_fixture();g=a['observation']['map'];idx=FrequencyIndex(load());rows=registered_rows(g,'诡意行商',idx)
        self.assertTrue(all(r['position_mapped']for r in rows.values()))
        unknown=[n for n in g['nodes']if not n['template_type']]
        self.assertTrue(any(rows[n['id']]['frequency']is not None for n in unknown))
        for n in g['nodes']:
            if n['template_type']:self.assertIsNone(rows[n['id']]['frequency'])

    def test_unknown_template_or_disagreeing_distance_does_not_get_numbers(self):
        a,_,_=map_fixture();g=a['observation']['map'];n=next(n for n in g['nodes']if not n['template_type']);n['distance']+=1
        self.assertIsNone(registered_rows(g,'诡意行商',FrequencyIndex(load()))[n['id']]['frequency'])
        g['template_id']='unconfirmed'
        self.assertFalse(any(r['position_mapped']for r in registered_rows(g,'作战',FrequencyIndex(load())).values()))

    def test_zero_is_preserved_and_missing_is_dash(self):
        d=load();d['counts']={'combat':{'0':{'2':5}},'rogue-trader':{'0':{'2':0}}};d['metadata']['sampleCount']=5
        rows=FrequencyIndex(d).rows('0',2);zero=next(r for r in rows if r['name']=='诡意行商')
        self.assertEqual(frequency_text(zero),'0%');self.assertEqual(frequency_text(None),'—')

    def test_battle_kind_without_title_cannot_open_another_stage(self):
        self.assertEqual(battle_targets({'observed_type':'作战'}),{})
        self.assertEqual(battle_targets({'content':{'kind':'battle','source':'same_frame_selected_node','title':'wrong','variant_id':'ro6_n_1_2'}}),{})

    def test_bound_battle_uses_existing_tomimi_and_prts_targets(self):
        node={'content':{'kind':'battle','source':'same_frame_selected_node','title':'遗忘时间','variant_id':'ro6_n_1_2'}}
        targets=battle_targets(node);self.assertIn('/ISW-NO_',targets['enemy']['url']);self.assertIn('tomimi.dev/zh/stages/',targets['map']['url'])

    def test_accepted_gates_change_only_by_explicit_pointer_exclusions(self):
        old=subprocess.check_output(['git','show','a6a9ddbbc:rouge/player_game_map.py']).decode('utf8')
        new=Path('rouge/player_game_map.py').read_text('utf8')
        fn=lambda text:next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='payload')
        original=fn(old);updated=fn(new)
        start=next(i for i,n in enumerate(updated.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='pointer_boxes')
        del updated.body[start:start+3]
        update=updated.body[start].body[0].value
        update.keywords=[k for k in update.keywords if k.arg!='cursor_occluded_anchors']
        self.assertEqual(ast.dump(original),ast.dump(updated))

class ControllerTests(unittest.TestCase):
    setUpClass=classmethod(SamplingFlowTests.setUpClass.__func__)
    def setUp(self):
        SamplingFlowTests.setUp(self);self.window.show_compact();self.c=self.window.compact_window;self.overlay=self.c.game_overlay
        self.overlay.timer.stop();self.c.game_binding.timer.stop()
        self.reference,self.current,self.snapshot=map_fixture();self.reference['run_id']=self.window.run.state['id'];self.window.map_overlay_reference=self.reference
        self.c.game_binding.api=SimpleNamespace(read=lambda _:self.snapshot)
        p=patch.object(self.window.capture.buffer,'latest',return_value=self.current);p.start();self.addCleanup(p.stop)
        self.clock=patch('rouge.player_game_map.time.time',return_value=100);self.clock.start();self.addCleanup(self.clock.stop)
        self.overlay.set_enabled(True)

    def test_default_entry_visible_without_script_selecting_type_and_toggle(self):
        self.qt.processEvents();self.assertTrue(self.overlay.interaction.isVisible());self.assertIsNone(self.overlay.kind)
        b=self.overlay.interaction.buttons['诡意行商'];QTest.mouseClick(b,Qt.MouseButton.LeftButton)
        self.qt.processEvents();self.assertEqual(self.overlay.kind,'诡意行商');self.assertTrue(b.isChecked())
        QTest.mouseClick(b,Qt.MouseButton.LeftButton);self.assertIsNone(self.overlay.kind)

    def test_only_hotspots_and_strip_take_input(self):
        self.qt.processEvents();layer=self.overlay.interaction;mask=layer.mask()
        self.assertFalse(mask.contains(QPoint(2,2)))
        identity,x,y=self.overlay.current['points'][0];self.assertFalse(mask.contains(QPoint(round(x),round(y))))
        self.assertTrue(mask.contains(self.overlay.current['label_rects'][identity].center()))
        self.assertTrue(self.overlay.surface.windowFlags()&Qt.WindowType.WindowTransparentForInput)
        self.assertFalse(layer.windowFlags()&Qt.WindowType.WindowDoesNotAcceptFocus)
        self.assertTrue(layer.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating))

    def test_manually_activated_interaction_keeps_overlay_and_other_windows_withdraw_it(self):
        self.snapshot.update(foreground_on_game=False,foreground_hwnd=int(self.overlay.interaction.winId()))
        self.overlay.tick()
        self.assertTrue(self.overlay.interaction.isVisible())
        self.assertFalse(self.snapshot['foreground_on_game'])
        self.overlay.open_node(self.overlay.current['points'][0][0])
        self.snapshot['foreground_hwnd']=int(self.c.winId())
        self.overlay.tick()
        self.assertFalse(self.overlay.card.isVisible())
        self.assertFalse(self.overlay.interaction.isVisible())
        self.assertFalse(self.overlay.surface.isVisible())

    def test_own_foreground_does_not_make_stale_reference_eligible(self):
        self.snapshot.update(foreground_on_game=False,foreground_hwnd=int(self.overlay.interaction.winId()))
        self.reference['captured_at']=69
        self.overlay.tick()
        self.assertFalse(self.overlay.interaction.isVisible())

    def test_pointer_return_activates_only_bound_game_from_interaction(self):
        self.snapshot.update(cursor_on_game=True,foreground_hwnd=int(self.overlay.interaction.winId()))
        with patch('ctypes.windll.user32.SetForegroundWindow',return_value=1) as activate, \
                patch('rouge.player_game_map.QApplication.platformName',return_value='windows'):
            self.overlay.return_game_focus()
            self.assertEqual(activate.call_args.args[0].value,self.snapshot['key'][0])
            activate.reset_mock()
            self.snapshot['cursor_on_game']=False
            self.overlay.return_game_focus()
            self.snapshot.update(cursor_on_game=True,foreground_hwnd=int(self.c.winId()))
            self.overlay.return_game_focus()
            activate.assert_not_called()

    def test_card_on_click_and_every_surface_removed_on_rejection(self):
        identity=self.reference['observation']['map']['nodes'][0]['id'];self.overlay.open_node(identity);self.qt.processEvents()
        self.assertTrue(self.overlay.card.isVisible());self.assertEqual(self.overlay.card.binding[-1],identity)
        self.snapshot['foreground_on_game']=False;self.overlay.tick()
        self.assertFalse(self.overlay.card.isVisible());self.assertFalse(self.overlay.interaction.isVisible());self.assertFalse(self.overlay.surface.isVisible())

    def test_click_on_visible_node_caption_opens_its_card(self):
        node=next(n for n in self.reference['observation']['map']['nodes']if not n['template_type']);rect=self.overlay.current['label_rects'][node['id']]
        QTest.mouseClick(self.overlay.interaction,Qt.MouseButton.LeftButton,pos=rect.center());self.qt.processEvents()
        self.assertTrue(self.overlay.card.isVisible());self.assertEqual(self.overlay.card.binding[-1],node['id'])

    def test_hover_keeps_card_and_node_icon_remains_click_through(self):
        identity=self.overlay.current['points'][0][0];self.overlay.open_node(identity);self.qt.processEvents()
        QTest.mouseMove(self.overlay.card,QPoint(8,8));self.qt.processEvents();self.assertTrue(self.overlay.card.isVisible())
        _,x,y=next(p for p in self.overlay.current['points']if p[0]==identity)
        self.assertFalse(self.overlay.interaction.mask().contains(QPoint(round(x),round(y))))
        self.assertTrue(self.overlay.interaction.mask().contains(self.overlay.card.geometry().center()))

    def test_close_button_releases_listener_and_removes_card_input_region_immediately(self):
        identity=self.overlay.current['points'][0][0]
        self.overlay.open_node(identity);self.qt.processEvents()
        QTest.mouseClick(self.overlay.card.close_button,Qt.MouseButton.LeftButton)
        self.assertFalse(self.overlay.card.isVisible())
        self.assertIsNone(self.overlay.mouse_listener)
        from PySide6.QtGui import QRegion
        expected=QRegion(self.overlay.interaction.strip.geometry())
        for rect in self.overlay.current['label_rects'].values():expected|=QRegion(rect.adjusted(-4,-4,4,4))
        self.assertEqual(self.overlay.interaction.mask(),expected)

    def test_card_refresh_does_not_collapse_rows_or_replace_unchanged_content(self):
        node=next(n for n in self.reference['observation']['map']['nodes']if not n['template_type'])
        self.overlay.open_node(node['id']);self.qt.processEvents();card=self.overlay.card
        first=card.grid.itemAt(0).widget();height=card.types_scroll.height();self.assertGreater(height,60)
        card.source.setChecked(True);node['label_box'][0][0]+=.0001;self.overlay.tick();self.qt.processEvents()
        self.assertIs(card.grid.itemAt(0).widget(),first);self.assertEqual(card.types_scroll.height(),height);self.assertTrue(card.source.isChecked())
        node['prediction']['candidates']+=['应急助力','先行一步','秘境行商','安全的角落'];self.overlay.tick();self.qt.processEvents()
        self.assertGreater(card.types_scroll.height(),height);self.assertGreaterEqual(card.types_scroll.height(),min(280,card.grid.sizeHint().height()))

    def test_reopening_same_cached_card_restores_binding_and_survives_refresh(self):
        identity=self.overlay.current['points'][0][0];self.overlay.open_node(identity);self.qt.processEvents()
        binding=self.overlay.card.binding;first=self.overlay.card.grid.itemAt(0).widget();self.overlay.card.source.setChecked(True)
        self.overlay.outside_click((binding,-1797,103));self.assertIsNone(self.overlay.card.binding)
        self.overlay.open_node(identity);self.overlay.tick();self.qt.processEvents()
        self.assertEqual(self.overlay.card.binding,binding);self.assertTrue(self.overlay.card.isVisible())
        self.assertIs(self.overlay.card.grid.itemAt(0).widget(),first);self.assertTrue(self.overlay.card.source.isChecked())

    def test_outside_press_closes_but_stale_press_cannot_close_another_card(self):
        a,b=self.overlay.current['points'][:2];self.overlay.open_node(a[0]);old=self.overlay.card.binding
        self.overlay.open_node(b[0]);self.overlay.outside_click((old,-1797,103));self.assertTrue(self.overlay.card.isVisible())
        self.overlay.outside_click((self.overlay.card.binding,-1797,103));self.assertFalse(self.overlay.card.isVisible())

    def test_native_mouse_listener_exists_only_during_card_and_all_closures_release_it(self):
        from rouge.player_game_map import GameMapOverlay
        from unittest.mock import Mock
        from PySide6.QtWidgets import QWidget
        for reason in('outside','escape','withdraw','disable','close'):
            with self.subTest(reason=reason),patch('pynput.mouse.Listener',side_effect=lambda **kw:Mock())as factory,patch('rouge.player_game_map.QApplication.platformName',return_value='windows'):
                self.snapshot['foreground_on_game']=True;overlay=GameMapOverlay(self.c,self.window);overlay.timer.stop();overlay.set_enabled(True)
                factory.assert_not_called();self.assertIsNone(overlay.mouse_listener)
                a,b=overlay.current['points'][:2];overlay.open_node(a[0]);listener=overlay.mouse_listener
                factory.assert_called_once();self.assertFalse(factory.call_args.kwargs['suppress']);self.assertNotIn('on_move',factory.call_args.kwargs)
                listener.start.assert_called_once();listener.wait.assert_called_once();overlay.open_node(b[0]);factory.assert_called_once()
                other=QWidget();QTest.keyClick(other,Qt.Key.Key_Escape);other.close();self.assertTrue(overlay.card.isVisible())
                if reason=='outside':overlay.outside_click((overlay.card.binding,-1797,103))
                elif reason=='escape':QTest.keyClick(self.c,Qt.Key.Key_Escape)
                elif reason=='withdraw':self.snapshot['foreground_on_game']=False;overlay.tick()
                elif reason=='disable':overlay.set_enabled(False)
                else:overlay.close()
                self.assertFalse(overlay.card.isVisible());self.assertIsNone(overlay.mouse_listener)
                listener.stop.assert_called_once();listener.join.assert_called_once();overlay.close();listener.stop.assert_called_once()
        self.snapshot['foreground_on_game']=True

    def test_occluded_template_slot_is_not_an_interactive_hotspot(self):
        node=self.reference['observation']['map']['nodes'][0];node['visible']=False;self.overlay.tick()
        self.assertNotIn(node['id'],{p[0]for p in self.overlay.current['points']})

    def test_white_map_selection_and_game_selection_share_one_state(self):
        from rouge.player_map import MapPanel
        panel=MapPanel(self.window,page_owner=self.c)
        self.addCleanup(panel.close)
        self.overlay.set_kind('诡意行商');self.assertEqual(panel.view.filter_kind,'诡意行商')
        panel.set_type_filter('不期而遇');self.assertEqual(self.overlay.kind,'不期而遇');self.assertTrue(self.overlay.interaction.buttons['不期而遇'].isChecked())

    def test_card_outside_region_does_not_capture_game_and_close_button_scope(self):
        identity=self.reference['observation']['map']['nodes'][0]['id'];self.overlay.open_node(identity);self.qt.processEvents()
        self.overlay.dismiss_card();self.overlay.interaction.register(self.overlay.current)
        self.assertFalse(self.overlay.interaction.mask().contains(QPoint(2,2)))

    def test_shared_web_page_is_reused_and_survives_overlay_rejection_and_minimize(self):
        from PySide6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QLineEdit,QLabel
        from PySide6.QtCore import QRect
        from rouge.player_reference_links import open_overlay_web
        target={'url':'https://prts.wiki/w/ISW-NO_test','name':'测试关卡','provider':'PRTS'}
        class Browser(QWidget):
            def __init__(self,target):
                super().__init__();self.navigation=QWidget();self.navigation_bar=QHBoxLayout(self.navigation);self.address=QLineEdit(target['url']);self.title=QLabel();self.environment=QLabel()
                self.navigation_bar.addWidget(self.title);self.navigation_bar.addWidget(self.environment)
                layout=QVBoxLayout(self);layout.addWidget(self.navigation);layout.addWidget(self.address)
        with patch('rouge.tomimi_view.TomimiPanel',Browser):
            a=open_overlay_web(self.c,target,QRect(0,0,1400,900));b=open_overlay_web(self.c,target,QRect(0,0,1400,900))
        self.assertIs(a,b);self.assertTrue(self.c.reference_window.isVisible())
        self.snapshot['foreground_on_game']=False;self.overlay.tick();self.assertTrue(self.c.reference_window.isVisible())
        self.c.game_binding.ever_bound=True;self.c.game_binding.apply(None)
        self.assertTrue(self.c.reference_window.isVisible())

if __name__=='__main__':unittest.main()
