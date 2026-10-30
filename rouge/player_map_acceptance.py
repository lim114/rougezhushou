"""Isolated native checks for the video-style map interaction, public fixtures only."""
from copy import deepcopy
from pathlib import Path
import json
from PySide6.QtCore import Qt,QPoint,QPointF,QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest

def fixtures():
    data=json.loads((Path(__file__).with_name('data')/'map-templates.json').read_text('utf8'));graphs=[]
    for zone in('zone_1','zone_2'):
        t=next(t for t in data['templates']if t['zone_id']==zone)
        nodes=[{**n,'template_type':n.get('fixed_type'),'visible':False,'center':[.5,.5]}for n in t['nodes']]
        graphs.append({'zone_id':zone,'template_id':t['id'],'nodes':nodes,'grid':{'rows':t['rows'],'cols':t['cols']},'edges':t['edges'],'source':data['source']})
    nodes=[n for n in graphs[0]['nodes']if not n.get('template_type')]
    nodes[0].update(observed_type='未知的诡秘',prediction={'candidates':['诡意行商','不期而遇']})
    nodes[1].update(observed_type='林间空地',remembered_type='诡意行商')
    nodes[2].update(observed_type='诡意行商')
    return graphs,nodes[0]['id'],nodes[1]['id'],nodes[2]['id']

def check(window,gui,require):
    def owned_move(view,point):
        event=QMouseEvent(QEvent.Type.MouseMove,QPointF(point),QPointF(view.mapToGlobal(point)),Qt.MouseButton.NoButton,Qt.MouseButton.NoButton,Qt.KeyboardModifier.NoModifier)
        gui.sendEvent(view,event)
    before=deepcopy(window.run.state);graphs,candidate,passed,known=fixtures()
    window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();bar=window.compact_window;bar.open_map();gui.processEvents();mp=bar.map_popup.panel
    require(len(mp.type_buttons)==5,'video_has_five_map_type_shortcuts')
    mp.type_buttons['诡意行商'].click();gui.processEvents()
    require(mp.view.filter_kind=='诡意行商'and sum(b.isChecked()for b in mp.type_buttons.values())==1,'type_shortcut_highlights_only_selected_kind')
    require(mp.view.overlay[candidate]['match']=='candidate'and mp.view.overlay[candidate]['frequency']is not None,'candidate_location_has_source_historical_rate')
    require(mp.view.overlay[passed]['match']=='history'and mp.view.overlay[passed]['frequency']is None,'passed_location_keeps_history_without_new_rate')
    require(mp.view.overlay[known]['match']=='observed'and mp.view.overlay[known]['frequency']is None,'revealed_location_not_prediction')
    mp.refresh();require(mp.type_buttons['诡意行商'].isChecked(),'refresh_preserves_type_filter')
    mp.type_buttons['诡意行商'].click();require(mp.view.filter_kind is None,'click_selected_shortcut_clears_filter')
    old_selection=mp.view.selected
    # Native show/layout can settle during the first wait. Derive the node point
    # afterwards, so a stale pre-layout coordinate cannot hover a different node.
    QTest.qWait(180);gui.processEvents();owned_move(mp.view,QPoint(3,3))
    point=mp.view._positions()[1][candidate].toPoint();owned_move(mp.view,point);mp.hover_timer.stop();mp.hover_timer.timeout.emit();gui.processEvents()
    card=mp.hover_card;require(card.isVisible(),'owned_mouse_hover_opens_node_card')
    require(mp.view.selected==old_selection and not mp.drawer.isVisible(),'hover_does_not_change_selection_or_force_drawer')
    require(set(card.type_values)=={'诡意行商','不期而遇'},'hover_uses_exact_node_candidate_types')
    require('不是本局概率'in card.notice.text()and'当前DLC'in card.notice.text(),'historical_rate_scope_visible_in_hover')
    require(card.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating),'hover_does_not_request_activation')
    event=next((r for r in card.entry_buttons if r[0]=='event'),None);require(event is not None,'hover_has_condition_scoped_event_cards')
    require(any(not button.icon().isNull()for _,_,button in card.entry_buttons),'event_cards_have_artwork_or_explicit_node_icon')
    require(all(button.height()>button.iconSize().height()+button.fontMetrics().height()+8 for _,_,button in card.entry_buttons),'thumbnail_cards_leave_room_for_readable_names')
    _,identity,button=event;button.click();gui.processEvents()
    require(mp.drawer.isVisible()and mp.selected_reference[1:]==('event',identity),'event_card_reads_exact_event_inside_map')
    require(not window.isVisible(),'event_card_reading_does_not_open_large_window')
    require('https://'not in mp.detail.toPlainText()and 'community_group_'not in mp.detail.toPlainText(),'map_event_reading_uses_player_chinese_not_raw_sources')
    mp.hover_timer.stop();mp.leave_timer.stop();point=mp.view._positions()[1][candidate].toPoint();mp.hover_pending=(candidate,mp.view.mapToGlobal(point));mp.show_hover();gui.processEvents()
    require(card.isVisible(),'card_reopens_after_drawer_layout_change');card.pin.click();binding=card.binding
    other=next(n['id']for n in graphs[0]['nodes']if n['id']!=candidate);owned_move(mp.view,mp.view._positions()[1][other].toPoint());mp.hover_timer.stop();mp.hover_timer.timeout.emit();gui.processEvents()
    require(card.isVisible()and card.pinned and card.binding==binding,'pinned_hover_not_rebound_by_neighbor')
    mp.refresh();require(card.pinned and card.binding==binding,'same_map_refresh_keeps_pinned_reading')
    mp.floors.setCurrentIndex(1);gui.processEvents();require(not card.isVisible()and not card.pinned,'floor_change_expires_pinned_card')
    mp.floors.setCurrentIndex(0);gui.processEvents();mp.set_type_filter('诡意行商');mp.details_toggle.setChecked(False)
    mp.queue_hover(candidate,mp.view.mapToGlobal(mp.view._positions()[1][candidate].toPoint()));QTest.qWait(250);gui.processEvents();card.pin.setChecked(True)
    require(card.binding[-1]==candidate,'return_to_floor_hover_has_own_node')
    mp.status.setText('隔离验收示例：公开模板与声明候选；不是本局游戏识别。历史节点比例不是本局概率。')
    require('本局最近已读资源'in mp.resources.accessibleName() and all(r['value']=='未读' for r in mp.resources.rows if r['key'] in ('life','shield','command','hope','action','valuation')),'resource_chips_do_not_invent_missing_values')
    window.run.state=before;QTest.qWait(100);gui.processEvents()
