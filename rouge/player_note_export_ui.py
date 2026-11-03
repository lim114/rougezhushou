"""User-initiated local export. The caller does not autosave an edited note."""
from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QMessageBox
from .player_note_export import export_note,suggested_name

def export_editor(dialog):
    if dialog.key is None:
        dialog.status.setText('请先打开一条场景笔记，再选择导出。');return False
    original_key=dialog.key;original_text=dialog.editor.toPlainText()
    def unchanged():
        if dialog.key==original_key and dialog.editor.toPlainText()==original_text:return True
        dialog.status.setText('选择保存位置期间，笔记或文字发生了变化；请重新导出。当前编辑和已有文件均保留。');return False
    title=(dialog.content or{}).get('title')or'场景笔记'
    name,_=QFileDialog.getSaveFileName(dialog,'把当前笔记导出到本机',suggested_name(title),'Markdown笔记 (*.md);;纯文本 (*.txt)',options=QFileDialog.Option.DontConfirmOverwrite)
    if not name:return False
    if not unchanged():return False
    path=Path(name);overwrite=False
    if path.exists()or path.is_symlink():
        answer=QMessageBox.question(dialog,'已有同名文件','此位置已有文件。是否用当前笔记替换？\n未保存的编辑会原样导出，场景笔记原件不会因此改写。',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if answer!=QMessageBox.StandardButton.Yes:
            dialog.status.setText('已取消导出，已有文件没有改动。');return False
        overwrite=True
    if not unchanged():return False
    try:result=export_note(original_text,path,overwrite=overwrite)
    except(OSError,ValueError,UnicodeError)as error:
        from .player_file_messages import file_issue
        dialog.status.setText('导出未完成：'+file_issue(error)+' 当前编辑仍保留。');dialog.status.setToolTip(str(error));return False
    dialog.status.setText('当前文字已导出到所选本机位置；'+('场景笔记仍有未保存修改。'if dialog.dirty else'场景笔记没有改动。')+(result['warning']or''));return True

