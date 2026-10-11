"""Read-only complete event-directory queries, never game actions."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.node_catalog import COMMANDS
def main():
    p=argparse.ArgumentParser(description='黑流树海节点内容目录（无生成概率）')
    p.add_argument('command',choices=sorted(COMMANDS));p.add_argument('--input',type=Path)
    a=p.parse_args()
    try:data=json.loads(a.input.read_text(encoding='utf-8-sig')) if a.input else {}
    except (OSError,ValueError) as e:p.error('输入文件不可读取或JSON不正确：'+str(e))
    if not isinstance(data,dict):p.error('输入需要对象。')
    try:r=COMMANDS[a.command](**data)
    except (TypeError,ValueError,KeyError) as e:p.error(str(e))
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False))
if __name__=='__main__':main()
