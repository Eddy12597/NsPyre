# ti_draw_mock.py
import turtle
from typing import Union, List, Tuple

# Internal state
_color = (0, 0, 0)  # RGB 0-255
_pen_thickness = "thin"
_pen_style = "solid"
_buffer_mode = False
_buffer_actions = []
_screen_dim = [318, 212]

# Setup turtle screen
_screen = turtle.Screen()
_screen.setup(width=_screen_dim[0] + 20, height=_screen_dim[1] + 20)
_screen.setworldcoordinates(-_screen_dim[0]//2, -_screen_dim[1]//2,
                             _screen_dim[0]//2, _screen_dim[1]//2)
_screen.tracer(0, 0)  # manual update control
_t = turtle.Turtle()
_t.hideturtle()
_t.speed(0)
_t.penup()


# ---------------- Utility ----------------

def _apply_pen():
    widths = {"thin": 1, "medium": 3, "thick": 5}
    _t.pensize(widths.get(_pen_thickness, 1))
    rgb: Tuple[float, float, float] = (
        _color[0] / 255.0,
        _color[1] / 255.0,
        _color[2] / 255.0
    )
    _t.pencolor(rgb)
    # Turtle doesn't support dashed easily, so we emulate dotted/dashed manually if needed


def _run_or_buffer(func, *args, **kwargs):
    if _buffer_mode:
        _buffer_actions.append((func, args, kwargs))
    else:
        func(*args, **kwargs)


def _draw_line_impl(x1, x2, y1, y2):
    _apply_pen()
    _t.penup()
    _t.goto(x1, y1)
    _t.pendown()
    _t.goto(x2, y2)
    _t.penup()


def _draw_rect_impl(x1, x2, y1, y2, fill=False):
    _apply_pen()
    if fill:
        _t.begin_fill()
    _t.penup()
    _t.goto(x1, y1)
    _t.pendown()
    _t.goto(x2, y1)
    _t.goto(x2, y2)
    _t.goto(x1, y2)
    _t.goto(x1, y1)
    if fill:
        _t.end_fill()
    _t.penup()


def _draw_circle_impl(x, y, radius, fill=False):
    _apply_pen()
    _t.penup()
    _t.goto(x, y - radius)
    _t.setheading(0)
    _t.pendown()
    if fill:
        _t.begin_fill()
    _t.circle(radius)
    if fill:
        _t.end_fill()
    _t.penup()


def _draw_text_impl(x, y, text):
    _apply_pen()
    _t.penup()
    _t.goto(x, y)
    _t.write(text, align="left", font=("Arial", 12, "normal"))


def _draw_arc_impl(x, y, width, height, startAngle, arcAngle, fill=False):
    # Turtle can't draw ellipses directly — we'll approximate
    _apply_pen()
    _t.penup()
    _t.goto(x, y)
    _t.setheading(startAngle)
    steps = 36
    angle_step = arcAngle / steps
    if fill:
        _t.begin_fill()
    _t.pendown()
    for _ in range(steps):
        _t.forward(width * 0.5 * 3.1415 / steps)  # crude approximation
        _t.left(angle_step)
    if fill:
        _t.end_fill()
    _t.penup()


def _draw_poly_impl(xlist, ylist, fill=False):
    if len(xlist) != len(ylist):
        raise ValueError("xlist and ylist must have same length")
    _apply_pen()
    if fill:
        _t.begin_fill()
    _t.penup()
    _t.goto(xlist[0], ylist[0])
    _t.pendown()
    for i in range(1, len(xlist)):
        _t.goto(xlist[i], ylist[i])
    _t.goto(xlist[0], ylist[0])
    if fill:
        _t.end_fill()
    _t.penup()


# ---------------- Public API ----------------

def draw_line(x1, x2, y1, y2):
    _run_or_buffer(_draw_line_impl, x1, x2, y1, y2)


def draw_rect(x, y, width, height):
    _run_or_buffer(_draw_rect_impl, x, x + width, y, y + height, False)


def fill_rect(x, y, width, height):
    _run_or_buffer(_draw_rect_impl, x, x + width, y, y + height, True)


def draw_circle(x, y, radius):
    _run_or_buffer(_draw_circle_impl, x, y, radius, False)


def fill_circle(x, y, radius):
    _run_or_buffer(_draw_circle_impl, x, y, radius, True)


def draw_text(x, y, text: str):
    _run_or_buffer(_draw_text_impl, x, y, text)


def draw_arc(x, y, width, height, startAngle, arcAngle):
    _run_or_buffer(_draw_arc_impl, x, y, width, height, startAngle, arcAngle, False)


def fill_arc(x, y, width, height, startAngle, arcAngle):
    _run_or_buffer(_draw_arc_impl, x, y, width, height, startAngle, arcAngle, True)


def draw_poly(xlist: List[Union[int, float]], ylist: List[Union[int, float]]):
    _run_or_buffer(_draw_poly_impl, xlist, ylist, False)


def fill_poly(xlist: List[Union[int, float]], ylist: List[Union[int, float]]):
    _run_or_buffer(_draw_poly_impl, xlist, ylist, True)


def plot_xy(x, y, mode: int = 1):
    _run_or_buffer(_draw_circle_impl, x, y, 1, True)


def clear():
    _t.clear()
    _screen.update()



def clear_rect(x, y, width, height):
    global _color
    old_color = _color
    set_color(255, 255, 255)
    fill_rect(x, y, width, height)
    _color = old_color
    _apply_pen()
    _screen.update()



def set_color(*args: Union[int, Tuple[int, int, int]]):
    global _color
    r: int
    g: int
    b: int
    if len(args) == 1 and isinstance(args[0], tuple):
        # Explicitly unpack into a typed tuple
        rgb_tuple: Tuple[int, int, int] = args[0]
        r, g, b = rgb_tuple
    elif len(args) == 3:
        r, g, b = args  # type: ignore[arg-type]
    else:
        raise ValueError("set_color() expects either (r,g,b) or ((r,g,b),)")

    _color = (
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b)))
    )
    _apply_pen()


def set_pen(thickness: str, style: str):
    global _pen_thickness, _pen_style
    _pen_thickness = thickness
    _pen_style = style
    _apply_pen()


def set_window(xmin, xmax, ymin, ymax):
    _screen.setworldcoordinates(xmin, ymin, xmax, ymax)


def get_screen_dim() -> List[int]:
    return list(_screen_dim)


def use_buffer():
    global _buffer_mode
    _buffer_mode = True


def paint_buffer():
    global _buffer_mode
    for func, args, kwargs in _buffer_actions:
        func(*args, **kwargs)
    _buffer_actions.clear()
    _buffer_mode = False
    _screen.update()
