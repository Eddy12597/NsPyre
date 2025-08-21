"""
TI-PlotLib (ti_draw/pygame-backed)
---------------------------------
A thin plotting layer that sits on top of your `ti_draw_pygame.py` module
and exposes a TI-like `ti_plotlib` API (commonly imported as `plt`).

Notes / deviations from real TI:
- Text is not rotated; y-axis label is placed horizontally at one of three
  horizontal anchors (left third / center / right third).
- Dashed / dotted lines are approximated in pixel space.
- Draw order is exactly the call order unless you use buffering.
  If you need the grid/axes behind your data, call `grid()` and `axes()`
  *before* `plot()` / `scatter()`.
- `show_plot()` always blits & updates the screen (even if not in buffer mode).
"""

from typing import Iterable, List, Sequence, Tuple, Union, Optional
import math

# Import your pygame-backed drawing shim
import ti_draw as d

Number = Union[int, float]

# --------------------------- Module State ---------------------------

# Public properties (kept in sync with current window / regression calls)
xmin: Number = 0
xmax: Number = 318
ymin: Number = 0
ymax: Number = 212
m: Optional[float] = None
b: Optional[float] = None

# Local state
_current_color: Tuple[int, int, int] = (0, 0, 0)
_current_pen: Tuple[str, str] = ("thin", "solid")  # (thickness, style)

# Cached screen metrics
_scr_w, _scr_h = d.get_screen_dim()

# --------------------------- Utilities -----------------------------

def _set_window_state(xmn: Number, xmx: Number, ymn: Number, ymx: Number) -> None:
    global xmin, xmax, ymin, ymax
    xmin, xmax, ymin, ymax = xmn, xmx, ymn, ymx


def _world_to_pixel(x: Number, y: Number) -> Tuple[float, float]:
    """Map world coords -> pixel coords using current window state."""
    wx = (x - xmin) / (xmax - xmin) * _scr_w
    wy = _scr_h - (y - ymin) / (ymax - ymin) * _scr_h
    return wx, wy


def _pixel_to_world(px: float, py: float) -> Tuple[float, float]:
    """Map pixel coords -> world coords using current window state."""
    x = xmin + (px / _scr_w) * (xmax - xmin)
    y = ymin + ((_scr_h - py) / _scr_h) * (ymax - ymin)
    return x, y


def _px_dx_to_world(dx_px: float) -> float:
    return (dx_px / _scr_w) * (xmax - xmin)


def _px_dy_to_world(dy_px: float) -> float:
    return (dy_px / _scr_h) * (ymax - ymin)


def _is_seq(obj) -> bool:
    return isinstance(obj, (list, tuple))


def _pairwise(seq: Sequence[Number]):
    for i in range(len(seq) - 1):
        yield seq[i], seq[i + 1]


def _with_temp_color(rgb: Tuple[int, int, int]):
    """Context-like helper: temporarily set color, then restore."""
    class _C:
        def __enter__(self):
            global _current_color
            self._old = _current_color
            color(*rgb)
            return self
        def __exit__(self, exc_type, exc, tb):
            color(*self._old)
    return _C()


def _with_temp_pen(thickness: str, style: str):
    class _C:
        def __enter__(self):
            global _current_pen
            self._old = _current_pen
            pen(thickness, style)
            return self
        def __exit__(self, exc_type, exc, tb):
            pen(*self._old)
    return _C()


