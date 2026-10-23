"""Plain-language, version-separated update reader; no game interactions."""
from copy import deepcopy
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,QTabWidget,QPushButton,QSplitter
from . import expansion_reference as model
from . import current_stage_directory as stage_directory
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class ExpansionUpdatePanel(QWidget):
    def __init__(self,parent=None,*,categories=None,full_catalog=False):
        super().__init__(parent)
        self.source_identity=None;self.result=None;self.image_raw=None
        self.full_catalog=full_catalog
        layout=QVBoxLayout(self);self.notice=QLabel(model.NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        bar=QHBoxLayout();self.category=QComboBox();self.category.setAccessibleName('资料分类')
        allowed=dict(model.CATEGORIES) if categories is None else {key:dict(model.CATEGORIES)[key] for key in categories}
        self.allowed_categories=tuple(allowed)
        common_labels={'stages':'关卡','scenes':'事件情景','choices':'事件选项','relics':'收藏品','scrap':'零件','squads':'分队','difficulty':'保密等级','regions':'区域','endings':'结局','initial':'开局设置'}
        for key,label in allowed.items():self.category.addItem(common_labels[key] if full_catalog else label,key)
        self.scope=QComboBox();self.scope.addItem('只看新增与改动',True);self.scope.addItem('查看本版本全部资料',False)
        if full_catalog:self.scope.setCurrentIndex(self.scope.findData(False));self.scope.hide()
        self.search=QLineEdit();self.search.setPlaceholderText('按中文名称搜索；同名资料分别保留')
        self.refresh_button=QPushButton('重新核对资料');bar.addWidget(self.category);bar.addWidget(self.scope);bar.addWidget(self.search,1);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        self.tickets_button=QPushButton('招募券：适用职业、留存与取出')
        self.tickets_button.setAccessibleName('招募券用途与留存规则')
        layout.addWidget(self.tickets_button)
        self.tickets_button.setVisible(full_catalog and categories is not None and 'relics' in categories)
        self.tickets_button.clicked.connect(self.open_recruit_tickets)
        self.bank_button=QPushButton('前瞻性投资：解锁门槛与条件说明')
        layout.addWidget(self.bank_button)
        self.bank_button.setVisible(full_catalog and categories is not None and 'initial' in categories)
        self.bank_button.clicked.connect(lambda:self.open_bank_reference())
        self.real_domain_button=QPushButton('实托邦：理念、方针与影响条件')
        layout.addWidget(self.real_domain_button)
        self.real_domain_button.setVisible(full_catalog and categories is not None and 'regions' in categories)
        self.real_domain_button.clicked.connect(lambda:self.open_real_domain())
        self.portal_rules_button=QPushButton('秘境乌托邦：雾色、规则与节点刷新')
        layout.addWidget(self.portal_rules_button)
        self.portal_rules_button.setVisible(full_catalog and categories is not None and 'regions' in categories)
        self.portal_rules_button.clicked.connect(lambda:self.open_portal_rules())
        self.region_resources_button=QPushButton('区域：入区行动力与离开条件')
        layout.addWidget(self.region_resources_button)
        self.region_resources_button.setVisible(full_catalog and categories is not None and any(key in categories for key in ['regions']))
        self.region_resources_button.clicked.connect(lambda:self.open_region_resources())
        self.upgrade_tickets_button=QPushButton('进阶券：适用职业、星级与取得方式')
        layout.addWidget(self.upgrade_tickets_button)
        self.upgrade_tickets_button.setVisible(full_catalog and categories is not None and any(key in categories for key in ['relics']))
        self.upgrade_tickets_button.clicked.connect(lambda:self.open_upgrade_tickets())
        self.legacy_reference_button=QPushButton('跨局助力：襁褓、失败与下次开始条件')
        layout.addWidget(self.legacy_reference_button)
        self.legacy_reference_button.setVisible(full_catalog and categories is not None and any(key in categories for key in ['relics', 'initial']))
        self.legacy_reference_button.clicked.connect(lambda:self.open_legacy_reference())
        self.item_kind=QComboBox();self.item_kind.setAccessibleName('物品与效果类型')
        for label,value in [('收藏品','RELIC'),('战术道具','ACTIVE_TOOL'),('培育与继承','LEGACY'),('地图标志','NODE_BUOY'),('其它特殊效果','FEATURE'),('分队效果说明','BAND'),('总览（含以上各类）',None)]:self.item_kind.addItem(label,value)
        if not full_catalog:self.item_kind.setCurrentIndex(self.item_kind.findData(None))
        layout.addWidget(self.item_kind);self.item_kind.hide()
        filters=QWidget();stage_bar=QHBoxLayout(filters);stage_bar.setContentsMargins(0,0,0,0);self.stage_filters=filters;self.stage_floor=QComboBox();self.stage_kind=QComboBox();self.stage_floor.setAccessibleName('当前关卡资料层数');self.stage_kind.setAccessibleName('当前关卡作战来源')
        for value,label in stage_directory.FLOORS:self.stage_floor.addItem(label,value)
        for value,label in stage_directory.KINDS:self.stage_kind.addItem(label,value)
        stage_bar.addWidget(self.stage_floor);stage_bar.addWidget(self.stage_kind);stage_bar.addWidget(QLabel('层数按文献分组；同名配置分别保留。'),1);layout.addWidget(filters)
        self.ending_button=QPushButton('旧日重燃：事件前置与相关作战');layout.addWidget(self.ending_button);self.ending_button.clicked.connect(self.open_ending_events)
        if categories is not None and 'endings' not in categories:self.ending_button.hide()
        self.count=QLabel();layout.addWidget(self.count)
        split=QSplitter();layout.addWidget(split,1);self.entries=QListWidget();self.entries.setAccessibleName('本版本资料条目');split.addWidget(self.entries)
        right=QWidget();body=QVBoxLayout(right);self.map_image=QLabel('选择关卡可查看固定原图');self.map_image.setAlignment(Qt.AlignmentFlag.AlignCenter);self.map_image.setMinimumSize(260,150);body.addWidget(self.map_image)
        self.next_button=QPushButton('查看原资料指定的后续场景');self.next_button.hide();body.addWidget(self.next_button)
        self.flow_button=QPushButton('查看这个情景的选项、奖励和后续');self.flow_button.hide();body.addWidget(self.flow_button);self.flow_button.clicked.connect(self.open_documented_flow)
        self.origins_button=QPushButton('查看已核对的取得方式');self.origins_button.hide();body.addWidget(self.origins_button);self.origins_button.clicked.connect(self.open_reward_origins)
        self.bank_item_button=QPushButton('查看投资解锁的两种说明')
        self.bank_item_button.hide();body.addWidget(self.bank_item_button)
        self.bank_item_button.clicked.connect(lambda:self.open_bank_reference(from_item=True))
        self.real_domain_item_button=QPushButton('查看相关实托邦理念与条件')
        self.real_domain_item_button.hide();body.addWidget(self.real_domain_item_button)
        self.real_domain_item_button.clicked.connect(lambda:self.open_real_domain(from_item=True))
        self.portal_rules_item_button=QPushButton('查看对应秘境规则与原区域说明')
        self.portal_rules_item_button.hide();body.addWidget(self.portal_rules_item_button)
        self.portal_rules_item_button.clicked.connect(lambda:self.open_portal_rules(from_item=True))
        self.region_resources_item_button=QPushButton('查看本区域行动力分项与耗尽条件')
        self.region_resources_item_button.hide();body.addWidget(self.region_resources_item_button)
        self.region_resources_item_button.clicked.connect(lambda:self.open_region_resources(from_item=True))
        self.upgrade_tickets_item_button=QPushButton('查看所附进阶券与准确取得方式')
        self.upgrade_tickets_item_button.hide();body.addWidget(self.upgrade_tickets_item_button)
        self.upgrade_tickets_item_button.clicked.connect(lambda:self.open_upgrade_tickets(from_item=True))
        self.legacy_reference_item_button=QPushButton('查看对应襁褓来源与下次助力条件')
        self.legacy_reference_item_button.hide();body.addWidget(self.legacy_reference_item_button)
        self.legacy_reference_item_button.clicked.connect(lambda:self.open_legacy_reference(from_item=True))
        self.event_battles_button=QPushButton('查看本事件的具名作战选项与固定地图');self.event_battles_button.hide();body.addWidget(self.event_battles_button);self.event_battles_button.clicked.connect(self.open_event_battles)
        self.exchange_button=QPushButton('查看当前回滚文明：能否交出与奖励条文');self.exchange_button.hide();body.addWidget(self.exchange_button);self.exchange_button.clicked.connect(self.open_current_exchange)
        self.battle_button=QPushButton('查看本版本关卡：原图、敌人和出怪条件');self.battle_button.hide();body.addWidget(self.battle_button)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True)
        self.tabs.addTab(self.player,'条件与用途');self.tabs.addTab(self.technical,'完整原值与来源');self.stage_source=QPlainTextEdit();self.stage_source.setReadOnly(True);self.tabs.addTab(self.stage_source,'层数分类依据');body.addWidget(self.tabs,1);split.addWidget(right);split.setSizes([300,750])
        self.category.currentIndexChanged.connect(self._filter_changed);self.scope.currentIndexChanged.connect(self._filter_changed);self.search.textChanged.connect(self._filter_changed)
        self.stage_floor.currentIndexChanged.connect(self._filter_changed);self.stage_kind.currentIndexChanged.connect(self._filter_changed)
        self.item_kind.currentIndexChanged.connect(self._filter_changed)
        self.entries.currentItemChanged.connect(self._selected);self.next_button.clicked.connect(self.follow_scene);self.refresh_button.clicked.connect(self.refresh_reference)
        self.battle_button.clicked.connect(self.open_current_battle)
        self.refresh_reference()

    def _clear_detail(self,notice='请先选择一项资料。'):
        if getattr(self,'legacy_reference_origin',None)=='item':self._close_legacy_reference()
        self.legacy_reference_item_button.hide()
        if getattr(self,'upgrade_tickets_origin',None)=='item':self._close_upgrade_tickets()
        self.upgrade_tickets_item_button.hide()
        if getattr(self,'region_resources_origin',None)=='item':self._close_region_resources()
        self.region_resources_item_button.hide()
        if getattr(self,'portal_rules_origin',None)=='item':self._close_portal_rules()
        self.portal_rules_item_button.hide()
        if getattr(self,'real_domain_origin',None)=='item':self._close_real_domain()
        self.real_domain_item_button.hide()
        if getattr(self,'bank_origin',None)=='item':self._close_bank()
        self.bank_item_button.hide()
        self._close_origins();self.origins_button.hide()
        self._close_event_battles();self.event_battles_button.hide()
        self._close_flow();self.flow_button.hide()
        self._close_exchange();self.exchange_button.hide()
        dialog=getattr(self,'current_battle_dialog',None)
        if dialog is not None:dialog.close()
        self.result=None;self.image_raw=None;self.map_image.clear();self.map_image.setText(notice);self.next_button.hide();self.next_button.setEnabled(False)
        self.stage_info=None;replace_text(self.stage_source,'',preserve=False);self.tabs.setTabVisible(2,False)
        self.battle_button.hide();self.battle_button.setEnabled(False)
        replace_text(self.player,'',preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)

    def _unavailable(self):
        self._close_legacy_reference();self.legacy_reference_button.setEnabled(False)
        self._close_upgrade_tickets();self.upgrade_tickets_button.setEnabled(False)
        self._close_region_resources();self.region_resources_button.setEnabled(False)
        self._close_portal_rules();self.portal_rules_button.setEnabled(False)
        self._close_real_domain();self.real_domain_button.setEnabled(False)
        self._close_bank();self.bank_button.setEnabled(False)
        self._close_tickets();self.tickets_button.setEnabled(False)
        dialog=getattr(self,'ending_dialog',None)
        if dialog is not None:dialog.close()
        self.source_identity=None
        # clear() destroys the C++ items. Suppress currentItemChanged while they
        # are being destroyed; its old-item argument must not reenter Python.
        blocked=self.entries.blockSignals(True)
        try:self.entries.clear()
        finally:self.entries.blockSignals(blocked)
        self._clear_detail(model.UNAVAILABLE);self.count.setText(model.UNAVAILABLE)

    def _filter_changed(self,*_):
        self._populate(preserve=False)

    def _populate(self,*,preserve):
        reference=model.packet()
        if reference is None:self._unavailable();return False
        same=self.source_identity==reference['source_identity']
        current=self.entries.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if preserve and same and current else None
        self.source_identity=reference['source_identity']
        items=model.rows(self.category.currentData(),changes_only=self.scope.currentData(),reference=reference)
        item_types=self.full_catalog and self.category.currentData()=='relics';self.item_kind.setVisible(item_types)
        if item_types and self.item_kind.currentData()is not None:
            items=[row for row in items if (row['value'].get('item')or{}).get('type')==self.item_kind.currentData()]
        is_stage=self.category.currentData()=='stages';self.stage_filters.setVisible(is_stage);stage_ref=stage_directory.packet()if is_stage else None
        if is_stage and stage_ref is None:self._unavailable();return False
        if is_stage:
            allowed={r['id']for r in stage_directory.rows(self.stage_floor.currentData(),self.stage_kind.currentData(),reference=stage_ref)};items=[r for r in items if r['id']in allowed]
        query=self.search.text().strip();visible=[r for r in items if not query or query in r['name']]
        blocked=self.entries.blockSignals(True);self.entries.clear()
        for row in visible:
            title=stage_directory.label(stage_directory.detail(row['id'],reference=stage_ref))if is_stage else row['label']
            item=QListWidgetItem(title);item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==selected:self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        self.count.setText('当前分类列出'+str(len(visible))+'项资料。条目包含同名变体与强化档位，不等于新增地图或新增分队的数量。')
        if is_stage:self.count.setText('当前列出'+str(len(visible))+'份关卡配置，保留同名变体。可按层数与来源分别筛选；资料目录不是本局必出关卡池。')
        if selected is None or self.entries.currentItem()is None:self.entries.setCurrentRow(-1);self._clear_detail()
        else:self._selected(self.entries.currentItem(),preserve=True)
        return True

    def refresh_reference(self):
        # After source loss, no old identity survives; recovery restores a list, not a prior selection.
        ready=self._populate(preserve=True)
        self.tickets_button.setEnabled(ready)
        self.legacy_reference_button.setEnabled(ready)
        child=getattr(self,'legacy_reference_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        self.upgrade_tickets_button.setEnabled(ready)
        child=getattr(self,'upgrade_tickets_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        self.region_resources_button.setEnabled(ready)
        child=getattr(self,'region_resources_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        self.bank_button.setEnabled(ready)
        self.real_domain_button.setEnabled(ready)
        self.portal_rules_button.setEnabled(ready)
        child=getattr(self,'tickets_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        child=getattr(self,'bank_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        child=getattr(self,'real_domain_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        child=getattr(self,'portal_rules_dialog',None)
        if ready and child is not None and child.isVisible():child.panel.refresh_reference()
        return ready

    def _close_region_resources(self):
        child=getattr(self,'region_resources_dialog',None)
        if child is not None:child.close()
        self.region_resources_origin=None

    def open_region_resources(self,*,from_item=False):
        if model.packet() is None:self._unavailable();return False
        from . import current_region_reference as reader
        target=None
        if from_item:
            if self.result is None:return False
            row=self.result['row'];key=row['id'];category=row['category']
            if model.detail(category,key)!=self.result:self._unavailable();return False
            target=reader.locate(category,key) if category=='regions' else None
            if target is None:return False
        elif not self.full_catalog or not any(key in self.allowed_categories for key in ['regions']):return False
        from .current_region_view import CurrentRegionDialog
        self._close_region_resources();self.region_resources_dialog=CurrentRegionDialog(target,self)
        if self.region_resources_dialog.panel.result is None:self._close_region_resources();return False
        self.region_resources_origin='item' if from_item else 'directory'
        self.region_resources_dialog.show();return True

    def _close_upgrade_tickets(self):
        child=getattr(self,'upgrade_tickets_dialog',None)
        if child is not None:child.close()
        self.upgrade_tickets_origin=None

    def open_upgrade_tickets(self,*,from_item=False):
        if model.packet() is None:self._unavailable();return False
        from . import current_upgrade_tickets as reader
        target=None
        if from_item:
            if self.result is None:return False
            row=self.result['row'];key=row['id'];category=row['category']
            if model.detail(category,key)!=self.result:self._unavailable();return False
            target=reader.locate(category,key) if category in ('relics','choices') else None
            if target is None:return False
        elif not self.full_catalog or not any(key in self.allowed_categories for key in ['relics']):return False
        from .current_upgrade_tickets_view import CurrentUpgradeTicketsDialog
        self._close_upgrade_tickets();self.upgrade_tickets_dialog=CurrentUpgradeTicketsDialog(self,target=target)
        if self.upgrade_tickets_dialog.panel.result is None:self._close_upgrade_tickets();return False
        self.upgrade_tickets_origin='item' if from_item else 'directory'
        self.upgrade_tickets_dialog.show();return True

    def _close_legacy_reference(self):
        child=getattr(self,'legacy_reference_dialog',None)
        if child is not None:child.close()
        self.legacy_reference_origin=None

    def open_legacy_reference(self,*,from_item=False):
        if model.packet() is None:self._unavailable();return False
        from . import current_legacy as reader
        target=None
        if from_item:
            if self.result is None:return False
            row=self.result['row'];key=row['id'];category=row['category']
            if model.detail(category,key)!=self.result:self._unavailable();return False
            target=reader.locate('items' if category=='scrap' else category,key) if category in ('relics','scrap','choices','difficulty','scenes') else None
            if target is None:return False
        elif not self.full_catalog or not any(key in self.allowed_categories for key in ['relics', 'initial']):return False
        from .current_legacy_view import CurrentLegacyDialog
        self._close_legacy_reference();self.legacy_reference_dialog=CurrentLegacyDialog(target,self)
        if self.legacy_reference_dialog.panel.result is None:self._close_legacy_reference();return False
        self.legacy_reference_origin='item' if from_item else 'directory'
        self.legacy_reference_dialog.show();return True

    def _close_portal_rules(self):
        child=getattr(self,'portal_rules_dialog',None)
        if child is not None:child.close()
        self.portal_rules_origin=None

    def open_portal_rules(self,*,from_item=False):
        if model.packet() is None:self._unavailable();return False
        from . import current_portal_rules as rules
        target=None
        if from_item:
            if self.result is None:return False
            row=self.result['row']
            if model.detail(row['category'],row['id'])!=self.result:self._unavailable();return False
            category='items' if row['category']=='relics' else row['category']
            target=rules.locate(category,row['id'])
            if target is None:return False
        elif not self.full_catalog or 'regions' not in self.allowed_categories:return False
        from .current_portal_rules_view import CurrentPortalRulesDialog
        self._close_portal_rules();self.portal_rules_dialog=CurrentPortalRulesDialog(target,self)
        if self.portal_rules_dialog.panel.result is None:self._close_portal_rules();return False
        self.portal_rules_origin='item' if from_item else 'directory'
        self.portal_rules_dialog.show();return True

    def _close_real_domain(self):
        child=getattr(self,'real_domain_dialog',None)
        if child is not None:child.close()
        self.real_domain_origin=None

    def open_real_domain(self,*,from_item=False):
        if model.packet() is None:self._unavailable();return False
        from . import current_real_domain as domain
        target=None
        if from_item:
            if self.result is None:return False
            row=self.result['row']
            if model.detail(row['category'],row['id'])!=self.result:self._unavailable();return False
            target=domain.locate(row['category'],row['id'])
            if target is None:return False
        elif not self.full_catalog or 'regions' not in self.allowed_categories:return False
        from .current_real_domain_view import CurrentRealDomainDialog
        self._close_real_domain();self.real_domain_dialog=CurrentRealDomainDialog(target,self)
        if self.real_domain_dialog.panel.result is None:self._close_real_domain();return False
        self.real_domain_origin='item' if from_item else 'directory'
        self.real_domain_dialog.show();return True

    def _close_bank(self):
        child=getattr(self,'bank_dialog',None)
        if child is not None:child.close()
        self.bank_origin=None

    def open_bank_reference(self,*,from_item=False):
        if model.packet() is None:self._unavailable();return False
        from . import current_bank_reference as bank
        target=None
        if from_item:
            if self.result is None:return False
            row=self.result['row']
            if model.detail(row['category'],row['id'])!=self.result:self._unavailable();return False
            target=bank.locate(row['category'],row['id'])
            if target is None:return False
        elif not self.full_catalog or 'initial' not in self.allowed_categories:return False
        from .current_bank_view import CurrentBankDialog
        self._close_bank();self.bank_dialog=CurrentBankDialog(target,self)
        if self.bank_dialog.panel.result is None:self._close_bank();return False
        self.bank_origin='item' if from_item else 'directory'
        self.bank_dialog.show();return True

    def _close_tickets(self):
        child=getattr(self,'tickets_dialog',None)
        if child is not None:child.close()

    def open_recruit_tickets(self):
        if not self.full_catalog or 'relics' not in self.allowed_categories:return False
        if model.packet() is None:self._unavailable();return False
        from .current_recruit_tickets_view import CurrentRecruitTicketsDialog
        self._close_tickets();self.tickets_dialog=CurrentRecruitTicketsDialog(self)
        if self.tickets_dialog.panel.result is None:self._close_tickets();return False
        self.tickets_dialog.show();return True

    def _selected(self,item,*_,preserve=False):
        if item is None:self._clear_detail();return
        key=item.data(Qt.ItemDataRole.UserRole);result=model.detail(self.category.currentData(),key)
        if result is None or result['source_identity']!=self.source_identity:self._unavailable();return
        keep=preserve and self.result is not None and self.result['row']['id']==key and self.result['row']['category']==result['row']['category']
        battle_dialog=getattr(self,'current_battle_dialog',None)
        if battle_dialog is not None:
            if not keep:battle_dialog.close()
            elif battle_dialog.isVisible():battle_dialog.panel.refresh_reference()
        if not keep:self._close_flow();self._close_exchange();self._close_event_battles();self._close_origins()
        self.result=deepcopy(result)
        from . import current_legacy as reader
        row=result['row'];category=row['category']
        target=reader.locate('items' if category=='scrap' else category,key) if category in ('relics','scrap','choices','difficulty','scenes') else None
        self.legacy_reference_item_button.setVisible(target is not None);self.legacy_reference_item_button.setEnabled(target is not None)
        if not keep and getattr(self,'legacy_reference_origin',None)=='item':self._close_legacy_reference()
        from . import current_upgrade_tickets as reader
        row=result['row'];category=row['category']
        target=reader.locate(category,key) if category in ('relics','choices') else None
        self.upgrade_tickets_item_button.setVisible(target is not None);self.upgrade_tickets_item_button.setEnabled(target is not None)
        if not keep and getattr(self,'upgrade_tickets_origin',None)=='item':self._close_upgrade_tickets()
        from . import current_region_reference as reader
        row=result['row'];category=row['category']
        target=reader.locate(category,key) if category=='regions' else None
        self.region_resources_item_button.setVisible(target is not None);self.region_resources_item_button.setEnabled(target is not None)
        if not keep and getattr(self,'region_resources_origin',None)=='item':self._close_region_resources()
        from . import current_portal_rules as rules
        category='items' if result['row']['category']=='relics' else result['row']['category']
        target=rules.locate(category,key) if category in ('scenes','regions','items') else None
        self.portal_rules_item_button.setVisible(target is not None);self.portal_rules_item_button.setEnabled(target is not None)
        if not keep and getattr(self,'portal_rules_origin',None)=='item':self._close_portal_rules()
        from . import current_real_domain as domain
        known={('scenes','scene_ro6_normal3_enter'),*((cat,identity)for _,cat,identity,_ in domain.LINKS.values())}
        target=domain.locate(result['row']['category'],key) if (result['row']['category'],key)in known else None
        self.real_domain_item_button.setVisible(target is not None);self.real_domain_item_button.setEnabled(target is not None)
        if not keep and getattr(self,'real_domain_origin',None)=='item':self._close_real_domain()
        from . import current_bank_reference as bank
        target=bank.locate('relics',key) if result['row']['category']=='relics' and key==bank.ITEM_ID else None
        self.bank_item_button.setVisible(target is not None);self.bank_item_button.setEnabled(target is not None)
        if not keep and getattr(self,'bank_origin',None)=='item':self._close_bank()
        from .current_reward_origins import reference as origins_reference
        origin=origins_reference(result['row']['category'],key)
        self.origins_button.setVisible(origin is not None);self.origins_button.setEnabled(origin is not None)
        child=getattr(self,'origins_dialog',None)
        if origin is None:self._close_origins()
        elif keep and child is not None and child.isVisible():child.panel.refresh_reference()
        from .current_event_battles import locate as event_battle_locate
        target=event_battle_locate(result['row']['category'],key)
        self.event_battles_button.setVisible(target is not None);self.event_battles_button.setEnabled(target is not None)
        child=getattr(self,'event_battles_dialog',None)
        if keep and child is not None and child.isVisible():child.panel.refresh_reference()
        from .documented_event_flows import event_for_scene
        from .box_event_reference import locate
        from .current_ritual_reference import locate as ritual_locate
        from .current_sand_reference import locate as sand_locate
        from .current_encounters import locate as encounter_locate
        from .current_lake import locate as lake_locate
        from .current_resource_events import locate as resource_locate
        from .current_unattended_shop import locate as shop_locate
        from .current_memory_tree import locate as memory_locate
        from .current_lone_dog import locate as dog_locate
        from .current_cave import locate as cave_locate
        from .current_vine_events import locate as vine_locate
        from .current_rest_travel import locate as rest_travel_locate
        from .current_exit import locate as exit_locate
        from .current_agency import locate as agency_locate
        from .current_portal import locate as portal_locate
        from .current_scout import locate as scout_locate
        from .current_peace import locate as peace_locate
        from .current_reconstruction import locate as reconstruction_locate
        from .current_resting import locate as resting_locate
        from .current_startup import locate as startup_locate
        from .current_shadow import locate as shadow_locate
        available=startup_locate(result['row']['category'],key)is not None or shadow_locate(result['row']['category'],key)is not None or resting_locate(result['row']['category'],key)is not None or reconstruction_locate(result['row']['category'],key)is not None or peace_locate(result['row']['category'],key)is not None or scout_locate(result['row']['category'],key)is not None or portal_locate(result['row']['category'],key)is not None or agency_locate(result['row']['category'],key)is not None or exit_locate(result['row']['category'],key)is not None or memory_locate(result['row']['category'],key)is not None or dog_locate(result['row']['category'],key)is not None or cave_locate(result['row']['category'],key)is not None or vine_locate(result['row']['category'],key)is not None or(result['row']['category']=='scenes'and event_for_scene(key)is not None)or locate(result['row']['category'],key)is not None or ritual_locate(result['row']['category'],key)is not None or sand_locate(result['row']['category'],key)is not None or encounter_locate(result['row']['category'],key)is not None or lake_locate(result['row']['category'],key)is not None or resource_locate(result['row']['category'],key)is not None or shop_locate(result['row']['category'],key)is not None or rest_travel_locate(result['row']['category'],key)is not None
        self.flow_button.setVisible(available);self.flow_button.setEnabled(available)
        self.flow_button.setText('查看本事件的条件、选项和相关作战')
        child=getattr(self,'flow_dialog',None)
        if keep and child is not None and child.isVisible():child.panel.refresh_reference()
        from .current_exchange_reference import target_entry
        category=result['row']['category'];name=result['row']['name']
        candidate=category=='relics'or(category=='scenes'and name=='回滚文明')or(category=='choices'and name in('复原藏品','接过藏品','复原零件','接过零件','复原“文明”','等待结果','离开','继续赞助它','有点可疑'))
        exchange_target=target_entry(category,key)if candidate else None
        self.exchange_button.setVisible(exchange_target is not None);self.exchange_button.setEnabled(exchange_target is not None)
        child=getattr(self,'exchange_dialog',None)
        if keep and child is not None and child.isVisible():child.panel.refresh_reference()
        is_stage=result['row']['category']=='stages';self.battle_button.setVisible(is_stage);self.battle_button.setEnabled(is_stage)
        self.stage_info=stage_directory.detail(key)if is_stage else None
        if is_stage and self.stage_info is None:self._unavailable();return
        player=(stage_directory.player_text(self.stage_info)+'\n'if self.stage_info else'')+result['player_text']
        self.tabs.setTabVisible(2,is_stage);replace_text(self.stage_source,_technical_json(self.stage_info)if self.stage_info else'',preserve=keep)
        replace_text(self.player,player,preserve=keep);replace_text(self.technical,_technical_json(result),preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)
        target=result['next_scene'];self.next_button.setVisible(target is not None);self.next_button.setEnabled(target is not None)
        if target:self.next_button.setText('查看后续场景：'+target['title'])
        self.image_raw=model.image_bytes(result['image'])
        self._draw_image()

    def _draw_image(self):
        if self.image_raw is None:
            self.map_image.clear();self.map_image.setText('本项无地图资料'if self.result and self.result['image']is None else'固定地图原图暂时无法核对。');return
        pixmap=QPixmap()
        if not pixmap.loadFromData(self.image_raw,'PNG')or pixmap.isNull():self.image_raw=None;self.map_image.clear();self.map_image.setText('原图无法读取。');return
        self.map_image.setPixmap(pixmap.scaled(max(1,self.map_image.width()-8),220,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        self.map_image.setToolTip('固定原图，可随窗口缩放查看；尚未校准位置，不显示未经核对的出怪标记。')

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'map_image'):self._draw_image()

    def follow_scene(self):
        if self.result is None or self.result['next_scene']is None:return False
        # Requery the exact choice before following its explicit nextSceneId; never infer its parent scene.
        current=model.detail(self.result['row']['category'],self.result['row']['id'])
        if current!=self.result:self._unavailable();return False
        target=current['next_scene']['id'];self.search.clear();self.scope.setCurrentIndex(self.scope.findData(False));self.category.setCurrentIndex(self.category.findData('scenes'))
        for i in range(self.entries.count()):
            if self.entries.item(i).data(Qt.ItemDataRole.UserRole)==target:self.entries.setCurrentRow(i);return True
        self._clear_detail('指定场景在本版本资料中无法核对。');return False

    def open_current_battle(self):
        if self.result is None or self.result['row']['category']!='stages':return False
        fresh=model.detail('stages',self.result['row']['id'])
        if fresh!=self.result:self._unavailable();return False
        if stage_directory.detail(self.result['row']['id'])!=self.stage_info:self._unavailable();return False
        from .current_battle_view import CurrentBattleDialog
        previous=getattr(self,'current_battle_dialog',None)
        if previous is not None:previous.close()
        self.current_battle_dialog=CurrentBattleDialog(fresh['row']['id'],self)
        self.current_battle_dialog.show()
        return True

    def open_ending_events(self):
        if model.packet()is None:self._unavailable();return False
        from .ending_event_view import EndingEventDialog
        previous=getattr(self,'ending_dialog',None)
        if previous is not None:previous.close()
        self.ending_dialog=EndingEventDialog(self);self.ending_dialog.show();return True

    def _close_flow(self):
        dialog=getattr(self,'flow_dialog',None)
        if dialog is not None:dialog.close()

    def open_documented_flow(self):
        if self.result is None or self.result['row']['category']not in('scenes','choices','relics'):return False
        category=self.result['row']['category'];fresh=model.detail(category,self.result['row']['id'])
        if fresh!=self.result:self._unavailable();return False
        from .current_startup import locate as startup_locate
        target=startup_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_startup_view import CurrentStartupDialog
            self._close_flow();self.flow_dialog=CurrentStartupDialog(target,self);self.flow_dialog.show();return True
        from .current_shadow import locate as shadow_locate
        target=shadow_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_shadow_view import CurrentShadowDialog
            self._close_flow();self.flow_dialog=CurrentShadowDialog(target,self);self.flow_dialog.show();return True
        from .current_resting import locate as resting_locate
        target=resting_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_resting_view import CurrentRestingDialog
            self._close_flow();self.flow_dialog=CurrentRestingDialog(target,self);self.flow_dialog.show();return True
        from .current_reconstruction import locate as reconstruction_locate
        target=reconstruction_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_reconstruction_view import CurrentReconstructionDialog
            self._close_flow();self.flow_dialog=CurrentReconstructionDialog(target,self);self.flow_dialog.show();return True
        from .current_peace import locate as peace_locate
        target=peace_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_peace_view import CurrentPeaceDialog
            self._close_flow();self.flow_dialog=CurrentPeaceDialog(target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_scout import locate as scout_locate
        target=scout_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_scout_view import CurrentScoutDialog
            self._close_flow();self.flow_dialog=CurrentScoutDialog(target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_portal import locate as portal_locate
        target=portal_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_portal_view import CurrentPortalDialog
            self._close_flow();self.flow_dialog=CurrentPortalDialog(target,self);self.flow_dialog.show();return True
        from .current_agency import locate as agency_locate
        target=agency_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_agency_view import CurrentAgencyDialog
            self._close_flow();self.flow_dialog=CurrentAgencyDialog(target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_exit import locate as exit_locate
        target=exit_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_exit_view import CurrentExitDialog
            self._close_flow();self.flow_dialog=CurrentExitDialog(target,self);self.flow_dialog.show();return True
        from .current_memory_tree import locate as memory_locate
        target=memory_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_memory_tree_view import CurrentMemoryTreeDialog
            self._close_flow();self.flow_dialog=CurrentMemoryTreeDialog(target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_lone_dog import locate as dog_locate
        target=dog_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_lone_dog_view import CurrentLoneDogDialog
            self._close_flow();self.flow_dialog=CurrentLoneDogDialog(target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_cave import locate as cave_locate
        target=cave_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_cave_view import CurrentCaveDialog
            self._close_flow();self.flow_dialog=CurrentCaveDialog(target,self);self.flow_dialog.show();return True
        from .current_vine_events import locate as vine_locate
        target=vine_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_vine_events_view import CurrentVineEventsDialog
            self._close_flow();self.flow_dialog=CurrentVineEventsDialog(target['event_id'],target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_rest_travel import locate as rest_travel_locate
        target=rest_travel_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_rest_travel_view import CurrentRestTravelDialog
            self._close_flow();self.flow_dialog=CurrentRestTravelDialog(target['event_id'],target,self);self.flow_dialog.show();return True
        from .current_unattended_shop import locate as shop_locate
        target=shop_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_unattended_shop_view import CurrentUnattendedShopDialog
            self._close_flow();self.flow_dialog=CurrentUnattendedShopDialog(target,self);self.flow_dialog.show();return True
        from .current_resource_events import locate as resource_locate
        target=resource_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_resource_events_view import CurrentResourceEventsDialog
            self._close_flow();self.flow_dialog=CurrentResourceEventsDialog(target['event_id'],target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_lake import locate as lake_locate
        target=lake_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_lake_view import CurrentLakeDialog
            self._close_flow();self.flow_dialog=CurrentLakeDialog(target,self);self.flow_dialog.show();return True
        from .current_encounters import locate as encounter_locate
        target=encounter_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_encounters_view import CurrentEncountersDialog
            self._close_flow();self.flow_dialog=CurrentEncountersDialog(target['event_id'],target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_sand_reference import locate as sand_locate
        target=sand_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_sand_view import CurrentSandDialog
            self._close_flow();self.flow_dialog=CurrentSandDialog(target['event_id'],target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .current_ritual_reference import locate as ritual_locate
        target=ritual_locate(category,fresh['row']['id'])
        if target is not None:
            from .current_ritual_view import CurrentRitualDialog
            self._close_flow();self.flow_dialog=CurrentRitualDialog(target['event_id'],target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .documented_event_flows import event_for_scene
        event_id=event_for_scene(fresh['row']['id'])if category=='scenes'else None
        if event_id is None:
            from .box_event_reference import locate
            target=locate(category,fresh['row']['id'])
            if target is None:self._close_flow();self.flow_button.hide();return False
            from .box_event_view import BoxEventDialog
            self._close_flow();self.flow_dialog=BoxEventDialog(target['scene_id'],target['choice_id'],self);self.flow_dialog.show();return True
        from .documented_event_flow_view import DocumentedEventFlowDialog
        self._close_flow();self.flow_dialog=DocumentedEventFlowDialog(event_id,fresh['row']['id'],self);self.flow_dialog.show();return True

    def _close_origins(self):
        dialog=getattr(self,'origins_dialog',None)
        if dialog is not None:dialog.close()
        self.origins_dialog=None

    def open_reward_origins(self):
        if self.result is None:return False
        row=self.result['row'];fresh=model.detail(row['category'],row['id'])
        if fresh!=self.result:self._unavailable();return False
        from .current_reward_origins import reference
        target=reference(row['category'],row['id'])
        if target is None:self._close_origins();self.origins_button.hide();return False
        from .current_reward_origins_view import CurrentRewardOriginsDialog
        self._close_origins();self.origins_dialog=CurrentRewardOriginsDialog(row['category'],row['id'],self)
        if self.origins_dialog.panel.result is None:self._close_origins();return False
        self.origins_dialog.show();return True

    def close_children(self):
        self._close_legacy_reference()
        self._close_upgrade_tickets()
        self._close_region_resources()
        self._close_portal_rules()
        self._close_real_domain()
        self._close_bank()
        self._close_tickets()
        self._close_origins()
        self._close_flow();self._close_exchange();self._close_event_battles()
        for name in ('ending_dialog','current_battle_dialog'):
            dialog=getattr(self,name,None)
            if dialog is not None:dialog.close()
    def closeEvent(self,event):
        self.close_children();super().closeEvent(event)

    def _close_exchange(self):
        dialog=getattr(self,'exchange_dialog',None)
        if dialog is not None:dialog.close()

    def _close_event_battles(self):
        dialog=getattr(self,'event_battles_dialog',None)
        if dialog is not None:dialog.close()

    def open_event_battles(self):
        if self.result is None:return False
        row=self.result['row'];fresh=model.detail(row['category'],row['id'])
        if fresh!=self.result:self._unavailable();return False
        from .current_event_battles import locate
        target=locate(row['category'],row['id'])
        if target is None:self._close_event_battles();self.event_battles_button.hide();return False
        from .current_event_battles_view import CurrentEventBattlesDialog
        self._close_event_battles();self.event_battles_dialog=CurrentEventBattlesDialog(target['event_id'],target['choice_id'],parent=self);self.event_battles_dialog.show();return True

    def open_current_exchange(self):
        if self.result is None:return False
        row=self.result['row'];fresh=model.detail(row['category'],row['id'])
        if fresh!=self.result:self._unavailable();return False
        from .current_exchange_reference import target_entry
        target=target_entry(row['category'],row['id'])
        if target is None:self._close_exchange();self.exchange_button.hide();return False
        from .current_exchange_view import CurrentExchangeDialog
        self._close_exchange();self.exchange_dialog=CurrentExchangeDialog(target,self);self.exchange_dialog.show();return True
