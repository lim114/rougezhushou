"""Conditional reward reader with exact links back to configured action rows."""
from PySide6.QtCore import Signal,QSize
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QTabWidget,QPlainTextEdit,QTreeWidget,QTreeWidgetItem,QHeaderView,QAbstractItemView,QScrollArea
from . import current_reward_reference as model
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentRewardPanel(QWidget):
    actionSelected=Signal(str)
    def __init__(self,stage_id,parent=None,*,load=True,settlement=None):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;self.row_id=None
        self.sections=None
        outer=QVBoxLayout(self);outer.setContentsMargins(0,0,0,0);body=QWidget();layout=QVBoxLayout(body)
        self.body_scroll=QScrollArea();self.body_scroll.setWidgetResizable(True);self.body_scroll.setFrameShape(QScrollArea.Shape.NoFrame);self.body_scroll.setWidget(body)
        if settlement is not None:
            self.sections=QTabWidget();self.sections.addTab(self.body_scroll,'可能获得');self.sections.addTab(settlement,'通关收入');outer.addWidget(self.sections)
            settlement.notice.hide();settlement.refresh_button.hide()
        else:outer.addWidget(self.body_scroll)
        self.notice=QLabel(model.NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.refresh_button=QPushButton('重新核对奖励资料');layout.addWidget(self.refresh_button)
        if settlement is not None:self.notice.hide();self.refresh_button.hide()
        self.combo=QComboBox();self.choices=BranchChoice(self.combo,[],overview_label='总览（本关奖励来源）',placeholder='请选择奖励目标',notify_unchanged=True);layout.addWidget(self.choices)
        from .collapsible_section import QCollapsible
        from .wrapped_item_delegate import WrappedItemDelegate
        self.reward_icons={};self._overview_scope=None;self._overview_folds={}
        self.overview_section=QCollapsible('奖励来源总览',expandedIcon='−',collapsedIcon='+');self.overview_section.setDuration(0);self.overview_section.content().hide();self.overview_section.toggled.connect(self.overview_section.content().setVisible)
        self.overview_section.toggleButton().setStyleSheet('text-align:left;background:transparent;color:#ededed;border:0;border-bottom:1px solid #585858;border-radius:0;padding:6px 2px;font-weight:600;')
        self.overview_notice=QLabel();self.overview_notice.setWordWrap(True);self.overview_section.addWidget(self.overview_notice)
        self.overview=QTreeWidget();self.overview.setAccessibleName('奖励来源、可获得内容及出现条件总览；点击或回车查看完整说明');self.overview.setHeaderLabels(['奖励来源','达成条件与可能获得','出现记录与限制']);self.overview.setIconSize(QSize(36,36));self.overview.setWordWrap(True);self.overview.setTextElideMode(Qt.TextElideMode.ElideNone);self.overview.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel);self.overview.setMinimumHeight(90);self.overview.setMaximumHeight(240)
        self.overview.setItemDelegate(WrappedItemDelegate(self.overview,(1,2)));header=self.overview.header();header.setMinimumSectionSize(75)
        for column,width in enumerate((185,290,230)):header.setSectionResizeMode(column,QHeaderView.ResizeMode.Interactive);self.overview.setColumnWidth(column,width)
        header.sectionResized.connect(self.overview.doItemsLayout);self.overview.setStyleSheet('QHeaderView::section {background:#333333;color:#ededed;border:1px solid #585858;padding:5px;} QTreeWidget::item {padding:4px;border-bottom:1px solid #585858;border-right:1px solid #585858;}')
        self.overview.itemClicked.connect(self._open_overview_item);self.overview.itemActivated.connect(self._open_overview_item);self.overview_section.addWidget(self.overview);layout.addWidget(self.overview_section)
        self.portrait=QLabel();self.portrait.setFixedHeight(74);self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter);self.portrait.hide();layout.addWidget(self.portrait)
        bar=QHBoxLayout();self.source_combo=QComboBox();self.source_combo.setAccessibleName('对应的出现条件');self.source_button=QPushButton('查看这条出现条件');bar.addWidget(self.source_combo,1);bar.addWidget(self.source_button);layout.addLayout(bar)
        self.shop_vault_dialog=None
        self.shop_vault_button=QPushButton('查看这份保险柜的领取条件与商店后果');self.shop_vault_button.hide();self.shop_vault_button.setEnabled(False)
        layout.addWidget(self.shop_vault_button);self.shop_vault_button.clicked.connect(self.open_shop_vault)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True);self.tabs.addTab(self.player,'奖励和条件');self.tabs.addTab(self.technical,'完整来源与候选');layout.addWidget(self.tabs,1)
        self.combo.currentIndexChanged.connect(self._selected);self.source_combo.currentIndexChanged.connect(self._source_changed);self.source_button.clicked.connect(self.follow_action);self.refresh_button.clicked.connect(self.refresh_reference)
        if load:self.refresh_reference()

    def clear_reference(self):
        self._close_shop_vault();self.shop_vault_button.hide();self.shop_vault_button.setEnabled(False)
        self.result=None;self.row_id=None;self.choices.set_groups([],emit=False)
        self.reward_icons={};self._sync_overview();self.overview_section.collapse(animate=False)
        self.portrait.clear();self.portrait.hide()
        blocked=self.source_combo.blockSignals(True);self.source_combo.clear();self.source_combo.blockSignals(blocked);self.source_button.setEnabled(False)
        self.source_combo.hide();self.source_button.hide()
        replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
        self.body_scroll.verticalScrollBar().setValue(0)

    def refresh_reference(self):
        fresh=model.stage_rewards(self.stage_id)
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity']and self.result['stage_id']==fresh['stage_id']
        selected=self.combo.currentData()if keep else None;self.result=fresh
        self.reward_icons={}
        for row in fresh['rows']:
            icon=QIcon();pixmap=QPixmap();raw=model.battle.picture_bytes(row['portrait'])if row['portrait']else None
            if raw and pixmap.loadFromData(raw,'PNG'):icon=QIcon(pixmap)
            self.reward_icons[row['id']]=icon
        groups=[(label,[(r['name']+' · 候选'+str(i+1),r['id'],self.reward_icons[r['id']])for i,r in enumerate(fresh['rows'])if r['kind']==kind])for kind,label in(('device','宝箱与装置'),('moving','移动恶笼草'),('rare','稀有敌人'))]
        blocked=self.combo.blockSignals(True);self.choices.set_groups(groups,emit=False)
        if selected is not None:self.choices.select_value(selected,emit=False)
        self.combo.blockSignals(blocked);self._selected(preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0);self.body_scroll.verticalScrollBar().setValue(0)
        return True

    def _selected(self,*_,preserve=False):
        identity=self.combo.currentData();row=next((r for r in self.result['rows']if r['id']==identity),None)if self.result else None
        keep=preserve and identity==self.row_id;source_key=self.source_combo.currentData()if keep else None;self.row_id=identity
        self._sync_overview()
        if not keep:
            if row is None:self.overview_section.expand(animate=False)
            else:self.overview_section.collapse(animate=False)
        self.portrait.clear();self.portrait.setVisible(row is not None and row['kind']!='device')
        if row is not None and row['kind']!='device':
            raw=model.battle.picture_bytes(row['portrait']);pixmap=QPixmap()
            if raw and pixmap.loadFromData(raw,'PNG'):self.portrait.setPixmap(pixmap.scaled(74,74,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.portrait.setText('此精确敌人引用的图片未取得；不借用同名单位图片。')
        replace_text(self.player,(model.row_text(row)if row else model.summary_text(self.result))if self.result else model.UNAVAILABLE,preserve=keep)
        replace_text(self.technical,_technical_json({'result':self.result,'selected_row':row})if self.result else'',preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0);self.body_scroll.verticalScrollBar().setValue(0)
        blocked=self.source_combo.blockSignals(True);self.source_combo.clear();self.source_combo.addItem('选择一条已明确对应的出现条件',None)
        for a in row['source_actions']if row else[]:
            q=a['queue'];title=(f"主波次{q['wave']} · 第{q['fragment']}组"if q['kind']=='main'else f"条件分支{q['branch_index']} · 第{q['phase']}段")
            self.source_combo.addItem(title+' · 条目'+str(a['action_index']),a['key'])
        if source_key is not None:self.source_combo.setCurrentIndex(max(0,self.source_combo.findData(source_key)))
        self.source_combo.blockSignals(blocked);self._source_changed()
        self.source_combo.setVisible(row is not None);self.source_button.setVisible(row is not None)
        self._sync_shop_vault(keep)

    def _sync_overview(self):
        scope=(self.stage_id,self.result['source_identity'])if self.result else None;same=scope is not None and scope==self._overview_scope;tree=self.overview
        if same:
            for i in range(tree.topLevelItemCount()):
                group=tree.topLevelItem(i);self._overview_folds[group.data(0,Qt.ItemDataRole.UserRole+1)]=group.isExpanded()
        else:self._overview_folds={}
        offset=tree.verticalScrollBar().value()if same else 0;horizontal=tree.horizontalScrollBar().value()if same else 0;blocked=tree.blockSignals(True);tree.clear();groups={};lookup={r['id']:r for r in self.result['rows']}if self.result else{}
        for title,key,icon in self.choices.entries():
            row=lookup[key];kind=row['kind']
            if kind not in groups:
                group=QTreeWidgetItem([{'device':'宝箱与装置','moving':'移动恶笼草','rare':'稀有敌人'}[kind]]);group.setData(0,Qt.ItemDataRole.UserRole+1,kind);tree.addTopLevelItem(group);group.setFirstColumnSpanned(True);groups[kind]=group
            count=len(row['source_action_keys']);appearance=f'已列{count}条对应出现记录；是否激活或生成仍未知。'if count else'尚未绑定唯一出现记录，不表示不会出现。'
            if row['candidate_groups']:appearance+='\n含同组候选，不能当作同时出现或相加。'
            item=QTreeWidgetItem([title,'\n'.join(model.outcome_lines(row['rule'])),appearance]);item.setData(0,Qt.ItemDataRole.UserRole,key);item.setIcon(0,icon);item.setToolTip(0,title+('；图片未取得，不借用同名图片。'if icon.isNull()else''));item.setToolTip(2,'点选后可查完整原文、同组候选和关联分支；记录条数不是实际出怪数。')
            for column in range(3):item.setTextAlignment(column,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
            groups[kind].addChild(item)
        for kind,group in groups.items():group.setExpanded(self._overview_folds.get(kind,True))
        tree.doItemsLayout();tree.verticalScrollBar().setValue(offset);tree.horizontalScrollBar().setValue(horizontal);tree.blockSignals(blocked);self._overview_scope=scope
        self.overview_notice.setText(f'当前分类{sum(g.childCount()for g in groups.values())}条奖励来源候选，不能相加成实际奖励。点击或回车查看完整条件。'if self.result else model.UNAVAILABLE)

    def _open_overview_item(self,item,*_):
        key=item.data(0,Qt.ItemDataRole.UserRole)
        if key is not None:self.choices.select_value(key)

    def _source_changed(self,*_):self.source_button.setEnabled(self.result is not None and self.source_combo.currentData()is not None)

    def follow_action(self):
        key=self.source_combo.currentData()
        if self.result is None or self.row_id is None or key is None:return False
        fresh=model.stage_rewards(self.stage_id)
        if fresh!=self.result:self.clear_reference();return False
        row=next((r for r in fresh['rows']if r['id']==self.row_id),None)
        if row is None or key not in row['source_action_keys']:return False
        self.actionSelected.emit(key);return True

    def closeEvent(self,event):
        self._close_shop_vault();super().closeEvent(event)

    def _close_shop_vault(self):
        child=getattr(self,'shop_vault_dialog',None)
        if child is not None:
            child.panel.clear_reference();child.close()
        self.shop_vault_dialog=None

    def _sync_shop_vault(self,keep):
        from . import current_cannot_reference as reader
        target=reader.target_for_reward(self.stage_id,self.row_id) if self.result is not None and self.row_id is not None else None
        available=target is not None
        self.shop_vault_button.setVisible(available);self.shop_vault_button.setEnabled(available)
        child=getattr(self,'shop_vault_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_shop_vault()
            elif not available:child.panel.clear_reference()
            else:child.panel.refresh_reference()
        return target

    def open_shop_vault(self):
        if self.result is None or self.row_id is None:return False
        if self.combo.currentData()!=self.row_id:
            self._close_shop_vault();return False
        if model.stage_rewards(self.stage_id)!=self.result:
            self.clear_reference();return False
        target=self._sync_shop_vault(True)
        if target is None:
            self._close_shop_vault();return False
        from .current_cannot_view import CurrentCannotDialog
        self._close_shop_vault();self.shop_vault_dialog=CurrentCannotDialog(target,self)
        if self.shop_vault_dialog.panel.result is None:
            self._close_shop_vault();self.shop_vault_button.hide();self.shop_vault_button.setEnabled(False);return False
        self.shop_vault_dialog.show();return True