def _draw_dashed_or_dotted_line(x1: Number, y1: Number, x2: Number, y2: Number, style: str):
    """Draw line with pixel-space dash/dot style."""
    p1x, p1y = _world_to_pixel(x1, y1)
    p2x, p2y = _world_to_pixel(x2, y2)

    dx = p2x - p1x
    dy = p2y - p1y
    length = math.hypot(dx, dy)
    if length == 0:
        d.plot_xy(x1, y1)
        return

    ux, uy = dx / length, dy / length  # unit vector in pixels

    if style == "dotted":
        step = 5.0
        r_px = 1.0
        t = 0.0
        while t <= length:
            px = p1x + ux * t
            py = p1y + uy * t
            wx, wy = _pixel_to_world(px, py)
            d.fill_circle(wx, wy, int(r_px))
            t += step
    else:  # dashed or default to dashed
        on = 8.0
        off = 6.0
        t = 0.0
        draw_on = True
        while t < length:
            seg = min(on if draw_on else off, length - t)
            sx = p1x + ux * t
            sy = p1y + uy * t
            ex = p1x + ux * (t + seg)
            ey = p1y + uy * (t + seg)
            if draw_on:
                (sxw, syw) = _pixel_to_world(sx, sy)
                (exw, eyw) = _pixel_to_world(ex, ey)
                d.draw_line(sxw, exw, syw, eyw)
            draw_on = not draw_on
            t += seg


def _draw_line_with_style(x1: Number, y1: Number, x2: Number, y2: Number, style: str):
    style = (style or "solid").lower()
    if style in ("solid", "default"):
        d.draw_line(x1, x2, y1, y2)
    elif style in ("dashed", "dotted"):
        _draw_dashed_or_dotted_line(x1, y1, x2, y2, style)
    else:
        d.draw_line(x1, x2, y1, y2)


def _draw_arrowhead(x1: Number, y1: Number, x2: Number, y2: Number, size_px: int = 8, angle_deg: float = 28.0):
    # Work in pixel space for geometry
    x1p, y1p = _world_to_pixel(x1, y1)
    x2p, y2p = _world_to_pixel(x2, y2)
    dx, dy = x2p - x1p, y2p - y1p
    theta = math.atan2(dy, dx)
    phi = math.radians(angle_deg)

    for sign in (+1, -1):
        ang = theta + sign * phi
        hx = x2p - size_px * math.cos(ang)
        hy = y2p - size_px * math.sin(ang)
        (wx1, wy1) = _pixel_to_world(x2p, y2p)
        (wx2, wy2) = _pixel_to_world(hx, hy)
        d.draw_line(wx1, wx2, wy1, wy2)


# --------------------------- Public API -----------------------------

# SETUP SECTION

def cls() -> None:
    """Clear the screen (and immediately update)."""
    d.clear()


def window(x_min: Number, x_max: Number, y_min: Number, y_max: Number) -> None:
    """Set the world window (also stored in public properties)."""
    if x_max == x_min:
        x_max = x_min + 1
    if y_max == y_min:
        y_max = y_min + 1
    d.set_window(x_min, x_max, y_min, y_max)
    _set_window_state(x_min, x_max, y_min, y_max)


def auto_window(x_list: Sequence[Number], y_list: Sequence[Number], pad: float = 0.02) -> None:
    """Auto-fit window to data with ~2% padding (per axis)."""
    if len(x_list) == 0 or len(x_list) != len(y_list):
        raise ValueError("auto_window: x_list and y_list must be non-empty and equal length.")
    xmn, xmx = min(x_list), max(x_list)
    ymn, ymx = min(y_list), max(y_list)
    # Avoid degenerate window
    if xmx == xmn:
        dx = max(1.0, abs(xmx) * 0.1 + 1.0)
        xmn -= dx
        xmx += dx
    if ymx == ymn:
        dy = max(1.0, abs(ymx) * 0.1 + 1.0)
        ymn -= dy
        ymx += dy
    # Padding
    dx = (xmx - xmn)
    dy = (ymx - ymn)
    xpad = dx * pad
    ypad = dy * pad
    window(xmn - xpad, xmx + xpad, ymn - ypad, ymx + ypad)


# Grid / Axes / Labels / Title state is minimal: we draw immediately.

def grid(x_scale: Number, y_scale: Number, style: str = "dotted") -> None:
    """Draw grid lines across the current window.
    `style` in {"dotted", "dashed", "solid"}.
    """
    if x_scale <= 0 or y_scale <= 0:
        return
    # Draw with light gray; restore afterward
    with _with_temp_color((200, 200, 200)):
        # Vertical lines
        start = math.ceil(xmin / x_scale) * x_scale
        x = start
        while x <= xmax:
            _draw_line_with_style(x, ymin, x, ymax, style)
            x += x_scale
        # Horizontal lines
        start = math.ceil(ymin / y_scale) * y_scale
        y = start
        while y <= ymax:
            _draw_line_with_style(xmin, y, xmax, y, style)
            y += y_scale


