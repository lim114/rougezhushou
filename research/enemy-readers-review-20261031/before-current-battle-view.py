"""Manual current-version battle reader, with real category branches."""
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPlainTextEdit,QPushButton,QTabWidget,QSplitter,QListWidget,QListWidgetItem,QDialog,QLineEdit,QCheckBox,QStackedWidget
from . import current_battle_reference as model,expansion_reference as version
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text
from .reference_image import ReferenceImage


class CurrentBattlePanel(QWidget):
    def __init__(self, stage_id, parent=None):
        super().__init__(parent)
        self.stage_id = stage_id
        self.result = None
        self.source_identity = None
        self.enemy_key = None
        self.action_key = None
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addWidget(QLabel('固定关卡参考 · 并非本局实况'), 1)
        self.details_toggle = QCheckBox('资料说明')
        self.source_toggle = QCheckBox('原始资料')
        self.refresh_button = QPushButton('刷新资料')
        for control in (self.details_toggle, self.source_toggle, self.refresh_button):
            header.addWidget(control)
        layout.addLayout(header)
        self.notice = QLabel(model.NOTICE)
        self.notice.setWordWrap(True)
        self.notice.hide()
        layout.addWidget(self.notice)
        self.reading_stack = QStackedWidget()
        self.tabs = QTabWidget()
        self.reading_stack.addWidget(self.tabs)
        self.technical = QPlainTextEdit()
        self.technical.setReadOnly(True)
        self.technical.setAccessibleName('本关完整原始资料与来源')
        self.reading_stack.addWidget(self.technical)
        layout.addWidget(self.reading_stack, 1)
        self.source_toggle.toggled.connect(lambda checked: self.reading_stack.setCurrentWidget(self.technical if checked else self.tabs))
        overview = QWidget()
        body = QVBoxLayout(overview)
        self.map_image = ReferenceImage()
        self.map_image.setMinimumSize(300, 160)
        self.map_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.addWidget(self.map_image)
        self.position_button = QPushButton('查看地图格子与已核对的原图位置')
        body.addWidget(self.position_button)
        self.position_button.clicked.connect(self.open_map_positions)
        self.event_origins_button = QPushButton('查看与本关对应的事件选项')
        body.addWidget(self.event_origins_button)
        self.event_origins_button.clicked.connect(self.open_event_origins)
        self.stage_objects_dialog = None
        self.stage_objects_button = QPushButton('查看本关物件与机关')
        body.addWidget(self.stage_objects_button)
        self.stage_objects_button.clicked.connect(self.open_stage_objects)
        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        body.addWidget(self.summary, 1)
        self.tabs.addTab(overview, '地图与关卡')
        enemies = QWidget()
        body = QVBoxLayout(enemies)
        self.enemy_search=QLineEdit();self.enemy_search.setMaxLength(120);self.enemy_search.setPlaceholderText('搜索本关敌人名称或图鉴原文，如隐匿、攻击');body.addWidget(self.enemy_search)
        self.enemy_search_notice=QLabel('');self.enemy_search_notice.setWordWrap(True);body.addWidget(self.enemy_search_notice)
        self.enemy_combo = QComboBox()
        self.enemy_choices = BranchChoice(self.enemy_combo, [], overview_label='总览（本关候选）', placeholder='请选择敌人或关联实体')
        self.enemy_search.textChanged.connect(self.filter_enemies)
        body.addWidget(self.enemy_choices)
        from .player_catalog_grid import CatalogGrid
        self.enemy_grid_toggle = QPushButton('收起敌人图册')
        self.enemy_grid_toggle.setCheckable(True)
        self.enemy_grid_toggle.setChecked(True)
        body.addWidget(self.enemy_grid_toggle)
        self.enemy_grid = CatalogGrid()
        self.enemy_grid.setAccessibleName('本关敌人候选图册；点击图片查看机制')
        self.enemy_grid.set_tile_size(48)
        self.enemy_grid.setMinimumHeight(124)
        self.enemy_grid.setMaximumHeight(132)
        body.addWidget(self.enemy_grid)
        self.enemy_grid_toggle.toggled.connect(self._show_enemy_grid)
        self.enemy_grid.currentItemChanged.connect(self._enemy_grid_selected)
        self.enemy_choices.branch.currentIndexChanged.connect(self._sync_enemy_grid)
        self.enemy_portrait = QLabel()
        self.enemy_portrait.setMinimumSize(85, 85)
        self.enemy_portrait.setMaximumSize(96, 96)
        self.enemy_portrait.setWordWrap(True)
        self.enemy_portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hanko_button = QPushButton('查看汉科、相关敌人和烟雾弹的完整机制')
        self.hanko_button.hide()
        body.addWidget(self.hanko_button)
        self.hanko_button.clicked.connect(self.open_hanko)
        self.elbert_button = QPushButton('查看本关首领、关联敌人与火种的完整机制')
        self.elbert_button.hide()
        body.addWidget(self.elbert_button)
        self.elbert_button.clicked.connect(self.open_elbert)
        self.shop_vault_dialog = None
        self.shop_vault_button = QPushButton('查看坎诺特与保险柜的条件和后果')
        self.shop_vault_button.hide()
        self.shop_vault_button.setEnabled(False)
        body.addWidget(self.shop_vault_button)
        self.shop_vault_button.clicked.connect(self.open_shop_vault)
        self.sun_boss_button = QPushButton('查看本关多形态首领与祭台的完整机制')
        self.sun_boss_button.hide()
        body.addWidget(self.sun_boss_button)
        self.sun_boss_button.clicked.connect(self.open_sun_boss)
        self.boss_documents_button = QPushButton('查看本关首领与关联实体的完整机制')
        self.boss_documents_button.hide()
        body.addWidget(self.boss_documents_button)
        self.boss_documents_button.clicked.connect(self.open_boss_documents)
        self.enemy_spawns_dialog = None
        self.enemy_spawns_button = QPushButton('查看这个敌人的出怪条目与条件')
        self.enemy_spawns_button.hide()
        body.addWidget(self.enemy_spawns_button)
        self.enemy_spawns_button.clicked.connect(self.open_enemy_spawns)
        self.guest_knights_button = QPushButton('恶意讨薪 · 双骑士联动与完整招式')
        self.guest_knights_button.hide()
        body.addWidget(self.guest_knights_button)
        self.guest_knights_button.clicked.connect(self.open_guest_knights)
        self.guest_crystals_button = QPushButton('晶矿惊蝗 · 双晶兽的护盾与捕杀')
        self.guest_crystals_button.hide()
        body.addWidget(self.guest_crystals_button)
        self.guest_crystals_button.clicked.connect(self.open_guest_crystals)
        self.guest_material_button = QPushButton('“物欲拮抗者” · 指令、屏障与斯第奇')
        self.guest_material_button.hide()
        body.addWidget(self.guest_material_button)
        self.guest_material_button.clicked.connect(self.open_guest_material)
        self.enemy_player = QPlainTextEdit()
        self.enemy_player.setReadOnly(True)
        enemy_detail = QHBoxLayout()
        enemy_detail.addWidget(self.enemy_portrait, 0, Qt.AlignmentFlag.AlignTop)
        enemy_detail.addWidget(self.enemy_player, 1)
        body.addLayout(enemy_detail, 1)
        self.tabs.addTab(enemies, '敌人和机制')
        wave = QWidget()
        body = QVBoxLayout(wave)
        self.queue_kind = QComboBox()
        self.queue_kind.addItem('总览（全部条目）', None)
        self.queue_kind.addItem('主波次', 'main')
        self.queue_kind.addItem('条件分支', 'branch')
        body.addWidget(self.queue_kind)
        filters=QHBoxLayout();self.action_group=QComboBox();self.action_group.addItem('全部波次/分支分组',None);filters.addWidget(self.action_group)
        self.action_focus=QComboBox();self.action_focus.addItem('全部资料条目',None)
        for key,label in(('enemy','含所选敌人的候选条目'),('hidden','带隐藏组标记'),('random','带随机组标记'),('predefined','预置单位或装置条目')):self.action_focus.addItem(label,key)
        filters.addWidget(self.action_focus);body.addLayout(filters)
        self.action_filter_notice=QLabel();self.action_filter_notice.setWordWrap(True);body.addWidget(self.action_filter_notice)
        split = QSplitter()
        self.actions = QListWidget()
        split.addWidget(self.actions)
        self.action_player = QPlainTextEdit()
        self.action_player.setReadOnly(True)
        split.addWidget(self.action_player)
        split.setSizes([350, 650])
        body.addWidget(split, 1)
        self.action_position_button = QPushButton('在地图上查看本条位置参考')
        body.addWidget(self.action_position_button)
        self.action_position_button.clicked.connect(self.open_action_positions)
        self.tabs.addTab(wave, '出怪与条件')
        self.spawn_candidates_button = QPushButton('查看出怪候选与关联记录')
        body.addWidget(self.spawn_candidates_button)
        self.spawn_candidates_button.clicked.connect(self.open_spawn_candidates)
        self.route_itinerary_dialog = None
        self.route_itinerary_button = QPushButton('查看完整行程与停留条件')
        body.addWidget(self.route_itinerary_button)
        self.route_itinerary_button.clicked.connect(self.open_route_itinerary)
        from .current_settlement_modes_view import CurrentSettlementModesPanel
        self.settlement = CurrentSettlementModesPanel(stage_id, load=False)
        from .current_reward_view import CurrentRewardPanel
        self.rewards = CurrentRewardPanel(stage_id, load=False, settlement=self.settlement)
        self.tabs.addTab(self.rewards, '奖励与条件')
        self.rewards.actionSelected.connect(self._reward_action_selected)
        self.details_toggle.toggled.connect(self._show_details)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.enemy_combo.currentIndexChanged.connect(self._enemy_changed)
        self.queue_kind.currentIndexChanged.connect(self._actions_changed)
        self.action_group.currentIndexChanged.connect(self._actions_changed);self.action_focus.currentIndexChanged.connect(self._actions_changed)
        self.actions.currentItemChanged.connect(self._action_changed)
        self.refresh_reference()

    def _show_details(self, checked):
        for label in (self.notice, self.rewards.notice, self.settlement.notice):
            label.setVisible(checked)

    def _clear(self):
        self._close_guest_material()
        self.guest_material_button.hide()
        self.guest_material_button.setEnabled(False)
        self._close_guest_crystals()
        self.guest_crystals_button.hide()
        self.guest_crystals_button.setEnabled(False)
        self._close_guest_knights()
        self.guest_knights_button.hide()
        self.guest_knights_button.setEnabled(False)
        self._close_route_itinerary()
        self.route_itinerary_button.setEnabled(False)
        self._close_stage_objects()
        self.stage_objects_button.setEnabled(False)
        self._close_enemy_spawns()
        self.enemy_spawns_button.hide()
        self.enemy_spawns_button.setEnabled(False)
        self._close_boss_documents()
        self.boss_documents_button.hide()
        self.boss_documents_button.setEnabled(False)
        self._close_sun_boss()
        self.sun_boss_button.hide()
        self.sun_boss_button.setEnabled(False)
        self._close_shop_vault()
        self.shop_vault_button.hide()
        self.shop_vault_button.setEnabled(False)
        self._close_elbert()
        self.elbert_button.hide()
        self.elbert_button.setEnabled(False)
        self._close_hanko()
        self.hanko_button.hide()
        self.hanko_button.setEnabled(False)
        self._close_spawn_candidates()
        self.spawn_candidates_button.setEnabled(False)
        self._close_event_origins()
        self.event_origins_button.setEnabled(False)
        self.event_origins_button.hide()
        self._close_map_positions()
        self.position_button.setEnabled(False)
        self.action_position_button.setEnabled(False)
        self.result = None
        self.source_identity = None
        self.enemy_key = None
        self.action_key = None
        self.map_image.clear()
        self.map_image.setText(model.UNAVAILABLE)
        self.enemy_portrait.clear()
        self.enemy_search_notice.setText('当前关卡资料暂不可用，旧搜索结果已清除。')
        self.enemy_choices.set_groups([], emit=False)
        self._sync_enemy_grid()
        blocked = self.actions.blockSignals(True)
        self.actions.clear()
        self.action_filter_notice.setText('当前关卡资料暂不可用，旧分组和出怪条目已清除。')
        group_blocked=self.action_group.blockSignals(True);self.action_group.clear();self.action_group.addItem('全部波次/分支分组',None);self.action_group.blockSignals(group_blocked)
        self.actions.blockSignals(blocked)
        for widget in (self.summary, self.enemy_player, self.action_player, self.technical):
            replace_text(widget, '', preserve=False)
        self.rewards.clear_reference()
        self.settlement.clear_reference()
        self.source_toggle.setChecked(False)
        self.details_toggle.setChecked(False)
        self.rewards.sections.setCurrentIndex(0)

    def refresh_reference(self):
        fresh = model.stage_reference(self.stage_id)
        if fresh is None:
            self._clear()
            return False
        keep = self.result is not None and self.source_identity == fresh['source_identity'] and (self.result['id'] == fresh['id'])
        if not keep:
            self._close_event_origins()
            self._close_spawn_candidates()
        old_enemy = self.enemy_combo.currentData() if keep else None
        self.result = fresh
        self.source_identity = fresh['source_identity']
        from .current_event_battles import stage_has_reference
        has_origins = stage_has_reference(self.stage_id)
        self.event_origins_button.setVisible(has_origins)
        self.event_origins_button.setEnabled(has_origins)
        origin = getattr(self, 'event_origins_dialog', None)
        if keep and origin is not None and origin.isVisible():
            origin.panel.refresh_reference()
        self.position_button.setEnabled(True)
        self.spawn_candidates_button.setEnabled(True)
        self.settlement.refresh_reference()
        replace_text(self.summary, model.summary_text(fresh), preserve=keep)
        replace_text(self.technical, _technical_json(fresh), preserve=keep)
        raw = version.image_bytes(fresh['image'])
        self.map_image.set_data(raw, '本关固定原图无法核对，不借用同名关卡图片。')
        self.install_enemy_choices(old_enemy)
        self._enemy_changed(preserve=keep, update_actions=False)
        if not keep:
            blocked=self.action_group.blockSignals(True);self.action_group.setCurrentIndex(0);self.action_group.blockSignals(blocked)
        self._actions_changed(preserve=keep)
        if not keep:
            self.tabs.setCurrentIndex(0)
            self.source_toggle.setChecked(False)
            self.details_toggle.setChecked(False)
            self.rewards.sections.setCurrentIndex(0)
        self.rewards.refresh_reference()
        for name in ('position_dialog', 'action_position_dialog', 'spawn_candidates_dialog'):
            dialog = getattr(self, name, None)
            if dialog is not None and dialog.isVisible():
                dialog.panel.refresh_reference()
        self._sync_stage_objects(keep)
        self._sync_route_itinerary(keep)
        return True

    def _close_spawn_candidates(self):
        dialog=getattr(self,'spawn_candidates_dialog',None)
        if dialog is not None:dialog.close()

    def _spawn_source_invalidated(self):
        dialog=getattr(self,'spawn_candidates_position_dialog',None)
        if dialog is not None:dialog.panel.clear_reference();dialog.close()
        self.spawn_candidates_position_dialog=None

    def _spawn_action_selected(self,key):
        dialog=getattr(self,'spawn_candidates_dialog',None)
        if self.result is None or dialog is None or dialog.panel.result is None:return False
        if dialog.panel.result['battle_source_identity']!=self.result['source_identity']:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        action=next((a for a in self.result['actions']if a['key']==key),None)
        if action is None:return False
        return self.focus_action(action)

    def _spawn_position_requested(self,key):
        okay=self._spawn_action_selected(key) and self.open_action_positions()
        if okay:self.spawn_candidates_position_dialog=self.action_position_dialog
        return okay

    def open_spawn_candidates(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_spawn_candidates_view import CurrentSpawnCandidatesDialog
        self._close_spawn_candidates();self.spawn_candidates_dialog=CurrentSpawnCandidatesDialog(self.stage_id,parent=self)
        panel=self.spawn_candidates_dialog.panel
        if panel.result is None:self._close_spawn_candidates();return False
        panel.actionSelected.connect(self._spawn_action_selected)
        panel.actionPositionRequested.connect(self._spawn_position_requested)
        panel.sourceInvalidated.connect(self._spawn_source_invalidated)
        self.spawn_candidates_dialog.show();return True

    def _reward_action_selected(self,key):
        if self.result is None or self.rewards.result is None or self.result['source_identity']!=self.rewards.result['battle_source_identity']:return False
        action=next((a for a in self.result['actions']if a['key']==key),None)
        if action is None:return False
        return self.focus_action(action)

    def install_enemy_choices(self,preferred=None):
        from .player_enemy_search import matches
        query=self.enemy_search.text();rows=[e for e in(self.result or{}).get('enemies',[])if matches(e,query)];groups=[]
        for tier,label in [*model.TIERS.items(),(None,'类别未确认')]:
            items=[]
            for enemy in rows:
                if enemy['tier']!=tier:continue
                picture=QPixmap();icon=QIcon();raw=model.picture_for_enemy(enemy)
                if raw and picture.loadFromData(raw,'PNG'):icon=QIcon(picture)
                items.append((enemy['name']+' · 引用资料'+str(enemy['reference_index']+1),enemy['key'],icon))
            groups.append((label,items))
        self.enemy_choices.keep_empty_groups=bool(query.strip())
        blocked=self.enemy_combo.blockSignals(True);self.enemy_choices.set_groups(groups,emit=False)
        if preferred is not None:self.enemy_choices.select_value(preferred,emit=False)
        self.enemy_combo.blockSignals(blocked)
        self._sync_enemy_grid()
        self.enemy_search_notice.setText(f'原文搜索匹配{len(rows)}条引用资料，可继续按分类查看；不是实际出怪数量。未匹配不表示没有这种机制，隐藏脚本和阶段变化不在此搜索范围。'if query.strip()else'可搜索名称与已列图鉴原文；同名不同引用分别保留，不相加为实际敌人数。')

    def _show_enemy_grid(self, checked):
        self.enemy_grid.setVisible(checked)
        self.enemy_grid_toggle.setText('收起敌人图册' if checked else '展开敌人图册')

    def _sync_enemy_grid(self, *_):
        key = self.enemy_combo.currentData()
        offset = self.enemy_grid.verticalScrollBar().value()
        names = {e['key']: e['name'] for e in (self.result or {}).get('enemies', [])}
        blocked = self.enemy_grid.blockSignals(True)
        self.enemy_grid.clear()
        # Reuse the already verified branch icons, without rereading images or
        # converting candidate references into actual spawn counts.
        for title, identity, icon in self.enemy_choices.entries():
            item = QListWidgetItem(icon, names[identity])
            item.setData(Qt.ItemDataRole.UserRole, identity)
            item.setToolTip(title + '；候选资料，不是实际出怪数量')
            self.enemy_grid.addItem(item)
            if identity == key:
                self.enemy_grid.setCurrentItem(item)
        self.enemy_grid.verticalScrollBar().setValue(offset)
        self.enemy_grid.blockSignals(blocked)
        self.enemy_grid._selected(self.enemy_grid.currentItem())

    def _enemy_grid_selected(self, item, *_):
        if item is not None:
            self.enemy_choices.select_value(item.data(Qt.ItemDataRole.UserRole))

    def _select_enemy_tile(self, key):
        current = self.enemy_grid.currentItem()
        if current is not None and current.data(Qt.ItemDataRole.UserRole) == key:
            return
        item = next((self.enemy_grid.item(i) for i in range(self.enemy_grid.count())
                     if self.enemy_grid.item(i).data(Qt.ItemDataRole.UserRole) == key), None)
        blocked = self.enemy_grid.blockSignals(True)
        self.enemy_grid.setCurrentItem(item)
        self.enemy_grid.blockSignals(blocked)
        self.enemy_grid._selected(item)
        if item is not None:
            self.enemy_grid.scrollToItem(item)

    def filter_enemies(self,*_):
        preferred=self.enemy_combo.currentData();self.install_enemy_choices(preferred);self._enemy_changed(preserve=True)

    def _enemy_changed(self, *_, preserve=False, update_actions=True):
        key = self.enemy_combo.currentData()
        enemy = next((e for e in self.result['enemies'] if e['key'] == key), None) if self.result else None
        keep = preserve and key == self.enemy_key
        self.enemy_key = key
        self._select_enemy_tile(key)
        self.enemy_portrait.setVisible(enemy is not None)
        replace_text(self.enemy_player, model.enemy_text(enemy) if enemy else '请选择敌人或关联实体。', preserve=keep)
        self.enemy_portrait.clear()
        pix = QPixmap()
        raw = model.picture_for_enemy(enemy)
        if raw and pix.loadFromData(raw, 'PNG'):
            self.enemy_portrait.setPixmap(pix.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.enemy_portrait.setText('此精确引用未取得图片。' if enemy else '')
        self._sync_boss_documents(keep)
        if update_actions and self.action_focus.currentData()=='enemy':self._actions_changed(preserve=True)
        self._sync_sun_boss(keep)
        self._sync_elbert(keep)
        self._sync_hanko(keep)
        self._sync_shop_vault(keep)
        self._sync_enemy_spawns(keep)
        self._sync_guest_knights(keep)
        self._sync_guest_crystals(keep)
        self._sync_guest_material(keep)

    def _actions_changed(self,*_,preserve=False):
        from .player_spawn_filters import action_rows,group_key,group_label
        old=self.actions.currentItem();key=old.data(Qt.ItemDataRole.UserRole)if old and preserve else None
        kind=self.queue_kind.currentData();actions=self.result['actions']if self.result else[]
        selected_group=None if self.sender()is self.queue_kind else self.action_group.currentData()
        groups=list(dict.fromkeys(group_key(a)for a in action_rows(actions,kind)if group_key(a)is not None))
        blocked=self.action_group.blockSignals(True);self.action_group.clear();self.action_group.addItem('全部波次/分支分组',None)
        for group in groups:self.action_group.addItem(group_label(group),group)
        index=self.action_group.findData(selected_group)
        if selected_group is not None and index<0:self.action_group.addItem('原分组在当前范围无资料',selected_group);index=self.action_group.count()-1
        self.action_group.setCurrentIndex(max(0,index));self.action_group.blockSignals(blocked)
        rows=action_rows(actions,kind,self.action_group.currentData(),self.action_focus.currentData(),self.enemy_key)
        blocked=self.actions.blockSignals(True);self.actions.clear()
        for action in rows:
            item=QListWidgetItem(model.action_label(action));item.setData(Qt.ItemDataRole.UserRole,action['key']);self.actions.addItem(item)
            if key==action['key']:self.actions.setCurrentItem(item)
        self.actions.blockSignals(blocked)
        if not any(a['key']==key for a in rows):self.actions.setCurrentRow(-1)
        self._action_changed(self.actions.currentItem(),preserve=preserve)
        self.action_filter_notice.setText(('请先在敌人页选择准确引用。'if self.action_focus.currentData()=='enemy'and self.enemy_key is None else f'显示{len(rows)}条资料，关卡完整资料共{len(actions)}条。')+'分组、隐藏与随机标记不证明实际触发、数量或出怪时刻；多等级候选仍需分别核对。')

    def focus_action(self,action):
        if self.result is None or action not in self.result['actions']:return False
        for widget in(self.action_group,self.action_focus):
            blocked=widget.blockSignals(True);widget.setCurrentIndex(0);widget.blockSignals(blocked)
        blocked=self.queue_kind.blockSignals(True);self.queue_kind.setCurrentIndex(self.queue_kind.findData(action['queue']['kind']));self.queue_kind.blockSignals(blocked);self._actions_changed()
        for i in range(self.actions.count()):
            if self.actions.item(i).data(Qt.ItemDataRole.UserRole)==action['key']:
                self.actions.setCurrentRow(i);self.source_toggle.setChecked(False);self.tabs.setCurrentIndex(2);return True
        return False

    def _action_changed(self,item,*_,preserve=False):
        key=item.data(Qt.ItemDataRole.UserRole)if item else None
        action=next((a for a in self.result['actions']if a['key']==key),None)if self.result else None
        if key!=self.action_key:
            dialog=getattr(self,'action_position_dialog',None)
            if dialog is not None:dialog.close()
        keep=preserve and key==self.action_key;self.action_key=key
        replace_text(self.action_player,model.action_text(action)if action else'请选择一条出怪、装置或条件分支资料。',preserve=keep)
        self.action_position_button.setEnabled(action is not None and action['raw'].get('actionType')in('SPAWN','ACTIVATE_PREDEFINED'))

    def _close_map_positions(self):
        for name in ('position_dialog','action_position_dialog'):
            dialog=getattr(self,name,None)
            if dialog is not None:dialog.close()

    def open_action_positions(self):
        if self.result is None or self.action_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_action_positions_view import CurrentActionPositionsDialog
        dialog=getattr(self,'action_position_dialog',None)
        self.enemy_spawns_position_dialog=None
        self.spawn_candidates_position_dialog=None
        if dialog is None:self.action_position_dialog=CurrentActionPositionsDialog(self.stage_id,self.action_key,self)
        else:dialog.panel.set_reference(self.stage_id,self.action_key)
        self.action_position_dialog.show();return True

    def open_map_positions(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_map_position_view import CurrentMapPositionDialog
        self._close_map_positions()
        dialog=getattr(self,'position_dialog',None)
        if dialog is None:self.position_dialog=CurrentMapPositionDialog(self.stage_id,self)
        else:dialog.panel.refresh_reference()
        self.position_dialog.show();return True

    def _close_hanko(self):
        child=getattr(self,'hanko_dialog',None)
        if child is not None:
            child.panel.clear_reference();child.close()

    def _sync_hanko(self,keep):
        from . import current_hanko as reader
        available=self.result is not None and self.enemy_key is not None and bool(reader.target_available(self.stage_id,self.enemy_key))
        self.hanko_button.setVisible(available);self.hanko_button.setEnabled(available)
        child=getattr(self,'hanko_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_hanko()
            elif not available:child.panel.clear_reference()
            else:child.panel.refresh_reference()

    def open_hanko(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_hanko as reader
        if not reader.target_available(self.stage_id,self.enemy_key):
            self._close_hanko();self.hanko_button.hide();return False
        from .current_hanko_view import CurrentHankoDialog
        self._close_hanko();self.hanko_dialog=CurrentHankoDialog(self.stage_id,self.enemy_key,self)
        if self.hanko_dialog.panel.result is None:self._close_hanko();return False
        self.hanko_dialog.show();return True

    def _close_elbert(self):
        child=getattr(self,'elbert_dialog',None)
        if child is not None:
            child.panel.clear_reference();child.close()

    def _sync_elbert(self,keep):
        from . import current_elbert_reference as reader
        available=self.result is not None and self.enemy_key is not None and bool(reader.locate(self.stage_id,self.enemy_key) is not None)
        self.elbert_button.setVisible(available);self.elbert_button.setEnabled(available)
        child=getattr(self,'elbert_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_elbert()
            elif not available:child.panel.clear_reference()
            else:
                child.panel.refresh_reference()
                child_result=child.panel.base
                if child_result is not None and child_result.get('battle_source_identity')!=self.result['source_identity']:
                    self._close_elbert()

    def open_elbert(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_elbert_reference as reader
        if not reader.locate(self.stage_id,self.enemy_key) is not None:
            self._close_elbert();self.elbert_button.hide();return False
        from .current_elbert_view import CurrentElbertDialog
        self._close_elbert();self.elbert_dialog=CurrentElbertDialog(self.stage_id,self.enemy_key,self)
        child_result=self.elbert_dialog.panel.result
        if child_result is None or child_result.get('battle_source_identity')!=self.result['source_identity']:
            self._close_elbert();return False
        self.elbert_dialog.show();return True

    def _close_sun_boss(self):
        child=getattr(self,'sun_boss_dialog',None)
        if child is not None:
            child.panel.clear_reference();child.close()

    def _sync_sun_boss(self,keep):
        from . import current_sun_boss as reader
        available=self.result is not None and self.enemy_key is not None and bool(reader.target_available(self.stage_id,self.enemy_key))
        self.sun_boss_button.setVisible(available);self.sun_boss_button.setEnabled(available)
        child=getattr(self,'sun_boss_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_sun_boss()
            elif not available:child.panel.clear_reference()
            else:
                child.panel.refresh_reference()
                child_result=child.panel.result
                if child_result is not None and child_result.get('battle_source_identity')!=self.result['source_identity']:
                    self._close_sun_boss()

    def open_sun_boss(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_sun_boss as reader
        if not reader.target_available(self.stage_id,self.enemy_key):
            self._close_sun_boss();self.sun_boss_button.hide();return False
        from .current_sun_boss_view import CurrentSunBossDialog
        self._close_sun_boss();self.sun_boss_dialog=CurrentSunBossDialog(self.stage_id,self.enemy_key,self)
        child_result=self.sun_boss_dialog.panel.result
        if child_result is None or child_result.get('battle_source_identity')!=self.result['source_identity']:
            self._close_sun_boss();return False
        self.sun_boss_dialog.show();return True

    def _boss_documents_enemy_requested(self,key):
        dialog=getattr(self,'boss_documents_dialog',None)
        if type(key)is not str or self.result is None or dialog is None or not dialog.isVisible():return False
        child=dialog.panel
        if child.result is None or child.stage_id!=self.stage_id or child.result.get('stage_id')!=self.stage_id:
            self._close_boss_documents();return False
        if child.result.get('battle_source_identity')!=self.result['source_identity']:
            self._close_boss_documents();return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_boss_documents as reader
        request=reader.resolve_entity(child.result,child.selected_key,child.related.currentData())
        if request is None or request['stage_id']!=self.stage_id or request['enemy_key']!=key:
            self._close_boss_documents();return False
        if not any(row['key']==key for row in self.result['enemies']):self._close_boss_documents();return False
        if self.enemy_combo.findData(key)<0:self.enemy_search.clear()
        selected=self.enemy_choices.select_value(key)
        if selected:
            self._close_boss_documents();self.source_toggle.setChecked(False);self.tabs.setCurrentIndex(1)
        return selected

    def _close_boss_documents(self):
        child=getattr(self,'boss_documents_dialog',None)
        if child is not None:
            child.panel.clear_reference();child.close()

    def _sync_boss_documents(self,keep):
        from . import current_boss_documents as reader
        available=self.result is not None and self.enemy_key is not None and bool(reader.target_available(self.stage_id,self.enemy_key))
        self.boss_documents_button.setVisible(available);self.boss_documents_button.setEnabled(available)
        child=getattr(self,'boss_documents_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_boss_documents()
            elif not available:child.panel.clear_reference()
            else:
                child.panel.refresh_reference()
                child_result=child.panel.result
                if child_result is not None and child_result.get('battle_source_identity')!=self.result['source_identity']:
                    self._close_boss_documents()

    def open_boss_documents(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_boss_documents as reader
        if not reader.target_available(self.stage_id,self.enemy_key):
            self._close_boss_documents();self.boss_documents_button.hide();return False
        from .current_boss_documents_view import CurrentBossDocumentsDialog
        self._close_boss_documents();self.boss_documents_dialog=CurrentBossDocumentsDialog(self.stage_id,self.enemy_key,self)
        child_result=self.boss_documents_dialog.panel.result
        if child_result is None or child_result.get('battle_source_identity')!=self.result['source_identity']:
            self._close_boss_documents();return False
        self.boss_documents_dialog.panel.enemy_requested.connect(self._boss_documents_enemy_requested)
        self.boss_documents_dialog.show();return True

    def _close_guest_knights(self):
        child=getattr(self,'guest_knights_dialog',None)
        if child is not None:child.panel.clear_reference();child.close()

    def _sync_guest_knights(self,keep):
        from . import current_guest_knights as reader
        available=self.result is not None and self.enemy_key is not None and reader.target_available(self.stage_id,self.enemy_key)
        self.guest_knights_button.setVisible(available);self.guest_knights_button.setEnabled(available)
        child=getattr(self,'guest_knights_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_guest_knights()
            elif not available:child.panel.clear_reference()
            else:
                child.panel.refresh_reference()
                result=child.panel.result
                if result is not None and result.get('battle_source_identity')!=self.result['source_identity']:self._close_guest_knights()

    def open_guest_knights(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_guest_knights as reader
        if not reader.target_available(self.stage_id,self.enemy_key):self._close_guest_knights();self.guest_knights_button.hide();return False
        from .current_guest_knights_view import CurrentGuestKnightsDialog
        self._close_guest_knights();self.guest_knights_dialog=CurrentGuestKnightsDialog(self.stage_id,self.enemy_key,self)
        result=self.guest_knights_dialog.panel.result
        if result is None or result.get('battle_source_identity')!=self.result['source_identity']:self._close_guest_knights();return False
        self.guest_knights_dialog.show();return True

    def _close_guest_crystals(self):
        child=getattr(self,'guest_crystals_dialog',None)
        if child is not None:child.panel.clear_reference();child.close()

    def _sync_guest_crystals(self,keep):
        from . import current_guest_crystals as reader
        available=self.result is not None and self.enemy_key is not None and reader.target_available(self.stage_id,self.enemy_key)
        self.guest_crystals_button.setVisible(available);self.guest_crystals_button.setEnabled(available)
        child=getattr(self,'guest_crystals_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_guest_crystals()
            elif not available:child.panel.clear_reference()
            else:
                child.panel.refresh_reference()
                result=child.panel.result
                if result is not None and result.get('battle_source_identity')!=self.result['source_identity']:self._close_guest_crystals()

    def open_guest_crystals(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_guest_crystals as reader
        if not reader.target_available(self.stage_id,self.enemy_key):self._close_guest_crystals();self.guest_crystals_button.hide();return False
        from .current_guest_crystals_view import CurrentGuestCrystalsDialog
        self._close_guest_crystals();self.guest_crystals_dialog=CurrentGuestCrystalsDialog(self.stage_id,self.enemy_key,self)
        result=self.guest_crystals_dialog.panel.result
        if result is None or result.get('battle_source_identity')!=self.result['source_identity']:self._close_guest_crystals();return False
        self.guest_crystals_dialog.show();return True

    def _close_guest_material(self):
        child=getattr(self,'guest_material_dialog',None)
        if child is not None:child.panel.clear_reference();child.close()

    def _sync_guest_material(self,keep):
        from . import current_guest_material as reader
        available=self.result is not None and self.enemy_key is not None and reader.target_available(self.stage_id,self.enemy_key)
        self.guest_material_button.setVisible(available);self.guest_material_button.setEnabled(available)
        child=getattr(self,'guest_material_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_guest_material()
            elif not available:child.panel.clear_reference()
            else:
                child.panel.refresh_reference()
                result=child.panel.result
                if result is not None and result.get('battle_source_identity')!=self.result['source_identity']:self._close_guest_material()

    def open_guest_material(self):
        if self.result is None or self.enemy_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from . import current_guest_material as reader
        if not reader.target_available(self.stage_id,self.enemy_key):self._close_guest_material();self.guest_material_button.hide();return False
        from .current_guest_material_view import CurrentGuestMaterialDialog
        self._close_guest_material();self.guest_material_dialog=CurrentGuestMaterialDialog(self.stage_id,self.enemy_key,self)
        result=self.guest_material_dialog.panel.result
        if result is None or result.get('battle_source_identity')!=self.result['source_identity']:self._close_guest_material();return False
        self.guest_material_dialog.show();return True

    def _close_event_origins(self):
        dialog=getattr(self,'event_origins_dialog',None)
        if dialog is not None:dialog.close()

    def open_event_origins(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_event_battles import stage_has_reference
        if not stage_has_reference(self.stage_id):self._close_event_origins();self.event_origins_button.hide();return False
        from .current_event_battles_view import CurrentEventBattlesDialog
        self._close_event_origins();self.event_origins_dialog=CurrentEventBattlesDialog(stage_id=self.stage_id,parent=self);self.event_origins_dialog.show();return True

    def _close_readers(self):
        self._close_guest_material()
        self._close_guest_crystals()
        self._close_guest_knights()
        self._close_route_itinerary()
        self._close_stage_objects()
        self._close_enemy_spawns()
        self._close_boss_documents()
        self._close_sun_boss()
        self._close_shop_vault()
        self.rewards._close_shop_vault()
        self._close_elbert()
        self._close_hanko()
        self.settlement.clear_reference()
        self._close_spawn_candidates()
        self._close_map_positions()
        self._close_event_origins()

    def closeEvent(self, event):
        self._close_readers()
        super().closeEvent(event)

    def _close_shop_vault(self):
        child=getattr(self,'shop_vault_dialog',None)
        if child is not None:
            child.panel.clear_reference();child.close()
        self.shop_vault_dialog=None

    def _sync_shop_vault(self,keep):
        from . import current_cannot_reference as reader
        target=reader.target_for_enemy(self.stage_id,self.enemy_key) if self.result is not None and self.enemy_key is not None else None
        available=target is not None
        self.shop_vault_button.setVisible(available);self.shop_vault_button.setEnabled(available)
        child=getattr(self,'shop_vault_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_shop_vault()
            elif not available:child.panel.clear_reference()
            else:child.panel.refresh_reference()
        return target

    def open_shop_vault(self):
        if self.result is None or self.enemy_key is None:return False
        if self.enemy_combo.currentData()!=self.enemy_key:
            self._close_shop_vault();return False
        if model.stage_reference(self.stage_id)!=self.result:
            self._clear();return False
        target=self._sync_shop_vault(True)
        if target is None:
            self._close_shop_vault();return False
        from .current_cannot_view import CurrentCannotDialog
        self._close_shop_vault();self.shop_vault_dialog=CurrentCannotDialog(target,self)
        if self.shop_vault_dialog.panel.result is None:
            self._close_shop_vault();self.shop_vault_button.hide();self.shop_vault_button.setEnabled(False);return False
        self.shop_vault_dialog.show();return True

    def _close_enemy_spawns(self):
        child=getattr(self,'enemy_spawns_dialog',None)
        if child is not None:child.panel.clear_reference(notify=False);child.close()
        self._enemy_spawns_source_invalidated()
        self.enemy_spawns_dialog=None
    def _enemy_spawns_source_invalidated(self):
        child=getattr(self,'enemy_spawns_position_dialog',None)
        if child is not None:child.panel.clear_reference();child.close()
        self.enemy_spawns_position_dialog=None
    def _sync_enemy_spawns(self,keep):
        available=self.result is not None and self.enemy_key is not None
        self.enemy_spawns_button.setVisible(available);self.enemy_spawns_button.setEnabled(available)
        child=getattr(self,'enemy_spawns_dialog',None)
        if child is not None and child.isVisible():
            if not keep or not available or child.panel.enemy_key!=self.enemy_key:self._close_enemy_spawns()
            else:child.panel.refresh_reference()
    def _enemy_spawns_action_selected(self,key):
        child=getattr(self,'enemy_spawns_dialog',None)
        if self.result is None or child is None or child.panel.result is None:return False
        if child.panel.result['battle_source_identity']!=self.result['source_identity']or child.panel.enemy_key!=self.enemy_key:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_enemy_spawns import resolve_action
        if resolve_action(child.panel.result,key)is None:child.panel.clear_reference();return False
        action=next((a for a in self.result['actions']if a['key']==key),None)
        if action is None:return False
        return self.focus_action(action)
    def _enemy_spawns_position_requested(self,key):
        okay=self._enemy_spawns_action_selected(key)and self.open_action_positions()
        if okay:self.enemy_spawns_position_dialog=self.action_position_dialog
        return okay
    def open_enemy_spawns(self):
        if self.result is None or self.enemy_key is None:return False
        if self.enemy_combo.currentData()!=self.enemy_key:self._close_enemy_spawns();return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_enemy_spawns_view import CurrentEnemySpawnsDialog
        self._close_enemy_spawns();self.enemy_spawns_dialog=CurrentEnemySpawnsDialog(self.stage_id,self.enemy_key,self)
        panel=self.enemy_spawns_dialog.panel
        if panel.result is None:self._close_enemy_spawns();return False
        panel.actionSelected.connect(self._enemy_spawns_action_selected);panel.actionPositionRequested.connect(self._enemy_spawns_position_requested);panel.sourceInvalidated.connect(self._enemy_spawns_source_invalidated)
        self.enemy_spawns_dialog.show();return True

    def _close_stage_objects(self):
        child=getattr(self,'stage_objects_dialog',None)
        if child is not None:child.panel.clear_reference(notify=False);child.close()
        self.stage_objects_dialog=None
    def _sync_stage_objects(self,keep):
        self.stage_objects_button.setEnabled(self.result is not None)
        child=getattr(self,'stage_objects_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_stage_objects()
            else:child.panel.refresh_reference()
    def _stage_objects_action_selected(self,key):
        child=getattr(self,'stage_objects_dialog',None)
        if self.result is None or child is None or child.panel.result is None:return False
        if child.panel.result['battle_source_identity']!=self.result['source_identity']:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_stage_objects import resolve
        row=child.panel.selected();action=child.panel.selected_action()
        if row is None or action is None or action['key']!=key or resolve(child.panel.result,row['key'],key)is None:child.panel.clear_reference();return False
        return self.focus_action(action)
    def open_stage_objects(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_stage_objects_view import CurrentStageObjectsDialog
        self._close_stage_objects();self.stage_objects_dialog=CurrentStageObjectsDialog(self.stage_id,self)
        child=self.stage_objects_dialog
        if child.panel.result is None or child.panel.result['battle_source_identity']!=self.result['source_identity']:self._close_stage_objects();return False
        child.panel.actionSelected.connect(self._stage_objects_action_selected);child.show();return True

    def _close_route_itinerary(self):
        child=getattr(self,'route_itinerary_dialog',None)
        if child is not None:child.panel.clear_reference(notify=False);child.close()
        self.route_itinerary_dialog=None
    def _sync_route_itinerary(self,keep):
        self.route_itinerary_button.setEnabled(self.result is not None)
        child=getattr(self,'route_itinerary_dialog',None)
        if child is not None and child.isVisible():
            if not keep:self._close_route_itinerary()
            else:child.panel.refresh_reference()
    def _route_itinerary_action_selected(self,key):
        child=getattr(self,'route_itinerary_dialog',None)
        if self.result is None or child is None or child.panel.result is None:return False
        if child.panel.result['battle_source_identity']!=self.result['source_identity']:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_route_itinerary import resolve
        route=child.panel.selected_route();action=child.panel.selected_action()
        if action is None or action['key']!=key or resolve(child.panel.result,route['key']if route else None,action_key=key)is None:child.panel.clear_reference();return False
        return self.focus_action(action)
    def open_route_itinerary(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_route_itinerary_view import CurrentRouteItineraryDialog
        self._close_route_itinerary();self.route_itinerary_dialog=CurrentRouteItineraryDialog(self.stage_id,self);child=self.route_itinerary_dialog
        if child.panel.result is None or child.panel.result['battle_source_identity']!=self.result['source_identity']:self._close_route_itinerary();return False
        child.panel.actionSelected.connect(self._route_itinerary_action_selected);child.show();return True


class CurrentBattleDialog(QDialog):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.setWindowTitle('固定关卡预览');self.resize(1120,820)
        layout=QVBoxLayout(self);self.panel=CurrentBattlePanel(stage_id);layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel._close_readers()
        super().closeEvent(event)
