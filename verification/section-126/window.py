"""Actual new comparison button with isolated public state; no external actions."""
import copy,hashlib,json,math,sys,tempfile
from pathlib import Path
ROOT=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
import rouge.app as product
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory(prefix='token-comparison126-') as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'account.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.auto_relics.setChecked(False);window.centralWidget().setCurrentIndex(1)
        for op,module,field,expected in (('char_110_deepcl','uniequip_002_deepcl','hp',2318.4),
                ('char_2027_wang','uniequip_002_wang','deployment_cost',2),
                ('mechanist','uniequip_002_mcnist','hp',None),
                ('kaltsit',None,'hp',None)):
            window.select_operator(op);window.calculate();app.processEvents()
            before_run=copy.deepcopy(window.run.state);before_account=copy.deepcopy(window.operator_observations)
            before_result=copy.deepcopy(window.damage_result)
            assert window.token_comparison_button.isEnabled()
            window.token_comparison_button.click();app.processEvents()
            dialog=window.token_comparison_dialog;assert dialog.isVisible()
            assert dialog.module_selector.currentData()==module
            result=dialog.comparison_result;token=result['tokens'][0]
            assert dialog.comparison_table.rowCount()==8*len(result['tokens'])
            if module:
                actual=token['stages'][3]['values'][field]
                assert actual is None if expected is None else math.isclose(actual,expected,rel_tol=0,abs_tol=1e-8)
                if op=='mechanist':assert all(s['state']=='unverified' for s in token['stages'][1:])
            else:assert len(token['stages'])==1
            dialog.module_selector.setCurrentIndex(0);app.processEvents()
            assert len(dialog.comparison_result['tokens'][0]['stages'])==1
            if module:
                dialog.module_selector.setCurrentIndex(dialog.module_selector.findData(module));app.processEvents()
                assert len(dialog.comparison_result['tokens'][0]['stages'])==4
            assert window.run.state==before_run and window.operator_observations==before_account and window.damage_result==before_result
            cases.append({'operator':op,'module':module,'field':field,'stage3_value':token['stages'][3]['values'][field] if module else None,'real_button_opened':True,'switch_to_base_and_back':True,'run_account_damage_unchanged':True})
            if op=='char_110_deepcl':assert dialog.grab().save(str(OUT/'module-upgrades.png'))
            dialog.close();app.processEvents()
        window.select_operator('char_002_amiya');app.processEvents()
        assert not window.token_comparison_button.isEnabled()
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
    finally:
        window.close();app.processEvents()
receipt={'passed':True,'actual_window_cases':cases,'non_token_operator_button_disabled':True,'game_capture':False,'chat_requests':0,'private_state_included':False,'native_windows_verified':False,'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('rouge/app.py','rouge/token_module_comparison.py')}}
(OUT/'window.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)},ensure_ascii=False))
