"""Run the existing Node bridge fixture suite; never contact the desktop client."""
from pathlib import Path
import shutil
import subprocess
import unittest


class DesktopReceiptTests(unittest.TestCase):
    def test_simulated_delivery_receipts_and_recovery(self):
        node=shutil.which('node')
        if node is None:self.skipTest('Node.js unavailable; desktop receipt integration not validated.')
        root=Path(__file__).resolve().parents[1]
        result=subprocess.run([node,'--test','tests/desktop-backend.test.cjs'],cwd=root,
                              capture_output=True,text=True,encoding='utf-8',timeout=60)
        self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
