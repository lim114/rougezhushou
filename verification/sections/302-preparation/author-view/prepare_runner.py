from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source=(ROOT/'.cache/p3-301-view/run_direct_dialog_checks.py').read_text(encoding='utf8')
source=source.replace('named_reward_items','ritual_weakening').replace('named-reward-items','ritual-weakening').replace('301','302')
source=source.replace("fallback=('rouge/player_node_information.py','rouge/ui_state.py')",
    "fallback=('rouge/player_node_information.py','rouge/ui_state.py','rouge/battle_view.py',"
    "'rouge/battle_preview.py','rouge/view_catalog.py','rouge/branch_choice.py','rouge/run_modifiers.py',"
    "'rouge/data/battle-previews.json','rouge/data/battle-maps/ro6_b_6.png')")
source=source.replace("    inputs[TEST]=HERE/'candidate'/TEST\n",
    "    inputs[TEST]=HERE/'candidate'/TEST\n"
    "    # Existing battle stage grouping asks the isolated catalog for this public table.\n"
    "    inputs['rouge/data/node-events.json']=ROOT/'rouge/data/node-events.json'\n")
(HERE/'run_direct_dialog_checks.py').write_text(source,encoding='utf8')
for path in (HERE/'candidate/rouge/ritual_weakening_view.py',
             HERE/'candidate/tests/test_ritual_weakening_view_302.py',HERE/'run_direct_dialog_checks.py'):
    compile(path.read_bytes(),str(path),'exec')
print('Three cache files compiled without imports or runtime checks.')
