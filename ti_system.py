# ti_system.py
import time
import sys

import pygame

pygame.init()
# pygame.display.set_mode((1,1))


# Internal storage to simulate TI-Nspire's variable store
_variable_store = {}

# Record boot time to simulate system clock behavior
_boot_time = time.time()


def recall_value(name: str):
    """Recalls the value of a variable stored in TI-Nspire."""
    return _variable_store.get(name)


def store_value(name: str, value):
    """Stores the value into TI-Nspire's variable store."""
    _variable_store[name] = value


def recall_list(name: str):
    """Recalls a list[int|float] from TI-Nspire's variable store."""
    val = _variable_store.get(name)
    if isinstance(val, list) and all(isinstance(x, (int, float)) for x in val):
        return val
    raise TypeError(f"Variable '{name}' is not a list of int/float")


def store_list(name: str, _list):
    """Stores a list[int|float] into TI-Nspire's variable store."""
    if not isinstance(_list, list) or not all(isinstance(x, (int, float)) for x in _list):
        raise TypeError("_list must be a list of int or float")
    _variable_store[name] = _list


def eval_function(name: str, value):
    """
    Calls a TI-Nspire function of one variable.
    Here we simulate this by looking for a Python callable stored under `name`.
    """
    func = _variable_store.get(name)
    if callable(func):
        return func(value)
    raise ValueError(f"No callable function stored under '{name}'")


def get_platform():
    """Returns 'hh' to indicate handheld."""
    return "hh"

# if sys.platform == "win32":
#     import msvcrt
#     def get_key():
#         return msvcrt.getch().decode()
# else:
#     import termios, tty
#     def get_key():
#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)  # type: ignore
#         try:
#             tty.setraw(fd)  # type: ignore
#             ch = sys.stdin.read(1)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # type: ignore
#         return ch



def get_time_ms():
    """
    Returns the current system clock (milliseconds since boot).
    Boot time is when this module was first imported.
    """
    return int((time.time() - _boot_time) * 1000)

# Map pygame keys to TI key names
_keymap = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_RETURN: "enter",
    pygame.K_ESCAPE: "esc",
    pygame.K_SPACE: " ",
    pygame.K_BACKSPACE: "del",
    pygame.K_a: "a",
    pygame.K_b: "b",
    pygame.K_c: "c",
    pygame.K_d: "d",
    pygame.K_e: "e",
    pygame.K_f: "f",
    pygame.K_g: "g",
    pygame.K_h: "h",
    pygame.K_i: "i",
    pygame.K_j: "j",
    pygame.K_k: "k",
    pygame.K_l: "l",
    pygame.K_m: "m",
    pygame.K_n: "n",
    pygame.K_o: "o",
    pygame.K_p: "p",
    pygame.K_q: "q",
    pygame.K_r: "r",
    pygame.K_s: "s",
    pygame.K_t: "t",
    pygame.K_u: "u",
    pygame.K_v: "v",
    pygame.K_w: "w",
    pygame.K_x: "x",
    pygame.K_y: "y",
    pygame.K_z: "z",
    pygame.K_0: "0",
    pygame.K_1: "1",
    pygame.K_2: "2",
    pygame.K_3: "3",
    pygame.K_4: "4",
    pygame.K_5: "5",
    pygame.K_6: "6",
    pygame.K_7: "7",
    pygame.K_8: "8",
    pygame.K_9: "9",

}

_last_key = None

def poll_events():
    """Polls pygame events and updates _last_key (called from ti_draw.update)."""
    global _last_key
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key in _keymap:
                _last_key = _keymap[event.key]

def _get_key_from_stdin() -> str:
    # Pygame not initialized → fallback to terminal input
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            # decode byte to string
            try:
                return ch.decode("utf-8")
            except:
                return ""
        else:
            return ""
    else:
        # Unix fallback
        import tty, termios
        import select
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if dr:
                ch = sys.stdin.read(1)
                return ch
            else:
                return ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
def _get_key_from_pygame(blocking=False) -> str:
    """
    Returns the last pressed key as a string (e.g. 'up', 'a').
    If blocking=True, waits until a key is pressed.
    If blocking=False, returns None if no key was pressed.
    """
    global _last_key
    if blocking:
        # spin until key available
        while True:
            poll_events()
            if _last_key is not None:
                k = _last_key
                _last_key = None
                return k
            time.sleep(0.005)
    else: # This is the TI Nspire way.
        poll_events()
        if _last_key is not None:
            k = _last_key
            _last_key = None
            return k
        return "" # not None!

def get_key() -> str:
    try:
        k = _get_key_from_pygame()
        if k == "":  # pygame active but no window/no focus/no events
            return _get_key_from_stdin()
        return k
    except pygame.error as e:
        if "video system not initialized" in str(e).lower():
            return _get_key_from_stdin()
        raise
