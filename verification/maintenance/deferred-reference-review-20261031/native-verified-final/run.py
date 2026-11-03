from pathlib import Path
import sys
from unittest.mock import patch
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import run
from tests.test_deferred_reference_review import native_check
from rouge import player_acceptance
with patch.object(player_acceptance,'check',side_effect=lambda section,window,gui,require:native_check(window,gui,require)):
    raise SystemExit(run(443,R/'verification/maintenance/deferred-reference-review-20261031/native-verified-final/window.json'))
