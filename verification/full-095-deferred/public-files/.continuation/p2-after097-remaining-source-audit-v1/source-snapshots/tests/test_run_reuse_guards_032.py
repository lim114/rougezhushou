"""Run ownership and historical geometry must not become fresh evidence."""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.run_config import confirmed_config
from rouge.run_state import RunState
from rouge.relic_recognition import resolve_difficulty_icons
from rouge.viewport import map_evidence
from tests.test_relic_grade_sync_032 import icon,bar,grade,BASE


class RunReuseGuardTests(unittest.TestCase):
    def test_observation_from_another_run_is_rejected_before_it_can_confirm_icons(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json');before=copy.deepcopy(run.state)
            rows=resolve_difficulty_icons([icon()],{'value':10})
            observation={**bar(rows,1,[BASE+'_c']),**grade(10),
                'config_reuse':{'run_id':'previous-run','fields':['difficulty']}}
            self.assertFalse(run.apply(observation,run.state['started_at']+1))
            self.assertEqual(run.state,before)

    def test_reused_badge_geometry_is_omitted_when_viewport_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json');at=run.state['started_at']+1
            badge={'box':[[.1,.8],[.2,.8],[.2,.9],[.1,.9]]}
            run.apply({'config':{'difficulty':{'value':10,'source':'badge','badge':badge},
                'squad':{'id':'rogue_6_band_19','name':'多边贸易分队','source':'badge',
                         'effect_verified':False,'badge':badge}}},at)
            context=run.recognition_context();saved=copy.deepcopy(context)
            reused=confirmed_config(context)
            map_evidence(reused,{'source_size':[1600,1000],'content_rect':[100,50,1500,950]})
            self.assertNotIn('badge',reused['difficulty']);self.assertNotIn('badge',reused['squad'])
            self.assertEqual(reused['difficulty']['value'],10)
            self.assertEqual(reused['difficulty']['captured_at'],at)
            self.assertEqual(context,saved)


if __name__=='__main__':unittest.main()
