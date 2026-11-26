"""Held-icon rejection is optional and cannot change CPU scoring on fallback."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import numpy as np

from rouge import held_icon_gpu as gpu
from rouge import relic_recognition as icons


class HeldIconGPUTests(unittest.TestCase):
    def test_failed_device_or_build_has_one_record_across_readers(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'nested' / 'reason.log'
            for reason in ('device unavailable', 'clBuildProgram (OpenCL -11)'):
                with self.subTest(reason=reason):
                    gpu._initialize.cache_clear()
                    self.addCleanup(gpu._initialize.cache_clear)
                    with patch.object(gpu, '_diagnostic', target), patch.object(
                        gpu, 'HeldIconScreen', side_effect=gpu.OpenCLUnavailable(reason)
                    ) as create, ThreadPoolExecutor(max_workers=4) as readers:
                        self.assertEqual(list(readers.map(lambda _: gpu.current_screen(), range(8))), [None] * 8)
                        create.assert_called_once_with()
                    self.assertEqual(target.read_text('utf-8').count(reason), 1)

    def test_unavailable_screen_keeps_the_same_cpu_bar(self):
        image = np.full((640, 960, 3), 25, np.uint8)
        anchor = {'text': '收起', 'box': [[.1,.90],[.14,.90],[.14,.94],[.1,.94]]}
        with patch.object(icons, '_match_bar', return_value=[]) as match, patch.object(
            gpu, 'current_screen', return_value=None
        ) as screen, patch('sys.platform', 'win32'):
            icons.match_held_icons(image, anchor, None)
            screen.assert_not_called()
            cpu = match.call_args
            icons.match_held_icons(image, anchor, None, gpu_screen=True)
            screen.assert_called_once_with()
            accelerated = match.call_args
            np.testing.assert_array_equal(cpu.args[0], accelerated.args[0])
            self.assertEqual(cpu.args[1:], accelerated.args[1:])
            self.assertIsNone(accelerated.kwargs['screen'])

    def test_moment_bound_and_per_pixel_input_share_the_same_mask(self):
        rng = np.random.default_rng(91)
        template = rng.integers(0, 256, (35, 47, 3), dtype=np.uint8)
        mask = np.full((35, 47), 255, np.uint8)
        mask[8:15, 11:24] = 0
        image = rng.integers(0, 256, (46, 62, 3), dtype=np.uint8)
        refs, positions, geometry, _, colors, indices, spans, energy = gpu.reference_bank([('icon', template, mask)])
        planes, _ = gpu._image_features(image)
        covered = np.zeros(mask.shape, np.int32)
        for (x, y) in [(0, 0), (15, 11)]:
            bound = 0
            for pos, ref in zip(positions, refs):
                level, iy, ix = int(pos >> 24), int((pos >> 12) & 4095), int(pos & 4095)
                if x == 0:
                    side = 1 << level
                    covered[iy:iy+side, ix:ix+side] += 1
                bound += np.square(.93 * planes[level, y + iy, x + ix].astype(np.float64) - ref).sum()
            exact = .93 * image[y:y+35, x:x+47][mask != 0].astype(np.float64) - template[mask != 0]
            self.assertLessEqual(bound, np.square(exact).sum() + 4)
        np.testing.assert_array_equal(covered, mask != 0)
        np.testing.assert_array_equal(colors[:, :3], template[indices >> 16, indices & 65535])
        self.assertEqual(tuple(geometry[0]), (0, len(refs), 47, 35))
        self.assertEqual(tuple(spans[0]), (0, np.count_nonzero(mask)))
        self.assertAlmostEqual(energy[0], np.square(colors, dtype=np.float64).sum(), delta=4)
