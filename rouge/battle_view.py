"""Scalable tile reference and a plain offline battle-preview panel."""
import copy,hashlib
from pathlib import Path
from PySide6.QtCore import Qt,QRectF,QPointF,Signal
from PySide6.QtGui import QColor,QPainter,QPen,QPixmap
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QListWidget,QListWidgetItem,QPlainTextEdit,QSplitter,QCheckBox,QSpinBox)
from .battle_preview import (DATA,battle_data,spawn_rows,enemy_preview,enemy_text,spawn_text)
from .spawn_reference import local_sequence,ordinal_offset
from .map_projection import projection_for,projection_data
from .ui_state import replace_text
from .view_catalog import stage_groups,enemy_groups,SubjectPicture,ENEMY_TIERS
from .branch_choice import BranchChoice,OVERVIEW

class BattleGrid(QWidget):
    cellSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.stage=None;self.rows=[];self.selected=None;self.selected_ordinal=1
        self.setMinimumSize(240,150)

    def set_reference(self,stage,rows):
        self.stage=stage;self.rows=rows;self.selected=None;self.update()

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
                anchor='阶段队列' if self.selected.get('branch') else '片段队列'
                painter.drawText(QRectF(8,2,max(0,self.width()-16),22),
                    Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,
                    f'第{self.selected_ordinal}次：{anchor}开始后 +{offset:g}秒（名义生成）')

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
        self.projection=None;self.image_sha256=None

    def set_file(self,path):
        try:raw=Path(path).read_bytes() if path else b''
        except OSError:raw=b''
        self.pixmap=QPixmap()
        if raw:self.pixmap.loadFromData(raw)
        self.image_sha256=hashlib.sha256(raw).hexdigest() if not self.pixmap.isNull() else None
        self.stage=None;self.rows=[];self.selected=None;self.projection=None;self.selected_ordinal=1
        self.update()

    def set_reference(self,stage,rows):
        self.stage=stage;self.rows=rows;self.selected=None;self.selected_ordinal=1
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
        if not self.selected:return
        route=self.selected['route'];points=[self.cell_center(p) for p in route.get('points',[])]
        painter.setPen(QPen(QColor('#ffe17d'),2,Qt.PenStyle.DashLine))
        # Segments only connect source checkpoints. Teleport/disappear records
        # do not acquire a fabricated continuous route or movement ETA.
        if route.get('continuous_reference'):
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

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            cell=self.cell_at(event.position())
            if cell:self.cellSelected.emit(cell)

