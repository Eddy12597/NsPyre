# test_ti_draw_basic.py
import unittest
import ti_draw as td

class TestTIDraw(unittest.TestCase):

    def setUp(self):
        # Always start fresh
        td.clear()
        td.set_color(0, 0, 0)
        td.set_pen("thin", "solid")

    def test_draw_primitives(self):
        # These should not raise exceptions
        td.draw_line(0, 100, 0, 100)
        td.draw_rect(0, 50, 0, 50)
        td.fill_rect(10, 60, 10, 60)
        td.draw_circle(0, 0, 20)
        td.fill_circle(10, 10, 15)
        td.draw_text(0, 0, "Hello")
        td.draw_arc(0, 0, 50, 50, 0, 90)
        td.fill_arc(0, 0, 40, 40, 90, 180)
        td.draw_poly([0, 50, 50], [0, 0, 50])
        td.fill_poly([0, 50, 50], [0, 0, 50])
        td.plot_xy(10, 10)

    def test_color_setting(self):
        td.set_color(255, 0, 0)
        self.assertEqual(td._color, (255, 0, 0))
        td.set_color((0, 255, 0))
        self.assertEqual(td._color, (0, 255, 0))

    def test_pen_setting(self):
        td.set_pen("medium", "dashed")
        self.assertEqual(td._pen_thickness, "medium")
        self.assertEqual(td._pen_style, "dashed")

    def test_screen_dim(self):
        dims = td.get_screen_dim()
        self.assertEqual(dims, [318, 212])

    def test_buffer_usage(self):
        td.use_buffer()
        td.draw_line(0, 50, 0, 50)  # Should be stored in buffer
        self.assertTrue(len(td._buffer_actions) > 0)
        td.paint_buffer()  # Flush buffer
        self.assertEqual(len(td._buffer_actions), 0)

    def test_clear_and_clear_rect(self):
        td.draw_rect(0, 100, 0, 100)
        td.clear()
        td.draw_rect(0, 100, 0, 100)
        td.clear_rect(10, 10, 50, 50)  # Can't verify visually, but should not crash


if __name__ == "__main__":
    unittest.main()
