from copy import deepcopy
from PySide6.QtCore import Qt

def check(window,gui,require):
    state=deepcopy(window.run.state)
    window.run.state['operators']={'mechanist':{'present':True,'fields':{'elite':1,'level':80,'potential':1,'trust':100,'selected_skill':2},'skill_ranks':{'1':7,'2':7,'3':7}},'kaltsit':{'present':False}}
    window.show_compact();bar=window.compact_window;bar.team_button.click();gui.processEvents();panel=bar.team_popup.panel
    require(bar.team_popup.isVisible()and not window.isVisible(),'team_in_own_compact_popover')
    require(panel.tabs.count()==10,'overview_eight_professions_and_unknown_have_separate_branches')
    overview=panel.lists[None];require(overview.count()==1,'overview_has_only_present_run_members')
    overview.setCurrentRow(0);gui.processEvents();require('机械师'in panel.detail.toPlainText()and '等级：80'in panel.detail.toPlainText(),'read_only_observed_training_visible')
    require(panel.detail.isReadOnly()and panel.skills.count()==3,'training_not_editable_and_all_three_skill_icons')
    require(not overview.currentItem().icon().isNull()and all(not panel.skills.item(i).icon().isNull()for i in range(3)),'actual_portrait_and_skill_assets_loaded')
    require(panel.lists['tank'].count()==1 and all(w.count()==0 for key,w in panel.lists.items()if key not in(None,'tank')),'profession_members_not_duplicated_into_other_branches')
    item=overview.currentItem();text=panel.detail.toPlainText();bar.refresh();require(overview.currentItem()is item and panel.detail.toPlainText()==text,'unchanged_refresh_keeps_team_reading')
    chosen=[];panel.openOperator.connect(chosen.append);panel.calculate.click();gui.processEvents();require(chosen==['mechanist']and window.operator.currentData()=='mechanist','exact_member_calculation_link')
    window.show_compact();bar.open_team();window.run.state['operators']['mechanist']['present']=False;bar.refresh();require(overview.count()==0 and not panel.calculate.isVisible(),'confirmed_departure_clears_team_and_link')
    window.run.state['operators']['mechanist']['present']=True;bar.refresh();overview.setCurrentRow(0);panel.notice.setText('隔离验收示例：机械师的已读培养；不是当前本局或完整预计面板。')
    window.run.state=state