def axes(mode: str = "axes") -> None:
    """Draw axes.
    modes:
      - "off": do nothing
      - "on" or "axes": draw x=0 and y=0 if they intersect the window
      - "window": draw the window bounding box
    """
    mode = (mode or "axes").lower()
    if mode == "off":
        return
    if mode in ("on", "axes"):
        if xmin <= 0 <= xmax:
            d.draw_line(0, 0, ymin, ymax)
        if ymin <= 0 <= ymax:
            d.draw_line(xmin, xmax, 0, 0)
    elif mode == "window":
        d.draw_rect(xmin, ymin, xmax - xmin, ymax - ymin)


# Labels & title ------------------------------------------------------

def labels(x_label: str, y_label: str, x_row: int = 15, y_row: int = 2) -> None:
    """Place axis labels.
    - x_row: integer 0..15 (0=top, 15=bottom). Text placed at that row, centered.
    - y_row: 1, 2, 3 -> place at left third / center / right third horizontally,
             vertically centered in the plot. (Text is horizontal; no rotation.)
    """
    x_row = int(max(0, min(15, x_row)))
    # X label centered at the given row
    text_at(x_row, x_label, align="center")

    # Y label: horizontal at requested horizontal third
    third = {1: _scr_w * (1 / 3), 2: _scr_w * 0.5, 3: _scr_w * (2 / 3)}.get(int(y_row), _scr_w * 0.5)
    px = float(third)
    py = float(_scr_h * 0.5)
    wx, wy = _pixel_to_world(px, py)
    d.draw_text(wx, wy, y_label)


def title(text: str) -> None:
    """Place a title on the top row (row 0), centered."""
    text_at(0, text, align="center")


def show_plot() -> None:
    """Flush to the screen. Always blits/updates even if not in buffer mode."""
    d.paint_buffer()


def use_buffer() -> None:
    """Enable ti_draw's buffering (subsequent draws queue until `show_plot()`)."""
    d.use_buffer()


# DRAW SECTION --------------------------------------------------------

def color(red: int, green: int, blue: int) -> None:
    global _current_color
    _current_color = (int(red), int(green), int(blue))
    d.set_color(_current_color)


def pen(size: str = "thin", style: str = "solid") -> None:
    """Set pen size/thickness and preferred style for our own helpers."""
    global _current_pen
    size = (size or "thin").lower()
    style = (style or "solid").lower()
    _current_pen = (size, style)
    d.set_pen(size, style)


def scatter(x_list: Sequence[Number], y_list: Sequence[Number], mark: str = ".") -> None:
    if len(x_list) != len(y_list):
        raise ValueError("scatter: x_list and y_list must have equal length.")
    for x, y in zip(x_list, y_list):
        _draw_mark(x, y, mark)


def plot(x: Union[Number, Sequence[Number]], y: Union[Number, Sequence[Number]], mark: str = ".") -> None:
    """If sequences are provided, connect them; if scalars, just plot a single mark."""
    if _is_seq(x) and _is_seq(y):
        xs: Sequence[Number] = x  # type: ignore
        ys: Sequence[Number] = y  # type: ignore
        if len(xs) != len(ys):
            raise ValueError("plot: x and y sequences must have equal length.")
        # Connect points
        line_style = _current_pen[1]
        for (x1, x2), (y1, y2) in zip(_pairwise(xs), _pairwise(ys)):
            _draw_line_with_style(x1, y1, x2, y2, line_style)
        # Draw marks
        if mark:
            for xi, yi in zip(xs, ys):
                _draw_mark(xi, yi, mark)
    else:
        # Single point
        xi = x if not _is_seq(x) else x[0]  # type: ignore
        yi = y if not _is_seq(y) else y[0] # type: ignore
        _draw_mark(xi, yi, mark)


