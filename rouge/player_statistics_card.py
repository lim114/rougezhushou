"""Explicit local presentation of qualified statistics; no private identifiers."""
# Header/grouped-metric layout adapted from FrostN0v0/nonebot-plugin-skland
# 29a0e428c7df4a522cdcdb784784d514e2f86f04, rogue.html.jinja2.
# Copyright (c) 2025 FrostN0v0; MIT, see licenses/skland-card-MIT.txt.
from copy import deepcopy
from pathlib import Path
from PySide6.QtCore import Qt,QBuffer,QByteArray,QIODevice
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QCheckBox,QPushButton,QScrollArea,QTabWidget,QFileDialog,QMessageBox,QComboBox

def card_lines(result,scope,selected=None):
    if not isinstance(result,dict):return None
    selected={'gold','parts_count','relic_count','relic'}if selected is None else set(selected)
    lines=['我的黑流树海读取记录',scope,f'本机归档样本：{result["archive_count"]}局（不是通关场数）']
    for key,row in result['measures'].items():
        if key not in selected:continue
        value=f'{row["mean"]:.2f}'if row['mean']is not None else'未知'
        lines+=[row['name']+'\n平均：'+value+f'；有效{row["sample_count"]}局，缺失{row["missing_count"]}局']
    relic=result.get('relic')
    if relic is not None and 'relic'in selected:
        value=f'{relic["fraction"]:.1%}'if relic['fraction']is not None else'未知'
        lines+=[relic['name']+' · 归档时持有率：'+value+f'\n持有{relic["held_count"]}局 / 完整清单{relic["sample_count"]}局；另有{relic["excluded_incomplete_count"]}局未计入。']
    lines+=['只统计归档前最近一次已读值；未读不按0计算。', '没有完整胜负与结算依据；持有率不是掉落概率。', '游戏版本未完整记录，个人选择和读取缺失可能造成偏差。', '在本机生成；只有点击保存图片才导出，不会自动上传。']
    return lines

