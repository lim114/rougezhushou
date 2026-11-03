import ast,subprocess,sys,unittest
from pathlib import Path
r=Path.cwd();sys.path.insert(0,str(r))
from rouge.current_battle_view import CurrentBattlePanel
from rouge.branch_choice import BranchChoice
for filename,cls,name in [('rouge/current_battle_view.py',CurrentBattlePanel,'set_context'),('rouge/branch_choice.py',BranchChoice,'set_groups')]:
 raw=subprocess.check_output(['git','show','a6923919b7d419f15b18d98b67a8ea0c8c5d7bfb:'+filename]);tree=ast.parse(raw.decode('utf8'));node=next(m for c in tree.body if isinstance(c,ast.ClassDef)and c.name==cls.__name__ for m in c.body if isinstance(m,ast.FunctionDef)and m.name==name)
 d=dict(getattr(cls,name).__globals__);exec(compile(ast.Module(body=[node],type_ignores=[]),'<frozen-baseline>','exec'),d);setattr(cls,name,d[name])
suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_current_battle_view_314.CurrentBattleView314Tests.test_refresh_preserves_selected_enemy_action_filter_tab_real_scroll_and_selection');result=unittest.TextTestRunner(verbosity=2).run(suite);raise SystemExit(not result.wasSuccessful())
