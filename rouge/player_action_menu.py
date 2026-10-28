"""Consolidate related reader actions without duplicating source/eligibility logic."""
from PySide6.QtWidgets import QWidget,QHBoxLayout,QLabel,QToolButton,QMenu

class ButtonMenu(QWidget):
    def __init__(self,owner,buttons,*,title='更多查询'):
        super().__init__(owner);layout=owner.layout()
        positions=[layout.indexOf(button)for button in buttons if layout.indexOf(button)>=0]
        index=min(positions)if positions else layout.count()
        self.holder=QWidget(owner);self.holder.hide();self.actions=[]
        row=QHBoxLayout(self);row.setContentsMargins(0,0,0,0)
        self.button=QToolButton();self.button.setText(title);self.button.setAccessibleName(title)
        self.menu=QMenu(self.button);self.button.setMenu(self.menu);self.button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        row.addWidget(self.button);row.addWidget(QLabel('按需要打开相关资料，不必逐个浏览工具栏目。'),1)
        for button in buttons:
            visible=not button.isHidden();layout.removeWidget(button);button.setParent(self.holder);button.setVisible(visible)
            action=self.menu.addAction(button.text());action.triggered.connect(lambda _checked=False,b=button:b.click())
            self.actions.append((button,action))
        self.menu.aboutToShow.connect(self.sync);layout.insertWidget(index,self);self.sync()
    def sync(self):
        for button,action in self.actions:
            action.setText(button.text());action.setVisible(not button.isHidden());action.setEnabled(button.isEnabled())
    def visible_actions(self):
        self.sync();return[action for _,action in self.actions if action.isVisible()]

    def expose_original_controls(self):
        """Real original controls, only for the explicit diagnostic layout."""
        if getattr(self,'diagnostic_controls_exposed',False):return
        owner=self.parentWidget();layout=owner.layout();index=layout.indexOf(self)
        if index<0:raise ValueError('原按钮布局无法核对。')
        layout.removeWidget(self);self.hide()
        for offset,(button,_)in enumerate(self.actions):
            eligible=not button.isHidden();button.setParent(owner);layout.insertWidget(index+offset,button);button.setVisible(eligible)
        self.diagnostic_controls_exposed=True
