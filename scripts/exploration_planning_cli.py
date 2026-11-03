"""Query fixed exploration tools using declared JSON; never performs game actions."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.exploration_planning import COMMANDS
from rouge.information_scope import require_query_scope,HISTORICAL_ROUTE_QUERIES

def main():
    parser=argparse.ArgumentParser(description='黑流树海离线零件与路线节点信息（无生成概率）')
    parser.add_argument('command',metavar='{'+','.join(sorted(set(COMMANDS)-HISTORICAL_ROUTE_QUERIES))+'}')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--historical-route-diagnostics',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    try:require_query_scope('exploration',args.command,args.historical_route_diagnostics)
    except ValueError as error:parser.error(str(error))
    if args.command not in COMMANDS:parser.error('没有这个节点信息查询。')
    try: payload=json.loads(args.input.read_text(encoding='utf-8-sig')) if args.input else {}
    except (OSError,ValueError) as error: parser.error('输入文件不可读取或JSON不正确：'+str(error))
    if not isinstance(payload,dict): parser.error('输入需要JSON对象。')
    try: result=COMMANDS[args.command](**payload)
    except (TypeError,ValueError,KeyError) as error: parser.error(str(error))
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__':main()
