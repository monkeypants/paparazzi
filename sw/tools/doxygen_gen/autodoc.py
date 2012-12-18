import os, sys, glob
import jinja2

# TODO: refactor these away
from gen_modules_doc import *

def get_paparazzi_home():
    # if PAPARAZZI_HOME not set, then assume the tree containing this
    # file is a reasonable substitute
    return os.getenv(
        "PAPARAZZI_HOME",
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../../../')))


class PaparazziParser(object):
    def __init__(self, modules_dir=None):
        if modules_dir:
            self.modules_dir = modules_dir
        else:
            self.modules_dir = os.path.join(
                get_paparazzi_home(),
                "conf/modules")

        self.modules = {}
        self.parse_modules()

    def parse_modules(self):
        ### Validate 
        # should be:
        #   throwing a locally defined error
        #   logging debug/warning
        # it should be up to the main program to sys.exit(1), not here
        if not os.path.isdir(self.modules_dir):
            msg = "Input directory with modules "
            msg += modules_dir + " not found."
            print(msg)
            sys.exit(1)
        ### Groundwork? 
        # flush before rescanning
        # info message if self.modules not empty
        ### Logic
        # get all xml files in modules_dir
        start_cwd = os.getcwd()
        os.chdir(self.modules_dir)
        for file in glob.glob("*.xml"):
            # debug message in the loop
            module = read_module_file(file)
            if len(module):
                self.modules[file] = module
        os.chdir(start_cwd) # housekeeping, avoid nasty side effects


class Generator(object):
    DEFAULT_OUTPUT_FORMAT = "Doxygen"
    
    def __init__(
            self, parser=None,
            output_dir=None,
            create_parents=True):

        # process arguments, apply defaults
        if not parser:
            self.parser = PaparazziParser()
        else:
            self.parser = parser
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(
                get_paparazzi_home(),
                "doc/manual")
        if create_parents:
            self.create_output_parent_dirs = True
        else:
            self.create_output_parent_dirs = False
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(
                    os.path.dirname(__file__),
                    'templates')))
        self.validate_output_dir()
        
    def validate_output_dir(self):
        if not os.path.isdir(self.output_dir):
            msg = "Output directory " + self.output_dir
            if self.create_output_parent_dirs:
                msg += " doesn't exit yet. Creating it." 
                print(msg)
                os.makedirs(self.output_dir)
            else:
                print(msg + " not valid.")
                sys.exit(1)

    def generate(self, output_format=None):
        if not output_format:
            output_format = self.DEFAULT_OUTPUT_FORMAT
        # WIP.
        modules = self.parser.modules
        output_dir = self.output_dir
        # generate overview
        outstring = modules_overview_page(modules)
        # generate each module subpage
        for (n, m) in modules.items():
            outstring += module_page(n, m)
        #print(outstring)
        outfile_name = os.path.join(output_dir, "onboard_modules.dox")
        with open(outfile_name, 'w') as outfile:
            outfile.write(outstring)
        #use logging instead
        #if options.verbose:
        #    print("Done.")

if __name__ == "__main__":
    import unittest
    import subprocess

    # get_paparazzi_home
    #    - if PAPARAZZI_HOME set, return it
    #    - for various cwd's
    #      - if PAPARAZZI_HOME not set
    #        - return a sensible guess
    #        - raise a sensible warning
    #
    # use logging

    class CLITestCase(unittest.TestCase):
        """Base class for TestCases that validate the CLI program.

        Defines convenience methods for interacting with the CLI.
        Abstracts interaction with CLI; consolidates assuptions
        about arguments, file system, etc.
        """
        program_name = "generate.py"

        def get_prog_name(self):
            # assume the test suite is adjacent to the program
            d = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(d, self.program_name)

        def get_cmd_argv(self, p=False):
            argv = ['python', self.get_prog_name()]
            if p:
                argv.append("-p")
            return argv

        def get_cmd_string(self):
            cmd = self.get_cmd_argv()
            argv0 = cmd.pop()
            argv1 = cmd.pop()
            cmd_str = "%s %s" % (argv0, argv1)
            for a in cmd:
                cmd_str += " %s" % a
            return cmd_str

    class TestOutputFile(CLITestCase):
        reldirs=(
            '.', '../', '../../',
            'sw', 'sw/tools',
            'sw/tools/doxygen_gen',
            'doc', 'doc/manual',
            'doc/manual/generated',
            'DELETE_THIS_DIRECTORY/THIS_FILE_WILL_BREAK_TESTS')
        absdirs = ('/','/tmp')

        def gen_dirs(self):
            ph = get_paparazzi_home()
            out = []
            for d in self.reldirs:
                out.append(os.path.join(ph, d))
            for d in self.absdirs:
                out.append(d)
            return tuple(out)

        def test_generate_executes_from_anywhere(self):
            """Matter not from where the CLI program is run."""
            argv = self.get_cmd_argv(p=True)
            devnull = open('/dev/null','w') # Yes, UNIX specific.
            for d in self.gen_dirs():
                if os.path.exists(d):
                    os.chdir(d)
                    try:
                        subprocess.check_call(argv, stdout=devnull)
                    except subprocess.CalledProcessError:
                        self.fail(
                            'unable to run from %s: %s' % 
                                (d, self.get_cmd_string()))

    unittest.main()
