# test_ti_system.py
import unittest
import time
import types
import builtins

import ti_system as tis

class TestTiSystem(unittest.TestCase):
    def setUp(self):
        # Reset state before each test
        tis._variable_store.clear()
        tis._last_key = None

    def test_store_and_recall_value(self):
        tis.store_value("x", 42)
        self.assertEqual(tis.recall_value("x"), 42)
        self.assertIsNone(tis.recall_value("y"))  # missing key

    def test_store_and_recall_list(self):
        data = [1, 2.5, 3]
        tis.store_list("arr", data)
        self.assertEqual(tis.recall_list("arr"), data)

    def test_recall_list_type_error(self):
        tis.store_value("bad", "notalist")
        with self.assertRaises(TypeError):
            tis.recall_list("bad")

    def test_store_list_invalid_type(self):
        with self.assertRaises(TypeError):
            tis.store_list("badlist", [1, "a", 3])

    def test_eval_function_success(self):
        def f(x): return x * 2
        tis.store_value("f", f)
        self.assertEqual(tis.eval_function("f", 3), 6)

    def test_eval_function_not_callable(self):
        tis.store_value("f", 123)
        with self.assertRaises(ValueError):
            tis.eval_function("f", 3)

    def test_get_platform(self):
        self.assertEqual(tis.get_platform(), "hh")

    def test_get_time_ms_increases(self):
        t1 = tis.get_time_ms()
        time.sleep(0.01)
        t2 = tis.get_time_ms()
        self.assertGreaterEqual(t2, t1)

    def test_poll_events_and_get_key(self):
        # Monkeypatch pygame.event.get
        class FakeEvent:
            def __init__(self, type, key=None):
                self.type = type
                self.key = key
        events = [FakeEvent(tis.pygame.KEYDOWN, tis.pygame.K_a)]
        tis.pygame.event.get = lambda: events
        tis.poll_events()
        self.assertEqual(tis._last_key, "a")

        # Now test _get_key_from_pygame
        k = tis._get_key_from_pygame()
        self.assertEqual(k, "a")

    def test_get_key_nonblocking_returns_empty(self):
        tis.pygame.event.get = lambda: []
        self.assertEqual(tis.get_key(), "")

    def test_get_key_blocking(self):
        # Make poll_events provide a key once
        def fake_event_get():
            # first call → event, next → none
            if not hasattr(fake_event_get, "called"):
                fake_event_get.called = True
                return [types.SimpleNamespace(type=tis.pygame.KEYDOWN, key=tis.pygame.K_b)]
            return []
        tis.pygame.event.get = fake_event_get
        k = tis._get_key_from_pygame(blocking=True)
        self.assertEqual(k, "b")

    def test_get_key_falls_back_on_video_error(self):
        # Force pygame.error with "video system not initialized"
        def raise_error():
            raise tis.pygame.error("video system not initialized")
        old = tis._get_key_from_pygame
        tis._get_key_from_pygame = lambda blocking=False: raise_error()

        # Patch _get_key_from_stdin to return "x"
        tis._get_key_from_stdin = lambda: "x"
        result = tis.get_key()
        self.assertEqual(result, "x")

        tis._get_key_from_pygame = old  # restore

if __name__ == "__main__":
    unittest.main()
