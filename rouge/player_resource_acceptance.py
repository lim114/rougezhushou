from copy import deepcopy

def check_capacities(window,gui,require):
    from PySide6.QtCore import QTimer
    from .map_recognition import map_data
    before=deepcopy(window.run.state)
    for timer in window.findChildren(QTimer):timer.stop()
    try:
        data=map_data();template=next(t for t in data['templates']if t['zone_id']=='zone_1')
        graph={**deepcopy(template),'status':'matched','template_id':template['id'],
            'grid':{'rows':template['rows'],'cols':template['cols']},'source':deepcopy(data['source'])}
        at=window.run.state['started_at']+1
        for index,limit in enumerate((13,17)):
            graph['current_node']=template['nodes'][index]['id']
            window.run.apply({'map':graph,'resources':{'hope':{'value':7,'capacity':limit}}},at+index)
        window.show_compact();bar=window.compact_window;bar.open_map();gui.processEvents()
        require(bar.map_popup.panel.resources.chips['hope'].accessibleName()=='希望 7/17','capacity442_current_limit_visible')
        require('当前值/上限'in bar.map_popup.panel.resources.chips['hope'].toolTip(),'capacity442_plain_format_explained')
        bar.open_replay();gui.processEvents();popup=bar.replay_popup;panel=popup.panel
        panel.tabs.setCurrentWidget(panel.resources);page=panel.resources
        page.filter.setCurrentIndex(page.filter.findData('hope'));page.entries.setCurrentRow(1)
        require(page.entries.count()==2,'capacity442_same_quantity_limit_change_in_history')
        require('上限相对上次变化：+4'in page.detail.toPlainText(),'capacity442_limit_change_is_separate')
        require('相对上次已读数量：+0'in page.detail.toPlainText(),'capacity442_no_fake_quantity_gain')
        page.entries.setCurrentRow(0)
        require('读到上限：13'in page.detail.toPlainText(),'capacity442_old_limit_visible')
        window.run.apply({'resources':{'hope':{'value':7,'capacity':19}}},at+2)
        bar.refresh();gui.processEvents()
        require(page.entries.currentRow()==0 and '读到上限：13'in page.detail.toPlainText(),'capacity442_refresh_keeps_old_selection')
        require('19'not in page.detail.toPlainText().split('读到数量：',1)[-1],'capacity442_no_future_limit_in_old_detail')
        panel.tabs.setCurrentWidget(panel.nodes);panel.nodes.entries.setCurrentRow(0);gui.processEvents()
        require(panel.nodes.resource_pills.chips['history:hope'].accessibleName()=='希望 7/13','capacity442_old_map_pill_uses_old_limit')
        require('7/19'not in panel.nodes.resource_pills.toolTip(),'capacity442_map_does_not_use_current_limit')
        require(window.run.state['resources']['hope']['capacity']==19,'capacity442_history_read_does_not_change_current')
        window.player_validation_target=popup
    finally:
        window.run.state=before


def check_hud(window,gui,require):
    from PySide6.QtCore import QTimer
    from .player_resource_history import resource_rows
    from .player_floor_resources import snapshots
    from .run_config import config_data
    before=deepcopy(window.run.state)
    for timer in window.findChildren(QTimer):timer.stop()
    try:
        window.show_compact();bar=window.compact_window;bar.open_map();gui.processEvents()
        popup=bar.map_popup;panel=popup.panel;strip=panel.resources
        require(popup.isVisible(),'hud441_actual_map_popup_visible')
        old=dict(strip.chips)
        values={'life':{'value':6,'capacity':8},'shield':{'value':0},'command':{'value':3},
                'hope':{'value':7},'action':{'value':4},'valuation':{'value':27}}
        zid=next(iter(config_data()['zones']));at=window.run.state['started_at']+1
        window.run.apply({'page':'run_map','relics':{'ids':[],'count':None},'resources':values,
            'config':{'zone':{'id':zid,'name':config_data()['zones'][zid]['name'],'source':'isolated-hud441'}}},at)
        bar.refresh();gui.processEvents()
        for key,text in {'life':'目标生命 6/8','shield':'护盾 0','command':'指挥等级 3',
                         'hope':'希望 7','action':'行动力 4','valuation':'总估价 27'}.items():
            require(strip.chips[key].accessibleName()==text,'hud441_visible_'+key)
            require(strip.chips[key].isVisible(),'hud441_chip_visible_'+key)
        require(dict(strip.chips)==old,'hud441_refresh_reuses_chips')
        require('不是所选历史层'in strip.chips['life'].toolTip(),'hud441_current_and_history_scope_visible')
        previous=deepcopy(window.run.state['resources'])
        window.run.apply({'relics':{'ids':[],'count':None},'resources':{}},at+1)
        bar.refresh();gui.processEvents()
        require(window.run.state['resources']==previous,'hud441_unread_preserves_time_and_values')
        window.run.apply({'relics':{'ids':[],'count':None},'resources':{'hope':{'value':0}}},at+2)
        bar.refresh();gui.processEvents()
        require(strip.chips['hope'].accessibleName()=='希望 0','hud441_current_zero_updates')
        require(bar.map_popup is popup and strip.chips==old,'hud441_same_popup_and_chips_after_partial_update')
        require({r['resource']for r in resource_rows(window.run.state)}>={'life','shield','command','hope','action','valuation'},'hud441_history_has_all_six_fields')
        require(bool(snapshots(window.run.state)),'hud441_same_frame_floor_snapshot_recorded')
        require(not set(values)&set(window.run.calculation_resources()),'hud441_no_unverified_relic_calculation_effect')
        window.player_validation_target=popup
    finally:
        window.run.state=before


def check(window,gui,require):
    before=deepcopy(window.run.state);window.run.state['history']=[{'kind':'resource_updated','resource':key,'value':value,'at':index+1}for index,(key,value)in enumerate([('gold',10),('parts_count',2),('gold',0),('gold',None),('gold',7),('parts_count',3)])]
    window.show_compact();bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.resources);gui.processEvents();page=panel.resources
    require(page.entries.count()==6,'resource_reads_have_separate_history_page')
    page.entries.setCurrentRow(0);require('变化：未知'in page.detail.toPlainText()or '相对上次已读数量：未知'in page.detail.toPlainText(),'first_resource_read_is_not_gain_from_zero')
    page.entries.setCurrentRow(2);require('读到数量：0'in page.detail.toPlainText()and '-10'in page.detail.toPlainText(),'valid_zero_and_negative_difference_preserved')
    page.entries.setCurrentRow(4);require('未知'in page.detail.toPlainText(),'unread_intermediate_breaks_difference_chain')
    page.filter.setCurrentIndex(page.filter.findData('parts_count'));require(page.entries.count()==2,'resource_filters_do_not_mix_baselines')
    page.entries.setCurrentRow(1);require('+1'in page.detail.toPlainText()and '不能据此确定'in page.detail.toPlainText(),'resource_difference_not_attributed_to_a_drop')
    old=page.entries.currentItem();bar.refresh();require(page.entries.currentItem()is old and page.filter.currentData()=='parts_count','unchanged_refresh_keeps_resource_reading')
    require(page.detail.isReadOnly(),'resource_history_is_read_only');window.player_validation_target=bar.replay_popup;window.run.state=before

