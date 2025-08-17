# ti_draw_pygame.py
import pygame
from typing import Union, List, Tuple
import math

# ---------------- Initialization ----------------
pygame.init()
_screen_dim = [318, 212]
_screen = pygame.display.set_mode(_screen_dim)
_surface = pygame.Surface(_screen_dim)

# Internal state
_color = (0, 0, 0)
_pen_thickness = "thin"
_pen_style = "solid"
_buffer_mode = False
_buffer_actions = []

# Map pen thickness
_pen_widths = {"thin": 1, "medium": 3, "thick": 5}

# Font for draw_text
_font = pygame.font.SysFont("Arial", 12)

# Window defaults
_window_coords = [0, 318, 0, 212]  # xmin, xmax, ymin, ymax
_screen_dim = [318, 212]  # in pixels


# ---------------- Utility Functions ----------------

def _apply_pen():
    global _pen_widths
    width = _pen_widths.get(_pen_thickness, 1)
    return width

def _run_or_buffer(func, *args, **kwargs):
    if _buffer_mode:
        _buffer_actions.append((func, args, kwargs))
    else:
        func(*args, **kwargs)

# ---------------- Primitive Drawing ----------------

def _color_val():
    """Return pygame.Color object from _color tuple"""
    return pygame.Color(*_color)

def _draw_line_impl(x1, x2, y1, y2):
    x1, y1 = _map_coords(x1, y1)
    x2, y2 = _map_coords(x2, y2)
    width = _apply_pen()
    pygame.draw.line(_surface, _color_val(), (x1, y1), (x2, y2), width)

def _draw_rect_impl(x1, x2, y1, y2, fill=False):
    x1, y1 = _map_coords(x1, y1)
    x2, y2 = _map_coords(x2, y2)
    rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
    width = 0 if fill else _apply_pen()
    pygame.draw.rect(_surface, _color_val(), rect, width)

def _draw_circle_impl(x, y, radius, fill=False):
    x, y = _map_coords(x, y)
    width = 0 if fill else _apply_pen()
    pygame.draw.circle(_surface, _color_val(), (x, y), radius, width)

def _draw_text_impl(x, y, text):
    x, y = _map_coords(x, y)
    text_surface = _font.render(text, True, _color_val())
    _surface.blit(text_surface, (x, y))

def _draw_poly_impl(xlist, ylist, fill=False):
    points = [_map_coords(x, y) for x, y in zip(xlist, ylist)]
    width = 0 if fill else _apply_pen()
    pygame.draw.polygon(_surface, _color_val(), points, width)

def _draw_arc_impl(x, y, width, height, startAngle, arcAngle, fill=False):
    """
    Draw an elliptical arc.
    x, y = top-left of bounding rectangle
    width, height = size of ellipse
    startAngle, arcAngle in degrees
    fill = whether to fill the arc
    """
    x0, y0 = _map_coords(x, y)
    x1, y1 = _map_coords(x+width, y+height)
    width = x1 - x0
    height = y1 - y0

    rect = pygame.Rect(x, y, width, height)
    start_rad = math.radians(startAngle)
    end_rad = math.radians(startAngle + arcAngle)

    if fill:
        # Approximate filled arc using polygon with many points along the ellipse
        steps = max(6, int(abs(arcAngle)/5))  # at least 6 points
        points = [(x + width/2, y + height/2)]  # center
        for i in range(steps + 1):
            theta = start_rad + (end_rad - start_rad) * (i / steps)
            px = x + width/2 + (width/2) * math.cos(theta)
            py = y + height/2 + (height/2) * math.sin(theta)
            points.append((px, py))
        pygame.draw.polygon(_surface, _color_val(), points)
    else:
        # Unfilled arc
        pygame.draw.arc(_surface, _color_val(), rect, start_rad, end_rad, _apply_pen())

def _map_coords(x, y):
    """
    Map virtual coordinates to pixel coordinates on the Pygame surface.
    """
    xmin, xmax, ymin, ymax = _window_coords
    w, h = _screen_dim
    px = int((x - xmin) / (xmax - xmin) * w)
    py = int(h - (y - ymin) / (ymax - ymin) * h)  # invert y-axis
    return px, py


# ---------------- Public API ----------------

def draw_line(x1, x2, y1, y2):
    _run_or_buffer(_draw_line_impl, x1, x2, y1, y2)

def draw_rect(x, y, width, height):
    _run_or_buffer(_draw_rect_impl, x, x+width, y, y+height, False)

def fill_rect(x, y, width, height):
    _run_or_buffer(_draw_rect_impl, x, x+width, y, y+height, True)

def draw_circle(x, y, radius):
    _run_or_buffer(_draw_circle_impl, x, y, radius, False)

def fill_circle(x, y, radius):
    _run_or_buffer(_draw_circle_impl, x, y, radius, True)

def draw_text(x, y, text: str):
    _run_or_buffer(_draw_text_impl, x, y, text)

def draw_poly(xlist: List[Union[int,float]], ylist: List[Union[int,float]]):
    _run_or_buffer(_draw_poly_impl, xlist, ylist, False)

def fill_poly(xlist: List[Union[int,float]], ylist: List[Union[int,float]]):
    _run_or_buffer(_draw_poly_impl, xlist, ylist, True)

def plot_xy(x, y, mode: int = 1):
    _run_or_buffer(_draw_circle_impl, x, y, 1, True)

def draw_arc(x, y, width, height, startAngle, arcAngle):
    _run_or_buffer(_draw_arc_impl, x, y, width, height, startAngle, arcAngle, False)

def fill_arc(x, y, width, height, startAngle, arcAngle):
    _run_or_buffer(_draw_arc_impl, x, y, width, height, startAngle, arcAngle, True)


# ---------------- Buffering ----------------

def use_buffer():
    global _buffer_mode
    _buffer_mode = True

def paint_buffer():
    global _buffer_mode, _buffer_actions
    for func, args, kwargs in _buffer_actions:
        func(*args, **kwargs)
    _buffer_actions.clear()
    _buffer_mode = False
    _screen.blit(_surface, (0,0))
    pygame.display.update()

# ---------------- Utilities ----------------

def clear():
    _surface.fill((255,255,255))
    _screen.blit(_surface, (0,0))
    pygame.display.update()

def clear_rect(x, y, width, height):
    old_color = _color
    set_color(255, 255, 255)
    fill_rect(x, y, width, height)
    set_color(*old_color)
    _screen.blit(_surface, (0,0))
    pygame.display.update()

def set_color(*args: Union[int, Tuple[int,int,int]]):
    global _color
    if len(args) == 1 and isinstance(args[0], tuple):
        _color = args[0]
    elif len(args) == 3:
        _color = tuple(args)
    else:
        raise ValueError("set_color expects (r,g,b) or ((r,g,b),)")
        
def set_pen(thickness: str, style: str):
    global _pen_thickness, _pen_style
    _pen_thickness = thickness
    _pen_style = style

def get_screen_dim() -> List[int]:
    return list(_screen_dim)

def set_window(xmin, xmax, ymin, ymax):
    """
    Set the virtual coordinate system for drawing.
    All drawing functions should map virtual coords -> pixels.
    """
    global _window_coords
    _window_coords = [xmin, xmax, ymin, ymax]


# ---------------- Keyboard Input ----------------

def get_key():
    """Poll pygame events and return key as string if pressed"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.KEYDOWN:
            return pygame.key.name(event.key)
    return None
