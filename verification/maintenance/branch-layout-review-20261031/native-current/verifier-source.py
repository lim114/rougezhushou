"""Actual Qt player-reader resizing; temporary state and no game/chat actions."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QStyleOptionComboBox,QStyle,QWidget,QVBoxLayout,QComboBox
        from PySide6.QtGui import QIcon,QFont
        import win32gui,win32process
        from rouge.player_map_reader import make_reader
        from rouge.branch_choice import BranchChoice
        initial=deepcopy(window.run.state)
        def save(widget,name):
            gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
        def readable(control,name):
            option=QStyleOptionComboBox();control.branch.initStyleOption(option)
            rect=control.branch.style().subControlRect(QStyle.ComplexControl.CC_ComboBox,option,QStyle.SubControl.SC_ComboBoxEditField,control.branch)
            icon=control.branch.iconSize().width()+4 if not option.currentIcon.isNull()else 0
            require(rect.width()-icon>=control.branch.fontMetrics().horizontalAdvance(control.branch.currentText()),name+'_complete_category_label')
        window.show_compact();window.hide();gui.processEvents()
        dialog=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定作战'},window.compact_window)
        require(dialog is not None,'actual_map_reader_factory_available');dialog.show();gui.processEvents()
        panel=dialog.panel;reward=panel.rewards;panel.tabs.setCurrentWidget(reward)
        require(dialog.objectName()=='mapReferenceWindow','normal_player_reader_style_applied')
        require(not window.isVisible(),'reader_does_not_force_full_main_window')
        row=next(r for r in reward.result['rows']if r['source_action_keys'])
        reward.choices.select_value(row['id']);reward.source_combo.setCurrentIndex(1)
        selected=(reward.combo.currentData(),reward.source_combo.currentData())
        for width in (720,1000):
            dialog.resize(width,650);gui.processEvents();readable(reward.choices,'rewards_'+str(width));save(dialog,'player-rewards-'+str(width))
            require(reward.choices.branch.height()==reward.combo.height(),'rewards_'+str(width)+'_matching_control_heights')
            require((reward.combo.currentData(),reward.source_combo.currentData())==selected,'resize_preserves_exact_reward_and_source')
        require(panel.refresh_reference(),'same_source_reference_refresh_passes')
        require((reward.combo.currentData(),reward.source_combo.currentData())==selected,'refresh_preserves_exact_reward_and_source')
        QTest.mouseClick(reward.source_button,Qt.MouseButton.LeftButton);gui.processEvents()
        require(panel.action_key==selected[1]and panel.tabs.currentIndex()==2,'real_source_button_still_maps_exact_action')
        require('准确时刻：未知'in panel.action_player.toPlainText(),'resizing_does_not_invent_actual_clock')
        panel.tabs.setCurrentIndex(1);gui.processEvents();readable(panel.enemy_choices,'enemy_categories');save(dialog,'player-enemy-categories')
        fixture=QWidget();layout=QVBoxLayout(fixture);combo=QComboBox()
        control=BranchChoice(combo,[('宝箱与装置',[('名称很长的准确奖励资料'*10,'box',QIcon())]),('移动恶笼草',[('移动奖励','moving',QIcon())])],overview_label='总览（本关奖励来源）',placeholder='请选择奖励目标')
        layout.addWidget(control);layout.addStretch();fixture.resize(900,160);fixture.show();gui.processEvents()
        width=fixture.minimumSizeHint().width()
        fixture.resize(width,160);gui.processEvents()
        require(fixture.width()==width,'long_item_does_not_force_wide_parent')
        require(combo.y()>control.branch.geometry().bottom(),'narrow_controls_automatically_wrap')
        readable(control,'narrow_fixture');save(fixture,'narrow-category-controls')
        control.branch.setFocus();QTest.keyClick(control.branch,Qt.Key.Key_End);gui.processEvents()
        require(control.branch.currentData()=='移动恶笼草','actual_keyboard_selects_category_branch')
        require(combo.count()==2 and combo.itemData(1)=='moving','branch_has_only_its_own_exact_target')
        QTest.keyClick(combo,Qt.Key.Key_End);gui.processEvents();require(combo.currentData()=='moving','actual_keyboard_selects_exact_target')
        before=(control.branch.currentData(),combo.currentData());emissions=[];combo.currentIndexChanged.connect(lambda _:emissions.append(combo.currentData()))
        fixture.resize(900,160);gui.processEvents();require(control.branch.y()==combo.y(),'widening_returns_to_one_row')
        require(before==(control.branch.currentData(),combo.currentData())and not emissions,'reflow_does_not_select_or_emit');save(fixture,'wide-category-controls')
        fixture.resize(460,200);font=QFont(fixture.font());font.setPointSize(18);fixture.setFont(font);gui.processEvents();readable(control,'large_font');save(fixture,'large-font-category-controls');fixture.close()
        require(window.run.state==initial,'all_owned_public_readers_preserve_fixture_state')
        window.player_validation_target=dialog
    player_acceptance.check=check;code=run(419,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)
