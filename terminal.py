from log import *
import filesys as fs
import cli
import femto
import fileio as fio
lg.set_fn(__file__)

# 'global' has to be absolute
stdout = ""
stdin = ""
currentTask = "bash" # may be useful later
# I know using a cli renderer object for keeping track of file system is spaghetti code, but im too lazy to change anything
c = cli.cli()
sudo = True # root
users_and_pwds = {
    "root": c.passwd
}

def main():
    global stdout, stdin, currentTask, c
    c.root = fs.root
    # type of c.commands: dict[str, tuple[function, str]]
    c.commands = None #defined later, also ignore type warnings on computer

    # note that c is passed around for cmds to control the screen rendering.
    # normally, if an application does not need 
    # interactive output or file management
    # just append to stdout, else use c.display().
    def clear(c):
        c.cls()
    def ls(c, rec=False):
        global stdout
        stdout += c.cwd.dir(rec)
    def alias(c, new: str, old: str):
        global stdout
        try:
            c.commands.update({new: (c.commands[old][0], "alias of " + old)})
            lg.info(str(new) + " set as alias of " + str(old))
        except KeyError as ke:
            lg.warn("Key named " + str(old) + " not found while setting alias")
            stdout += ("KeyError: key " + str(old) + " not found while setting alias")
    def mkdir(c, name):
        c.cwd.addfolder(name)
    def rmdir(c, name):
        c.cwd.removefolder(name)
    def error(c, msg): # wait, maybe remove c as argument? but that would change too many references to c.commands["error"][0](c, msg)
        global stdout
        stdout += ("Error encountered: \n") + str(msg)

    # the help function is buggy; it outputs other things correct, but when it comes to alias,
    # it just breaks (throwing a TI-Nspire native error, not a python error).
    def help(c, msg=None) -> str: # c is not used here again.
        global stdout
        lg.call("help", msg)
        stdout += "--- Help ---\n"
        for com in c.commands.keys():
            stdout += (com + ": " + c.commands[com][1]) + "\n"
        if msg is not None:
            stdout += msg + "\n"
        lg.end(stdout)
    
    # enough for today!