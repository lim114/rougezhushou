"""Offline fixed-stage planning JSON interface; no private state or desktop."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.battle_planning import *
from rouge.enemy_panel import enemy_panel_reference

def main():
    parser=argparse.ArgumentParser(description='固定关卡局外规划：查询完整动作、条件与地图资料。')
    parser.add_argument('command',choices=['actions', 'activations', 'candidates', 'window', 'enemy-sources', 'branches', 'route', 'cell', 'mechanism', 'compare', 'panel'])
    parser.add_argument('stage')
    parser.add_argument('--enemy');parser.add_argument('--level',type=int,default=0)
    parser.add_argument('--start',type=float,default=0);parser.add_argument('--end',type=float,default=60)
    parser.add_argument('--limit',type=int,default=256);parser.add_argument('--branch')
    parser.add_argument('--route',type=int,default=0)
    parser.add_argument('--row',type=int,default=0);parser.add_argument('--col',type=int,default=0)
    parser.add_argument('--other-stage');parser.add_argument('--other-level',type=int,default=0)
    parser.add_argument('--run-config',default='{}')
    parser.add_argument('--other-run-config')
    args=parser.parse_args()
    try:
        if args.command=='actions': result=action_catalog(args.stage)
        elif args.command=='activations': result=predefined_activations(args.stage)
        elif args.command=='candidates': result=candidate_groups(args.stage)
        elif args.command=='window': result=local_time_window(args.stage,args.start,args.end,limit=args.limit)
        elif args.command=='enemy-sources': result=enemy_entry_sources(args.stage,args.enemy,args.level)
        elif args.command=='branches': result=branch_phase_catalog(args.stage,args.branch)
        elif args.command=='route': result=route_segments(args.stage,args.route)
        elif args.command=='cell': result=cell_planning_references(args.stage,args.row,args.col)
        elif args.command=='mechanism': result=mechanism_provenance(args.stage,args.enemy,args.level)
        elif args.command=='panel': result=enemy_panel_reference(args.stage,args.enemy,args.level)
        elif args.command=='compare': result=enemy_scenario_comparison(args.stage,args.other_stage,args.enemy,args.level,args.other_level,run_config=json.loads(args.run_config),right_run_config=json.loads(args.other_run_config) if args.other_run_config else None)
    except (ValueError,KeyError,TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__':main()
