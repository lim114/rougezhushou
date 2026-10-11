import json,tempfile,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from rouge.scenario_library import ScenarioLibrary,model_signature
from rouge.scenario_comparison import compare_saved_scenarios,scenario_differences,format_scenario_comparison

BASE={'operator':'mechanist','skill':3,'base_attack':1000,'skill_rank':7,'window_seconds':10}
SIGNATURE='a'*64

class ScenarioLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'library.json'
        self.mock=patch('rouge.scenario_library.model_signature',return_value=SIGNATURE);self.mock.start();self.addCleanup(self.mock.stop)

    def test_no_write_at_load_save_restore_and_copies(self):
        library=ScenarioLibrary(self.path);self.assertFalse(self.path.exists())
        before=deepcopy(BASE);identity=library.save_new('公开情景',BASE);saved=self.path.read_bytes()
        restored=ScenarioLibrary(self.path);self.assertEqual(restored.get(identity)['scenario'],BASE)
        self.assertEqual(self.path.read_bytes(),saved);self.assertEqual(BASE,before)
        restored.get(identity)['scenario']['base_attack']=0
        self.assertEqual(restored.get(identity)['scenario'],BASE)

    def test_opaque_metadata_and_future_records_preserved(self):
        library=ScenarioLibrary(self.path);identity=library.save_new('甲',BASE)
        raw=json.loads(self.path.read_text());raw['future']={'keep':[1,2]}
        raw['records'][identity]['future-note']={'keep':True};raw['records'][identity]['id']='opaque-id'
        raw['records']['future-record']={'kind':'future','payload':['do not consume']}
        self.path.write_text(json.dumps(raw));restored=ScenarioLibrary(self.path)
        self.assertEqual(len(restored.records()),1);self.assertEqual(restored.records()[0]['id'],identity)
        restored.save_new('乙',{**BASE,'future-condition':{'native_activation':True}})
        after=json.loads(self.path.read_text());self.assertEqual(after['future'],raw['future'])
        self.assertEqual(after['records'][identity]['future-note'],{'keep':True})
        self.assertEqual(after['records']['future-record'],raw['records']['future-record'])

    def test_broken_or_future_schema_file_not_overwritten(self):
        for raw in (b'{broken',b'{"schema_version":2,"topic_id":"rogue_6","records":{}}'):
            self.path.write_bytes(raw);library=ScenarioLibrary(self.path);library.save_new('当前窗口',BASE)
            self.assertEqual(self.path.read_bytes(),raw);self.assertIsNotNone(library.issue)
            self.assertEqual(len(library.records()),1);self.assertIn('当前窗口',library.persistence_notice())

    def test_external_change_and_atomic_failure_keep_original(self):
        first=ScenarioLibrary(self.path);identity=first.save_new('甲',BASE);second=ScenarioLibrary(self.path)
        first.save_new('乙',BASE);saved=self.path.read_bytes();second.save_new('丙',BASE)
        self.assertEqual(self.path.read_bytes(),saved);self.assertIn('其他窗口',second.issue)
        current=ScenarioLibrary(self.path)
        with patch('rouge.scenario_library.os.replace',side_effect=OSError('injected')):
            current.delete(identity)
        self.assertEqual(self.path.read_bytes(),saved);self.assertEqual(list(self.path.parent.glob('scenario-*.tmp')),[])
        self.assertIsNotNone(current.issue)

    def test_invalid_names_conditions_and_capacity(self):
        library=ScenarioLibrary(self.path)
        for name in ('','\n','x'*61,True):
            with self.assertRaises(ValueError):library.save_new(name,BASE)
        for scenario in ({'operator':'not-supported','skill':1},{**BASE,'skill_rank':True},{**BASE,'future':float('nan')}):
            with self.assertRaises(ValueError):library.save_new('无效',scenario)
        self.assertFalse(self.path.exists())
        for i in range(20):library.save_new(str(i),BASE)
        saved=self.path.read_bytes()
        with self.assertRaises(ValueError):library.save_new('第21项',BASE)
        with self.assertRaises(ValueError):library.save_new('0',BASE)
        self.assertEqual(self.path.read_bytes(),saved)
        library.delete(library.records()[0]['id']);self.assertEqual(len(ScenarioLibrary(self.path).records()),19)

    def test_scenario_remains_separate_from_public_run_files(self):
        private=self.path.parent/'run.json';private.write_text('{"public-fixture":"keep"}')
        library=ScenarioLibrary(self.path);library.save_new('甲',BASE)
        self.assertEqual(private.read_text(),'{"public-fixture":"keep"}')

    def test_json_depth_and_nontext_keys_do_not_rewrite_conditions(self):
        library=ScenarioLibrary(self.path);nested={'leaf':1}
        for _ in range(70):nested={'child':nested}
        for scenario in ({**BASE,'future':nested},{**BASE,'future':{1:'integer key'}}):
            with self.assertRaises(ValueError):library.save_new('无效结构',scenario)
        self.assertFalse(self.path.exists())
        self.path.write_text('{"deep":'+'['*1100+'0'+']'*1100+'}')
        original=self.path.read_bytes();protected=ScenarioLibrary(self.path)
        protected.save_new('窗口条件',BASE);self.assertEqual(self.path.read_bytes(),original)

