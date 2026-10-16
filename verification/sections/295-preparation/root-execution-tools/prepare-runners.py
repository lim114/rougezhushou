from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
original=(ROOT/'.cache/run_section_294_necessary.py').read_bytes().decode()
start=original.index("modules=['tests.test_direct_landmark_294'")
end=original.index("assert all(p.is_file()",start)
replacement="""modules=['tests.test_documented_choice_items_295','tests.test_documented_choice_item_view_295',
 'tests.test_documented_item_integration_295','tests.test_event_named_reward_integration_289',
 'tests.test_event_named_reward_links_289','tests.test_node_rewards',
 'tests.test_player_node_information_286','tests.test_node_catalog_view']
paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
paths|={ROOT/('tests/'+m.split('.')[-1]+'.py') for m in modules}
paths|={ROOT/'scripts/verify_documented_choice_item_window_295.py',ROOT/'scripts/build_documented_choice_items_295.py',
 ROOT/'verification/sections/295-preparation/pre295-query-baseline.json',
 ROOT/'rouge/data/relic-icons/rogue_6_relic_final_1.png'}
for packet in ('p3-documented-choice-items-295','p3-event-named-rewards-289'):
    paths|={p for p in (ROOT/'research'/packet).rglob('*') if p.is_file()}
"""
script=original[:start]+replacement+original[end:]
script=script.replace("'section':294", "'section':295")
with(ROOT/'.cache/run_section_295_necessary.py').open('xb') as stream:stream.write(script.encode())
native=(ROOT/'.cache/run_section_294_window.py').read_bytes()
native=native.replace(b'294',b'295').replace(b'verify_direct_map_window_295.py',b'verify_documented_choice_item_window_295.py')
with(ROOT/'.cache/run_section_295_window.py').open('xb') as stream:stream.write(native)
print('295 necessary/native owned wrappers prepared; no checks launched')
