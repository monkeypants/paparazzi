import os, sys, glob
import xml.etree.ElementTree as ET

import logging
import jinja2

# TODO: refactor these away
from gen_modules_doc import modules_overview_page
from gen_modules_doc import module_page

class InvalidModuleInputDirError(Exception):
    """Specified module_dir is inalid."""

class InvalidOutputDirectoryAndNotCreatingItError(Exception):
    """Specified output_dir is invalid, and not create_parents_dir."""

class InvalidModuleXMLError(Exception):
    """autodoc could not parse an invalid module xml file."""

class MalformedModuleXMLError(Exception):
    """autodoc encountered a malformed module xml file."""

class MissingTemplateError(Exception):
    """autodoc could not load a template (because it wasn't there)."""

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
        self.logger = logging.getLogger('autodoc.PaparazziParser')
        self.modules = {}
        self.parse_modules()

    def parse_modules(self):
        if not os.path.isdir(self.modules_dir):
            raise InvalidModuleInputDirError
        # Ideas:
        # - flush before rescanning?
        # - log if self.modules not empty?
        # - lazy-lookups mechanism?

        # get all xml files in modules_dir
        start_cwd = os.getcwd()
        os.chdir(self.modules_dir)
        for file in glob.glob("*.xml"):
            try:
                tree = ET.parse(file)
            except ET.ParseError:
                msg = "Xml file {0} is not well formed."
                msg.format(file)
                self.logger.warning(msg)
                raise MalformedModuleXMLError
            root = tree.getroot()
            if root.tag != "module":
                msg = "Xml file {0} doesn't have 'module'"
                msg += "as root node."
                msg.format(file)
                self.logger.warning(msg)
                raise InvalidModuleXMLError
            else:
                module = root
            if len(module):
                self.modules[file] = module
        os.chdir(start_cwd) # leave it like you found it

    def module_subsections(self):
        #return list of subsections, which is each a list of modules
        dirs = {}
        for (mfile, m) in self.modules.items():
            #mdir = get_module_dir(m)
            mdir =  m.get("dir", m.get("name")).strip()
            if mdir not in dirs:
                dirs[mdir] = {mfile: m}
            else:
                dirs[mdir][mfile] = m
        # use OrderedDict?
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
        self.logger = logging.getLogger('autodoc.Generator')
        if not parser:
            msg = 'None parser passed to Generator'
            msg += ', using default' 
            self.logger.debug(msg)
            self.parser = PaparazziParser()
        else:
            self.parser = parser

        if create_parents:
            self.create_output_parent_dirs = True
        else:
            self.create_output_parent_dirs = False

        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(
                get_paparazzi_home(),
                "doc/manual/generated")

        if not os.path.isdir(self.output_dir):
            msg = "Output directory " + self.output_dir
            if self.create_output_parent_dirs:
                msg += " doesn't exit yet. Creating it." 
                self.logger.info(msg)
                os.makedirs(self.output_dir)
            else:
                self.logger.error(msg + ' not valid')
                raise InvalidOutputDirectoryAndNotCreatingIts

        # any output_format uses the same template environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(
                    os.path.dirname(__file__),
                    'templates')))

        # maintain this to match the contents of templates/
        self.templates = {
            'modules': {
                'Doxygen':'modules_overview.dox'}}

    def modules_doc(self, output_format=None):
        if not output_format:
            self.logger.debug('generate called with output_format=None')
            fmt = self.DEFAULT_OUTPUT_FORMAT
            self.logger.debug('using default output_format, %s' % fmt)
            output_format = fmt

        module_templates = self.templates['modules']
        if output_format not in module_templates.keys():
            msg = "No module template configured for %s" % output_format
            self.logger.warning(msg)
            raise MissingTemplateError
        else:
            template_name = self.templates['modules'][output_format]
        template = self.env.get_template(template_name)

        outstring = template.render(
            name="onboard_modules",
            heading="Onboard Modules",
            subsections = self.parser.module_subsections())

        # WIP...
        modules = self.parser.modules
        output_dir = self.output_dir
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
        self.logger.info('Finished building module documentation')

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
