"""Scalable tile reference and a plain offline battle-preview panel."""
import copy,hashlib
from pathlib import Path
from PySide6.QtCore import Qt,QRectF,QPointF,Signal
from PySide6.QtGui import QColor,QPainter,QPen,QPixmap
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QListWidget,QListWidgetItem,QPlainTextEdit,QSplitter,QCheckBox,QSpinBox,QPushButton)
from .battle_preview import (DATA,battle_data,spawn_rows,enemy_preview,enemy_text,spawn_text)
from .spawn_reference import local_sequence,ordinal_offset
from .map_projection import projection_for,projection_data
from .ui_state import replace_text
from .view_catalog import stage_groups,enemy_groups,SubjectPicture,ENEMY_TIERS
from .branch_choice import BranchChoice,OVERVIEW
from .battle_reward_planning import stage_reward_sources,reward_source_text
from .branch_reference_view import BranchReferencePanel
from .duel_reward_planning import is_duel_stage
from .duel_reward_view import DuelRewardPanel
from .highland_top_view import HighlandTopDialog
from .battle_entry_reference_view import BattleEntryReferencePanel,entry_packet
from . import spawn_candidates
from .spawn_candidates_view import SpawnCandidatesPanel

class BattleGrid(QWidget):
    cellSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.stage=None;self.rows=[];self.selected=None;self.selected_ordinal=1;self.reference_cell=None;self.branch_positions=[]
        self.setMinimumSize(240,150)

    def set_reference(self,stage,rows):
        self.stage=stage;self.rows=rows;self.selected=None;self.reference_cell=None;self.branch_positions=[];self.update()

    def grid_rect(self):
        if not self.stage:return QRectF()
        nr=len(self.stage['map']);nc=len(self.stage['map'][0])
        size=max(1,min((self.width()-24)/nc,(self.height()-24)/nr))
        return QRectF((self.width()-size*nc)/2,(self.height()-size*nr)/2,size*nc,size*nr)

    def cell_center(self,cell):
        rect=self.grid_rect();size=rect.width()/len(self.stage['map'][0])
        return QPointF(rect.left()+(cell['col']+.5)*size,rect.top()+(cell['row']+.5)*size)

    def cell_at(self,point):
        if not self.stage:return None
        rect=self.grid_rect()
        if not rect.contains(QPointF(point)):return None
        nr=len(self.stage['map']);nc=len(self.stage['map'][0]);size=rect.width()/nc
        r=int((point.y()-rect.top())/size);c=int((point.x()-rect.left())/size)
        return {'row':r,'col':c} if 0<=r<nr and 0<=c<nc else None

    def paintEvent(self,event):
        painter=QPainter(self);painter.fillRect(self.rect(),QColor('#18222e'))
        if not self.stage:
            painter.setPen(QColor('white'));painter.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'请选择战斗关卡')
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grid=self.grid_rect();nc=len(self.stage['map'][0]);size=grid.width()/nc
        colors={'tile_start':'#873e41','tile_end':'#2c658e','tile_hole':'#111820',
            'tile_forbidden':'#293039','tile_road':'#435562','tile_floor':'#68736c'}
        for r,line in enumerate(self.stage['map']):
            for c,index in enumerate(line):
                tile=self.stage['tiles'][index];key=tile['tileKey']
                rect=QRectF(grid.left()+c*size,grid.top()+r*size,size,size)
                fallback='#69736b' if tile.get('heightType')=='HIGHLAND' else '#435562'
                painter.setBrush(QColor(colors.get(key,fallback)));painter.setPen(QPen(QColor('#18222e'),1))
                painter.drawRect(rect)
                label={'tile_start':'入口','tile_end':'保护点','tile_hole':'洞'}.get(key,'')
                if label and size>=25:
                    painter.setPen(QColor('white'));painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,label)
        # Numbered marks are wave references, not the sum of possible enemies.
        cells={}
        for row in self.rows:
            start=row['route']['start']
            if start:cells.setdefault((start['row'],start['col']),set()).add(row['wave'])
        for (r,c),waves in cells.items():
            center=self.cell_center({'row':r,'col':c});radius=max(4,min(size*.18,12))
            painter.setPen(QPen(QColor('#fff3a0'),2));painter.setBrush(QColor('#282410'))
            painter.drawEllipse(center,radius,radius)
            if size>=25:
                painter.setPen(QColor('#fff3a0'))
                painter.drawText(QRectF(center.x()-radius,center.y()-radius,2*radius,2*radius),
                    Qt.AlignmentFlag.AlignCenter,str(next(iter(waves))) if len(waves)==1 else '*')
        if self.reference_cell:
            center=self.cell_center(self.reference_cell)
            painter.setPen(QPen(QColor('#f0a2ef'),3));painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(center.x()-size*.4,center.y()-size*.4,size*.8,size*.8))
        if self.selected:
            route=self.selected['route'];points=route.get('points',[])
            painter.setPen(QPen(QColor('#ffe17d'),2,Qt.PenStyle.DashLine))
            if route.get('continuous_reference'):
                for a,b in zip(points,points[1:]):painter.drawLine(self.cell_center(a),self.cell_center(b))
            for point in points:
                painter.setBrush(QColor('#ffe17d'));painter.drawEllipse(self.cell_center(point),3,3)
            if route['start']:
                painter.setPen(QPen(QColor('#ffffff'),3));painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(self.cell_center(route['start']),size*.32,size*.32)
            offset=ordinal_offset(self.selected,self.selected_ordinal)
            if offset is not None:
                # Local queue anchor stays explicit; this label is not an
                # absolute/live spawn timestamp or an actual movement ETA.
                painter.setPen(QColor('#fff3a0'))
                anchor='本阶段出场计划' if self.selected.get('branch') else '本段出场计划'
                painter.drawText(QRectF(8,2,max(0,self.width()-16),22),
                    Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,
                    f'第{self.selected_ordinal}次：{anchor}启动后 +{offset:g}秒（非开战计时）')
        for marker in self.branch_positions:
            center=self.cell_center(marker['cell']);radius=max(8,min(size*.28,18))
            painter.setPen(QPen(QColor('#f0a2ef'),2));painter.setBrush(QColor('#34213b'))
            painter.drawRect(QRectF(center.x()-radius,center.y()-radius,2*radius,2*radius))
            painter.drawText(QRectF(center.x()-radius,center.y()-radius,2*radius,2*radius),Qt.AlignmentFlag.AlignCenter,'P'+str(marker['ordinal']))

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            cell=self.cell_at(event.position())
            if cell:self.cellSelected.emit(cell)