class StatisticsCard(QWidget):
    def __init__(self,lines,result,selected,parent=None):
        super().__init__(parent);self.lines=list(lines);self.setFixedWidth(600);self.setObjectName('personalStatisticsCard')
        self.setStyleSheet('''#personalStatisticsCard{background:#1e1e20;border:0;}
            #personalStatisticsCard QLabel{color:#e9e9ec;background:transparent;border:0;font-size:11px;}
            #personalStatisticsCard #cardTitle{font-size:19px;font-weight:bold;color:white;}
            #personalStatisticsCard #cardBadge{background:#2b3f42;color:#9be3e9;font-size:22px;font-weight:bold;}
            #personalStatisticsCard #cardMetricName{color:#9be3e9;font-size:11px;}
            #personalStatisticsCard #cardMetricValue{color:white;font-size:26px;font-weight:bold;}
            #personalStatisticsCard #cardSampleNote,#personalStatisticsCard #cardLimits{color:#b9bdc3;font-size:10px;}''')
        layout=QVBoxLayout(self);layout.setContentsMargins(24,20,24,18);layout.setSpacing(16)
        header=QHBoxLayout();badge=QLabel('黑流');badge.setObjectName('cardBadge');badge.setAlignment(Qt.AlignmentFlag.AlignCenter);badge.setFixedSize(64,64);header.addWidget(badge)
        titles=QVBoxLayout();header.addLayout(titles,1)
        for index,text in enumerate(lines[:3]):
            label=QLabel(text);label.setTextFormat(Qt.TextFormat.PlainText);label.setWordWrap(True)
            if index==0:label.setObjectName('cardTitle')
            titles.addWidget(label)
        layout.addLayout(header);metrics=QGridLayout();metrics.setHorizontalSpacing(18);metrics.setVerticalSpacing(10);layout.addLayout(metrics);column=0
        for key,row in result['measures'].items():
            if key not in selected:continue
            block=QVBoxLayout();block.setSpacing(2);metrics.addLayout(block,0,column);metrics.setColumnStretch(column,1);column+=1
            value=f'{row["mean"]:.2f}'if row['mean']is not None else'未知'
            for name,text in [('cardMetricName',row['name'].removeprefix('归档前最近读到的')),('cardMetricValue',value),('cardSampleNote',f'有效{row["sample_count"]}局 · 缺失{row["missing_count"]}局')]:
                label=QLabel(text);label.setTextFormat(Qt.TextFormat.PlainText);label.setObjectName(name);label.setWordWrap(True);block.addWidget(label)
        relic=result.get('relic')
        if relic is not None and 'relic'in selected:
            from .expansion_reference import packet
            from .view_catalog import relic_icon
            data=packet();item=data['current']['details']['items'].get(relic['id'],{})if data is not None else{};artwork=relic_icon(item.get('iconId')or'')
            row=QHBoxLayout();picture=QLabel();picture.setAccessibleName('统计条目图标：'+relic['name']);picture.setFixedSize(44,44)
            if artwork.isNull():picture.setText('无图')
            else:picture.setPixmap(artwork.pixmap(44,44))
            row.addWidget(picture);block=QVBoxLayout();block.setSpacing(2);row.addLayout(block,1)
            for name,text in [('cardMetricName',relic['name']+' · 归档时持有率'),('cardSampleNote',f'持有{relic["held_count"]}局 / 完整清单{relic["sample_count"]}局；另{relic["excluded_incomplete_count"]}局未计入')]:
                label=QLabel(text);label.setTextFormat(Qt.TextFormat.PlainText);label.setObjectName(name);label.setWordWrap(True);block.addWidget(label)
            value=QLabel(f'{relic["fraction"]:.1%}'if relic['fraction']is not None else'未知');value.setObjectName('cardMetricValue');row.addWidget(value);layout.addLayout(row)
        if column==0 and not(relic is not None and 'relic'in selected):
            label=QLabel('本次未选择展示指标，可返回勾选。');label.setWordWrap(True);layout.addWidget(label)
        limits=QLabel(' '.join(lines[-4:]));limits.setObjectName('cardLimits');limits.setWordWrap(True);layout.addWidget(limits)
        self.adjustSize();self.resize(self.width(),self.heightForWidth(self.width()))
    def png(self):
        raw=QByteArray();buffer=QBuffer(raw);buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not self.grab().save(buffer,'PNG'):raise ValueError('展示卡图片未能生成，未写入文件。')
        return bytes(raw)

