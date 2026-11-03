"""Explicit before307 player presentation replay, only for historical checks.

The current307 renderer is tested directly elsewhere. No new role helper,
qualification, resource result, source validity or live rendering is patched.
"""
from hashlib import sha256
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'verification/sections/307-preparation/before/rouge/player_node_information.py'
SOURCE_SHA256 = '1ba06ff239ac5dbedae5a7e928c5eebeaf3afbd6a50984aacba4495271b25be4'
SOURCE_BYTES = 34724
SOURCE_COMMIT = 'c45ffb00f1932a27919885440b98a52094b087e0'


def legacy_node_information_text(*args, **kwargs):
    path = ROOT / SOURCE
    raw = path.read_bytes()
    if len(raw) != SOURCE_BYTES or sha256(raw).hexdigest() != SOURCE_SHA256:
        raise AssertionError('Exact public before307 player source is required.')
    module = types.ModuleType('rouge._historical_player_presentation_306')
    module.__package__ = 'rouge'
    module.__file__ = str(ROOT / 'rouge/player_node_information.py')
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module.node_information_text(*args, **kwargs)