class MapOriginal(QWidget):
    """Static original image with independently calibrated ground references."""
    cellSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.pixmap=QPixmap();self.setMinimumSize(220,130)
        self.stage=None;self.rows=[];self.selected=None;self.selected_ordinal=1
        self.projection=None;self.image_sha256=None;self.reference_cell=None;self.branch_positions=[]

    def set_file(self,path):
        try:raw=Path(path).read_bytes() if path else b''
        except OSError:raw=b''
        self.pixmap=QPixmap()
        if raw:self.pixmap.loadFromData(raw)
        self.image_sha256=hashlib.sha256(raw).hexdigest() if not self.pixmap.isNull() else None
        self.stage=None;self.rows=[];self.selected=None;self.projection=None;self.selected_ordinal=1;self.reference_cell=None;self.branch_positions=[]
        self.update()

    def set_reference(self,stage,rows):
        self.stage=stage;self.rows=rows;self.selected=None;self.selected_ordinal=1;self.reference_cell=None;self.branch_positions=[]
        self.projection=projection_for(stage,self.image_sha256,(self.pixmap.width(),self.pixmap.height()))
        self.update()

    def image_rect(self):
        if self.pixmap.isNull():return QRectF()
        ratio=min(self.width()/self.pixmap.width(),self.height()/self.pixmap.height())
        w,h=self.pixmap.width()*ratio,self.pixmap.height()*ratio
        return QRectF((self.width()-w)/2,(self.height()-h)/2,w,h)

    def cell_center(self,cell):
        if not self.projection:return None
        point=self.projection.project(cell)
        if point is None:return None
        rect=self.image_rect()
        return QPointF(rect.left()+point[0]*rect.width()/self.pixmap.width(),
            rect.top()+point[1]*rect.height()/self.pixmap.height())

    def cell_at(self,point):
        rect=self.image_rect()
        if not self.projection or not rect.contains(QPointF(point)):return None
        return self.projection.cell_at((point.x()-rect.left())*self.pixmap.width()/rect.width(),
            (point.y()-rect.top())*self.pixmap.height()/rect.height())

    def marker_cells(self):
        cells={}
        if not self.projection:return cells
        for row in self.rows:
            start=row['route']['start']
            if start and self.cell_center(start) is not None:
                cells.setdefault((start['row'],start['col']),set()).add(row['wave'])
        return cells

    def projected_branch_positions(self):
        if not self.stage or not self.projection:return []
        result=[]
        for marker in self.branch_positions:
            cell=marker['cell'];tile=self.stage['tiles'][self.stage['map'][cell['row']][cell['col']]]
            if tile.get('heightType')!='LOWLAND':continue
            center=self.cell_center(cell)
            if center is not None:result.append((marker,center))
        return result

    def _paint_branch_positions(self,painter,radius):
        for marker,center in self.projected_branch_positions():
            painter.setPen(QPen(QColor('#f0a2ef'),2));painter.setBrush(QColor('#34213b'))
            painter.drawRect(QRectF(center.x()-radius-3,center.y()-radius-3,2*radius+6,2*radius+6))
            painter.drawText(QRectF(center.x()-radius-3,center.y()-radius-3,2*radius+6,2*radius+6),Qt.AlignmentFlag.AlignCenter,'P'+str(marker['ordinal']))

    def paintEvent(self,event):
        painter=QPainter(self);painter.fillRect(self.rect(),QColor('#18222e'))
        if self.pixmap.isNull():return
        rect=self.image_rect();painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(rect,self.pixmap,QRectF(self.pixmap.rect()))
        if not self.projection:return
        painter.setClipRect(rect);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius=max(4,min(9,rect.width()/60))
        for (r,c),waves in self.marker_cells().items():
            center=self.cell_center({'row':r,'col':c})
            painter.setPen(QPen(QColor('#fff3a0'),2));painter.setBrush(QColor('#282410'))
            painter.drawEllipse(center,radius,radius)
            painter.setPen(QColor('#fff3a0'))
            painter.drawText(QRectF(center.x()-radius,center.y()-radius,2*radius,2*radius),
                Qt.AlignmentFlag.AlignCenter,str(next(iter(waves))) if len(waves)==1 else '*')
        if self.reference_cell:
            center=self.cell_center(self.reference_cell)
            if center is not None:
                painter.setPen(QPen(QColor('#f0a2ef'),3));painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(QRectF(center.x()-radius-3,center.y()-radius-3,2*radius+6,2*radius+6))
        if not self.selected:
            self._paint_branch_positions(painter,radius)
            return
        route=self.selected['route'];points=[self.cell_center(p) for p in route.get('points',[])]
        painter.setPen(QPen(QColor('#ffe17d'),2,Qt.PenStyle.DashLine))
        # Segments only connect source checkpoints. Teleport/disappear records
        # do not acquire a fabricated continuous route or movement ETA.
        if route.get('continuous_reference') and getattr(self.projection,'supports_segment_reference',True):
            for a,b in zip(points,points[1:]):
                if a is not None and b is not None:painter.drawLine(a,b)
        painter.setBrush(QColor('#ffe17d'))
        for point in points:
            if point is not None:painter.drawEllipse(point,3,3)
        center=self.cell_center(route['start'])
        if center is not None:
            painter.setPen(QPen(QColor('white'),3));painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center,radius+4,radius+4)
            offset=ordinal_offset(self.selected,self.selected_ordinal)
            if offset is not None:
                anchor='阶段队列' if self.selected.get('branch') else '片段队列'
                text=f'第{self.selected_ordinal}次 +{offset:g}秒\n{anchor}名义生成'
                width=min(rect.width(),max(painter.fontMetrics().horizontalAdvance(t) for t in text.splitlines())+12)
                height=min(rect.height(),2*painter.fontMetrics().height()+6)
                x=max(rect.left(),min(center.x()+radius+6,rect.right()-width))
                y=max(rect.top(),min(center.y()+radius+6,rect.bottom()-height))
                label=QRectF(x,y,width,height)
                painter.fillRect(label,QColor(24,34,46,220));painter.setPen(QColor('#fff3a0'))
                painter.drawText(label.adjusted(4,2,-4,-2),Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,text)
        self._paint_branch_positions(painter,radius)

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            cell=self.cell_at(event.position())
            if cell:self.cellSelected.emit(cell)

