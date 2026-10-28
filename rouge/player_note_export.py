"""Explicit local export; never upload, never silently replace an existing file."""
from pathlib import Path
import os,re,tempfile

def suggested_name(title):
    stem=re.sub(r'[<>:"/\\|?*\x00-\x1f\ud800-\udfff]','_',str(title)).strip(' .')[:80].rstrip(' .')or'场景笔记'
    if stem.upper().split('.')[0]in{'CON','PRN','AUX','NUL',*('COM'+str(i)for i in range(1,10)),*('LPT'+str(i)for i in range(1,10))}:stem='笔记_'+stem
    return stem+'.md'

def export_note(text,target,*,overwrite=False):
    if not isinstance(text,str):raise ValueError('笔记正文需要是文本。')
    path=Path(target)
    if path.suffix.lower()not in('.md','.txt'):raise ValueError('请保存为.md或.txt笔记文件。')
    if path.is_symlink()or path.is_dir():raise ValueError('所选位置不是普通笔记文件，未写入。')
    if path.exists()and not overwrite:raise FileExistsError('目标已存在，未覆盖。')
    raw=text.encode('utf8');fd,name=tempfile.mkstemp(prefix='.note-export-',dir=path.parent);published=False;warning=None
    try:
        with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        if overwrite:
            if path.is_symlink()or path.is_dir():raise ValueError('目标位置已变化，未覆盖。')
            os.replace(name,path)
        else:os.link(name,path)
        published=True
    finally:
        try:Path(name).unlink(missing_ok=True)
        except OSError:
            if published:warning='文件已导出，但一份临时副本未能清理。'
    return {'bytes':len(raw),'path':path,'warning':warning}
