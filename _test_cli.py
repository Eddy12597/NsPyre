import threading
from cli import *

def threaded_input(cli_instance, prompt):
    """
    Runs cli.getInput in a separate thread.
    Returns the result in a thread-safe way.
    """
    result_container = {"result": None}

    def target():
        result_container["result"] = cli_instance.getInput(prompt)

    t = threading.Thread(target=target)
    t.start()
    return t, result_container


c = cli({"user_name": "root"}, {})

# Start input in a separate thread
thread, container = threaded_input(c, c.getPrefix())

# Meanwhile, the main thread can keep turtle responsive
while thread.is_alive():
    d.paint_buffer()  # or any other GUI updates
    t.sleep(0.01)

# When done
user_input = container["result"]
print("User entered:", user_input)