class ScenarioComparisonTests(unittest.TestCase):
    def setUp(self):
        self.mock=patch('rouge.scenario_comparison.model_signature',return_value=SIGNATURE);self.mock.start();self.addCleanup(self.mock.stop)

    def test_recalculate_upgrade_difference_and_changed_model(self):
        before=deepcopy(BASE);record={'name':'专三','scenario':{**BASE,'skill_rank':10},'model_signature':'b'*64}
        result=compare_saved_scenarios(BASE,[record]);base,upgrade=result['rows']
        self.assertEqual(base['delta_window_damage'],0);self.assertGreater(upgrade['delta_window_damage'],0)
        self.assertFalse(upgrade['saved_model_matches_current']);self.assertEqual(BASE,before)
        self.assertEqual(upgrade['differences'][0]['path'],'/skill_rank')
        self.assertIn('当前重新测算',format_scenario_comparison(result))

    def test_different_windows_never_produce_delta(self):
        result=compare_saved_scenarios(BASE,[{'name':'短窗','scenario':{**BASE,'window_seconds':5},'model_signature':SIGNATURE}])
        row=result['rows'][1];self.assertIsNone(row['delta_window_damage']);self.assertFalse(row['same_window_as_baseline'])
        self.assertTrue(row['saved_model_matches_current'])

    def test_unknown_healing_not_zero_and_invalid_saved_row(self):
        scenario={'operator':'char_2025_shu','skill':1,'skill_rank':7,'window_seconds':10}
        result=compare_saved_scenarios(scenario,[{'name':'旧专三','scenario':{**scenario,'elite':1,'skill_rank':10}}])
        self.assertIsNone(result['rows'][0]['window_healing']);self.assertIsNone(result['rows'][0]['delta_window_healing'])
        self.assertEqual(result['rows'][1]['status'],'当前不可测算')
        with self.assertRaises(ValueError):compare_saved_scenarios({'operator':'bad','skill':1},[])

    def test_type_sensitive_diff_add_remove_and_json_pointer(self):
        before={'bool':True,'old':2,'nested':{'a/b~c':[1]}}
        after={'bool':1,'new':3,'nested':{'a/b~c':[]}}
        changes=scenario_differences(before,after)
        self.assertEqual([r['kind'] for r in changes],['changed','changed','added','removed'])
        self.assertEqual(changes[1]['path'],'/nested/a~1b~0c')
        self.assertEqual(scenario_differences(BASE,deepcopy(BASE)),[])

    def test_selection_limit_and_opaque_provenance_not_consumed(self):
        with self.assertRaises(ValueError):compare_saved_scenarios(BASE,[{}]*7)
        result=compare_saved_scenarios({**BASE,'unconfirmed_training':{'future':'preserved'}},[])
        self.assertEqual(result['rows'][0]['scenario']['unconfirmed_training'],{'future':'preserved'})

    def test_real_model_signature_excludes_private_state(self):
        signature=model_signature();self.assertEqual(len(signature),64)
        self.assertTrue(all(c in '0123456789abcdef' for c in signature))
