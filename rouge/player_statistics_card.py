"""Explicit local presentation of qualified statistics; no private identifiers."""
from copy import deepcopy
from pathlib import Path
from PySide6.QtCore import QBuffer,QByteArray,QIODevice
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QCheckBox,QPushButton,QScrollArea,QTabWidget,QFileDialog,QMessageBox

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
    def __init__(self,lines,parent=None):
        super().__init__(parent);self.lines=list(lines);self.setFixedWidth(560);self.setObjectName('personalStatisticsCard')
        self.setStyleSheet('#personalStatisticsCard{background:#f3f5f4;color:#25352e;border:1px solid #9eada4;border-radius:12px;} #personalStatisticsCard QLabel{color:#25352e;background:transparent;border:0;font-size:14px;}')
        layout=QVBoxLayout(self);layout.setContentsMargins(24,24,24,24);layout.setSpacing(15)
        for index,line in enumerate(lines):
            label=QLabel(line);label.setWordWrap(True)
            if index==0:label.setStyleSheet('font-size:22px;font-weight:bold;')
            layout.addWidget(label)
        self.adjustSize()
    def png(self):
        raw=QByteArray();buffer=QBuffer(raw);buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not self.grab().save(buffer,'PNG'):raise ValueError('展示卡图片未能生成，未写入文件。')
        return bytes(raw)

class CardControls:
    def __init__(self,page,body):
        self.page=page;self.key=None;self.card=None
        body.removeWidget(page.detail);self.pages=QTabWidget();self.pages.addTab(page.detail,'数值与适用范围');body.insertWidget(body.count()-1,self.pages,1)
        widget=QWidget();layout=QVBoxLayout(widget);self.fields={};bar=QHBoxLayout()
        for key,label in [('gold','源石锭'),('parts_count','零件'),('relic_count','藏品栏总数'),('relic','所选藏品持有率')]:
            box=QCheckBox(label);box.setChecked(True);self.fields[key]=box;bar.addWidget(box);box.toggled.connect(self.invalidate)
        layout.addLayout(bar);actions=QHBoxLayout();self.build=QPushButton('生成本机展示卡');self.save=QPushButton('保存为图片');self.save.setEnabled(False);actions.addWidget(self.build);actions.addWidget(self.save);layout.addLayout(actions)
        self.status=QLabel('只整理当前筛选后的统计，不含账户名、聊天、截图、对局身份或私人路径。');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(False);layout.addWidget(self.scroll,1);self.pages.addTab(widget,'本机展示卡');self.build.clicked.connect(self.generate);self.save.clicked.connect(self.export)
    def scope(self):
        from .player_cohort_ui import filter_text
        return filter_text(self.page)
    def sync(self):
        key=repr((self.page.result,self.scope()))
        if key!=self.key:self.key=key;self.invalidate()
    def invalidate(self,*_):
        old=self.scroll.takeWidget()
        if old is not None:old.deleteLater()
        self.card=None;self.save.setEnabled(False);self.status.setText('统计或展示内容已变化；请重新生成，避免保存过时结果。')
    def generate(self):
        lines=card_lines(self.page.result,self.scope(),[key for key,box in self.fields.items()if box.isChecked()])
        if lines is None:self.invalidate();self.status.setText('本机历史暂不可用，未用旧结果或0局生成图片。');return False
        self.invalidate();self.card=StatisticsCard(lines);self.scroll.setWidget(self.card);self.save.setEnabled(True);self.status.setText('已在本机生成。可自行保存图片；没有向网站发送记录。');return True
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

