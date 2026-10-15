"""Manual source-only one-hop reading, with no game or run-state actions."""
import json
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QPushButton,QTabWidget,QPlainTextEdit)
from . import resting_corner_results as results
from .player_node_information import _plain
from .ui_state import replace_text

EVENT='community_group_023'
_KEEP_CHOICE=object()
NOTICE=('这里只是在查阅选项资料，尚未确认本局已进行。各项是不同的可能后续；'
        '奖励写在后续场景的按钮中，需要另行选择，不能把各项相加。')
RESOURCES={'hope':'希望','shield':'护盾','gold':'源石锭'}


def reward_text(button):
    amount=button.get('quantity_reference');resource=button.get('resource')
    if type(amount) is int and resource in RESOURCES:return f'{amount}{RESOURCES[resource]}'
    if type(amount) is int and button.get('category_text'):
        return f'{amount}件{_plain(button["category_text"])}（具体物品与完整候选范围未知）'
    return _plain(button.get('description')) or '数量未确认'


def card_text(card):
    lines=[f'【正在查阅】场景{card["scene_number"]} · {_plain(card["choice_title"])}',NOTICE,'']
    if card.get('conflict_notice'):
        lines+=['【资料数量对不上】',_plain(card['conflict_notice']),
                '无法确认是漏项还是说明不准确；这里只列资料已写出的后续。','']
    else:
        lines+=[f'资料明列{card["listed_branch_count"]}项后续；当前完整候选范围仍未确认。','']
    for number,branch in enumerate(card['branches'],1):
        lines += [f'{number}. {_plain(branch["label"])} → 后续场景{branch["target_scene_number"]}']
        for button in branch['future_buttons']:
            lines += [f'   后续按钮“{_plain(button["title"])}”写明：{reward_text(button)}。']
            if not button.get('game_choice_ids'):
                lines += ['   这段后续尚未与原游戏入口对应；可阅读资料，当前能否进入或领取未知。']
        lines += ['   本局是否看到、按钮是否可选、是否领取：均未确认。','']
    lines+=['可在下方选一项，手动阅读该后续的完整场景。']
    return '\n'.join(lines)


def scene_text(scene):
    lines=[f'【后续场景{scene["scene_number"]} · 社区资料原文】',
        '这是手动打开的资料页，不表示已进入游戏中的该场景。','',_plain(scene['description'])]
    for note in scene.get('edesc_texts',[]):lines+=['说明：'+_plain(note)]
    for choice in scene['choices']:
        lines+=['',f'按钮：{_plain(choice.get("title"))}',_plain(choice.get('description'))]
        if choice.get('conditional'):lines+=['原注：'+_plain(choice['conditional'])]
    lines+=['','本页按钮仅供阅读；当前是否出现、可选与实际领取仍未知。']
    return '\n'.join(lines)


