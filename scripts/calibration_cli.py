"""Emit read-only calibration JSON; never read the application's private state."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.calibration import COMMANDS

def main(argv=None):
    parser=argparse.ArgumentParser(description='首批三名干员局外校准工具')
    parser.add_argument('command',choices=sorted(COMMANDS))
    parser.add_argument('--input',type=Path,help='声明测试条件JSON；不自动读取私人运行目录')
    args=parser.parse_args(argv)
    payload=json.loads(args.input.read_text(encoding='utf-8-sig')) if args.input else {
        'scenario':{'operator':'mechanist','skill':3,'charge_count':0}}
    if not isinstance(payload,dict):parser.error('输入需要JSON对象。')
    try:result=COMMANDS[args.command](**payload)
    except (ValueError,TypeError,KeyError) as exc:parser.error(str(exc))
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
