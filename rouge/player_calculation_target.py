"""Read the selected calculation target in the existing fixed-stage reader."""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QTimer
from .player_map_reader import make_reader


def open_target(window, *, source='calculator'):
    legacy=source=='stage'
    parent=window.battle_preview if legacy else window.damage_page
    status=window.battle_preview.current_reference_status if legacy else window.target_preview_status
    def context():
        if legacy:
            stage=parent.current_stage;pair=parent.enemy_combo.currentData()
            target={'enemy_id':pair[0],'level':pair[1]}if pair is not None else None
        else:
            stage=window.target_stage.currentData();target=window.target_enemy.currentData()
        return (stage,target,None if legacy else window.calculation_scope.currentData())if stage is not None else None
    if context() is None:
        return False
    window.show_compact()
    owner=window.compact_window
    if not owner.open_full(parent):
        return False
    status.hide()
    def create(page_owner):
        stage,target,_scope=context()
        page=make_reader('battle',{'id':stage,'title':'计算目标'},window,
                         historical=True,page_owner=page_owner)
        if page is None:
            status.setText('该关卡暂无作战资料。');status.show()
            return None
        page.resize(800,600)
        if target is not None:
            matches=[enemy for enemy in page.panel.result['enemies']
                     if enemy['id']==target['enemy_id'] and enemy['level']==target['level']]
            if len(matches)==1:
                page.panel.enemy_choices.select_value(matches[0]['key'],emit=True)
                page.panel.tabs.setCurrentIndex(1)
                QTimer.singleShot(0,page.panel.enemy_scroll,lambda:page.panel.enemy_scroll.ensureWidgetVisible(page.panel.enemy_details))
        back=QPushButton('返回计算')
        back.clicked.connect(lambda:page_owner.open_full(window.damage_page))
        page.header_bar.addWidget(back)
        return page
    return owner.reference_window.open_reference(parent,('calculation-target',source),context,create)
