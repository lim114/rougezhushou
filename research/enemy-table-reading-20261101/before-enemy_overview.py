"""Foldable, exact-reference mechanism overview; never substitutes base stats."""
from PySide6.QtCore import Qt,QSize,Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QTreeWidget,QTreeWidgetItem,QHeaderView,QSizePolicy
from .current_enemy_traits import MOTION,ATTACK,DAMAGE


def overview_cells(enemy,forecast=None):
    traits=enemy.get('declared_traits')or{};values=traits.get('values')or{}
    kinds=[MOTION.get(values.get('motion'),'行动方式未核对'),ATTACK.get(values.get('applyWay'),'攻击途径未核对')]
    damage=traits.get('handbook_damage_types')
    if damage:kinds.append('图鉴：'+'、'.join(DAMAGE.get(v,'类型未核对')for v in damage))
    text='\n'.join(enemy['abilities'])or enemy['description']or'尚无独立说明，请查看完整资料。'
    summary=text if len(text)<=180 else text[:180]+'…（点选查看全文）'
    from .current_enemy_forecast import component_numbers
    return [enemy['name'],*component_numbers(forecast),'\n'.join(kinds),summary]


class EnemyOverview(QWidget):
    selected=Signal(str)

    def __init__(self,parent=None):
        super().__init__(parent);self._scope=None;self._expanded={}
        self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Ignored)
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        self.notice=QLabel('点选一行查看完整机制。这里列的是本关候选，不是实际敌人数；数值仅为已证环境分项，不含完整藏品、阶段和技能影响，完整本局总量仍未知，不用白值填入。');self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.tree=QTreeWidget();self.tree.setAccessibleName('按普通精英领袖分组的敌人机制总览');self.tree.setHeaderLabels(['敌人','生命分项','攻击分项','防御分项','法抗分项','行动与攻击（资料）','机制要点']);self.tree.setIconSize(QSize(36,36));self.tree.setWordWrap(True);self.tree.setIndentation(15);self.tree.setAllColumnsShowFocus(True)
        header=self.tree.header()
        for column,width in enumerate((155,88,83,77,77,135)):
            header.setSectionResizeMode(column,QHeaderView.ResizeMode.Interactive);self.tree.setColumnWidth(column,width)
        header.setSectionResizeMode(6,QHeaderView.ResizeMode.Stretch);header.setMinimumSectionSize(65)
        self.tree.setStyleSheet('QHeaderView::section {background:#333333;color:#ededed;border:1px solid #585858;padding:5px;} QTreeWidget::item {padding:4px;}')
        layout.addWidget(self.tree,1)
        self.tree.currentItemChanged.connect(lambda item,_:self._select(item))
        self.tree.itemClicked.connect(lambda item,_:self._select(item))
        self.tree.itemActivated.connect(lambda item,_:self._select(item))

    def _select(self,item):
        key=item.data(0,Qt.ItemDataRole.UserRole)if item is not None else None
        if key is not None:self.selected.emit(key)

    def set_rows(self,enemies,entries,scope,forecasts=None):
        if self._scope==scope:
            for i in range(self.tree.topLevelItemCount()):
                group=self.tree.topLevelItem(i);self._expanded[group.data(0,Qt.ItemDataRole.UserRole+1)]=group.isExpanded()
        else:self._expanded={}
        self._scope=scope;offset=self.tree.verticalScrollBar().value()if scope is not None else 0
        blocked=self.tree.blockSignals(True);self.tree.clear();lookup={e['key']:e for e in enemies};groups={}
        for _,key,icon in entries:
            enemy=lookup[key];tier=enemy['tier'];label={'NORMAL':'普通','ELITE':'精英','BOSS':'领袖'}.get(tier,'类别未确认')
            if tier not in groups:
                group=QTreeWidgetItem([label]);group.setData(0,Qt.ItemDataRole.UserRole+1,tier);self.tree.addTopLevelItem(group);group.setFirstColumnSpanned(True);groups[tier]=group
            forecast=(forecasts or{}).get(key)
            item=QTreeWidgetItem(overview_cells(enemy,forecast));item.setData(0,Qt.ItemDataRole.UserRole,key);item.setIcon(0,icon)
            item.setToolTip(0,enemy['name']+' · 引用资料'+str(enemy['reference_index']+1)+'；同名不同引用分开保留')
            for column in range(1,5):item.setToolTip(column,'仅已证环境分项；完整本局总量未知。\n'+(forecast or{}).get('conditions_label','难度与区域尚未带入')+'\n'+'\n'.join((forecast or{}).get('player_pending',[])))
            item.setToolTip(5,'资料中的行动与攻击声明，不证明当前阻挡、免疫或阶段状态。');item.setToolTip(6,'\n'.join(enemy['abilities'])or enemy['description']);groups[tier].addChild(item)
        for tier,group in groups.items():
            group.setText(0,group.text(0)+' · '+str(group.childCount())+'条候选资料');group.setExpanded(self._expanded.get(tier,True))
        self.tree.verticalScrollBar().setValue(offset);self.tree.blockSignals(blocked)
