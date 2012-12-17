import os, sys, glob

# TODO: refactor these away
from gen_modules_doc import *


class ModulesParser(object):
    def __init__(self, modules_dir):
        self.modules_dir = modules_dir
        self.modules = {}
        self.scan_modules_dir()

    def validate_modules_dir(self):
        # should be:
        #   throwing a locally defined error
        #   logging debug/warning
        # it should be up to the main program to sys.exit(1), not here
        if not os.path.isdir(self.modules_dir):
            msg = "Input directory with modules "
            msg += modules_dir + " not found."
            print(msg)
            sys.exit(1)

    def scan_modules_dir(self):
        # flush before rescanning
        # info message if self.modules not empty
        self.validate_modules_dir()
        # get all xml files in modules_dir
        start_cwd = os.getcwd()
        os.chdir(self.modules_dir)
        for file in glob.glob("*.xml"):
            # debug message in the loop
            module = read_module_file(file)
            if len(module):
                self.modules[file] = module
        os.chdir(start_cwd) # housekeeping, avoid nasty side effects

if __name__ == "__main__":
    unittest.main()
