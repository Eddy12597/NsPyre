from cli import *

c = cli({"user_name": "root"}, {})


inp = c.getInput("Hello, Enter something: ")
print(inp)