class BattlePreviewPanel(QWidget):
    stageSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.context={};self.current_stage=None;self.rows=[]
        self._rows_stage=None;self._shown_enemy=None;self._tile_cell=None;self._detail_key=None
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
        self.include_branches=QCheckBox('显示条件分支参考（位置未核验）');self.include_branches.setChecked(True)
        layout.addWidget(self.include_branches)
        self.technical=QCheckBox('显示技术资料（原始参数、标识与来源）');layout.addWidget(self.technical)
        self.occurrence_bar=QWidget();occurrence_layout=QHBoxLayout(self.occurrence_bar)
        occurrence_layout.setContentsMargins(0,0,0,0)
        occurrence_layout.addWidget(QLabel('条目内生成序号'))
        self.occurrence=QSpinBox();self.occurrence.setRange(1,1)
        occurrence_layout.addWidget(self.occurrence)
        self.occurrence_label=QLabel();occurrence_layout.addWidget(self.occurrence_label,1)
        layout.addWidget(self.occurrence_bar);self.occurrence_bar.hide()
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
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

    def _technical_changed(self):
        """Change detail presentation without rebuilding choices or occurrences."""
        row=self.grid.selected
        if self._tile_cell:
            self._cell_selected(self._tile_cell,preserve=True)
        elif row:
            replace_text(self.spawn_detail,spawn_text(row,self.current_stage,technical=self.technical.isChecked()),preserve=False)
        if self._shown_enemy:self._render_enemy(*self._shown_enemy[1:],preserve=False)

    def _load_stage(self,sid):
        self._rows_stage=None;self._shown_enemy=None;self._tile_cell=None;self._detail_key=None
        self.current_stage=sid;stage=battle_data()['stages'].get(sid)
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
        self.render_rows()

    def render_rows(self,*_):
        stage=battle_data()['stages'].get(self.current_stage)
        same_stage=self._rows_stage==self.current_stage
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
            prefix='波'+str(row['wave']) if row['wave'] else '分支'
            seq=local_sequence(row,limit=0)
            local=('队列后 +'+format(seq['first_offset'],'g')+'～'+format(seq['last_offset'],'g')+'秒'
                if seq['first_offset'] is not None else '局部时间未知')
            item=QListWidgetItem(prefix+' '+names.get(a['key'],a['key'])+' ×'+str(a['count'])+
                ' · '+local+(' ['+'/'.join(flags)+']' if flags else ''))
            item.setData(Qt.ItemDataRole.UserRole,row);self.spawn_list.addItem(item)
        self.spawn_list.blockSignals(False);self.grid.set_reference(stage,self.rows)
        self.original.set_reference(stage,self.rows)
        self.map_caption.setText('固定原图 · 地面参考标记（近似校准；检查点连线非实际寻路）'
            if self.original.projection else '固定原图参考（本图坐标尚未校准或版本不匹配）')
        if self.original.projection:
            data=projection_data();binding=data['stages'][stage['id']]
            columns={check['col'] for check in data['calibrations'][binding['calibration']]['checks']}
            coverage=(f'独立地标仅覆盖第{int(next(iter(columns)))+1}列，其他列为外推参考。'
                      if len(columns)==1 else '独立地标仅核验记录的部分地面格，其余位置为外推参考。')
            self.map_caption.setText(self.map_caption.text()+'\n'+coverage+'高台、入口立体图标及实际出生偏移未核验。')
        if stage:
            self.summary.setText(stage['name']+'：'+str(len(self.rows))+'个调度条目（含候选，并非实际敌人数）。'
                '点击出生标记或条目查看位置、局部计划和条件；绝对时刻、分支触发和实际寻路尚未核验。')
        else:self.summary.setText('读取节点详情后自动跟随已确认关卡；也可手动选择关卡进行局外预览。')
        retained=next((i for i,row in enumerate(self.rows) if row['id']==previous_id),None)
        if self.rows:
            self.spawn_list.blockSignals(True)
            self.spawn_list.setCurrentRow(retained if retained is not None else 0)
            self.spawn_list.blockSignals(False)
        if tile:
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

    def _render_enemy(self,enemy_id,level=None,*,preserve=False):
        stage=battle_data()['stages'].get(self.current_stage)
        if not stage:return
        choices=[e for e in stage['enemies'] if e['id']==enemy_id and (level is None or e['level']==level)]
        if len(choices)!=1:
            self._shown_enemy=None
            self.enemy_picture.set_subject(None,None,'')
            replace_text(self.enemy_detail,'敌人引用等级不能唯一确认，请通过敌人筛选选择。',preserve=False);return
        key=(self.current_stage,enemy_id,choices[0]['level'])
        keep=preserve and self._shown_enemy==key;self._shown_enemy=key
        entry=choices[0]
        self.enemy_picture.set_subject('enemy',enemy_id,entry['name']+' · '+ENEMY_TIERS.get(entry['level_type'],'类别未确认'))
        text=enemy_text(enemy_preview(self.current_stage,enemy_id,choices[0]['level'],self.context),technical=self.technical.isChecked())
        replace_text(self.enemy_detail,text,preserve=keep)

    def _spawn_selected(self,item,*_,preserve=False):
        if not item:return
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

    def _occurrence_changed(self,ordinal):
        row=self.grid.selected
        if not row:return
        self.grid.selected_ordinal=ordinal;self.grid.update()
        self.original.selected_ordinal=ordinal;self.original.update()
        offset=ordinal_offset(row,ordinal)
        anchor='所选阶段动作队列开始' if row.get('branch') else '本片段动作队列开始'
        self.occurrence_label.setText('以'+anchor+'为0秒：+'+format(offset,'g')+'秒；绝对时刻/可见入场未核验。'
            if offset is not None else '此条目局部时间无法确认。')

    def _cell_selected(self,cell,*,preserve=False):
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
        self.occurrence_bar.hide();self.grid.selected=None;self.grid.update()
        self.original.selected=None;self.original.selected_ordinal=1;self.original.update()
        key=(self.current_stage,'tile',cell['row'],cell['col'])
        replace_text(self.spawn_detail,f"格图第{cell['row']+1}行、第{cell['col']+1}列\n"+
            '地形：'+tile['tileKey']+'\n高度：'+str(tile.get('heightType'))+
            '\n可部署类型：'+str(tile.get('buildableType'))+'\n通行类型：'+str(tile.get('passableMask'))+
            '\n当前筛选下没有映射到此格的主波次出生条目。',preserve=preserve and self._detail_key==key)
        self._detail_key=key
