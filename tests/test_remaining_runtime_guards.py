"""Source-data separation preserves every captured public result and data guard."""
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from hashlib import sha256
import ast,json,unittest
from tests.reference_guard_cases import MODELS,current,packets,cases,normalize,builder_reads

ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'verification/maintenance/remaining-runtime-guards-20261031/candidate-probe.json'


class RemainingRuntimeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.record=json.loads(RECORD.read_bytes())

    def test_seven_loaders_keep_all_functions_and_only_rebind_manifest_declarations(self):
        def tree(raw):
            node=ast.parse(raw);node.body=[n for n in node.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ('MANIFEST','MANIFEST_SHA256')for t in n.targets))];return ast.dump(node,include_attributes=False)
        for model,_ in MODELS:
            name=Path(model.__file__).name;self.assertEqual(tree(Path(model.__file__).read_bytes()),tree((ROOT/'research/remaining-runtime-guards-20261031/baseline'/name).read_bytes()))

    def test_all_original_nonprogram_runtime_bytes_and_historical_provenance_are_kept(self):
        for model,_ in MODELS:
            old=self.record['old_bindings'][model.__name__];original=json.loads((ROOT/old['path']).read_bytes());manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
            expected={n:v for n,v in original.get('runtime_files',original['files']).items()if not n.endswith('.py')}
            self.assertEqual(manifest.get('runtime_files',manifest['files']),expected)
            self.assertEqual(manifest['historical_recipe_manifest']['sha256'],old['sha256'])
            self.assertTrue(manifest['historical_recipe_code_sources'])
            for n,v in expected.items():raw=(ROOT/n).read_bytes();self.assertEqual((len(raw),sha256(raw).hexdigest()),(v['bytes'],v['sha256']))

    def test_unused_build_scripts_can_change_but_corrupted_data_still_refuses_after_warm_read(self):
        for model,_ in MODELS:
            with TemporaryDirectory()as folder,ExitStack()as stack:
                root=Path(folder);manifest=json.loads((ROOT/model.MANIFEST).read_bytes());runtime=manifest.get('runtime_files',manifest['files'])
                # The stage-entry reader separately pins generated DATA with
                # DATA_SHA256; it is deliberately outside manifest['files'].
                files={model.MANIFEST,*runtime}
                if hasattr(model,'DATA'):files.add(model.DATA)
                for n in files:p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
                for n in manifest['historical_recipe_code_sources']:p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'# Deliberately different unused build input.\n')
                stack.enter_context(patch.object(model,'ROOT',root));load=model.packet if model is current else model.source_data
                self.assertIsNotNone(load(),model.__name__);name=model.PACK+'/selected-originals.json'if model is current else model.DATA;p=root/name;original=p.read_bytes();p.write_bytes(original+b' ')
                self.assertIsNone(load());p.write_bytes(original);self.assertIsNotNone(load())

    def test_all_255_captured_source_and_public_results_match_after_actual_promotion(self):
        actual=cases();self.assertEqual({k:len(v)for k,v in actual.items()},self.record['case_counts'])
        for key,value in actual.items():self.assertEqual(sha256(normalize(value,self.record)).hexdigest(),self.record['normalized_output_sha256'][key],key)

    def test_round_of_seven_packets_removes_only_the_ten_build_script_reads(self):
        self.assertEqual(sum(builder_reads(ROOT,self.record).values()),0)
        with ExitStack()as stack:
            for model,_ in MODELS:
                old=self.record['old_bindings'][model.__name__];stack.enter_context(patch.object(model,'MANIFEST',old['path']));stack.enter_context(patch.object(model,'MANIFEST_SHA256',old['sha256']))
            self.assertEqual(sum(builder_reads(ROOT,self.record).values()),10)

    def test_declared_runtime_binding_audit_remains_complete_and_data_only(self):
        from scripts.audit_runtime_reference_bindings import audit
        report=audit(ROOT);self.assertEqual(report['static_resolved_runtime_bindings'],92);self.assertFalse(report['unresolved']);self.assertTrue(report['all_resolved_runtime_bytes_match']);self.assertFalse(any(r['runtime_code_files']for r in report['rows']))

if __name__=='__main__':unittest.main()
