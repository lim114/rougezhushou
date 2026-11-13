"""Ready frames wake recognition without waiting for another polling tick."""
import unittest

from PySide6.QtTest import QTest
from tests import test_sampling_flow as fixtures


class SamplingDeadlineTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.SamplingFlowTests.setUpClass.__func__)
    setUp = fixtures.SamplingFlowTests.setUp
    wait_for = fixtures.SamplingFlowTests.wait_for
    offer = fixtures.SamplingFlowTests.offer

    def test_settled_frame_starts_without_another_regular_poll(self):
        self.release.set()
        self.offer(20)
        self.window.auto.setChecked(True)
        self.window.timer.stop()
        QTest.qWait(30)
        self.assertEqual(self.seen, [])
        self.wait_for(lambda: self.seen == [20], .4)
        self.wait_for(lambda: not self.window.busy)

    def test_pause_cancels_waiting_sample(self):
        self.release.set()
        self.offer(20)
        self.window.auto.setChecked(True)
        self.window.auto.setChecked(False)
        QTest.qWait(200)
        self.assertEqual(self.seen, [])

    def test_empty_buffer_does_not_schedule_deadline_wakeups(self):
        self.window.auto.setChecked(True)
        self.assertFalse(self.window.ready_timer.isActive())

    def test_regular_poll_consumption_cancels_the_old_deadline(self):
        self.release.set()
        self.offer(20)
        self.window.auto.setChecked(True)
        self.window.timer.stop()
        self.assertTrue(self.window.ready_timer.isActive())
        self.offer(40)
        self.window.sample_now(automatic=True)
        self.assertFalse(self.window.ready_timer.isActive())
        self.wait_for(lambda: not self.window.busy)

    def test_expired_wait_uses_current_buffer_instead_of_a_stored_old_frame(self):
        self.release.set()
        self.offer(20)
        self.window.auto.setChecked(True)
        self.window.timer.stop()
        self.window.capture.discard_pending()
        self.offer(40)
        self.wait_for(lambda: self.seen == [40], .4)
        self.wait_for(lambda: not self.window.busy)


if __name__ == '__main__':unittest.main()
