from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QScrollArea
from rouge import player_acceptance
from player_ui_verification import run
out=R/'verification/maintenance/player-tool-navigation-review-20261031/native-current';out.mkdir(exist_ok=False);images=[]
def check(section,w,gui,require):
    w.select_operator('mechanist');w.skill.setCurrentIndex(w.skill.findData(2));w.show_compact();w.compact_window.open_operators();gui.processEvents()
    workspace=w.centralWidget();page=next(p for p,(_,label)in workspace.pages.items()if label=='干员与技能')
    panel=w.offline_tools;dialog=workspace.developer_dialog;owned=id(dialog);state=deepcopy(w.run.state)
    def image(name,widget=dialog):
        gui.processEvents();file=out/(name+'.png');assert widget.grab().save(str(file));images.append({'path':file.relative_to(R).as_posix(),'sha256':sha256(file.read_bytes()).hexdigest()})
    require(not w.mechanist_reference_tools.toggle.isChecked()and not w.barrier_ledger_button.isVisible(),'raw_mechanism_tools_collapsed_by_default')
    image('default-player-technical-fold',w)
    toggle=w.mechanist_reference_tools.toggle;parent=toggle.parentWidget()
    while parent:
        if isinstance(parent,QScrollArea):parent.ensureWidgetVisible(toggle,16,16)
        parent=parent.parentWidget()
    gui.processEvents();QTest.mouseClick(toggle,Qt.MouseButton.LeftButton);gui.processEvents()
    require(toggle.isChecked(),'actual_mouse_expands_technical_tools')
    for control,query in(('barrier_ledger_button','barrier-ledger'),('shield_grant_button','shield-grants'),('shield_inventory_button','shield-inventory'),('explosion_values_button','explosion-values')):
        workspace.setCurrentWidget(page);gui.processEvents();button=getattr(w,control);parent=button.parentWidget()
        while parent:
            if isinstance(parent,QScrollArea):parent.ensureWidgetVisible(button,16,16)
            parent=parent.parentWidget()
        gui.processEvents();require(button.isVisible()and button.isEnabled(),'eligible_visible_player_button_'+query)
        QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents()
        require(dialog.isVisible()and panel.isVisible()and workspace.currentWidget()is panel,'actual_mouse_click_opens_exact_reader_'+query)
        require(panel.current_query()==('calibration',query),'accurate_query_'+query)
        require(id(workspace.developer_dialog)==owned,'same_owned_dialog_reused_'+query)
        require(not workspace.developer_tools and not workspace.developer_tabs.tabBar().isVisible(),'no_generic_debug_navigation_'+query)
        if query in('barrier-ledger','explosion-values'):image(query)
        if query=='barrier-ledger':panel.editor.setPlainText('{"manual_test_draft": true}')
    workspace.setCurrentWidget(page);gui.processEvents();button=w.barrier_ledger_button
    parent=button.parentWidget()
    while parent:
        if isinstance(parent,QScrollArea):parent.ensureWidgetVisible(button,16,16)
        parent=parent.parentWidget()
    QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents()
    require(panel.editor.toPlainText()=='{"manual_test_draft": true}','original_query_draft_survives_four_tool_round_trip')
    require(workspace.go_back()and workspace.currentWidget()is page and not dialog.isVisible(),'back_returns_to_original_player_reader')
    w.show_shield_grants();gui.processEvents();QTest.keyClick(dialog,Qt.Key.Key_Escape);gui.processEvents()
    require(not dialog.isVisible(),'escape_closes_query_window')
    require(not workspace.setCurrentWidget(w.paired_calibration)and not dialog.isVisible(),'ordinary_debug_navigation_stays_blocked')
    require(w.run.state==state,'query_navigation_does_not_change_run')
    w.show_shield_inventory();gui.processEvents();image('single-player-query');w.player_validation_target=dialog
with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'temporary_public_preview_only':True,'query_execution_or_mechanism_calibration_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
