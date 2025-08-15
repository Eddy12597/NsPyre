import unittest

from filesys import folder, file, root

class TestFolderFileSystem(unittest.TestCase):
    def setUp(self):
        # Rebuild a fresh root for each test
        global root
        root = folder(parent=None, name="")
        root.parent = root
        self.home = root.addfolder("home")
        self.bin = root.addfolder("bin")
        self.config = root.addfolder("config")
        self.dev = root.addfolder("dev")

    def test_add_folder(self):
        docs = self.home.addfolder("docs")
        self.assertIn("docs", self.home.folderlist)
        self.assertEqual(self.home.folderlist["docs"], docs)

    def test_add_file(self):
        f = self.home.addfile("test", ".txt")
        self.assertIn("test", self.home.filelist)
        self.assertEqual(self.home.filelist["test"].ext, ".txt")

    def test_duplicate_folder_name(self):
        # Adding same name should trigger "(copy)" logic
        self.home.addfolder("docs")
        copy_folder = self.home.addfolder("docs")
        self.assertTrue("(copy)" in copy_folder.name)

    def test_duplicate_file_name(self):
        self.home.addfile("report", ".pdf")
        copy_file = self.home.addfile("report", ".pdf")
        self.assertTrue("(copy)" in copy_file.name)

    def test_remove_folder(self):
        docs = self.home.addfolder("docs")
        self.home.removefolder(docs)
        self.assertNotIn("docs", self.home.folderlist)

    def test_remove_file(self):
        f = self.home.addfile("temp", ".tmp")
        self.home.removefile(f)
        self.assertNotIn("temp", self.home.filelist)

    def test_add_method(self):
        f = file(self.home, "standalone", ".txt")
        self.home.add(f)
        self.assertIn("standalone", self.home.filelist)

    def test_remove_method(self):
        f = self.home.addfile("deleteme", ".txt")
        self.home.remove(f)
        self.assertNotIn("deleteme", self.home.filelist)

    def test_repr_folder_and_file(self):
        f = self.home.addfile("myfile", ".log")
        folder_repr = repr(self.home)
        file_repr = repr(f)
        self.assertTrue(folder_repr.startswith("/"))
        self.assertTrue(file_repr.endswith(".log"))

    def test_dir_non_recursive(self):
        self.home.addfolder("docs")
        self.home.addfile("readme", ".txt")
        output = self.home.dir(recurse=False)
        self.assertIn("Folder: home/", output)
        self.assertIn("docs/", output)
        self.assertIn("readme.txt", output)

    def test_dir_recursive(self):
        docs = self.home.addfolder("docs")
        docs.addfile("nested", ".dat")
        output = self.home.dir(recurse=True)
        self.assertIn("nested.dat", output)

if __name__ == "__main__":
    unittest.main()
