"""Frozen original landmarks and actual fixed-preview widget entry points."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from rouge.battle_preview import battle_data, spawn_rows, DATA
from rouge.map_projection import grid_digest, projection_for, projection_data
from scripts.extend_fixed_map_projections import build, fit, BASE

NEW = ('ro6_n_2_1', 'ro6_e_2_1', 'ro6_n_2_5', 'ro6_e_2_5')
REJECTED = ('ro6_n_2_2', 'ro6_e_2_2', 'ro6_n_3_1', 'ro6_e_3_1')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FrozenGroundExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output, cls.receipt = build()

    def projection(self, sid, **changes):
        stage = copy.deepcopy(battle_data()['stages'][sid])
        for key, value in changes.items():
            stage[key] = value
        image = stage['image']
        return projection_for(stage, image['sha256'], (image['width'], image['height']))

    def test_production_adds_two_original_images_and_four_exact_stage_bindings(self):
        # Later independently reviewed maps may be appended. This receipt
        # freezes its own source-bound records rather than global coverage.
        current = projection_data()
        for group in ('calibrations', 'stages'):
            for key, value in self.output[group].items():
                self.assertEqual(current[group][key], value)
        self.assertEqual((self.receipt['total_calibrations'], self.receipt['total_bound_stages']), (12, 24))
        self.assertEqual((self.receipt['remaining_unbound_stages'], self.receipt['remaining_distinct_bitmaps']), (81, 59))
        prior = read(BASE / 'prior-projections.json')
        for group in ('calibrations', 'stages'):
            for key, value in prior[group].items():
                self.assertEqual(self.output[group][key], value)
        for key, value in prior['source'].items():
            self.assertEqual(self.output['source'][key], value)
        self.assertEqual(len(prior['calibrations']), 10)
        self.assertEqual(len(prior['stages']), 20)

    def test_thirty_separate_lowland_centers_pass_the_original_four_pixel_gate(self):
        count = 0
        for sid in ('ro6_n_2_1', 'ro6_n_2_5'):
            stage = battle_data()['stages'][sid]
            calibration = self.output['calibrations'][sid]
            anchors = {(r, c) for r, c, *_ in calibration['anchors']}
            projection = self.projection(sid)
            self.assertEqual(calibration['tolerance_px'], 4)
            for point in calibration['checks']:
                self.assertNotIn((point['row'], point['col']), anchors)
                tile = stage['tiles'][stage['map'][point['row']][point['col']]]
                self.assertEqual(tile['heightType'], 'LOWLAND')
                self.assertIn(tile['tileKey'], ('tile_road', 'tile_floor'))
                error = math.dist(projection.project(point), point['observed_pixel'])
                self.assertLessEqual(error, 4)
                self.assertAlmostEqual(error, point['error_px'], places=12)
                count += 1
        self.assertEqual(count, 30)

    def test_fitting_uses_only_the_frozen_original_seam_corners(self):
        source = read(BASE / 'source-receipt.json')
        for name, original_hash in source['recorded_crlf_sha256'].items():
            canonical = (BASE / name).read_bytes()
            self.assertNotIn(b'\r\n', canonical)
            self.assertEqual(hashlib.sha256(canonical.replace(b'\n', b'\r\n')).hexdigest(), original_hash)
        for number in source['included_observations']:
            frozen = read(BASE / f'frozen-observation-{number}.json')['calibrations'][0]
            result = fit(frozen)
            self.assertEqual(result, read(BASE / f'initial-fit-{number}.json')[0])
            matrix, _ = cv2.findHomography(
                np.array([[c, r] for r, c, x, y in frozen['anchors']], float),
                np.array([[x, y] for r, c, x, y in frozen['anchors']], float), method=0)
            self.assertEqual(matrix.ravel().tolist(), result['matrix'])
            changed = copy.deepcopy(frozen)
            changed['checks'][0][2] += 100
            denied = fit(changed)
            self.assertEqual(denied['matrix'], result['matrix'])
            self.assertFalse(denied['accepted'])
            changed = copy.deepcopy(frozen)
            changed['checks'][0][:2] = changed['anchors'][0][:2]
            with self.assertRaises(ValueError):
                fit(changed)

    def test_two_failed_first_fits_remain_excluded_without_adjusted_points(self):
        self.assertEqual([r['id'] for r in self.receipt['rejected']], ['ro6_n_2_2', 'ro6_n_3_1'])
        for number in (2, 3):
            entry = read(BASE / f'frozen-observation-{number}.json')['calibrations'][0]
            result = fit(entry)
            self.assertEqual(result, read(BASE / f'initial-fit-{number}.json')[0])
            self.assertFalse(result['accepted'])
            self.assertGreater(max(c['error_px'] for c in result['checks']), 4)
        for sid in REJECTED:
            self.assertNotIn(sid, self.output['stages'])
            self.assertIsNone(self.projection(sid))

    def test_source_bytes_and_all_four_aliases_have_independent_identity_guards(self):
        source = read(BASE / 'source-receipt.json')
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            binding = self.output['stages'][sid]
            calibration = self.output['calibrations'][binding['calibration']]
            image = DATA / stage['image']['file']
            self.assertEqual(digest(image), calibration['bitmap_sha256'])
            self.assertEqual(image.stat().st_size, stage['image']['bytes'])
            raw = image.read_bytes()
            self.assertEqual(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), stage['image']['source_blob_sha1'])
            original = source['sources'][binding['calibration']]
            level = BASE / Path(original['level_local_file']).name
            self.assertEqual(digest(level), binding['level_sha256'])
            self.assertEqual(read(level)['mapData']['map'], stage['map'])
            self.assertEqual(read(level)['mapData']['tiles'], stage['tiles'])
            self.assertEqual(grid_digest(stage), calibration['grid_sha256'])
            self.assertIsNotNone(self.projection(sid))
            for mutate in ('level', 'image_file', 'grid', 'alias', 'size'):
                wrong = copy.deepcopy(stage)
                if mutate == 'level':
                    wrong['level_source']['sha256'] = 'changed'
                elif mutate == 'image_file':
                    wrong['image']['file'] = 'another-bitmap.png'
                elif mutate == 'grid':
                    wrong['tiles'][wrong['map'][2][3]]['heightType'] = 'HIGHLAND'
                elif mutate == 'alias':
                    wrong['id'] = 'similar-name-without-exact-binding'
                else:
                    wrong['image']['width'] += 1
                self.assertIsNone(projection_for(wrong, wrong['image']['sha256'],
                    (wrong['image']['width'], wrong['image']['height'])), (sid, mutate))
            self.assertIsNone(projection_for(stage, 'f' * 64, (512, 286)))

    def test_only_measured_ground_agreement_is_claimed(self):
        for sid in ('ro6_n_2_1', 'ro6_n_2_5'):
            record = self.output['calibrations'][sid]
            self.assertIn('not independently measured', record['independent_coverage'])
            for unknown in ('elevated surfaces', 'portal roofs', 'actual spawn offsets', 'random ranges', 'hitboxes', 'pathfinding', 'timings'):
                self.assertIn(unknown, record['scope'])
        self.assertEqual(self.receipt['game_actions'], 0)
        self.assertEqual(self.receipt['chat_requests'], 0)
        self.assertEqual(self.receipt['live_samples'], 0)

    def test_readonly_rebuild_leaves_archived_sources_and_production_unchanged(self):
        paths = list(BASE.glob('*')) + [DATA / 'battle-map-projections.json']
        before = {p: digest(p) for p in paths if p.is_file()}
        output, receipt = build(write=False)
        self.assertEqual(output, self.output)
        self.assertEqual(receipt, self.receipt)
        canonical = json.dumps(output, ensure_ascii=False, indent=2).encode('utf-8')
        self.assertEqual(receipt['output_sha256'], hashlib.sha256(canonical).hexdigest())
        self.assertEqual({p: digest(p) for p in before}, before)


class OriginalMapWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_all_new_fixed_previews_show_reference_spawns_and_inverse_click_cells(self):
        from rouge.battle_view import MapOriginal
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            rows = spawn_rows(sid)
            view = MapOriginal()
            view.set_file(DATA / stage['image']['file'])
            view.set_reference(stage, rows)
            self.assertIsNotNone(view.projection)
            self.assertTrue(view.marker_cells(), sid)
            self.assertTrue(all(r['absolute_time'] is None and r['probability'] is None for r in rows))
            for width, height in ((1024, 572), (640, 720), (1600, 500)):
                view.resize(width, height)
                view.show()
                self.app.processEvents()
                for check in projection_data()['calibrations'][self.output_calibration(sid)]['checks']:
                    cell = {'row': check['row'], 'col': check['col']}
                    point = view.cell_center(cell)
                    self.assertIsNotNone(point)
                    self.assertEqual(view.cell_at(point), cell)
                selected = next(r for r in rows if r['route']['start'] is not None)
                view.selected = selected
                view.update()
                self.app.processEvents()
                self.assertFalse(view.grab().isNull())
            view.close()

    @staticmethod
    def output_calibration(sid):
        return projection_data()['stages'][sid]['calibration']

    def test_rejected_maps_keep_original_image_but_do_not_draw_unverified_overlay(self):
        from rouge.battle_view import MapOriginal
        for sid in REJECTED:
            stage = battle_data()['stages'][sid]
            view = MapOriginal()
            view.set_file(DATA / stage['image']['file'])
            view.set_reference(stage, spawn_rows(sid))
            self.assertFalse(view.pixmap.isNull())
            self.assertIsNone(view.projection)
            self.assertEqual(view.marker_cells(), {})
            view.close()


if __name__ == '__main__':
    unittest.main()
