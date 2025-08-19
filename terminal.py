# My Spaghetti masterpiece ~

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

backup_prompt_end_char = c.prompt_end_char

if sudo:
    c.prompt_end_char = "#"

def main():
    global stdout, stdin, currentTask, c, backup_prompt_end_char
    c.root = fs.root
    # type of c.commands: dict[str, tuple[function, str]]
    c.commands = None # type: ignore

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

    # the help function is buggy; it outputs other things correct, but when it comes to the `alias` command,
    # it just breaks (throwing a TI-Nspire native error, not a python error).
    def help(c, msg=None) -> str:
        global stdout
        lg.call("help", msg)
        stdout += "--- Help ---\n"
        for com in c.commands.keys():
            stdout += (com + ": " + c.commands[com][1]) + "\n"
        if msg is not None:
            stdout += msg + "\n"
        lg.end(stdout)
        return stdout
    
    def cd(c, foldername):
        global stdout
        try:
            # crappy logic, but works currently
            if foldername == ".":
                pass
            elif foldername != "..":
                if foldername.startswith("/"):
                    try:
                        c.setCwd(c.root)
                        for name in foldername.split("/"):
                            if name == "":
                                continue
                            lg.info("Trying to set path " + name)
                            c.setCwd(c.cwd.folderlist[name])
                    except:
                        lg.fatal("absolute path " + str(foldername) + " not recognized")
                        stdout += "absolute path " + str(foldername) + " not recognized"
                # normal
                elif foldername != "-":
                    c.setCwd(c.folderlist[foldername])
                elif foldername == "-":
                    c.setCwd(c.root.home.folderlist[c.user_name])
                # elif foldername is None: raise KeyError()
            elif c.cwd != fs.root:
                c.setCwd(c.cwd.parent)
            else:
                pass # technically not needed since newer version patched root to be its own parent
        except KeyError as ke:
            stdout += "\ncd: directory not found"
            lg.warn("cd: directory " + foldername + " not found, " + repr(ke))
    def useradd(c, username: str):
        global sudo, stdout, users_and_pwds
        if sudo:
            confirmed=False
            passwd = c.getInput("Enter password for user " + username)
            confirmed = c.getInput("Re-enter password for user " + username) == passwd
            while not confirmed:
                passwd = c.getInput("Passwords do not match. Please re-enter password: ")
                confirmed = c.getInput("Re-enter password: ") == passwd
            # This is important, could cause bugs with login under rare cases?
            c.root.home.addfolder(username)
            
            users_and_pwds.update({username: passwd})
            lg.info("U: " + username + ", P: " + passwd)
        else:
            stdout += "You cannot perform this operation unless you are root."
            lg.warn("useradd attempt by non-root user")
    def login(c, username: str = ""):
        global stdout, sudo, users_and_pwds
        if username == "":
            username = c.getInput("Login for: ")
        if username not in users_and_pwds.keys():
            c.commands["error"][0](c, "User " + username + " not found!")
            return
        passwd = c.getInput("Enter password: ")
        if users_and_pwds[username] == passwd:
            sudo = False # no longer root user
            c.commands["cd"][0](c, "/home/"+username)
            c.user_name = username
            c.prompt_end_char = backup_prompt_end_char
        else:
            lg.warn("paassword incorrect")
            c.prompt_end_char = '#'
            return
    def echo(c, what):
        global stdout
        stdout += str(what)
        return what # not needed, but could be useful
    def start_femto(c, fn=None):
        c.cls()
        c.commands["touch"][0](c, fn)
        f=femto.femto(("temp.file" if fn is None else fn))
        f.cli = c # pass renderer
        f.start()
    def set_color(c, r, g, b):
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            c.color = (r, g, b)
        else:
            c.commands["eror"][0](c, "error in setting color. perhaps wrong format?")
    def touch(c, filename):
        if not (filename in c.cwd.filelist.keys()):
            c.cwd.addfile(filename)
            lg.info("line: " + filename + " created")
    def cat(c, fn: str):
        global stdout
        if fn in c.cwd.filelist.keys():
            f=fio.file(fn, fio.ios_app | fio.ios_in)
            lg.info("file with filename " + fn + " successfully absorbed for cat command")
            stdout += "\n".join(f.toStrList())
        else:
            c.commands["error"][0](c, "cat: file " + fn + " does not exist")
    def logout(c):
        global stdout, sudo
        if c.user_name == "root":
            stdout += "you are already root"
        else:
            rootpwd = c.getInput("Enter password for root: ")
            if rootpwd == c.passwd:
                stdout += "successfully logged out, you are now root user"
                c.prompt_end_char = '#'
            else:
                stdout += "password for root incorrect"
                c.prompt_end_char = backup_prompt_end_char
                return
        sudo = True
        c.user_name = "root"
    
    # command name: str: (command callback: function, description: str)
    c.commands = { # type: ignore
        "alias": (alias, "make an alias of a command. format: alias new_alias=\"old command\""),
        "ls": (ls, "list child items of a directory. flags: -r for recurse"),
        "clear": (clear, "clear screen"),
        "mkdir": (mkdir, "create a directory (folder)"),
        "rmdir": (rmdir, "remove a directory (recursive)"),
        "error": (error, "internal error function"),
        "help": (help, "display this help message"), # yea nothing related to python help
        "cd": (cd, "go to a directory"),
        "useradd": (useradd, "add a user"),
        "echo": (echo, "redirect stdin to stdout (prints output)"),
        "femto": (start_femto, "text editor. usage: femto <filename>"),
        "color": (set_color, "set color of text. takes 3 arguments (r, g, b)"),
        "touch": (touch, "create a file under the cwd if nonexistent"),
        "cat": (cat, "output content of file"),
        "login": (login, "log in to a user"),
        "logout": (logout, "log out of a user to root"),
    }
    # should refactor this to c.root.etc, ...
    c.etc = c.root.addfolder("etc") # type: ignore
    c.etc.logs: folder = c.etc.addfolder("logs") # type: ignore

    # set up logging (future implementation)
    c.setCwd(c.etc.logs) # type: ignore
    c.commands["touch"][0](c, "log") # type: ignore
    c.cwd = c.root
    
    lg.cus("debug", str(c.commands.keys())) # type: ignore

    while stdin != "exit":
        stdout = ""
        stdin = c.getInput(c.getPrefix()).strip() # strip removes leading and trailing whitespace so fine
        lg.cus("input", stdin)
        # added this because I planned on doing something else but batch deindenting is difficult and confusing
        if currentTask == "bash":
            if stdin.startswith("sudo"):
                stdin = stdin[stdin.index("sudo ") + len("sudo ") + 1:]
                if c.getInput("[sudo] password for sudo: ") == c.passwd:
                    sudo = True
                    backup_prompt_end_char = c.prompt_end_char
                    c.prompt_end_char='#'
                else:
                    sudo = False
                    c.prompt_end_char = backup_prompt_end_char
                    stdout += "password for sudo incorrect"
                    continue
            if stdin.startswith("alias"):
                try:
                    newaliasname = stdin[len("alias") + 1 : stdin.index("=")].strip()
                    oldaliasname = stdin[stdin.index("=")+1:]
                    c.commands["alias"][0](c, newaliasname, oldaliasname) # type: ignore
                except ValueError as ve:
                    stdout += "Format incorrect. Format should be 'alias alias_name=old_command_name'\n"
            elif stdin.startswith("clear"):
                c.commands["clear"][0](c) # type: ignore
            elif stdin.startswith("ls"):
                if stdin.find("-r") != -1:
                    c.commands["ls"][0](c, True) # type: ignore
                else:
                    c.commands["ls"][0](c, False) # type: ignore
            elif stdin.startswith("mkdir"):
                try:
                    foldername = stdin[stdin.index("mkdir ") + len("mkdir "):]
                    c.commands["mkdir"][0](c, foldername) # type: ignore
                except ValueError as ve:
                    stdout += "second argument 'name' needed. enter 'help' for help"
            elif stdin.startswith("rmdir "):
                try:
                    foldername = stdin[stdin.index("rmdir") + len("rmdir "):]
                    c.commands["rmdir"][0](c, foldername) # type: ignore
                except:
                    stdout += "second argument 'name' needed. enter 'help' for help"
            elif stdin.startswith("help"):
                c.commands["help"][0](c) # type: ignore
            elif stdin.startswith("cd "):
                try:
                    foldername = stdin[stdin.index("cd ") + len("cd "):]
                    c.commands["cd"][0](c, foldername) # type: ignore
                except:
                    stdout += "cd: no directory argument found"
            elif stdin.startswith("useradd "):
                try:
                    username = stdin[stdin.index("useradd ") + len("useradd "):]
                    c.commands["useradd"][0](c, username) # type: ignore
                except:
                    stdout += "incorrect format for useradd. format: 'useradd <username>'"
            elif stdin.startswith("login"):
                username = stdin[len("login "):] if stdin.find("login ") != -1 else ""
                c.commands["login"][0](c, username) # type: ignore
            elif stdin.startswith("logout"):
                c.commands["logout"][0](c) # type: ignore
            elif stdin.startswith("femto"):
                try:
                    fn = stdin[stdin.index("femto ") + len("femto "):]
                except:
                    fn=None
                c.commands["femto"][0](c, fn) # type: ignore
            elif stdin.startswith("cat"):
                fn = stdin[len("cat "):]
                lg.info("catting " + fn)
                c.commands["cat"][0](c, fn) # type: ignore
            elif stdin.startswith("color "):
                tokens = stdin.split(" ")
                try:
                    r = int(tokens[1])
                    g = int(tokens[2])
                    b = int(tokens[3])
                    c.commands["color"][0](c, r, g, b) # type: ignore
                except:
                    try:
                        tokens = [s.strip() for s in stdin.split(",")]
                        r = int(tokens[1])
                        g = int(tokens[2])
                        b = int(tokens[3])
                        c.commands["color"][0](c, r, g, b) # type: ignore
                    except:
                        c.commands["error"][0](c, "color must be space/comma separated") # type: ignore
                        c.display("e.g, 'color 50 100 200")
            elif stdin.startswith("touch"):
                filename = stdin[len("touch "):]
                c.commands["touch"][0](c, filename) # type: ignore
            elif stdin in c.commands.keys(): # type: ignore # definitely not a good catch but its alright
                c.commands[stdin][0](c) # type: ignore
            elif stdin != "exit" and stdin != "":
                c.commands["error"][0](c, "command " + stdin + " not found.") # type: ignore
                stdout += "\nenter help to help"
        lines = stdout.split("\n")
        for i in range(len(lines)):
            c.display(lines[i])
            lg.info("displayed " + lines[i])
        lg.info("REPL loop cycle completed")

    

try:
    main()
except BaseException as be:
    lg.fatal(repr(be))
    c.color = (200, 0, 0)
    c.display(repr(be))