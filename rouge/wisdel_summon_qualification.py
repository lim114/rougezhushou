"""Two pinned original summon routes; qualification data never places a token."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def _source():
    return json.loads((Path(__file__).with_name('data') /
                       'wisdel-summon-qualification-reference.json').read_text(encoding='utf-8'))


def reference(profile, scenario):
    data = _source()
    elite = scenario.get('elite', 2)
    level = scenario.get('level') or profile['phases'][elite]['max_level']
    potential = scenario.get('potential', 1)

    def qualified(route):
        phase = route['unlock_elite']
        return (elite >= phase and (elite > phase or level >= route['unlock_level']) and
                potential - 1 >= route.get('required_potential_rank', 0))

    talent = deepcopy(data['talent_route'])
    talent['cultivation_qualified'] = qualified(talent)
    skill = deepcopy(data['skill_route'])
    levels = skill.pop('levels')
    skill['cultivation_qualified'] = qualified(skill)
    skill['currently_selected'] = scenario['skill'] == skill['skill_number']
    skill['selected_level_source'] = (levels[scenario.get('skill_rank', 10)-1]
                                     if skill['currently_selected'] else None)
    return {'operator_id': data['operator_id'], 'token_id': data['token_id'],
            'scope': data['scope'], 'source_commit': data['source_commit'],
            'current_cultivation': {'elite': elite, 'level': level, 'potential': potential},
            'talent_route': talent, 'skill_route': skill,
            'actual_source_provenance': None, 'actual_presence_verified': False,
            'actual_cast_clock_verified': False, 'covers_all_routes': False,
            'declared_counts_reinterpreted': False}
