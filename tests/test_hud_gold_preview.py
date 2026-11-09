import unittest
from unittest.mock import Mock, patch

import numpy as np

from rouge.hud_gold_preview import LABELS, match_digits, read_gold_preview
from rouge.recognition import ScreenReader


GLYPHS = {
    '2': ['11111', '00001', '00001', '11111', '10000', '10000', '11111'],
    '8': ['11111', '10001', '10001', '11111', '10001', '10001', '11111'],
    '3': ['11111', '00001', '00001', '11111', '00001', '00001', '11111'],
}


def number_frame(digits):
    image = np.full((200, 480, 3), 48, np.uint8)
    right = 430
    for digit in reversed(digits):
        glyph = np.array([list(row) for row in GLYPHS[digit]]) == '1'
        mask = glyph.repeat(2, axis=0).repeat(2, axis=1)
        image[23:37, right-10:right][mask] = 240
        right -= 13
    return image


def corners(left, top, right, bottom):
    return np.array([(left, top), (right, top), (right, bottom), (left, bottom)])


class GoldPreviewTests(unittest.TestCase):
    def test_first_entry_requires_current_labels_and_the_real_amount_field(self):
        from rouge.hud_gold_preview import read_initial_gold
        image = np.zeros((800, 1280, 3), np.uint8)
        # A cyan component proposes a layout but cannot authorize a reading.
        image[7:38, 1111:1147] = (175, 211, 2)
        good = [([(name, .99)], None) for name in LABELS]
        self.assertIsNone(read_initial_gold(image, Mock(side_effect=good)))
        with patch('rouge.hud_gold_preview.read_plate_gold', return_value={'value': 0}) as plate:
            self.assertEqual(read_initial_gold(image, Mock(side_effect=good)), {'value': 0})
            plate.assert_called_once()
            for bad in [([('商品', .99)], None), ([('收藏品', .89)], None)]:
                self.assertIsNone(read_initial_gold(image, Mock(side_effect=[*good[:-1], bad])))
            image[47:78, 1111:1147] = (175, 211, 2)
            self.assertIsNone(read_initial_gold(image, Mock()))
            plate.assert_called_once()

    def setUp(self):
        self.prior = number_frame('28')
        self.box = corners(404, 20, 432, 40)
        self.view = {'source_size': [480, 200], 'content_rect': [0, 0, 480, 200]}
        texts = [{'text': label, 'confidence': .99,
                  'box': (corners(10+50*i, 5, 50+50*i, 15)/[480, 200]).tolist()}
                 for i, label in enumerate(LABELS)]
        texts.append({'text': '28', 'confidence': .99, 'box': (self.box/[480, 200]).tolist()})
        self.seed = {'page': 'exploration', 'viewport': self.view, 'texts': texts,
                     'run': {'page': 'run_map', 'resources': {'gold': {'value': 28}}}}

    def test_new_combinations_keep_all_digits_and_alignment(self):
        for number in ('2', '22', '828', '2882'):
            with self.subTest(number=number):
                result = match_digits(number_frame(number), self.prior, self.box, '28', .76, 1.53)
                self.assertEqual(result[0], int(number))

    def test_unseen_partial_darkened_shifted_or_excess_digits_fall_back(self):
        cut = number_frame('28')
        cut[24:36, 423:426] = 0
        hidden = number_frame('28')
        hidden[23:37, 407:417] = 0
        extra = self.prior.copy()
        extra[23:37, 444:452] = 240
        for image in (number_frame('3'), number_frame('22222'), cut, hidden, extra,
                      np.roll(self.prior, 2, axis=1)):
            self.assertIsNone(match_digits(image, self.prior, self.box, '28', .76, 1.53))

    def test_one_shape_with_two_conflicting_reference_labels_is_ambiguous(self):
        image = number_frame('22')
        self.assertIsNone(match_digits(image, image, self.box, '28', .76, 1.53))

    def test_window_borders_do_not_offset_the_observed_field(self):
        bordered = np.pad(self.prior, ((11, 9), (7, 13), (0, 0)))
        now = np.pad(number_frame('22'), ((11, 9), (7, 13), (0, 0)))
        self.view.update(source_size=[500, 220], content_rect=[7, 11, 487, 211])
        for text in self.seed['texts']:
            text['box'] = ((np.array(text['box']) * (480, 200) + (7, 11)) / (500, 220)).tolist()
        with patch('rouge.hud_gold_preview.find_gold_icon', return_value=(.97, .76, .15)):
            self.assertEqual(read_gold_preview(now, bordered, self.seed, self.view, Mock())['value'], 22)

    def test_only_current_icon_and_four_qualified_labels_authorize_a_value(self):
        image = number_frame('22')
        engine = Mock(return_value=([['wrong', .99]], None))
        with patch('rouge.hud_gold_preview.find_gold_icon', return_value=(.97, .76, .15)) as icon:
            def read():
                return read_gold_preview(image, self.prior, self.seed, self.view, engine)
            self.assertEqual(read()['value'], 22)
            engine.assert_not_called()
            image[8, 15] = 255
            self.assertIsNone(read())
            engine.return_value = ([['目标生命值', .99]], None)
            self.assertEqual(read()['value'], 22)
            icon.return_value = None
            self.assertIsNone(read())
            self.assertIsNone(read_gold_preview(image, self.prior, self.seed,
                                                {**self.view, 'content_rect': [1, 0, 480, 200]}, engine))

    def test_reward_and_shop_require_verified_hud_and_ignore_off_header_price(self):
        from copy import deepcopy
        price = deepcopy(self.seed['texts'][-1])
        price['box'] = (corners(40, 120, 75, 142)/[480, 200]).tolist()
        self.seed['texts'].append(price)
        def read():
            return read_gold_preview(number_frame('22'), self.prior, self.seed, self.view, Mock())
        with patch('rouge.hud_gold_preview.find_gold_icon', return_value=(.97, .76, .15)):
            for page in ('shop', 'unknown'):
                self.seed['page'] = page
                self.assertEqual(read()['value'], 22)
            self.seed['run']['page'] = 'run_roster'
            self.assertIsNone(read())
            self.seed['run']['page'] = 'run_map'
            price['box'] = (corners(40, 20, 75, 40)/[480, 200]).tolist()
            self.assertIsNone(read())

    def test_seed_follows_window_and_run_not_learned_difficulty(self):
        reader = ScreenReader()
        observation = {'page': 'exploration', 'performance': {}}
        reader._read = Mock(side_effect=lambda *a, **kw: {**observation, 'performance': {}})
        image = self.prior.copy()
        def take(source, run, difficulty):
            image[0, 0] += 1
            reader.read(image, on_hud=Mock(), hud_source=source,
                        run_context={'run_id': run, 'config': difficulty})
            return reader._read.call_args.kwargs['gold_seed']
        self.assertIsNone(take((1, 2, 3), 'a', {}))
        self.assertIsNotNone(take((1, 2, 3), 'a', {'difficulty': {'value': 4}}))
        self.assertIsNone(take((2, 3, 4), 'a', {}))
        self.assertIsNone(take((2, 3, 4), 'b', {}))

    def test_partial_hud_keeps_only_one_layout_for_current_frame_recheck(self):
        from copy import deepcopy
        reader = ScreenReader()
        partial = {'viewport': self.view, 'texts': [r for r in self.seed['texts']
                   if r['text'] in ('目标生命值', '指挥等级', '收藏品')]}
        calls = []
        def read(image, **kwargs):
            calls.append(kwargs['gold_seed'])
            return {**deepcopy(self.seed if len(calls) == 1 else partial), 'performance': {}}
        reader._read = read
        for i in range(4):
            reader.read(self.prior+i, on_hud=Mock(), hud_source=(1, 2, 3))
        self.assertEqual({r['text'] for r in calls[2]['texts']}, set(LABELS))
        self.assertEqual(calls[3]['texts'], partial['texts'])
