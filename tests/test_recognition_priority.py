import threading
import unittest

from rouge.recognition_priority import ReadPriority, yield_to_current


class RecognitionPriorityTests(unittest.TestCase):
    def test_current_read_precedes_old_continuation_and_failure_releases_it(self):
        for fails in (False, True):
            with self.subTest(fails=fails):
                priority = ReadPriority();order = [];errors = []
                entered = threading.Event();proceed = threading.Event();waiting = threading.Event()
                priority.register(1, 10)
                def old():
                    try:
                        with priority.read(1):
                            entered.set();proceed.wait(2);waiting.set()
                            yield_to_current();order.append('old')
                    except BaseException as error:errors.append(error)
                worker = threading.Thread(target=old);worker.start()
                self.assertTrue(entered.wait(2))
                priority.register(2, 20);proceed.set()
                try:
                    with priority.read(2):
                        self.assertTrue(waiting.wait(2))
                        self.assertEqual(order, [])
                        order.append('current')
                        if fails:raise ValueError('failed current read')
                except ValueError:
                    self.assertTrue(fails)
                worker.join(2)
                self.assertFalse(worker.is_alive())
                self.assertFalse(errors)
                self.assertEqual(order, ['current', 'old'])
                self.assertEqual(priority.pending, {})
                yield_to_current()  # A HUD worker outside this scope never waits.


if __name__ == '__main__':unittest.main()
