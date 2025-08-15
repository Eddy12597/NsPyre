root = None
indent=0
indentstr="  "

class FSError(BaseException):
    def __init__(s, name):
        s.name=name

class FileError(FSError):
    def __init__(s, name):
        s.name = name

class FolderError(FSError):
    def __init__(s, name):
        s.name = name

class folder:
    def __init__(s, parent: "folder | None", name: str | None = None):
        s.parent = parent
        s.name = name if name is not None else "new folder"
        s.filelist: dict[str, file] = {}
        s.folderlist: dict[str, folder] = {}
    def addfile(s, name: str, ext: str = ".file") -> "file":
        if name in s.filelist.keys():
            return s.addfile(s.name + " (copy)", ext=ext)
        tmp = file(s, str(name), ext)
        s.filelist.update({name: tmp})
        return tmp
    def addfolder(s, name: str) -> "folder":
        if name in s.folderlist.keys():
            return s.addfolder(s.name + " (copy)")
        tmp = folder(s, name)
        s.folderlist.update({name: tmp})
        return tmp
    def removefile(s, f: "file") -> None:
        if f in s.filelist.values():
            s.filelist.pop(f.name)
    def removefolder(s, f: "folder") -> None:
        if f in s.folderlist.values():
            s.folderlist.pop(f.name)
    def add(s, element: "file | folder") -> "file | folder":
        if (type(element) == file):
            s.filelist.update({element.name: element})
        elif (type(element) == folder):
            s.folderlist.update({element.name: element})
        return element
    def remove(s, element) -> None:
        if type(element) == file:
            s.removefile(element)
        elif type(element) == folder:
            s.removefolder(element)
    def __repr__(s) -> str:
        parts = []
        current = s
        visited = set()
        while current is not None and id(current) not in visited:
            visited.add(id(current))
            if current.name:
                parts.append(current.name + "/")
            if current is root:
                break
            current = current.parent
        return "/" + "".join(reversed(parts))




    def dir(s, recurse=False) -> str:
        result = ""
        global indent, indentstr
        result += (indent * indentstr) + "Folder: " + s.name + "/" + "\n"
        indent += 1
        
        # List folders
        for fname in sorted(s.folderlist):
            folder_obj = s.folderlist[fname]
            result += indent * indentstr + repr(folder_obj) + "\n"
            if recurse:
                result += folder_obj.dir(recurse=True)
        
        # List files
        for fname in sorted(s.filelist):
            file_obj = s.filelist[fname]
            result += indent * indentstr + repr(file_obj) + "\n"
        
        indent -= 1
        return result

class file:
    def __init__(s, parent: folder, name: str | None = None, ext=".file") -> None:
        s.name = name if name is not None else "new file"
        s.parent = parent
        s.ext = ext
    def __repr__(s) -> str:
        return repr(s.parent) + s.name + s.ext



root = folder(parent = None, name="")
root.parent = root
root.home = root.addfolder("home")
root.bin = root.addfolder("bin")
root.config = root.addfolder("config")
root.dev = root.addfolder("dev")

