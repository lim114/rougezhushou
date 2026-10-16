"""Static-only review receipts; no product imports, Qt, tests or state access."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAIRS = [
    ('verification/sections/297-preparation/before-node_catalog_view.py','rouge/node_catalog_view.py'),
    ('verification/sections/297-preparation/before-player_node_information.py','rouge/player_node_information.py')]
PATHS = [p for pair in PAIRS for p in pair] + ['rouge/expedition_results_view.py',
    'tests/test_expedition_integration_297.py','tests/test_expedition_results_view_297.py',
    'verification/sections/297-preparation/historical295-presentation-scope/original-test.py',
    'tests/test_documented_item_integration_295.py','verification/sections/297-preparation/before-output-hashes.json']


def sha(path):
    data = (ROOT/path).read_bytes()
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


def functions(node, prefix=''):
    found = {}
    for item in node.body:
        if isinstance(item, ast.ClassDef): found.update(functions(item,prefix+item.name+'.'))
        elif isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)):
            found[prefix+item.name]=ast.dump(item,include_attributes=False)
    return found


def assertions(tree):
    return Counter(ast.dump(node,include_attributes=False) for node in ast.walk(tree)
        if isinstance(node,ast.Assert) or isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute)
        and node.func.attr.startswith('assert'))


def main():
    before = {name:sha(name) for name in PATHS}
    differences = {}
    for old,new in PAIRS:
        first = functions(ast.parse((ROOT/old).read_text(encoding='utf8')))
        last = functions(ast.parse((ROOT/new).read_text(encoding='utf8')))
        differences[new] = {'changed_existing_functions':[name for name in first if name in last and first[name]!=last[name]],
            'removed_functions':sorted(first.keys()-last.keys()),'new_functions':sorted(last.keys()-first.keys()),
            'unchanged_existing_functions':len([name for name in first if name in last and first[name]==last[name]])}
    original = ast.parse((ROOT/PATHS[7]).read_text(encoding='utf8'))
    current = ast.parse((ROOT/PATHS[8]).read_text(encoding='utf8'))
    original_asserts,current_asserts=assertions(original),assertions(current)
    # The exact caller paths, not a product/runtime test or source execution.
    result = {'kind':'limited-static-integration-review-not-test-or-native-acceptance',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'sources_before':before,
        'function_AST_comparison':differences,
        'historical295_assertion_AST':{'original_total':sum(original_asserts.values()),
            'current_total':sum(current_asserts.values()),
            'all_original_assertion_multiset_preserved':not bool(original_asserts-current_asserts)},
        'manual_review_conclusion':'No substantive blocking source/control-flow issue found within reviewed integration scope.',
        'reviewed_boundaries':[
            'Player compares complete catalog.event_details rows JSON to fresh expected_event.scenes before phase annotations.',
            'Only exact source annotation tuple becomes return explanation; it is omitted from generic button/resource formatting.',
            'Three real choices keep source original identity; root return2hope+beacon and rest immediate2hope are separate.',
            'Ordinary promotion and special-region return-clock meaning remain unknown; beak never numerically applied.',
            'Node button is exact target only, manual open; dialog default none and item never auto-opened.',
            'Dialog refresh revalidates event/choice/item identity; invalid source clears readers/icon/selection; recovery unselected.',
            'Same scope keeps reader/tab/selection; other event clears; old295/296 helpers stay structurally unchanged.'],
        'limits':[
            'No Qt/native/test process was run by this review; actual Windows visual and timing validation belongs to root.',
            'Technical legacy resource formatter remains unchanged, including generic nominal reference labels; actual default page adds the phase distinction.',
            'Source-unavailable fallback preserves original text and generic references with explicit timing-unknown notice; it does not certify instant reward.',
            'Dialog scope is a fixed event reading key, not an observed dispatch or per-run receipt; no actual state claim is made.'],
        'new_findings':[],'production_writes':False,'Qt_tests_GUI_game_chat_private_Git_mutation':False}
    after = {name:sha(name) for name in PATHS}
    result['sources_after']=after;result['sources_unchanged_during_static_review']=before==after
    destination=HERE/'receipt.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'receipt':str(destination.relative_to(ROOT)),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
        'function_AST_comparison':differences,'historical295_assertion_AST':result['historical295_assertion_AST'],
        'source_unchanged':before==after,'new_findings':[]},ensure_ascii=False,indent=2))


if __name__ == '__main__':main()