class BattlePreviewPanel(QWidget):
    stageSelected=Signal(object)
    entryEventSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.context={};self.current_stage=None;self.rows=[]
        self._rows_stage=None;self._shown_enemy=None;self._tile_cell=None;self._detail_key=None;self.reward_result=None;self._branch_marker=None
        layout=QVBoxLayout(self);controls=QHBoxLayout()
        self.stage_combo=QComboBox()
        self.stage_choices=BranchChoice(self.stage_combo,stage_groups(battle_data()['stages']),
            overview_label='总览（全部关卡）',placeholder='尚未选择战斗节点')
        controls.addWidget(self.stage_choices,1)
        self.wave_combo=QComboBox();controls.addWidget(self.wave_combo)
        self.enemy_combo=QComboBox()
        self.enemy_choices=BranchChoice(self.enemy_combo,[],overview_label='总览（当前关卡）',placeholder='全部敌人引用',notify_unchanged=True)
        for combo in (self.stage_combo,self.enemy_combo):
            combo.setMinimumContentsLength(12)
            combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        layout.addLayout(controls)
        layout.addWidget(self.enemy_choices)
        self.include_branches=QCheckBox('包含特定条件下才可能出现的敌人（不保证本局出现）');self.include_branches.setChecked(True)
        layout.addWidget(self.include_branches)
        self.technical=QCheckBox('显示技术资料（原始参数、标识与来源）');layout.addWidget(self.technical)
        self.occurrence_bar=QWidget();occurrence_layout=QHBoxLayout(self.occurrence_bar)
        occurrence_layout.setContentsMargins(0,0,0,0)
        occurrence_layout.addWidget(QLabel('这一组的第几名敌人'))
        self.occurrence=QSpinBox();self.occurrence.setRange(1,1)
        occurrence_layout.addWidget(self.occurrence)
        self.occurrence_label=QLabel();occurrence_layout.addWidget(self.occurrence_label,1)
        layout.addWidget(self.occurrence_bar);self.occurrence_bar.hide()
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        rewards=QHBoxLayout();rewards.addWidget(QLabel('可能获得的额外奖励'))
        self.reward_combo=QComboBox();rewards.addWidget(self.reward_combo,1);layout.addLayout(rewards)
        self.reward_summary=QPushButton('查看结算与全部奖励说明');rewards.addWidget(self.reward_summary)
        self.duel_reward_button=QPushButton('左中右档次奖励');rewards.addWidget(self.duel_reward_button)
        self.duel_reward_window=None
        self.duel_reward_button.clicked.connect(self.open_duel_rewards)
        self.highland_top_button=QPushButton('高台名义表面资料');rewards.addWidget(self.highland_top_button)
        self.highland_top_dialog=None;self.highland_top_button.clicked.connect(self.open_highland_top)
        self.entry_reference_button=QPushButton("查看对应节点与进入方式资料");layout.addWidget(self.entry_reference_button)
        self.entry_reference_button.hide();self.entry_reference_window=None
        self.entry_reference_button.clicked.connect(self.open_entry_references)
        candidates=QHBoxLayout()
        self.spawn_candidates_button=QPushButton('查看本关全部候选资料');candidates.addWidget(self.spawn_candidates_button)
        self.spawn_group_button=QPushButton('查看所选条目的同组候选');candidates.addWidget(self.spawn_group_button)
        layout.addLayout(candidates)
        self.spawn_candidates_window=None;self.candidate_preview_window=None
        self._spawn_candidates_current=False;self._candidate_preview_token=None
        self.spawn_candidates_button.clicked.connect(lambda:self.open_spawn_candidates())
        self.spawn_group_button.clicked.connect(self.open_current_spawn_candidates)
        self.branch_toggle=QCheckBox('展开特殊出怪条件与位置');layout.addWidget(self.branch_toggle)
        self.branch_panel=BranchReferencePanel();layout.addWidget(self.branch_panel);self.branch_panel.hide()
        maps=QSplitter(Qt.Orientation.Horizontal)
        left=QWidget();l=QVBoxLayout(left);l.setContentsMargins(0,0,0,0)
        l.addWidget(QLabel('地图格与出生位置；*表示多波共用'))
        self.grid=BattleGrid();l.addWidget(self.grid)
        right=QWidget();r=QVBoxLayout(right);r.setContentsMargins(0,0,0,0)
        self.map_caption=QLabel();self.map_caption.setWordWrap(True);r.addWidget(self.map_caption)
        self.original=MapOriginal();r.addWidget(self.original)
        maps.addWidget(left);maps.addWidget(right);layout.addWidget(maps,2)
        details=QSplitter(Qt.Orientation.Horizontal)
        self.spawn_list=QListWidget();details.addWidget(self.spawn_list)
        self.spawn_detail=QPlainTextEdit();self.spawn_detail.setReadOnly(True);details.addWidget(self.spawn_detail)
        enemy_box=QWidget();enemy_layout=QVBoxLayout(enemy_box);enemy_layout.setContentsMargins(0,0,0,0)
        self.enemy_picture=SubjectPicture();enemy_layout.addWidget(self.enemy_picture)
        self.enemy_form_button=QPushButton('查看伪装与现身资料');enemy_layout.addWidget(self.enemy_form_button)
        self.enemy_form_button.hide();self.enemy_form_window=None
        self.enemy_form_button.clicked.connect(self.open_enemy_form)
        self.boss_phase_button=QPushButton('查看首领形态与转换');enemy_layout.addWidget(self.boss_phase_button)
        self.boss_phase_button.hide();self.boss_phase_window=None
        self.boss_phase_button.clicked.connect(self.open_boss_phase_reference)
        self.boss_cycle_button=QPushButton('查看交替激活与模块条件');enemy_layout.addWidget(self.boss_cycle_button)
        self.boss_cycle_button.hide();self.boss_cycle_window=None
        self.boss_cycle_button.clicked.connect(self.open_boss_cycle_reference)
        self.boss_hunt_button=QPushButton('查看卡德霍与相关敌人机制资料');enemy_layout.addWidget(self.boss_hunt_button)
        self.boss_hunt_button.hide();self.boss_hunt_window=None
        self.boss_hunt_button.clicked.connect(self.open_boss_hunt_reference)
        self.enemy_detail=QPlainTextEdit();self.enemy_detail.setReadOnly(True);enemy_layout.addWidget(self.enemy_detail,1)
        details.addWidget(enemy_box)
        details.setSizes([260,340,380]);layout.addWidget(details,3)
        self.source_label=QLabel('');self.source_label.setWordWrap(True);layout.addWidget(self.source_label)
        self.stage_combo.currentIndexChanged.connect(self._stage_changed)
        self.wave_combo.currentIndexChanged.connect(self.render_rows)
        self.enemy_combo.currentIndexChanged.connect(self.render_rows)
        self.include_branches.toggled.connect(self.render_rows)
        self.technical.toggled.connect(self._technical_changed)
        self.spawn_list.currentItemChanged.connect(self._spawn_selected)
        self.grid.cellSelected.connect(self._cell_selected)
        self.original.cellSelected.connect(self._cell_selected)
        self.occurrence.valueChanged.connect(self._occurrence_changed)
        self.reward_combo.currentIndexChanged.connect(self._reward_selected)
        self.reward_summary.clicked.connect(self._reward_summary)
        self.branch_toggle.toggled.connect(self.branch_panel.setVisible)
        self.branch_toggle.toggled.connect(self._refresh_branch_positions)
        self.branch_panel.positionsChanged.connect(self._refresh_branch_positions)
        self.branch_panel.referenceCellSelected.connect(self._branch_reference_cell)
        self.technical.toggled.connect(self.branch_panel.set_technical)
        self._load_stage(None)

    def set_stage(self,stage_id):
        if not self.stage_choices.select_value(stage_id,emit=False):self.stage_choices.select_value(None,emit=False)
        sid=self.stage_combo.currentData()
        if self.current_stage!=sid:self._load_stage(sid)

    def _stage_changed(self):
        sid=self.stage_combo.currentData();self._load_stage(sid);self.stageSelected.emit(sid)

    def set_context(self,context):
        # Context changes enemy attributes, not static scheduling or geometry.
        context=copy.deepcopy(context or {})
        if context==self.context:return
        self.context=context
        if self._shown_enemy:
            self._render_enemy(*self._shown_enemy[1:],preserve=True)

    def _refresh_entry_reference(self):
        try:packet=entry_packet(self.current_stage)
        except (OSError,ValueError,KeyError,TypeError):packet=None
        self.entry_reference_button.setVisible(packet is not None)
        self.entry_reference_button.setEnabled(bool(packet and packet['result'].get('status')=='documented_reference'))
        if self.entry_reference_window:self.entry_reference_window.set_stage(self.current_stage)

    def open_entry_references(self):
        try:packet=entry_packet(self.current_stage)
        except (OSError,ValueError,KeyError,TypeError):packet=None
        if not packet or packet['result'].get('status')!='documented_reference':
            if self.entry_reference_window:self.entry_reference_window.set_stage(None)
            return False
        if self.entry_reference_window is None:
            self.entry_reference_window=BattleEntryReferencePanel(self)
            self.entry_reference_window.eventReferenceSelected.connect(self._request_entry_event)
        self.entry_reference_window.set_stage(self.current_stage)
        self.entry_reference_window.show();self.entry_reference_window.raise_();self.entry_reference_window.activateWindow()
        return True

    def _request_entry_event(self,token):
        from .battle_event_references import resolve_stage_event_reference
        row=resolve_stage_event_reference(self.current_stage,token)
        if not row:return False
        self.entryEventSelected.emit(copy.deepcopy(row['token']));return True

    def _clear_candidate_preview(self):
        if self.candidate_preview_window is not None:
            self.candidate_preview_window.set_stage(None)
            self.candidate_preview_window.close()
            self.candidate_preview_window.deleteLater()
            self.candidate_preview_window=None
        self._candidate_preview_token=None

    def _current_main_spawn_id(self):
        item=self.spawn_list.currentItem()
        row=item.data(Qt.ItemDataRole.UserRole) if item else None
        return row['id'] if row and not row.get('branch') and self._rows_stage==self.current_stage else None

    def _refresh_spawn_candidates(self):
        packet=spawn_candidates.stage_reference(self.current_stage)
        known=bool(packet and packet.get('source_valid'))
        self.spawn_candidates_button.setVisible(packet is not None)
        self.spawn_candidates_button.setEnabled(known)
        identity=self._current_main_spawn_id()
        linked=known and identity is not None and any(m['action_id']==identity
            for r in packet['groups']+packet['packages'] for m in r['members'])
        self.spawn_group_button.setVisible(packet is not None)
        self.spawn_group_button.setEnabled(bool(linked))
        self.spawn_group_button.setToolTip('这里查看常规出怪资料；特殊出怪请使用上方的条件与位置入口。')
        if self.spawn_candidates_window is not None:
            origin=self._current_main_spawn_id() if self._spawn_candidates_current else None
            if self._spawn_candidates_current and origin is None:
                self.spawn_candidates_window.set_reference(None)
            else:
                self.spawn_candidates_window.set_reference(self.current_stage,origin,
                    scope_key=(self.current_stage,'current' if self._spawn_candidates_current else 'all',origin))
        if self._candidate_preview_token is not None and not spawn_candidates.resolve_reference(self._candidate_preview_token):
            self._clear_candidate_preview()

    def open_spawn_candidates(self,origin_action_id=None):
        packet=(spawn_candidates.stage_reference(self.current_stage) if origin_action_id is None else
                spawn_candidates.action_reference(self.current_stage,origin_action_id))
        if not packet or not packet.get('source_valid') or not (packet['groups'] or packet['packages']):
            if self.spawn_candidates_window is not None:self.spawn_candidates_window.set_reference(None)
            return False
        self._spawn_candidates_current=origin_action_id is not None
        if self.spawn_candidates_window is None:
            self.spawn_candidates_window=SpawnCandidatesPanel(self)
            self.spawn_candidates_window.spawnReferenceSelected.connect(self._request_spawn_candidate)
            self.spawn_candidates_window.sourceInvalidated.connect(self._clear_candidate_preview)
        self.spawn_candidates_window.set_reference(self.current_stage,origin_action_id,
            scope_key=(self.current_stage,'current' if self._spawn_candidates_current else 'all',origin_action_id))
        self.spawn_candidates_window.show();self.spawn_candidates_window.raise_();self.spawn_candidates_window.activateWindow()
        return True

    def open_current_spawn_candidates(self):
        identity=self._current_main_spawn_id()
        return False if identity is None else self.open_spawn_candidates(identity)

    def _request_spawn_candidate(self,token):
        panel=self.spawn_candidates_window
        if panel is None or not isinstance(token,dict) or not panel.packet or not panel.packet.get('source_valid'):
            return False
        if token.get('stage_id')!=self.current_stage or token.get('origin_action_id')!=panel.origin_action_id or (
                token.get('scope_key')!=panel.packet.get('scope_key')):return False
        if self._spawn_candidates_current and self._current_main_spawn_id()!=token.get('origin_action_id'):return False
        relation,member=panel._selected()
        if not relation or not member or not panel.open_spawn_button.isEnabled() or member.get('token')!=token:
            return False
        resolved=spawn_candidates.resolve_reference(token)
        if not resolved:
            self._refresh_spawn_candidates()
            return False
        reference=resolved['member'].get('spawn_reference')
        if not reference or reference['stage_id']!=self.current_stage:return False
        rows=spawn_rows(self.current_stage,include_branches=False)
        matching=[row for row in rows if row['id']==reference['action_id'] and
            row['action']==resolved['member']['raw_action'] and row['action']['key']==reference['enemy_id']]
        if len(matching)!=1:return False
        self._clear_candidate_preview()
        # A separate fixed preview keeps the reader's original filters, cell,
        # enemy, ordinal and text untouched. It never controls a game instance.
        preview=BattlePreviewPanel(self);preview.setWindowFlag(Qt.WindowType.Window,True)
        preview.setWindowTitle('候选条目的独立战斗预览')
        preview.resize(1050,720);preview.set_context(copy.deepcopy(self.context));preview.set_stage(self.current_stage)
        index=next((i for i,row in enumerate(preview.rows) if row['id']==reference['action_id']),None)
        if index is None:
            preview.close();preview.deleteLater();return False
        preview.spawn_list.setCurrentRow(index);preview._spawn_selected(preview.spawn_list.currentItem())
        preview._render_enemy(reference['enemy_id'],reference['level'])
        self.candidate_preview_window=preview;self._candidate_preview_token=copy.deepcopy(token)
        preview.show();preview.raise_();preview.activateWindow();return True

    def open_highland_top(self):
        if not self.current_stage:return
        if self.highland_top_dialog is None:
            self.highland_top_dialog=HighlandTopDialog(self.current_stage,self)
        else:self.highland_top_dialog.set_stage(self.current_stage)
        self.highland_top_dialog.show();self.highland_top_dialog.raise_()

    def open_duel_rewards(self):
        if not is_duel_stage(self.current_stage):return
        if self.duel_reward_window is None:
            self.duel_reward_window=DuelRewardPanel(self)
            self.duel_reward_window.stageSelected.connect(self.stageSelected.emit)
        # Enemy calculation context does not establish an event entry or victory.
        self.duel_reward_window.set_reference(self.current_stage)
        self.duel_reward_window.show();self.duel_reward_window.raise_()

    def _technical_changed(self):
        """Change detail presentation without rebuilding choices or occurrences."""
        self.source_label.setVisible(self.technical.isChecked())
        if self._branch_marker and self._detail_key and self._detail_key[1]=='branch_reference':
            self._branch_reference_cell(self._branch_marker,preserve=True)
            if self._shown_enemy:self._render_enemy(*self._shown_enemy[1:],preserve=False)
            return
        if self._detail_key and self._detail_key[1]=='reward':
            self._reward_selected(preserve=True)
            if self._shown_enemy:self._render_enemy(*self._shown_enemy[1:],preserve=False)
            return
        row=self.grid.selected
        if self._tile_cell:
            self._cell_selected(self._tile_cell,preserve=True)
        elif row:
            replace_text(self.spawn_detail,spawn_text(row,self.current_stage,technical=self.technical.isChecked()),preserve=False)
        if self._shown_enemy:self._render_enemy(*self._shown_enemy[1:],preserve=False)

    def _load_stage(self,sid):
        self._clear_candidate_preview()
        if self.spawn_candidates_window is not None:self.spawn_candidates_window.set_reference(None)
        self._rows_stage=None;self._shown_enemy=None;self._tile_cell=None;self._detail_key=None
        self._refresh_enemy_form()
        self._refresh_boss_phase()
        self._refresh_boss_cycle()
        self._refresh_boss_hunt()
        self._branch_marker=None;self.branch_panel.set_stage(sid)
        self.current_stage=sid;stage=battle_data()['stages'].get(sid)
        self.duel_reward_button.setVisible(is_duel_stage(sid))
        self.highland_top_button.setEnabled(bool(stage and any(t.get('tileKey')=='tile_wall' and
            t.get('heightType')=='HIGHLAND' for t in stage['tiles'])))
        self.reward_combo.blockSignals(True);self.reward_combo.clear()
        self.reward_combo.addItem('选择来源查看数量条件；实际奖励总量未知',None)
        self.reward_result=stage_reward_sources(sid) if stage else None
        for row in (self.reward_result or {}).get('rows',[]):
            cell=row['display_cell'];position=f"第{cell['row']+1}行、第{cell['col']+1}列" if cell else '分支位置未绑定'
            self.reward_combo.addItem(row['name']+' · '+position,row)
        self.reward_combo.blockSignals(False);self.reward_combo.setEnabled(bool(self.reward_result))
        self.reward_summary.setEnabled(bool(self.reward_result))
        for combo in (self.wave_combo,self.enemy_combo):combo.blockSignals(True);combo.clear()
        self.wave_combo.addItem('全部波次及分支',None)
        self.enemy_choices.set_groups(enemy_groups(stage['enemies'] if stage else [],
                   lambda e:(e['id'],e['level'])),emit=False)
        if stage:
            for wave in stage['waves']:self.wave_combo.addItem('第'+str(wave['index'])+'波',wave['index'])
        for combo in (self.wave_combo,self.enemy_combo):combo.blockSignals(False)
        self.original.set_file(DATA/stage['image']['file'] if stage else None)
        source=battle_data()['source']
        self.source_label.setText('资料版本：游戏 '+source['game_commit'][:10]+'；原图 '+source['resource_commit'][:10]+
            '。地图素材版权归鹰角网络。完整来源见条目详情及本项目验收记录。')
        self.source_label.setVisible(self.technical.isChecked())
        self.render_rows()

    def render_rows(self,*_):
        self._refresh_entry_reference()
        stage=battle_data()['stages'].get(self.current_stage)
        same_stage=self._rows_stage==self.current_stage
        branch_marker=copy.deepcopy(self._branch_marker) if same_stage else None
        selected_reward=copy.deepcopy(self.reward_combo.currentData()) if same_stage else None
        reward_summary_selected=same_stage and self._detail_key==(self.current_stage,'reward',None)
        item=self.spawn_list.currentItem()
        previous_id=item.data(Qt.ItemDataRole.UserRole)['id'] if same_stage and item else None
        ordinal=self.occurrence.value();scroll=self.spawn_list.verticalScrollBar().value()
        tile=copy.deepcopy(self._tile_cell) if same_stage else None
        self._rows_stage=self.current_stage
        self.spawn_list.blockSignals(True);self.spawn_list.clear()
        selected_enemy=self.enemy_combo.currentData();enemy_id=selected_enemy[0] if selected_enemy else None
        self.rows=spawn_rows(self.current_stage,self.wave_combo.currentData(),enemy_id,self.include_branches.isChecked())
        if self.enemy_choices.branch.currentData()!=OVERVIEW:
            allowed={value[0] for _,value,_ in self.enemy_choices.entries()}
            self.rows=[row for row in self.rows if row['action']['key'] in allowed]
        names={e['id']:e['name'] for e in stage['enemies']} if stage else {}
        for row in self.rows:
            a=row['action'];flags=[]
            if row['branch']:flags.append('条件分支')
            if a.get('hiddenGroup'):flags.append('隐藏组')
            if a.get('randomSpawnGroupKey') or a.get('randomSpawnGroupPackKey'):flags.append('随机候选')
            prefix=(f"第{row['wave']}波·第{row['fragment']}段" if row['wave'] else f"条件出怪·第{row['phase']}阶段")
            seq=local_sequence(row,limit=0)
            local=('本段出场计划 +'+format(seq['first_offset'],'g')+'～'+format(seq['last_offset'],'g')+'秒'
                if seq['first_offset'] is not None else '局部时间未知')
            item=QListWidgetItem(prefix+' '+names.get(a['key'],'名称待确认的敌人')+' ×'+str(a['count'])+
                ' · '+local+(' ['+'/'.join(flags)+']' if flags else ''))
            item.setData(Qt.ItemDataRole.UserRole,row);self.spawn_list.addItem(item)
        self.spawn_list.blockSignals(False);self.grid.set_reference(stage,self.rows)
        self.original.set_reference(stage,self.rows)
        self.map_caption.setText('固定原图 · 近似地面位置；连线只表示资料中的途经点，不代表实际行进路径'
            if self.original.projection else '原图位置尚未核对：请看左侧方格图；不会把未核对的位置画到原图上。')
        direct=getattr(self.original.projection,'mapping_mode',None)=='direct_verified_centers'
        if direct:
            count=len(self.original.projection.points)
            self.map_caption.setText(f'固定原图 · {count}个已核对的地面格中心（近似参考）\n'
                '只显示这些格的点；其他位置尚未核对，不据此猜测或延伸路线。'
                '标记为资料中的近似地面位置，实际出生位置可能有偏移。')
        elif self.original.projection:
            data=projection_data();binding=data['stages'][stage['id']]
            columns={check['col'] for check in data['calibrations'][binding['calibration']]['checks']}
            coverage=(f'独立地标仅覆盖第{int(next(iter(columns)))+1}列，其他列为外推参考。'
                      if len(columns)==1 else '独立地标仅核验记录的部分地面格，其余位置为外推参考。')
            self.map_caption.setText(self.map_caption.text()+'\n'+coverage+'高台、入口立体图标及实际出生偏移未核验。')
        if stage:
            self.summary.setText(stage['name']+'：'+str(len(self.rows))+'组出怪资料（含可能不出现的候选，并非实际敌人数）。'
                '点选一组或地图标记，可查看敌人、出生位置与出现条件。+秒数从本段出场计划启动时计算，既不是开战倒计时，也不是从首只敌人出现计时；计划启动前的等待另列。实际出场时刻与行进路径尚未确认。')
            from .stage_floor_reference import sixth_floor_reference,floor_reference_text
            reference=sixth_floor_reference(stage['id'],stage)
            if reference:self.summary.setText(self.summary.text()+'\n'+floor_reference_text(reference))
        else:self.summary.setText('读取节点详情后自动跟随已确认关卡；也可手动选择关卡进行局外预览。')
        retained=next((i for i,row in enumerate(self.rows) if row['id']==previous_id),None)
        if self.rows:
            self.spawn_list.blockSignals(True)
            self.spawn_list.setCurrentRow(retained if retained is not None else 0)
            self.spawn_list.blockSignals(False)
        if selected_reward or reward_summary_selected or branch_marker:
            pass  # Keep the reward detail key/text while rebuilding static map rows.
        elif tile:
            self._cell_selected(tile,preserve=True)
        elif self.rows:
            self._spawn_selected(self.spawn_list.currentItem(),preserve=retained is not None)
            if retained is not None:
                self.occurrence.setValue(min(ordinal,self.occurrence.maximum()))
        else:
            self._tile_cell=None;self._detail_key=None;self._shown_enemy=None
            self.spawn_detail.clear();self.enemy_detail.clear();self.occurrence_bar.hide()
            self.enemy_picture.set_subject(None,None,'')
            self.occurrence_label.clear()
            if selected_enemy and stage:self._render_enemy(*selected_enemy)
        if retained is not None or tile:self.spawn_list.verticalScrollBar().setValue(scroll)
        if selected_reward:
            index=next((i for i in range(self.reward_combo.count())
                if (self.reward_combo.itemData(i) or {}).get('id')==selected_reward['id']),0)
            self.reward_combo.blockSignals(True);self.reward_combo.setCurrentIndex(index);self.reward_combo.blockSignals(False)
            self._reward_selected(preserve=True)
        elif reward_summary_selected:self._reward_selected(preserve=True)
        elif branch_marker:self._branch_reference_cell(branch_marker,preserve=True)
        self._refresh_branch_positions()
        self._refresh_spawn_candidates()

        self._refresh_enemy_form()
        self._refresh_boss_phase()
        self._refresh_boss_cycle()
        self._refresh_boss_hunt()

    def _refresh_branch_positions(self,*_):
        from .branch_position_overview import branch_position_overview
        rows=[]
        if (self.current_stage and self.branch_toggle.isChecked() and self.branch_panel.overlay.isChecked()
                and self.branch_panel.stage_id==self.current_stage):
            result=branch_position_overview(self.current_stage,self.branch_panel.branch.currentData(),self.branch_panel.phase.currentData())
            rows=copy.deepcopy(result['rows'])
        self.grid.branch_positions=copy.deepcopy(rows);self.original.branch_positions=copy.deepcopy(rows)
        self.grid.update();self.original.update()

    def _branch_reference_cell(self,reference,*,preserve=False):
        stage=battle_data()['stages'].get(self.current_stage)
        if not isinstance(reference,dict) or not stage or reference.get('stage_id')!=self.current_stage:return
        if reference.get('level_sha256')!=stage['level_source']['sha256']:return
        allowed=[r for row in (self.branch_panel.result or {}).get('rows',[]) for r in row['map_references']]
        if reference not in allowed:return
        cell=reference.get('cell')
        if not isinstance(cell,dict) or type(cell.get('row')) is not int or type(cell.get('col')) is not int:return
        if not (0<=cell['row']<len(stage['map']) and 0<=cell['col']<len(stage['map'][0])):return
        self._branch_marker=copy.deepcopy(reference);self._clear_reward_selection()
        self._tile_cell=None;self.grid.selected=None;self.original.selected=None;self.occurrence_bar.hide()
        self.grid.reference_cell=copy.deepcopy(cell);self.original.reference_cell=copy.deepcopy(cell)
        self.grid.update();self.original.update();key=(self.current_stage,'branch_reference',reference['reference_id'])
        label='来源预置声明' if reference['source_kind']=='producer_declaration' else '唯一alias对应激活对象'
        text=f"条件分支资料格：{reference['name']}\n{label} · 第{cell['row']+1}行、第{cell['col']+1}列\n仅标记原件位置；实际触发、出生及路线仍未核验。"
        if self.technical.isChecked():text+='\n原件位置：'+reference['source_selector']
        replace_text(self.spawn_detail,text,preserve=preserve and self._detail_key==key);self._detail_key=key

    def _reward_summary(self):
        self.reward_combo.blockSignals(True);self.reward_combo.setCurrentIndex(0);self.reward_combo.blockSignals(False)
        self._reward_selected()

    def _reward_selected(self,*_,preserve=False):
        self._branch_marker=None
        row=self.reward_combo.currentData()
        self.grid.reference_cell=copy.deepcopy(row['display_cell']) if row else None
        self.original.reference_cell=copy.deepcopy(row['display_cell']) if row else None
        self.grid.update();self.original.update()
        if self.reward_result is None:return
        self._tile_cell=None;self.grid.selected=None;self.original.selected=None;self.occurrence_bar.hide()
        key=(self.current_stage,'reward',row['id'] if row else None)
        replace_text(self.spawn_detail,reward_source_text(self.reward_result,row,technical=self.technical.isChecked()),
            preserve=preserve and self._detail_key==key)
        self._detail_key=key
        if row and row['kind']=='rare_enemy_action':
            self._render_enemy(row['entity_id'],preserve=preserve)

    def _clear_reward_selection(self):
        self.reward_combo.blockSignals(True);self.reward_combo.setCurrentIndex(0);self.reward_combo.blockSignals(False)
        self.grid.reference_cell=None;self.original.reference_cell=None

    def _render_enemy(self,enemy_id,level=None,*,preserve=False):
        stage=battle_data()['stages'].get(self.current_stage)
        if not stage:
            self._shown_enemy=None;self._refresh_enemy_form();self._refresh_boss_phase();self._refresh_boss_cycle();self._refresh_boss_hunt();return
        choices=[e for e in stage['enemies'] if e['id']==enemy_id and (level is None or e['level']==level)]
        if len(choices)!=1:
            self._shown_enemy=None
            self.enemy_picture.set_subject(None,None,'')
            replace_text(self.enemy_detail,'敌人引用等级不能唯一确认，请通过敌人筛选选择。',preserve=False)
            self._refresh_enemy_form();self._refresh_boss_phase();self._refresh_boss_cycle();self._refresh_boss_hunt();return
        key=(self.current_stage,enemy_id,choices[0]['level'])
        keep=preserve and self._shown_enemy==key;self._shown_enemy=key
        entry=choices[0]
        self.enemy_picture.set_subject('enemy',enemy_id,entry['name']+' · '+ENEMY_TIERS.get(entry['level_type'],'类别未确认'))
        text=enemy_text(enemy_preview(self.current_stage,enemy_id,choices[0]['level'],self.context),technical=self.technical.isChecked())
        replace_text(self.enemy_detail,text,preserve=keep)
        self._refresh_enemy_form()
        self._refresh_boss_phase()
        self._refresh_boss_cycle()
        self._refresh_boss_hunt()

    def _refresh_enemy_form(self):
        from .enemy_form_view import target_identity
        from .enemy_form_reference import disguise_reference
        key=self._shown_enemy
        target=target_identity(key)
        result=disguise_reference(*key)if target else None
        valid=bool(result and result.get('source_valid')is True)
        self.enemy_form_button.setVisible(target);self.enemy_form_button.setEnabled(valid)
        if self.enemy_form_window is not None:
            if not valid:
                self.enemy_form_window.clear_reference((result or {}).get('notice','已更换敌人，旧伪装与现身资料已清除。'))
            elif self.enemy_form_window.identity==key:
                self.enemy_form_window.set_reference(key,result)
            else:
                self.enemy_form_window.clear_reference('已更换敌人；请手动打开当前敌人的伪装与现身资料。')
        return result

    def open_enemy_form(self):
        result=self._refresh_enemy_form()
        if not result or result.get('source_valid')is not True:return False
        from .enemy_form_view import EnemyFormReferencePanel
        if self.enemy_form_window is None:self.enemy_form_window=EnemyFormReferencePanel(self)
        if not self.enemy_form_window.set_reference(self._shown_enemy,result):return False
        self.enemy_form_window.show();self.enemy_form_window.raise_()
        return True

    def _refresh_boss_phase(self):
        from .boss_phase_view import target_identity
        from .boss_phase_reference import phase_reference
        key=self._shown_enemy;target=target_identity(key)
        try:result=phase_reference(*key)if target else None
        except (OSError,ValueError,TypeError,KeyError):result=None
        valid=bool(result and result.get('source_valid')is True and result.get('status')=='documented_reference')
        self.boss_phase_button.setVisible(target);self.boss_phase_button.setEnabled(valid)
        if self.boss_phase_window is not None:
            window=self.boss_phase_window
            if not valid:
                window.clear_reference('当前首领或资料无法核对，旧形态与转换内容已清除。')
            elif(window.identity==key and window.result is not None
                    and window.result.get('source_identity')==result.get('source_identity')):
                window.set_reference(key,result)
            else:
                window.clear_reference('当前阅读身份或资料已变化；请手动打开首领形态与转换资料。')
        return result

    def open_boss_phase_reference(self):
        result=self._refresh_boss_phase()
        if not result or result.get('source_valid')is not True:return False
        from .boss_phase_view import BossPhaseReferencePanel
        if self.boss_phase_window is None:self.boss_phase_window=BossPhaseReferencePanel(self)
        if not self.boss_phase_window.set_reference(self._shown_enemy,result):return False
        self.boss_phase_window.show();self.boss_phase_window.raise_()
        return True

    def _refresh_boss_cycle(self):
        from .boss_cycle_view import target_identity
        from .boss_cycle_reference import cycle_reference
        key=self._shown_enemy;target=target_identity(key)
        try:result=cycle_reference(*key)if target else None
        except (OSError,ValueError,TypeError,KeyError):result=None
        valid=bool(result and result.get('source_valid')is True and result.get('status')=='documented_reference')
        self.boss_cycle_button.setVisible(target);self.boss_cycle_button.setEnabled(valid)
        if self.boss_cycle_window is not None:
            window=self.boss_cycle_window
            if not valid:
                window.clear_reference('当前首领或资料无法核对，旧交替激活与模块条件内容已清除。')
            elif(window.identity==key and window.result is not None
                    and window.result.get('source_identity')==result.get('source_identity')):
                window.set_reference(key,result)
            else:
                window.clear_reference('当前阅读身份或资料已变化；请手动打开首领交替激活与模块条件资料。')
        return result

    def open_boss_cycle_reference(self):
        result=self._refresh_boss_cycle()
        if not result or result.get('source_valid')is not True:return False
        from .boss_cycle_view import BossCycleReferencePanel
        if self.boss_cycle_window is None:self.boss_cycle_window=BossCycleReferencePanel(self)
        if not self.boss_cycle_window.set_reference(self._shown_enemy,result):return False
        self.boss_cycle_window.show();self.boss_cycle_window.raise_()
        return True

    def _refresh_boss_hunt(self):
        from .boss_hunt_view import target_identity
        from .boss_hunt_reference import hunt_reference
        key=self._shown_enemy;target=target_identity(key)
        try:result=hunt_reference(*key)if target else None
        except (OSError,ValueError,TypeError,KeyError):result=None
        valid=bool(result and result.get('source_valid')is True and result.get('status')=='documented_reference')
        self.boss_hunt_button.setVisible(target);self.boss_hunt_button.setEnabled(valid)
        if self.boss_hunt_window is not None:
            window=self.boss_hunt_window
            if not valid:
                window.clear_reference('当前敌人或资料无法核对，旧机制资料与图片已清除。')
            elif(window.identity==key and window.result is not None
                    and window.result.get('source_identity')==result.get('source_identity')):
                window.set_reference(key,result)
            else:
                window.clear_reference('当前敌人或资料已变化；请重新手动打开机制资料。')
        return result

    def open_boss_hunt_reference(self):
        result=self._refresh_boss_hunt()
        if not result or result.get('source_valid')is not True:return False
        from .boss_hunt_view import BossHuntReferencePanel
        if self.boss_hunt_window is None:self.boss_hunt_window=BossHuntReferencePanel(self)
        if not self.boss_hunt_window.set_reference(self._shown_enemy,result):return False
        self.boss_hunt_window.show();self.boss_hunt_window.raise_()
        return True

    def _spawn_selected(self,item,*_,preserve=False):
        if not item:return
        self._branch_marker=None
        self._clear_reward_selection()
        self._tile_cell=None
        row=item.data(Qt.ItemDataRole.UserRole);self.grid.selected=row;self.grid.update()
        self.original.selected=row;self.original.update()
        seq=local_sequence(row,limit=0);valid=not seq['pending'] and bool(seq['count'])
        self.occurrence.blockSignals(True);self.occurrence.setRange(1,seq['count'] if valid else 1)
        self.occurrence.setValue(1);self.occurrence.blockSignals(False)
        self.occurrence_bar.setVisible(valid);self._occurrence_changed(1)
        key=(self.current_stage,'row',row['id'])
        replace_text(self.spawn_detail,spawn_text(row,self.current_stage,technical=self.technical.isChecked()),preserve=preserve and self._detail_key==key)
        self._detail_key=key
        selected=self.enemy_combo.currentData()
        self._render_enemy(row['action']['key'],selected[1] if selected else None,preserve=preserve)
        self._refresh_spawn_candidates()

    def _occurrence_changed(self,ordinal):
        row=self.grid.selected
        if not row:return
        self.grid.selected_ordinal=ordinal;self.grid.update()
        self.original.selected_ordinal=ordinal;self.original.update()
        offset=ordinal_offset(row,ordinal)
        anchor='本分支阶段的出场计划启动' if row.get('branch') else '本段出场计划启动'
        self.occurrence_label.setText('以'+anchor+'为0秒：+'+format(offset,'g')+'秒；绝对时刻/可见入场未核验。'
            if offset is not None else '此条目局部时间无法确认。')

    def _cell_selected(self,cell,*,preserve=False):
        self._branch_marker=None
        self._clear_reward_selection()
        matching=[i for i,row in enumerate(self.rows) if row['route']['start']==cell]
        if matching:
            # The list preserves every same-cell action for independent selection.
            self.spawn_list.setCurrentRow(matching[0]);self._spawn_selected(self.spawn_list.currentItem())
            self.spawn_detail.appendPlainText('\n本格共有'+str(len(matching))+'个资料条目，详细选择请用左侧列表。')
            return
        stage=battle_data()['stages'].get(self.current_stage)
        if not stage:return
        tile=stage['tiles'][stage['map'][cell['row']][cell['col']]]
        self._tile_cell=copy.deepcopy(cell)
        self.occurrence_bar.hide();self.grid.selected=None;self.grid.reference_cell=copy.deepcopy(cell);self.grid.update()
        self.original.reference_cell=copy.deepcopy(cell) if self.original.cell_center(cell) is not None else None
        self.original.selected=None;self.original.selected_ordinal=1;self.original.update()
        key=(self.current_stage,'tile',cell['row'],cell['col'])
        from .player_tile_information import tile_information_text
        replace_text(self.spawn_detail,tile_information_text(cell,tile,
            mapped=self.original.reference_cell is not None,technical=self.technical.isChecked()),
            preserve=preserve and self._detail_key==key)
        self._detail_key=key
