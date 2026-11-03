import json
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication,QDialog,QHBoxLayout,QLabel,QLineEdit,QListWidget,
    QListWidgetItem,QPlainTextEdit,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout)
from .scenario_library import ScenarioLibrary,check_json_structure
from .scenario_comparison import compare_saved_scenarios,format_scenario_comparison
from .manual_scenario import parse_preview_object


class ScenarioLibraryDialog(QDialog):
    def __init__(self,scenario,path,parent=None):
        super().__init__(parent);self.library=ScenarioLibrary(path);self.result=None
        self.opening_scenario=deepcopy(scenario)
        self.setWindowTitle('局外情景库 · 保存与条件对照');self.resize(1150,830)
        layout=QVBoxLayout(self)
        label=QLabel('本窗口编辑局外条件，保存后可在以后重新对照。载入进入下方编辑器；主计算、账户与本局各自保留。最多保存20项，每次对照最多选择6项。')
        label.setWordWrap(True);layout.addWidget(label)
        self.persistence=QLabel();self.persistence.setWordWrap(True);layout.addWidget(self.persistence)
        top=QHBoxLayout();self.records=QListWidget();self.records.setMaximumHeight(160)
        self.records.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection);top.addWidget(self.records,1)
        self.editor=QPlainTextEdit();self.editor.setMaximumHeight(200)
        self.editor.setPlainText(json.dumps(scenario,ensure_ascii=False,indent=2));top.addWidget(self.editor,2);layout.addLayout(top)
        actions=QHBoxLayout();self.name=QLineEdit();self.name.setPlaceholderText('新情景名称（同名不会覆盖）');actions.addWidget(self.name,1)
        self.save_button=QPushButton('保存为新情景');self.load_button=QPushButton('载入选中情景到局外编辑器')
        self.delete_button=QPushButton('删除选中的一个局外情景');self.opening_button=QPushButton('打开本窗口初始条件')
        for button in (self.save_button,self.load_button,self.delete_button,self.opening_button):actions.addWidget(button)
        layout.addLayout(actions)
        comparisons=QHBoxLayout();self.compare_button=QPushButton('当前编辑条件与选中情景对照');self.copy_button=QPushButton('复制对照与字段差异')
        comparisons.addWidget(self.compare_button);comparisons.addWidget(self.copy_button);layout.addLayout(comparisons)
        self.fields=('name','operator_name','skill','status','window_seconds','window_damage','delta_window_damage','window_healing','delta_window_healing')
        self.table=QTableWidget(0,len(self.fields));self.table.setHorizontalHeaderLabels(['情景','干员','技能','状态','窗口/秒','窗口伤害','伤害差值','窗口治疗','治疗差值'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);layout.addWidget(self.table,1)
        self.notice=QPlainTextEdit();self.notice.setReadOnly(True);layout.addWidget(self.notice,1)
        self.editor.textChanged.connect(self.invalidate);self.records.itemSelectionChanged.connect(self.selection_changed)
        self.save_button.clicked.connect(self.save_new);self.load_button.clicked.connect(self.load_selected)
        self.delete_button.clicked.connect(self.delete_selected);self.compare_button.clicked.connect(self.compare)
        self.opening_button.clicked.connect(lambda:self.editor.setPlainText(json.dumps(self.opening_scenario,ensure_ascii=False,indent=2)))
        self.copy_button.clicked.connect(lambda:QApplication.clipboard().setText(format_scenario_comparison(self.result)) if self.result else None)
        self.populate();self.compare()

    def populate(self,selected=None):
        self.records.blockSignals(True);self.records.clear()
        for record in self.library.records():
            stamp=datetime.fromisoformat(record['saved_at']).astimezone(timezone(timedelta(hours=8)))
            item=QListWidgetItem(record['name']+' · '+stamp.strftime('%m-%d %H:%M')+' 北京时间')
            item.setData(Qt.ItemDataRole.UserRole,record['id']);self.records.addItem(item)
            if record['id']==selected:item.setSelected(True)
        self.records.blockSignals(False);self.persistence.setText(self.library.persistence_notice());self.selection_changed()

    def invalidate(self):
        self.result=None;self.copy_button.setEnabled(False);self.table.setRowCount(0)
        self.notice.setPlainText('条件或选择已修改，请重新对照。')

    def selection_changed(self):
        single=len(self.records.selectedItems())==1
        self.load_button.setEnabled(single);self.delete_button.setEnabled(single);self.invalidate()

    def editor_scenario(self):
        try: scenario=parse_preview_object(self.editor.toPlainText(),'局外情景')
        except RecursionError: raise ValueError('局外情景JSON层级过深。') from None
        check_json_structure(scenario);return scenario

    def selected_identity(self):
        items=self.records.selectedItems()
        if len(items)!=1:raise ValueError('请选择一个已保存的局外情景。')
        return items[0].data(Qt.ItemDataRole.UserRole)

    def save_new(self):
        try:identity=self.library.save_new(self.name.text(),self.editor_scenario())
        except (ValueError,KeyError,TypeError) as error:self.notice.setPlainText(str(error));return
        self.name.clear();self.populate(identity);self.notice.setPlainText('新情景已加入列表。'+self.library.persistence_notice())

    def load_selected(self):
        try:record=self.library.get(self.selected_identity())
        except ValueError as error:self.notice.setPlainText(str(error));return
        self.editor.setPlainText(json.dumps(record['scenario'],ensure_ascii=False,indent=2));self.name.clear()
        self.notice.setPlainText('已载入局外编辑器：'+record['name']+'。请重新对照。')

    def delete_selected(self):
        try:self.library.delete(self.selected_identity())
        except ValueError as error:self.notice.setPlainText(str(error));return
        self.populate();self.notice.setPlainText('已从本窗口列表移除选中情景。'+self.library.persistence_notice())

    def compare(self):
        self.invalidate()
        try:
            records=[self.library.get(item.data(Qt.ItemDataRole.UserRole)) for item in self.records.selectedItems()]
            result=compare_saved_scenarios(self.editor_scenario(),records)
        except (ValueError,KeyError,TypeError) as error:self.notice.setPlainText(str(error));return
        self.result=result;self.table.setRowCount(len(result['rows']))
        for i,row in enumerate(result['rows']):
            for j,key in enumerate(self.fields):
                value=row[key];text='未知' if value is None else format(value,'.8g') if type(value) in (int,float) else str(value)
                if row.get(key+'_applicable') is False:text='不适用'
                self.table.setItem(i,j,QTableWidgetItem(text))
        self.table.resizeColumnsToContents();self.notice.setPlainText(format_scenario_comparison(result));self.copy_button.setEnabled(True)