def line(x1: Number, y1: Number, x2: Number, y2: Number, mode: str = "default") -> None:
    style = _current_pen[1]
    _draw_line_with_style(x1, y1, x2, y2, style)
    if (mode or "default").lower() == "arrow":
        _draw_arrowhead(x1, y1, x2, y2)


def lin_reg(x_list: Sequence[Number], y_list: Sequence[Number], display: str = "left") -> Tuple[float, float]:
    """Least-squares linear regression. Draw the fit line and print the equation.
    Returns (m, b).
    display in {"left","center","right"} controls where the text is placed on row 1.
    """
    if len(x_list) != len(y_list) or len(x_list) == 0:
        raise ValueError("lin_reg: x_list and y_list must be non-empty and same length.")

    n = float(len(x_list))
    sx = sum(float(x) for x in x_list)
    sy = sum(float(y) for y in y_list)
    sxx = sum(float(x) * float(x) for x in x_list)
    sxy = sum(float(x) * float(y) for x, y in zip(x_list, y_list))

    denom = n * sxx - sx * sx
    if denom == 0:
        mm = 0.0
        bb = float(y_list[0]) if n > 0 else 0.0
    else:
        mm = (n * sxy - sx * sy) / denom
        bb = (sy - mm * sx) / n

    # Store in public props
    global m, b
    m, b = mm, bb

    # Draw fit line across current window
    y1 = mm * xmin + bb
    y2 = mm * xmax + bb
    with _with_temp_pen(_current_pen[0], "solid"):
        d.draw_line(xmin, xmax, y1, y2)

    # Render text
    eq = f"y = {mm:.4g}x + {bb:.4g}"
    align = (display or "left").lower()
    row = 1
    if align not in ("left", "center", "right"):
        align = "left"
    text_at(row, eq, align)

    return mm, bb


def text_at(row: int, text: str, align: str = "left") -> None:
    """Draw text at screen row (0..15), aligned left/center/right.
    Text baseline is placed near the top of the row.
    """
    row = int(max(0, min(15, row)))
    align = (align or "left").lower()

    # Compute pixel position
    row_h = _scr_h / 16.0
    py = row * row_h + 2  # a slight margin from the top of the band

    if align == "left":
        px = 6
    elif align == "center":
        px = _scr_w / 2
    else:  # right
        px = _scr_w - 6

    # Convert to world & draw
    wx, wy = _pixel_to_world(px, py)
    # For right alignment, pygame font doesn't know; approximate by shifting left by text width
    # (We don't have direct text width; keep it simple and rely on anchor approximation.)
    d.draw_text(wx, wy, text)


# MARKERS ------------------------------------------------------------

def _draw_mark(x: Number, y: Number, mark: str) -> None:
    mark = (mark or ".").lower()
    # Marker sizes in pixels
    if mark == ".":
        d.fill_circle(x, y, 1)
    elif mark == "o":
        d.fill_circle(x, y, 2)
    elif mark == "+":
        dxw = _px_dx_to_world(3)
        dyw = _px_dy_to_world(3)
        d.draw_line(x - dxw, x + dxw, y, y)
        d.draw_line(x, x, y - dyw, y + dyw)
    elif mark == "x":
        dxw = _px_dx_to_world(3)
        dyw = _px_dy_to_world(3)
        d.draw_line(x - dxw, x + dxw, y - dyw, y + dyw)
        d.draw_line(x - dxw, x + dxw, y + dyw, y - dyw)
    else:
        # Fallback to a small filled circle
        d.fill_circle(x, y, 2)


# Aliases for convenience -------------------------------------------
# Keep TI-like names if you prefer

# Expose properties in module namespace (already defined at top)
__all__ = [
    # properties
    "xmin", "xmax", "ymin", "ymax", "m", "b",
    # setup
    "cls", "window", "auto_window", "grid", "axes", "labels", "title", "show_plot", "use_buffer",
    # draw
    "color", "pen", "scatter", "plot", "line", "lin_reg", "text_at",
]
