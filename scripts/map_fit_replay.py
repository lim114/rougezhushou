"""Numerical replay of hash-sealed fits; source/gate decisions remain exact.

OpenCV findHomography converts input point matrices to CV_32F before its
homography kernel/iterative refinement. Use an explicit cross-build replay
policy: one float32 epsilon scaled by the numeric leaf, only for computed
matrix/projection/error leaves. This is an engineering replay policy, not a
proven solver error bound, new pixel tolerance or claim of native precision.
"""
import copy
import math
import re

import numpy as np

REPLAY_EPSILON = float(np.finfo(np.float32).eps)
COMPUTED_FLOAT = re.compile(r'^/(matrix/\d+|checks/\d+/(projected_pixel/[01]|error_px))$')


def _number_close(current, frozen):
    return math.isfinite(current) and math.isfinite(frozen) and abs(current - frozen) <= REPLAY_EPSILON * max(1.0, abs(current), abs(frozen))


def verify_fit_replay(current, frozen):
    """Validate both unchanged 4px decisions and every structural/data leaf."""
    for value in (current, frozen):
        if not isinstance(value, dict) or not isinstance(value.get('accepted'), bool):
            raise ValueError('Fit replay schema/qualification changed.')
        errors = [check['error_px'] for check in value['checks']]
        if not errors or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in errors):
            raise ValueError('Fit replay has a nonfinite or malformed error.')
        if value['accepted'] is not (max(errors) <= 4):
            raise ValueError('The independent original 4px fit gate changed.')
    differences = []
    def visit(a, b, path):
        if type(a) is not type(b):
            raise ValueError('Fit replay structure/type changed: ' + path)
        if isinstance(a, dict):
            if set(a) != set(b):
                raise ValueError('Fit replay keys changed: ' + path)
            for key in a:
                visit(a[key], b[key], path + '/' + key)
        elif isinstance(a, list):
            if len(a) != len(b):
                raise ValueError('Fit replay list shape changed: ' + path)
            for index, (one, two) in enumerate(zip(a, b)):
                visit(one, two, path + '/' + str(index))
        elif isinstance(a, float) and COMPUTED_FLOAT.fullmatch(path):
            if not _number_close(a, b):
                raise ValueError('Computed fit exceeds the float32 numerical replay policy: ' + path)
            if a != b:
                differences.append({'path': path, 'current': a, 'frozen': b, 'difference': abs(a - b),
                    'allowed_numeric_difference': REPLAY_EPSILON * max(1.0, abs(a), abs(b))})
        elif a != b:
            raise ValueError('Fit source or qualification changed: ' + path)
    visit(current, frozen, '')
    return {'floating_policy': 'one_float32_epsilon_scaled_computed_leaf_only',
        'epsilon': REPLAY_EPSILON, 'differing_computed_leaves': differences,
        'qualification_and_source_structure_exact': True, 'original_pixel_gate': 4}


def canonical_inverse(current, frozen):
    """Recheck algebra, then retain already hash-sealed published inverse values."""
    if not isinstance(current, list) or not isinstance(frozen, list) or len(current) != 9 or len(frozen) != 9:
        raise ValueError('Canonical inverse shape changed.')
    if any(type(a) is not float or type(b) is not float or not _number_close(a, b) for a, b in zip(current, frozen)):
        raise ValueError('Canonical inverse exceeds the numerical replay policy.')
    return copy.deepcopy(frozen)
