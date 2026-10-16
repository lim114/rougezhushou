"""Manual documented-item reading; no reward, eligibility or inventory actions."""
import json
from html import unescape
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QPushButton,QTabWidget,QPlainTextEdit)
from . import documented_choice_items as results
from .ui_state import replace_text

NOTICE='这里查阅的是资料明确写出的物品，不表示本局已选择、已领取、已持有或已生效。'


def _plain(value):return re.sub(r'<[^>]*>','',unescape(value or '')).strip()


def choice_text(reference):
    return '\n'.join(['【资料中的具体选项】',_plain(reference['choice_title']),
        _plain(reference['choice_description']),'',
        '资料写明的物品：'+_plain(reference['name'])+'（'+_plain(reference['item_kind_name'])+'）。',
        '数量、本局实际领取与当前可选状态：尚未确认。',
        '物品身份来自文献明确记载，不表示该选项的原游戏入口已经恢复。',
        '部署费用变化是物品用途，不是本节点的即时资源费用。'])


def item_text(details):
    item=details['item'];reference=details['reference']
    return '\n'.join([_plain(item['name'])+' · '+_plain(reference['item_kind_name']),NOTICE,'',
        '【用途】',_plain(item.get('usage')) or '资料未写明。','',
        '【物品说明】',_plain(item.get('description')) or '资料未写明。','',
        '【物品条目的解锁说明】',_plain(item.get('unlockCondDesc')) or '资料未写明。',
        _plain(details['unlock_notice']),'',
        '数量、实际领取和是否持有：尚未确认。',
        '上述用途是物品资料，不据此判断本局相关节点已出现或效果已生效。'])


class DocumentedChoiceItemPanel(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('节点物品 · 资料说明');self.setModal(False);self.resize(850,650)
        self.event_id=None;self.scope_key=None;self.packet=None;self._view_key=None;self._details_identity=None
        layout=QVBoxLayout(self);self.notice=QLabel(NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        row=QHBoxLayout();self.choice=QComboBox();self.choice.setAccessibleName('资料中的完整选项与具名物品')
        self.choice.setPlaceholderText('请选择资料中的物品');row.addWidget(self.choice,1)
        self.open_item_button=QPushButton('查看物品说明');self.open_item_button.setEnabled(False)
        row.addWidget(self.open_item_button);layout.addLayout(row)
        self.icon=QLabel();self.icon.setAccessibleName('所查物品的固定来源图标');self.icon.hide();layout.addWidget(self.icon)
        self.reading_tabs=QTabWidget();layout.addWidget(self.reading_tabs,1)
        self.item_text=QPlainTextEdit();self.choice_text=QPlainTextEdit();self.source_text=QPlainTextEdit()
        for widget,label in ((self.item_text,'物品说明'),(self.choice_text,'选项与适用范围'),(self.source_text,'资料与依据')):
            widget.setReadOnly(True);widget.setAccessibleName('节点物品 · '+label);self.reading_tabs.addTab(widget,label)
        self.choice.currentIndexChanged.connect(self.refresh_reference)
        self.open_item_button.clicked.connect(self.open_selected_item)
        self.refresh_reference()

    def _populate(self,rows,selected):
        self.choice.blockSignals(True)
        try:
            self.choice.clear()
            for row in rows:
                self.choice.addItem(_plain(row['choice_title'])+' · '+_plain(row['name']),row['reference_id'])
            self.choice.setCurrentIndex(self.choice.findData(selected) if type(selected) is str else -1)
        finally:self.choice.blockSignals(False)

    def _clear_icon(self):self.icon.clear();self.icon.hide()

    def _invalidate(self,message):
        self.packet=None;self._view_key=None;self._details_identity=None;self._populate([],None)
        self._clear_icon();self.open_item_button.setEnabled(False)
        for widget in (self.item_text,self.choice_text,self.source_text):replace_text(widget,message,preserve=False)

    def set_reference(self,event_id,*,scope_key=None):
        scope=(event_id,scope_key)
        if scope!=(self.event_id,self.scope_key):
            self._invalidate('尚未选择物品；请手动选择后查看资料。');self.reading_tabs.setCurrentIndex(0)
        self.event_id,self.scope_key=scope;self.refresh_reference()

    def _details(self,reference):
        return results.item_details(self.event_id,reference['scene_key'],reference['choice_key'],reference['item_id'])

    def _render_details(self,details,*,preserve):
        icon=details['icon_reference'];pixmap=QPixmap(str(results.ROOT/icon['file']))
        self.icon.clear()
        if pixmap.isNull():self.icon.setText('图标暂时不可显示。')
        else:self.icon.setPixmap(pixmap.scaledToWidth(104,Qt.TransformationMode.SmoothTransformation))
        self.icon.show();replace_text(self.item_text,item_text(details),preserve=preserve)
        replace_text(self.source_text,json.dumps(details,ensure_ascii=False,indent=2),preserve=preserve)

    def refresh_reference(self,*_):
        selected=self.choice.currentData()
        try:packet=results.event_item_references(self.event_id)
        except (OSError,ValueError,KeyError,TypeError):packet=None
        if not packet or packet.get('status')!='documented_reference':
            self._invalidate('物品资料未能核对；旧选择、图标与说明已清除，请稍后重新选择。'
                if self.event_id==results.EVENT else '当前没有可查阅的这组物品资料。');return
        self.packet=packet;self._populate(packet['items'],selected)
        reference=next((r for r in packet['items'] if r['reference_id']==self.choice.currentData()),None)
        key=(self.event_id,self.scope_key,reference['reference_id']) if reference else None
        same=key is not None and key==self._view_key
        self.open_item_button.setEnabled(reference is not None)
        replace_text(self.choice_text,choice_text(reference) if reference else '请选择物品；这里只查阅资料，不代表本局作出了选择。',preserve=same)
        if same and self._details_identity==key:
            try:details=self._details(reference)
            except (OSError,ValueError,KeyError,TypeError):details=None
            if (not details or details.get('status')!='documented_reference'
                    or details.get('reference',{}).get('reference_id')!=reference['reference_id']):
                self._invalidate('物品详情未能重新核对；旧选择、图标与说明已清除。');return
            self._render_details(details,preserve=True)
        else:
            self._details_identity=None;self._clear_icon()
            replace_text(self.item_text,'尚未手动打开物品说明；选择后请点击“查看物品说明”。',preserve=False)
            replace_text(self.source_text,json.dumps({'sources':packet['sources'],'selected_reference':reference,
                'notice':packet['notice']},ensure_ascii=False,indent=2),preserve=same)
        self._view_key=key

    def open_selected_item(self):
        selected=self.choice.currentData()
        reference=next((r for r in (self.packet or {}).get('items',[]) if r['reference_id']==selected),None)
        if type(selected) is not str or not reference:
            self._invalidate('所选物品未能对应完整选项；旧内容已清除，请重新选择。');return
        try:details=self._details(reference)
        except (OSError,ValueError,KeyError,TypeError):details=None
        if (not details or details.get('status')!='documented_reference'
                or details.get('reference',{}).get('reference_id')!=selected):
            self._invalidate('所选物品资料未能重新核对；旧选择、图标与说明已清除。');return
        self.refresh_reference()
        if self.choice.currentData()!=selected:return
        identity=(self.event_id,self.scope_key,selected)
        self._render_details(details,preserve=self._details_identity==identity)
        self._details_identity=identity;self.reading_tabs.setCurrentWidget(self.item_text)
