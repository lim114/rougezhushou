from PySide6.QtWidgets import QComboBox,QHBoxLayout
from .player_statistics_cohorts import cohort_options,select_cohort,cohort_note

def attach_filters(page,body):
    bar=QHBoxLayout();page.grade_filter=QComboBox();page.squad_filter=QComboBox();bar.addWidget(page.grade_filter);bar.addWidget(page.squad_filter);body.insertLayout(1,bar)
    page.grade_filter.addItem('全部保密等级',None);page.squad_filter.addItem('全部分队类型',None)
    page.grade_filter.currentIndexChanged.connect(page.render);page.squad_filter.currentIndexChanged.connect(page.render)

def refresh_filters(page):
    options=cohort_options(page.records)
    for combo,key,title in [(page.grade_filter,'difficulty','全部保密等级'),(page.squad_filter,'squad','全部分队类型')]:
        old,label=combo.currentData(),combo.currentText();combo.blockSignals(True);combo.clear();combo.addItem(title,None)
        for identity,name in options[key]:combo.addItem(name,identity)
        index=combo.findData(old)
        if index<0 and old is not None:combo.addItem(label+'（当前无样本）',old);index=combo.count()-1
        combo.setCurrentIndex(max(0,index));combo.blockSignals(False)

def selected_records(page):return select_cohort(page.records,difficulty=page.grade_filter.currentData(),squad=page.squad_filter.currentData())
def filter_text(page):return page.grade_filter.currentText()+' · '+page.squad_filter.currentText()
def filter_notes(page):return filter_text(page)+'\n'+cohort_note(page.grade_filter.currentData(),page.squad_filter.currentData())

