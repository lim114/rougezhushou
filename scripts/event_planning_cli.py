"""Source-bound event requirements and battle-page links; no game operations."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.event_planning import COMMANDS

def main():
    p=argparse.ArgumentParser(description='事件资格三态与准确固定作战入口资料')
    p.add_argument('command',choices=sorted(COMMANDS));p.add_argument('--input',type=Path)
    a=p.parse_args()
    try:payload=json.loads(a.input.read_text(encoding='utf-8-sig')) if a.input else {}
    except (OSError,ValueError) as error:p.error(str(error))
    if not isinstance(payload,dict):p.error('输入需要JSON对象。')
    try:result=COMMANDS[a.command](**payload)
    except (TypeError,ValueError,KeyError) as error:p.error(str(error))
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__':main()
