# ti_system_mock.py
import time
import sys
import termios
import tty
import sys

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

if sys.platform == "win32":
    import msvcrt
    def get_key():
        return msvcrt.getch().decode()
else:
    import termios, tty
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)  # type: ignore
        try:
            tty.setraw(fd)  # type: ignore
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # type: ignore
        return ch



def get_time_ms():
    """
    Returns the current system clock (milliseconds since boot).
    Boot time is when this module was first imported.
    """
    return int((time.time() - _boot_time) * 1000)


# get_mouse intentionally omitted as per request