class CardControls:
    def __init__(self,page,body):
        self.page=page;self.key=None;self.card=None;self.viewer=None
        body.removeWidget(page.detail);self.pages=QTabWidget();self.pages.addTab(page.detail,'数值与适用范围');body.insertWidget(body.count()-1,self.pages,1)
        from .flow_layout import FlowLayout
        widget=QWidget();layout=QVBoxLayout(widget);self.fields={};bar=FlowLayout();bar.setSpacing(6)
        for key,label in [('gold','源石锭'),('parts_count','零件'),('relic_count','藏品栏总数'),('relic','所选藏品持有率')]:
            box=QCheckBox(label);box.setChecked(True);self.fields[key]=box;bar.addWidget(box);box.toggled.connect(self.invalidate)
        layout.addLayout(bar);period=QHBoxLayout();period.addWidget(QLabel('卡片样本'));self.period=QComboBox()
        for count in(0,20,50,100):self.period.addItem('全部已归档记录'if count==0 else f'筛选后最近{count}局归档',count)
        self.period.setToolTip('只改变展示卡；在当前保密等级、分队筛选中，按本机归档时间取最近记录，不是通关时间。');period.addWidget(self.period,1);self.period.currentIndexChanged.connect(self.invalidate);layout.addLayout(period)
        actions=QHBoxLayout();self.build=QPushButton('生成本机展示卡');self.view=QPushButton('放大查看');self.view.setEnabled(False);self.save=QPushButton('保存为图片');self.save.setEnabled(False);actions.addWidget(self.build);actions.addWidget(self.view);actions.addWidget(self.save);layout.addLayout(actions)
        self.status=QLabel('只整理当前筛选后的统计，不含账户名、聊天、截图、对局身份或私人路径。');self.status.setWordWrap(True);layout.addWidget(self.status)
        from .reference_image import ReferenceImage
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.preview=ReferenceImage('勾选指标后生成展示卡');self.preview.setAccessibleName('本机统计展示卡缩放预览');self.scroll.setWidget(self.preview);layout.addWidget(self.scroll,1);self.pages.addTab(widget,'本机展示卡');self.build.clicked.connect(self.generate);self.view.clicked.connect(self.open_viewer);self.save.clicked.connect(self.export)
    def scope(self):
        from .player_cohort_ui import filter_text
        count=self.period.currentData()
        return filter_text(self.page)+' · '+('全部归档'if count==0 else f'最多最近{count}局归档（按本机归档时间）')
    def sync(self):
        key=repr((self.page.result,self.scope()))
        if key!=self.key:self.key=key;self.invalidate()
    def invalidate(self,*_):
        self.preview.clear();self.preview.setAccessibleDescription('')
        if self.viewer is not None:self.viewer.close();self.viewer.deleteLater();self.viewer=None
        if self.card is not None:self.card.deleteLater()
        self.card=None;self.view.setEnabled(False);self.save.setEnabled(False);self.status.setText('统计或展示内容已变化；请重新生成，避免保存过时结果。')
    def generate(self):
        if self.page.result is None:self.invalidate();self.status.setText('本机历史暂不可用，未用旧结果或0局生成图片。');return False
        from .player_cohort_ui import selected_records
        from .player_personal_statistics import statistics
        records=selected_records(self.page);count=self.period.currentData();result=statistics(records[:count]if count else records,self.page.relic.currentData());selected=[key for key,box in self.fields.items()if box.isChecked()];lines=card_lines(result,self.scope(),selected)
        self.invalidate();self.card=StatisticsCard(lines,result,selected,self.page);self.card.hide();self.preview.set_data(self.card.png(),'展示卡图片暂不可读');self.preview.setAccessibleDescription('\n'.join(lines));self.key=repr((self.page.result,self.scope()));self.view.setEnabled(True);self.save.setEnabled(True);self.status.setText('已在本机生成。可放大查看；保存图片保留完整尺寸，不会上传。');return True
    def open_viewer(self):
        if self.card is None:return False
        if self.viewer is None:
            from .player_compact import ToolPopover
            from .reference_image import ReferenceImage
            picture=ReferenceImage();picture.set_data(self.card.png(),'展示卡图片暂不可读');picture.setAccessibleDescription('\n'.join(self.card.lines))
            style='#statisticsCardViewer{background:#1e1e20;border-color:#1e1e20;}'
            self.viewer=ToolPopover('统计展示卡',picture,self.page,theme='dark',extra_style=style,object_name='statisticsCardViewer');self.viewer.resize(self.card.width()+32,self.card.height()+72)
        self.viewer.show();self.viewer.raise_();return True
    def export(self):
        card=self.card
        if card is None:return False
        name,_=QFileDialog.getSaveFileName(self.page,'保存本机统计展示卡','黑流树海读取记录.png','PNG图片 (*.png)',options=QFileDialog.Option.DontConfirmOverwrite)
        if not name:return False
        if card is not self.card or self.page.result is None:self.status.setText('统计在选择位置期间发生变化，请重新生成。');return False
        target=Path(name);overwrite=False
        if target.exists()or target.is_symlink():
            answer=QMessageBox.question(self.page,'已有同名图片','是否用当前展示卡替换所选文件？',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
            if answer!=QMessageBox.StandardButton.Yes:return False
            overwrite=True
        if card is not self.card or self.page.result is None:return False
        try:
            from .player_note_export import publish_bytes
            result=publish_bytes(card.png(),target,overwrite=overwrite,suffixes=('.png',))
        except(OSError,ValueError)as error:
            from .player_file_messages import file_issue
            self.status.setText('图片未保存：'+file_issue(error));self.status.setToolTip(str(error));return False
        self.status.setText('图片已保存到所选本机位置。'+(result['warning']or''));return True

