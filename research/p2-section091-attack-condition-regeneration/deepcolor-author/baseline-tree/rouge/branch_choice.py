"""A selectable category branch and its own filtered item choices."""
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget,QHBoxLayout,QComboBox

OVERVIEW='__overview__'


class BranchChoice(QWidget):
    def __init__(self,combo,groups,*,overview_label,placeholder=None,overview=None,empty_label='此分支暂无条目',notify_unchanged=False,branch_icons=None):
        super().__init__()
        self.combo=combo;self.groups=[];self.overview=overview
        self.overview_label=overview_label;self.placeholder=placeholder;self.empty_label=empty_label
        self.notify_unchanged=notify_unchanged
        self.branch_icons=branch_icons or {}
        self.branch=QComboBox();self.branch.setAccessibleName(overview_label+'；选择分类分支')
        self.branch.setIconSize(QSize(26,26))
        self.branch.setMinimumContentsLength(7)
        self.branch.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        layout=QHBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.branch);layout.addWidget(combo,1)
        combo.setIconSize(QSize(28,28));combo.setMaxVisibleItems(24)
        self.set_groups(groups,emit=False)
        self.branch.currentIndexChanged.connect(self._branch_changed)

    def entries(self,branch=None):
        key=self.branch.currentData() if branch is None else branch
        if key==OVERVIEW:
            items=[item for _,items in self.groups for item in items]
            return items if self.overview is None else [item for item in items if item[1] in self.overview]
        return next((items for name,items in self.groups if name==key),[])

    def _rebuild(self,preferred,*,emit=True,force=False):
        previous=self.combo.currentData();blocked=self.combo.blockSignals(True)
        self.combo.clear();items=self.entries()
        if self.placeholder is not None:self.combo.addItem(self.placeholder,None)
        for title,value,icon in items:self.combo.addItem(icon,title,value)
        if not items and self.placeholder is None:self.combo.addItem(self.empty_label,None)
        index=next((i for i in range(self.combo.count()) if self.combo.itemData(i)==preferred),-1)
        self.combo.setCurrentIndex(index if index>=0 else 0 if self.combo.count() else -1)
        self.combo.setEnabled(bool(items))
        self.combo.blockSignals(blocked)
        if emit and not blocked and (force or self.combo.currentData()!=previous):
            self.combo.currentIndexChanged.emit(self.combo.currentIndex())

    def set_groups(self,groups,*,emit=True):
        previous=self.combo.currentData();key=self.branch.currentData()
        self.groups=[(name,list(items)) for name,items in groups if items]
        blocked=self.branch.blockSignals(True);self.branch.clear()
        self.branch.addItem(self.overview_label,OVERVIEW)
        for name,_ in self.groups:
            icon=self.branch_icons.get(name)
            if icon is not None:self.branch.addItem(icon,name,name)
            else:self.branch.addItem(name,name)
        index=self.branch.findData(key);self.branch.setCurrentIndex(max(0,index))
        self.branch.blockSignals(blocked);self._rebuild(previous,emit=emit,force=True)

    def set_overview(self,values,*,emit=True):
        values=tuple(values)
        if values==self.overview:return False
        self.overview=values
        if self.branch.currentData()==OVERVIEW:self._rebuild(self.combo.currentData(),emit=emit,force=True)
        return True

    def select_branch(self,key):
        index=self.branch.findData(key)
        if index<0:return False
        self.branch.setCurrentIndex(index);return True

    def select_value(self,value,*,emit=True):
        """Reveal an externally selected identity without treating lookup as selection."""
        index=self.combo.findData(value)
        if index>=0:
            if emit:self.combo.setCurrentIndex(index)
            else:
                blocked=self.combo.blockSignals(True);self.combo.setCurrentIndex(index);self.combo.blockSignals(blocked)
            return True
        key=next((name for name,items in self.groups if any(v==value for _,v,_ in items)),None)
        if key is None:return False
        blocked=self.branch.blockSignals(True);self.branch.setCurrentIndex(self.branch.findData(key));self.branch.blockSignals(blocked)
        self._rebuild(value,emit=emit,force=True);return True

    def _branch_changed(self):
        self._rebuild(self.combo.currentData(),force=self.notify_unchanged)
