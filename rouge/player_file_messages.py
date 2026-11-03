"""Short player-facing file errors; callers may keep raw detail in a tooltip."""
import json
import re

def file_issue(error):
    if isinstance(error,PermissionError):return '文件或目录暂时无法访问，可能正在被占用或没有访问权限。'
    if isinstance(error,FileNotFoundError):return '所需文件或目录已不存在，请检查保存位置。'
    if isinstance(error,FileExistsError):return '所选位置已有内容，未自动覆盖。'
    if isinstance(error,UnicodeError):return '文件的文字格式无法读取，原件未改动。'
    if isinstance(error,json.JSONDecodeError):return '记录内容无法核对，原件未改动。'
    if isinstance(error,OSError):return '本机文件暂时无法读写，请检查占用、可用空间和保存位置。'
    text=str(error)
    return text if re.search(r'[\u4e00-\u9fff]',text)else'记录内容暂时无法核对，原件和当前编辑均保留。'
