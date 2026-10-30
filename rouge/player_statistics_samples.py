"""Inspect the local observations behind a statistic, with exact archive links."""
from copy import deepcopy
from .player_personal_statistics import unique_archives,nonnegative_integer,complete_inventory
from .record_flags import active_record

MEASURES={'gold':'归档前最近读到的源石锭','parts_count':'归档前最近读到的零件数','relic_count':'归档前最近读到的藏品栏总数（含道具）'}

def numeric_value(state,key):
    try:value=state.get('relic_count')if key=='relic_count'else state.get('resources',{}).get(key,{}).get('value')
    except(AttributeError,TypeError):value=None
    return value if nonnegative_integer(value)else None

def sample_rows(records,key,relic_id=None):
    if key not in(*MEASURES,'relic'):return []
    if key=='relic':
        from .catalog import catalog
        if relic_id not in catalog()['relics']:return []
    rows=[]
    for record in unique_archives(records):
        state=record['state']
        if key=='relic':
            included=complete_inventory(state);value=bool(active_record(state.get('relics',{}).get(relic_id,{'held':False}),'held'))if included else None
            reason='藏品清单已核对完整'if included else'清单尚未核对完整'
        else:
            value=numeric_value(state,key);included=value is not None;reason='有可核对的已读数量'if included else'该数量未读到或无法核对'
        rows.append({'id':state['id'],'state_sha256':record.get('state_sha256'),'started_at':state.get('started_at'),
            'included':included,'value':value,'reason':reason})
    return deepcopy(rows)

def sample_binding(row):
    if not isinstance(row,dict)or not isinstance(row.get('id'),str):return None
    digest=row.get('state_sha256')
    if not isinstance(digest,str)or len(digest)!=64 or any(c not in'0123456789abcdef'for c in digest):return None
    return {'id':row['id'],'state_sha256':digest}

from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QComboBox,QTableWidget,QTableWidgetItem,QAbstractItemView,QPushButton,QHeaderView

class StatisticsSamplesPage(QWidget):
    archiveRequested=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.records=[];self.rows=[];self.relic_id=None;self.signature=None
        body=QVBoxLayout(self);self.metric=QComboBox()
        for key,name in MEASURES.items():self.metric.addItem(name,key)
        self.metric.addItem('所选收藏品的归档时持有情况','relic');body.addWidget(self.metric)
        self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.table=QTableWidget(0,3);self.table.setHorizontalHeaderLabels(['对局开始时间','本项读到的内容','是否计入本项统计'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows);self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection);self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);body.addWidget(self.table,1)
        self.open_button=QPushButton('查看这局的本机归档');self.open_button.setEnabled(False);body.addWidget(self.open_button)
        self.metric.currentIndexChanged.connect(self.render);self.table.itemSelectionChanged.connect(self.selection_changed);self.open_button.clicked.connect(self.request_archive)

    def install(self,records,relic_id):
        self.records=records;self.relic_id=relic_id;self.render()

    def render(self,*_):
        from .player_replay import observation_time
        key=self.metric.currentData();rows=sample_rows(self.records,key,self.relic_id);signature=repr((key,self.relic_id,rows))
        if signature==self.signature:return
        old=self.table.currentRow();keep=sample_binding(self.rows[old])if 0<=old<len(self.rows)else None
        self.signature=signature;self.rows=rows;self.table.setRowCount(0)
        for index,row in enumerate(rows):
            self.table.insertRow(index);value=row['value']
            label=('确认持有'if value else'完整清单中未持有')if key=='relic'and value is not None else str(value)if value is not None else'未知（未计入）'
            for col,text in enumerate((observation_time(row['started_at']),label,('计入：'if row['included']else'未计入：')+row['reason'])):
                self.table.setItem(index,col,QTableWidgetItem(text))
            if keep is not None and sample_binding(row)==keep:self.table.selectRow(index)
        included=sum(row['included']for row in rows)
        self.notice.setText('请先在上方选择一件收藏品。'if key=='relic'and self.relic_id is None else f'当前筛选下共{len(rows)}局，计入{included}局，另有{len(rows)-included}局未计入。0是实际读到的数量；未知不会当作0。这里只解释归档记录，不是结算、掉落概率或分队强弱。')
        self.selection_changed()

    def selection_changed(self):
        index=self.table.currentRow();row=self.rows[index]if 0<=index<len(self.rows)else None
        self.open_button.setEnabled(sample_binding(row)is not None)

    def request_archive(self):
        index=self.table.currentRow();binding=sample_binding(self.rows[index])if 0<=index<len(self.rows)else None
        if binding is not None:self.archiveRequested.emit(binding)
