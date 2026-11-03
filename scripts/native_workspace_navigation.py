"""Click the actual two-level player navigation in native acceptance scripts."""
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest


def click_reader(workspace,page,gui):
    target=workspace.aliases.get(page,page)
    group=workspace.groups[workspace.pages[target][0]]
    bar=workspace.tabBar();index=workspace.indexOf(group)
    assert index>=0
    QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center())
    gui.processEvents()
    bar=group.tabBar();index=group.indexOf(target)
    assert index>=0
    QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center())
    gui.processEvents()
    return workspace.currentWidget()is page and page.isVisible()
