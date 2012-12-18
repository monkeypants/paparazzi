import os, sys, glob
import jinja2

# TODO: refactor these away
from gen_modules_doc import modules_overview_page
from gen_modules_doc import module_page
from gen_modules_doc import read_module_file
from gen_modules_doc import get_module_dir

def get_paparazzi_home():
    # if PAPARAZZI_HOME not set, then assume the tree containing this
    # file is a reasonable substitute
    return os.getenv(
        "PAPARAZZI_HOME",
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../../../')))

class InvalidModuleInputDirError(Exception):
    """Specified module_dir is not Valid."""


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
        if not os.path.isdir(self.modules_dir):
            raise InvalidModuleInputDirError

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

    def module_subsections(self):
        #return list of subsections, which is each a list of modules
        dirs = {}
        for (mfile, m) in self.modules.items():
            mdir = get_module_dir(m)
            if mdir not in dirs:
                dirs[mdir] = {mfile: m}
            else:
                dirs[mdir][mfile] = m
        # what I want here is an OrderedDict
        subsections = []
        misc = {}
        for d in sorted(dirs.keys()):
            # dir is a subsection if it contains multiple modules
            if len(dirs[d]) > 1:
                subsections.append((d, dirs[d]))
            else:
                # othewise, lone module belongs in "misc" subsection
                (mfile, m) = dirs[d].popitem()
                misc[mfile] = m
        subsections.append(('misc', misc))
        return subsections


class Generator(object):
    DEFAULT_OUTPUT_FORMAT = "Doxygen"
    
    def __init__(
            self, parser=None,
            output_dir=None,
            create_parents=True):

        if not parser:
            self.parser = PaparazziParser()
        else:
            self.parser = parser

        # respect  "-p" cli switch
        if create_parents:
            self.create_output_parent_dirs = True
        else:
            self.create_output_parent_dirs = False

        # respect "-o" cli swirch
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(
                get_paparazzi_home(),
                "doc/manual/generated")

        # "-o" and "-p" interact
        if not os.path.isdir(self.output_dir):
            msg = "Output directory " + self.output_dir
            if self.create_output_parent_dirs:
                # TODO: logging
                msg += " doesn't exit yet. Creating it." 
                print(msg)
                os.makedirs(self.output_dir)
            else:
                # TODO: logging
                print(msg + " not valid.")
                # TODO: shift sys.exit to caller, here we should just
                # be throwing an appropriate error
                sys.exit(1)

        # any output_format uses the same template environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(
                    os.path.dirname(__file__),
                    'templates')))

    def generate(self, output_format=None):
        if not output_format:
            output_format = self.DEFAULT_OUTPUT_FORMAT
        # TODO: test that templates exist for specified output_format
        
        # WIP.
        modules = self.parser.modules
        output_dir = self.output_dir
        # generate overview
        # TODO: replace this with jinja2 template
        template = self.env.get_template('modules_overview.dox')
        
        outstring = template.render(
            name="onboard_modules",
            subsections = self.parser.module_subsections())
        
        outstring += "************************"
        outstring += modules_overview_page(modules) # TODO: UNROLL/REFACRTOR

        # generate each module subpage
        # TODO: replace this with jinja2 template
        for (n, m) in modules.items():
            outstring += module_page(n, m) # TODO: UNROLL/REFACTOR
        # TODO: this should be a function of the output_format
        outfile_name = os.path.join(output_dir, "onboard_modules.dox")
        # Are we it's always exactly 1 file? No
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

    class PaparazziParserModuleTestCases(unittest.TestCase):
        def test_module_dir_validation(self):
            """InvalidModuleInputDirError with invalid modules_dir."""
            bogus_name = '/delme'
            while os.path.isdir(bogus_name): # unlikely
                bogus_name += "DEADBEEF" # ROASTBEEF?
            self.assertRaises(
                InvalidModuleInputDirError,
                PaparazziParser,
                modules_dir=bogus_name)

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
