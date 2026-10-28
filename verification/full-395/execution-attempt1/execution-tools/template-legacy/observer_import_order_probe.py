"""Non-GUI actual calculator/unchanged observer import-order counterexample."""
import argparse
import ast
import functools
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--order',choices=('early_app','original'),required=True)
    args=parser.parse_args()
    original=HERE/'attempt1-original-seal/used-tools/original261-window.py'
    source=original.read_bytes().decode('utf-8')
    names={'_deadline_check100','_replace_binding100','_increment100','_install_narrow_observers100'}
    functions=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names]
    if len(functions)!=4 or 'rouge.app' in sys.modules:raise ValueError('Exact four original functions and a fresh unimported app are required')
    namespace={'functools':functools,'time':time,'_deadline100':time.perf_counter()+1200,
               '_count_enabled100':True,'_restorations100':[], 'entry_counts090':{},
               'profile_case090':None,'profile_trace090':[]}
    # Compile the original observer functions without changing any AST/code statement.
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(original),'exec'),namespace)
    if args.order=='early_app':
        import rouge.app as module
    namespace['_install_narrow_observers100']()
    if args.order=='original':
        import rouge.app as module
    import rouge.damage as damage
    import rouge.estimate as estimate
    import rouge.reporting as reporting
    matches={'calculate_damage':module.calculate_damage is damage.calculate_damage,
             'format_estimate':module.format_estimate is estimate.format_estimate,
             'format_report':module.format_report is reporting.format_report}
    payload={'operator':'mechanist','skill':1,'elite':2,'level':90,'skill_rank':10,
             'potential':1,'trust':100,'module_id':None,'module_level':0,
             'enemy_defense':0,'enemy_resistance':0,'relic_ids':[]}
    before=dict(namespace['entry_counts090'])
    actual=module.calculate_damage(payload)
    after=dict(namespace['entry_counts090'])
    delta={key:after.get(key,0)-before.get(key,0) for key in sorted(set(before)|set(after))}
    actual_raw=json.dumps(actual,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode('utf-8')
    from PySide6.QtWidgets import QApplication
    record={'kind':'SECTION275_REAL_NON_GUI_UNCHANGED_OBSERVER_IMPORT_ORDER_PROBE',
            'order':args.order,'unchanged_original_observer_functions':sorted(names),
            'original_functions_source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'app_source_sha256':hashlib.sha256((ROOT/'rouge/app.py').read_bytes()).hexdigest(),
            'actual_alias_identity_matches_installed_observers':matches,
            'actual_same_call_entry_delta':delta,'actual_result_sha256':hashlib.sha256(actual_raw).hexdigest(),
            'public_input':payload,'actual_result_returned':True,
            'QApplication_created':QApplication.instance() is not None,
            'window_or_full_suite_started':False,'game_operations':0,'chat_requests':0,
            'private_state_access':False,'counter_values_or_result_rewritten':False}
    for owner,name,value in reversed(namespace['_restorations100']):setattr(owner,name,value)
    target=HERE/('observer-import-order-'+args.order+'.json')
    with target.open('x',encoding='utf-8') as stream:stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'order':args.order,'alias_matches':matches,
        'actual_calculate_damage_delta':delta.get('calculate_damage',0),
        'actual_result_sha256':record['actual_result_sha256'],'QApplication_created':record['QApplication_created']},ensure_ascii=False))


if __name__=='__main__':main()
