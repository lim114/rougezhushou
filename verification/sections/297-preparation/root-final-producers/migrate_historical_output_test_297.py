from pathlib import Path
from hashlib import sha256
import json,ast
ROOT=Path(__file__).resolve().parents[1];name='tests/test_documented_item_integration_295.py'
path=ROOT/name;raw=path.read_bytes();s=raw.decode().replace('\r\n','\n')
old="""        old=json.loads(BASELINE.read_bytes())
        for event_id,row in old['events'].items():
            if event_id==model.EVENT:continue
            text=node_information_text(entry(event_id))
            self.assertEqual(sha256(text.encode()).hexdigest(),row['player_sha256'],event_id)
"""
new="""        old=json.loads(BASELINE.read_bytes())
        # Replay the295 presentation scope;297 separately verifies all37 current
        # non-target outputs and the new delayed expedition-result rendering.
        with patch('rouge.player_node_information.expedition_results.event_reference',return_value=None):
            for event_id,row in old['events'].items():
                if event_id==model.EVENT:continue
                text=node_information_text(entry(event_id))
                self.assertEqual(sha256(text.encode()).hexdigest(),row['player_sha256'],event_id)
"""
assert s.count(old)==1;after=s.replace(old,new,1).replace('\n','\r\n').encode()
def asserts(blob):
 return [ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(blob))if isinstance(n,ast.Call)
         and isinstance(n.func,ast.Attribute)and n.func.attr.startswith('assert')]
assert sorted(asserts(raw))==sorted(asserts(after))
dest=ROOT/'verification/sections/297-preparation/historical295-presentation-scope';dest.mkdir(exist_ok=False)
(dest/'original-test.py').write_bytes(raw);path.write_bytes(after)
(dest/'migration.json').write_bytes((json.dumps({'kind':'PROACTIVE_HISTORICAL_PRESENTATION_SCOPE_REPLAY_NOT_FAILED_TEST_REPAIR',
 'path':name,'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha256(after).hexdigest(),
 'all_original_assertion_AST_preserved':True,'legacy37_comparison_still_includes_expedition_event':True,
 'only_new297_reference_temporarily_disabled_for_historical295_player_comparison':True,
 'current_default37_nontarget_and190resource_hashes_covered_by':'tests/test_expedition_integration_297.py',
 'production_source_changes':False,'actual_tests_executed_by_this_script':False},ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'historical_test_assertions_retained':True,'path':name,'after_sha256':sha256(after).hexdigest()}))
