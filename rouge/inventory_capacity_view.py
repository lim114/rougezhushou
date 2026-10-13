"""Independent inventory/occupancy and hypothetical cleanup workspace."""
from copy import deepcopy
import html
import json
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QPlainTextEdit,QTextBrowser,QSplitter)
from .inventory_capacity import inventory_capacity_plan,public_capacity_payload


def render_capacity_result(result):
    esc = lambda value: html.escape(str(value))
    state_text = lambda state: ('声明超载：来源容量条件阻断（含追猎），实际未知' if state['declared_overloaded'] is True else
        '容量条件不阻断；其它资格仍未知' if state['declared_overloaded'] is False else '容量状态未知')
    value = lambda number: '未知' if number is None else str(number)
    rows = [('独立初始快照',result['initial'])]
    for row in result['proposals']:
        rows.extend([(row['id']+'：假设丢弃后',row['after_discard']),
            (row['id']+'：假设领取后',row['after_receive'])])
    output = ['<h2>声明容量与行动条件</h2><table border="1" cellpadding="5"><tr><th>情形</th><th>占用/容量</th><th>容量差额（负为不足）</th><th>已知占用下界</th><th>行动条件</th></tr>']
    for label,state in rows:
        output.append('<tr><td>'+esc(label)+'</td><td>'+esc(value(state['declared_occupied']))+'/'+
            esc(value(state['capacity']))+'</td><td>'+esc(value(state['free_units']))+'</td><td>'+str(state['known_occupied_lower_bound'])+'</td><td>'+esc(state_text(state))+'</td></tr>')
    output.append('</table><h3>保留偏好下的最少释放实例</h3>')
    releases = [('初始快照',result['minimum_release'])]+[(row['id'],row['minimum_release']) for row in result['proposals']]
    for label,release in releases:
        output.append('<p>'+esc(label)+'：最少实例 '+esc(value(release['minimum_discarded_instances']))+
            '；全部候选已列 '+('是' if release['complete_candidate_enumeration'] else '否')+'</p>')
        for row in release['candidate_discard_sets']:
            output.append('<p>实例 '+esc('、'.join(row['instance_ids']) or '无需释放')+'；释放声明单位 '+str(row['released_units'])+'</p>')
    output.append('<h3>来源与边界</h3><p>'+esc(result['source_rule'])+'</p>')
    output.extend('<p>'+esc(note)+'</p>' for note in result['notes'])
    return ''.join(output)


class InventoryCapacityPanel(QWidget):
    resultReady=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self._result=None;self._host_context=None
        layout=QVBoxLayout(self)
        notice=QLabel('独立声明总容量、逐件占用单位和清单完整性；比较保留、丢弃与领取方案。未知填null，没有自动读取或改写本局。')
        notice.setWordWrap(True);layout.addWidget(notice)
        bar=QHBoxLayout();self.load_example=QPushButton('载入占用算术演示');self.run_button=QPushButton('复核容量与整理方案')
        bar.addWidget(self.load_example);bar.addWidget(self.run_button);layout.addLayout(bar)
        split=QSplitter();self.editor=QPlainTextEdit();self.editor.setAccessibleName('独立库存容量与假设方案JSON')
        self.result_view=QTextBrowser();self.result_view.setOpenExternalLinks(False)
        split.addWidget(self.editor);split.addWidget(self.result_view);layout.addWidget(split,1)
        self.status=QLabel('等待独立声明');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.load_example.clicked.connect(self._load);self.run_button.clicked.connect(self.calculate)
        self.editor.textChanged.connect(self._edited);self._load()
    def _load(self):
        self.editor.setPlainText(json.dumps(public_capacity_payload(),ensure_ascii=False,indent=2))
    def _edited(self):
        self._result=None;self.status.setText('声明已变化；请重新复核，旧结果仅供阅读。')
    def calculate(self):
        try:
            def finite(value):raise ValueError('不接受非有限数值：'+value)
            def unique(pairs):
                output={}
                for key,value in pairs:
                    if key in output:raise ValueError('重复声明键：'+key)
                    output[key]=value
                return output
            payload=json.loads(self.editor.toPlainText(),parse_constant=finite,object_pairs_hook=unique)
            if type(payload) is not dict:raise ValueError('输入需要对象。')
            self._result=inventory_capacity_plan(**payload)
        except (ValueError,TypeError,KeyError) as error:
            self._result=None;self.result_view.clear();self.status.setText('无法复核：'+str(error));return
        self.result_view.setHtml(render_capacity_result(self._result));self.status.setText('已复核声明容量条件；未执行丢弃或领取。')
        self.resultReady.emit(deepcopy(self._result))
    def result_snapshot(self):return deepcopy(self._result)
    def set_context(self,context):
        # The host can identify its current context, never fill inventory/capacity.
        self._host_context=deepcopy(context)
