"""A small player navigation surface; existing readers keep their own state."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTabWidget,QDialog,QVBoxLayout

GROUPS=('本局','地图与节点','干员计算','资料查询','聊天')
PAGE_GROUP={
 '采样测试':('本局','本局信息'),'伤害测试':('干员计算','干员与技能'),
 '聊天分析':('聊天','分析对话'),'地图预览':('地图与节点','探索地图'),
 '本图节点':('地图与节点','节点详情'),'战斗计算参考':('干员计算','关卡目标'),
 '战斗预览':('地图与节点','关卡与敌人'),'节点事件':('地图与节点','事件查询'),
 '藏品与零件':('资料查询','藏品与零件'),'探索设置':('本局','分队与难度'),
 '零件箱整理':('本局','零件箱'),'长期科技':('本局','长期科技'),
}
DEVELOPER_PAGES=frozenset(('局外工具','前后校准','路线约束','居民路线','路线资源',
 '多情景路线','路线续接','攻击状态序列','时刻校准','有界校准','多记录实验','HP原值资格','藏品处理精度'))

class PlayerWorkspace(QTabWidget):
    activePageChanged=Signal(object)
    def __init__(self,parent=None,*,developer_tools=False):
        super().__init__(parent)
        self.setAccessibleName('助手主要栏目')
        self.groups={};self.pages={};self.developer_tools=developer_tools;self._last_page=None
        self.developer_dialog=QDialog(self);self.developer_dialog.setWindowTitle('开发核对工具')
        self.developer_dialog.resize(1000,760);self.developer_tabs=QTabWidget()
        QVBoxLayout(self.developer_dialog).addWidget(self.developer_tabs)
        for name in GROUPS:
            tabs=QTabWidget();tabs.setAccessibleName(name+'内容')
            self.groups[name]=tabs;super().addTab(tabs,name)
            tabs.currentChanged.connect(self._announce)
        super().currentChanged.connect(self._announce)

    def addTab(self,page,label):
        if label in DEVELOPER_PAGES:
            self.pages[page]=('developer',label)
            return self.developer_tabs.addTab(page,label)
        group,title=PAGE_GROUP.get(label,('资料查询',label))
        self.pages[page]=(group,title)
        result=self.groups[group].addTab(page,title);self._announce()
        return result

    def currentWidget(self):
        """Return the selected reader for callers that route exact content."""
        group=super().currentWidget()
        return group.currentWidget() if isinstance(group,QTabWidget) else group

    def setCurrentWidget(self,page):
        if page in self.pages:
            group,_=self.pages[page]
            if group=='developer':
                if not self.developer_tools:return False
                self.developer_tabs.setCurrentWidget(page);self.developer_dialog.show();return True
            self.groups[group].setCurrentWidget(page)
            super().setCurrentWidget(self.groups[group]);self._announce();return True
        if page in self.groups.values():
            super().setCurrentWidget(page);return True
        return False

    def _announce(self,*_):
        page=self.currentWidget()
        if page is not self._last_page:
            self._last_page=page;self.activePageChanged.emit(page)

    def close_developer_tools(self):
        self.developer_dialog.close()
