import ti_system as tis
from format import *

class Logger:
    def __init__(self, filename=__file__):
        self._filename = filename
        self._start_time = tis.get_time_ms()
        self._idx = 0
        self._disabled = False
        self._log_messages = []
        self._call_stack = []
        self._indent_level = 0

    def _basename(self):
      """Return filename without path or extension."""
      # Handle both forward and backward slashes (compatibility with testing on Windows)
      fname = self._filename.replace("\\", "/").split("/")[-1]
      return fname[:-3] if fname.endswith(".py") else fname

    def _log(self, msg):
        if self._disabled:
            return
        entry = f"{self._idx}: {self._basename()}: {tis.get_time_ms() - self._start_time}ms: {msg}"
        self._log_messages.append(entry)
        self._idx += 1

    def set_fn(self, name): # for compatibility
        self._filename = name

    def enable(self):
        self._disabled = False

    def disable(self):
        self._disabled = True

    # ===== Basic Logging =====
    def raw(self, *args):
        for a in args:
            self._log(a)

    def info(self, *args):
        for a in args:
            self._log(F("[info] %v", a))

    def warn(self, *args):
        for a in args:
            self._log(F("[warn] %v", a))

    def fatal(self, *args):
        for a in args:
            self._log(F("[fatal] %v", a))

    def cus(self, level, *args):
        for a in args:
            self._log(F("[%v] %v", level, a))

    # ===== Call Stack =====
    def call(self, fn_name, *args):
        self._call_stack.append(fn_name)
        indent = "  " * self._indent_level
        self.cus("fn", f"{indent}fn: {fn_name} {args}")
        self._indent_level += 1

    def end(self, retval=None):
        if not self._call_stack:
            self.warn("call stack already empty")
            return
        self._indent_level -= 1
        indent = "  " * self._indent_level
        fn_name = self._call_stack.pop()
        self.cus("fn", F("%vend fn: %v -> %v", indent, fn_name, retval))

    def stack(self):
        for s in self._call_stack:
            print(s)

    def clear_stack(self):
        self._call_stack.clear()

    # ===== Viewing Logs =====
    def show(self, page_size=10):
        print("=====+++++==           LOGS           ==+++++=====")
        idx = 0
        while idx < len(self._log_messages):
            for i in range(idx, min(idx+page_size, len(self._log_messages))):
                print(self._log_messages[i])
            idx += page_size
            cont = input("-- More -- (q to quit) ")
            if cont.lower() in ["q", "quit", "exit", "esc"]:
                break
        print("=====+++++==    END OF LOGS    ==+++++=====")

    # ===== Filtering =====
    def filter(self, level):
        """Return logs matching a level like 'info', 'warn', 'fatal'."""
        level_tag = f"[{level}]"
        return [m for m in self._log_messages if level_tag in m]


# ===== Usage =====
lg = Logger()
lg.info("logging set up")