class RestingCornerPanel(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('安眠一隅 · 可能的后续与场景原文')
        self.setModal(False);self.resize(900,660)
        self.event_id=None;self.scope_key=None;self.packet=None
        self._view_key=None;self._scene_identity=None
        layout=QVBoxLayout(self)
        self.notice=QLabel(NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.choice=QComboBox();self.choice.setAccessibleName('正在查阅的安眠资料选项')
        self.choice.setPlaceholderText('请选择要查阅的资料选项');layout.addWidget(self.choice)
        self.reading_tabs=QTabWidget();layout.addWidget(self.reading_tabs,1)
        self.result_text=QPlainTextEdit();self.scene_text=QPlainTextEdit();self.source_text=QPlainTextEdit()
        for widget,label in ((self.result_text,'可能的后续'),(self.scene_text,'所选场景原文'),(self.source_text,'资料与依据')):
            widget.setReadOnly(True);widget.setAccessibleName('安眠一隅 · '+label)
            self.reading_tabs.addTab(widget,label)
        row=QHBoxLayout();self.branch=QComboBox();self.branch.setAccessibleName('手动阅读的后续场景')
        self.branch.setPlaceholderText('请选择要阅读的后续')
        self.open_scene_button=QPushButton('阅读所选场景原文');self.open_scene_button.setEnabled(False)
        row.addWidget(self.branch,1);row.addWidget(self.open_scene_button);layout.addLayout(row)
        self.choice.currentIndexChanged.connect(self.refresh_reference)
        self.branch.currentIndexChanged.connect(self.refresh_reference)
        self.open_scene_button.clicked.connect(self.open_selected_scene)
        self.refresh_reference()

    @staticmethod
    def _populate(control,rows,selected):
        control.blockSignals(True)
        try:
            control.clear()
            for label,key in rows:control.addItem(label,key)
            index=control.findData(selected) if type(selected) is str else -1
            control.setCurrentIndex(index)
        finally:control.blockSignals(False)

    def _invalidate(self,message):
        self.packet=None;self._view_key=None;self._scene_identity=None
        self._populate(self.choice,[],None);self._populate(self.branch,[],None)
        self.open_scene_button.setEnabled(False)
        for widget in (self.result_text,self.scene_text,self.source_text):
            replace_text(widget,message,preserve=False)

    def set_reference(self,event_id,choice_key=_KEEP_CHOICE,scope_key=None):
        scope=(event_id,scope_key)
        if scope!=(self.event_id,self.scope_key):
            self._invalidate('尚未选择要查阅的资料。')
            self.reading_tabs.setCurrentIndex(0)
        self.event_id,self.scope_key=scope
        self.refresh_reference()
        if choice_key is not _KEEP_CHOICE:
            index=self.choice.findData(choice_key) if type(choice_key) is str else -1
            self.choice.setCurrentIndex(index)

    def refresh_reference(self,*_):
        selected=self.choice.currentData();branch_key=self.branch.currentData()
        try:packet=results.resting_result_cards(self.event_id)
        except (ValueError,KeyError,TypeError,OSError):packet=None
        if not packet or packet.get('status')!='documented_reference':
            self._invalidate('后续资料尚未通过核对；旧选择已清除，请稍后重新选择。' if self.event_id==EVENT
                             else '当前未查阅安眠一隅；请选择相应事件后打开。')
            return
        self.packet=packet
        self._populate(self.choice,[(f'场景{card["scene_number"]} · {_plain(card["choice_title"])}',card['choice_key'])
                                    for card in packet['cards']],selected)
        card=next((row for row in packet['cards'] if row['choice_key']==self.choice.currentData()),None)
        key=(self.event_id,self.scope_key,card['choice_key']) if card else None
        same=key is not None and key==self._view_key
        if not same:branch_key=None;self._scene_identity=None
        self._populate(self.branch,[(f'{_plain(row["label"])} → 场景{row["target_scene_number"]}',row['branch_id'])
                                    for row in (card or {}).get('branches',[])],branch_key)
        branch=next((row for row in (card or {}).get('branches',[]) if row['branch_id']==self.branch.currentData()),None)
        self.open_scene_button.setEnabled(branch is not None)
        replace_text(self.result_text,card_text(card) if card else '请选择要查阅的资料选项；尚未认定本局进行了任何选择。',preserve=same)
        replace_text(self.source_text,json.dumps({'sources':packet.get('sources'), 'selected_reference':card,
            'notice':'仅一跳社区资料关联；不补原入口、不更改资格、库存或本局。'},ensure_ascii=False,indent=2),preserve=same)
        current_identity=(key,branch['branch_id'],branch['target_scene_key']) if branch else None
        if self._scene_identity!=current_identity or current_identity is None:
            self._scene_identity=None
            replace_text(self.scene_text,'尚未手动打开后续场景；请选择下方一项并点击阅读。',preserve=False)
        self._view_key=key

    def open_selected_scene(self):
        choice_key=self.choice.currentData();branch_key=self.branch.currentData()
        if type(choice_key) is not str or type(branch_key) is not str:return
        try:result=results.resting_result_scene(self.event_id,choice_key,branch_key)
        except (ValueError,KeyError,TypeError,OSError):result=None
        if (not result or result.get('status')!='documented_reference'
                or result.get('choice_key')!=choice_key or result.get('branch_id')!=branch_key):
            self._invalidate('所选后续资料未能重新核对；旧内容已清除，请重新选择。');return
        self.refresh_reference()
        if self.choice.currentData()!=choice_key or self.branch.currentData()!=branch_key:return
        card=next((row for row in self.packet['cards'] if row['choice_key']==choice_key),None)
        branch=next((row for row in (card or {}).get('branches',[]) if row['branch_id']==branch_key),None)
        scene=result.get('scene')
        if not branch or not scene or scene.get('key')!=branch['target_scene_key']:
            self._invalidate('所选后续与场景原文未能对应；旧内容已清除。');return
        identity=(self._view_key,branch_key,scene['key'])
        replace_text(self.scene_text,scene_text(scene),preserve=self._scene_identity==identity)
        self._scene_identity=identity
        self.reading_tabs.setCurrentWidget(self.scene_text)
