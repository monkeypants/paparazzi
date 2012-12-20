import os, sys, glob, re
import xml.etree.ElementTree as ET
import lxml, lxml.etree # for DTD processing

import logging
import jinja2

# TODO: refactor these away
from gen_modules_doc import modules_overview_page
from gen_modules_doc import get_module_description

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

class UnableToParseModuleError(Exception):
    """autodoc could not parse the module xml file."""

def get_paparazzi_home():
    # if PAPARAZZI_HOME not set, then assume the tree containing this
    # file is a reasonable substitute
    return os.getenv(
        "PAPARAZZI_HOME",
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../../../')))

class Module(object):
    """Paparazzi artefact parser relating to a module."""
   
    def __init__(self, filename):
        """Parse XML then defer to other methods to populate attributes."""
        self.filename = filename
        self.logger = logging.getLogger('autodoc.Module')
        try:
            #tree = ET.parse(filename)
            tree = lxml.etree.parse(filename)
        except lxml.etree.ParseError:
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
            self._etree = root

        dtd_file = os.path.join(
            os.path.dirname(self.filename), 'module.dtd')
        dtd = lxml.etree.DTD(dtd_file)

        # seems I need a newer lxml to iterate over dtd.elements()
        # self.logger.debug(lxml.etree.LXML_VERSION) <- mine is 2.3
        if not dtd.validate(self._etree):
            msg = "[Module] %s: is not valid" % self.filename
            logger.warn(msg)

        # .name
        try:
            self.name = self._etree.attrib['name']
        except KeyError:
            self.name = "mystery_module"

        # .dir
        try:
            self.dir = self._etree.attrib['dir']
        except KeyError:
            self.dir = "misc"

        ### DOC element ###
        for a in self._etree:
            if a.tag == 'doc':
                for b in a:
                    if b.tag == 'description':
                        desc = b.text
                        details = "No detailed description...\n"
                        if desc is None or desc.text is None:
                            brief = self.name.replace('_', ' ').title()
                        else:
                            # treat first line until dot as brief
                            d = re.split(r'\.|\n', desc.text.strip(), 1)
                            brief = d[0].strip()
                            if len(d) > 1:
                                details = d[1].strip()+"\n"
                        self.brief_description = brief
                        self.detailed_description = details                
            elif a.tag == 'header':
                pass
            elif a.tag == 'init':
                pass
            elif a.tag == 'periodic':
                pass
            elif a.tag == 'makefile':
                pass
        """
        #.brief_description
        #.detailed_description
        msg = "[Module]: %s %s %s"
        desc = doc.get('description')
        try:
            msg = msg % (self.name, ' found description ',  desc)
        except:
            msg = msg % ('no description found for ', self.name, '')
            desc = None
        self.logger.debug(msg)
        
        


        # Sometimes elementtree methods are used directly, which is OK.
        # So long as only primative types end up as attribute values.
        #confs = self.etree_findall("./doc/configure")
        confs = None
        if confs:
            msg = "processing configuration in %s" % self.filename
            self.logger.debug(msg)
            self.configures = {}
            for c in confs:
                msg = "processing configuration %s in %s" % (
                    c, self.filename)
                self.logger.debug(msg)
                self.configures[c] = {
                    'name': c.get('name'),
                    'value': c.get('value'),
                    'description': c.get('description')}
        else:
            msg = "%s contains no ./doc/configure" % self.filename
            self.logger.info(msg)

        #defines = self.etree_findall("./doc/define")
        defines = None
        if defines:
            msg = "processing defines in %s" % self.filename
            self.logger.debug(msg)
            self.defines = {}
            for d in defines:
                msg = "processing define %s in %s" % (
                    d, self.filename)
                self.logger.debug(msg)
                self.defines[d] = {
                    'name': d.get('name'),
                    'value': d.get('value'),
                    'description': d.get('description')}
        else:
            msg = "%s contains no ./doc/define" % self.filename
            self.logger.info(msg)       
        
        #secs = self.etree_findall("./doc/section")
        secs = None
        if secs:
            msg = "processing sections in %s" % self.filename
            self.logger.debug(msg)
            self.sections = {}
            for s in secs:
                msg = "processing section %s in %s" % (
                    s, self.filename)
                self.logger.debug(msg)
                defines = {}
                for d in s.findall("./define"):
                    defines[d] = {
                        'name': d.get('name'),
                        'value': d.get('value'),
                        'description': d.get('description')}
                self.sections[s] = {
                    'name': s.get('name'),
                    'prefix': s.get('prefix'),
                    'defines': defines}
        else:
            msg = "%s contains no ./doc/section" % self.filename
            self.logger.info(msg)
    """
    #    self._functions()
    #    self._headers()
    #    self._sources()
    """
    def etree_get(self, element_name, default=None):
        try:
            value = self._etree.get(element_name)
            if value is not None:
                msg = "[Module] %s: found %s=%s"
                msg = msg % (self.filename, element_name, value)
                self.logger.debug(self._etree)
            else:
                value = default
                msg = "[Module] %s: no value for '%s'"
                msg = msg % (self.filename, element_name)
                self.logger.info(msg)
                msg = "[Module] %s: using default value, %s=%s"
                msg = msg % (self.filename, element_name, value)
            self.logger.debug(msg)
        except:
            msg = "Unable to process file %s"
            msg = msg % (element_name, self.filename)
            self.logger.critical(msg)
            raise InvalidModuleXMLError
       
        return value

    def etree_findall(self, element_name):
        try:
            found = self._etree.findall(element_name)
        except:
            msg = "Unable to findall % from %s"
            msg = msg % (elenent_name, self.filename)
            self.logger.critical(msg)
            raise InvalidModuleXMLError
        return found
    
    def _functions(self):
        pass

    def _headers(self):
        pass

    def _sources(self):
        pass
    """

class PaparazziParser(object):
    def __init__(self, modules_dir=None):
        # expect this signature to change
        self.logger = logging.getLogger('autodoc.PaparazziParser')
        if modules_dir:
            self.modules_dir = modules_dir
        else:
            self.modules_dir = self.default_modules_dir()
        if not os.path.isdir(self.modules_dir):
            raise InvalidModuleInputDirError

        # this parser needs a collection of modules
        start_cwd = os.getcwd() # as farmer's gates you find
        self.modules = []
        os.chdir(self.modules_dir)
        for file in glob.glob("*.xml"):
            self.modules.append(Module(file))
        os.chdir(start_cwd) # leave them you should

        # also, sorted into groups
        self.module_dirs = {'misc':[]}
        for m in self.modules:
            self.logger.debug(m.dir)
            if not self.module_dirs.has_key(m.dir):
                self.module_dirs[m.dir] = []
            self.module_dirs[m.dir].append(m)
        # now shift lonly ones to misc
        for d in self.module_dirs.keys():
            if d.lower() != 'misc':
                if len(self.module_dirs[d]) == 1:
                    self.module_dirs['misc'].append(
                        self.module_dirs[d])
                    del(self.module_dirs[d])

    @classmethod
    def default_modules_dir(self):
        return os.path.join(
            get_paparazzi_home(),
            "conf/modules")


class Generator(object):
    """Creates documentation using pluggable templates.

    Renders jinja2 templates to the output_dir, using the parser
    as context. If no parser is passed in, it creates a default one.

    Simple changes to the generated content (e.g. formatting) can
    be achieved by editing the template, as can more complicated
    changes (so long as the required information is available from
    the parser).

    To create a new output format, make the appropriate template(s)
    and register them with the generator by editing self.templates
    """
    DEFAULT_OUTPUT_FORMAT = "Doxygen"
    DEFAULT_OUTPUT_PATH = "doc/manual/generated"
    DEFAULT_TEMPLATE_PATH = "templates"

    def __init__(
            self, parser=None,
            output_dir=None,
            create_parents=True):
        """Sets up parser, output and template system."""
        
        self.logger = logging.getLogger('autodoc.Generator')
        
        if not parser:
            msg = 'Generator; None parser received, using default.' 
            self.logger.debug(msg)
            self.parser = PaparazziParser()
        else:
            self.parser = parser

        msg = "Generator; %s create output_dir parents"
        if create_parents:
            self.logger.debug(msg % "will")
            self.create_output_parent_dirs = True
        else:
            self.logger.debug(msg % "will not")
            self.create_output_parent_dirs = False

        msg = "Generator; using output_dir %s"
        if output_dir:
            self.logger.debug(msg % output_dir)
            self.output_dir = output_dir
        else:
            od = self.default_output_dir()
            self.logger.debug(msg % ("%s [default]" % od,))
            self.output_dir = od

        # validate output_dir
        if not os.path.isdir(self.output_dir):
            msg = "Generator; Output directory " + self.output_dir
            if self.create_output_parent_dirs:
                msg += " doesn't exit yet. Creating it, OK." 
                self.logger.info(msg)
                os.makedirs(self.output_dir)
            else:
                self.logger.error(msg + ' is not valid.')
                raise InvalidOutputDirectoryAndNotCreatingItError
        else:
            msg = "Output directory already exists."
            self.logger.debug(msg)

        # any output_format uses the same template environment
        # TODO: parameters for chosing a different template path
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(
                    os.path.dirname(__file__),
                    self.DEFAULT_TEMPLATE_PATH)))

        ### MAINTAIN THIS ###
        # to reflect the actual templates.
        #
        # Obviously, there is some opportunity to expand...
        #  - configuration-driven unit testing framework
        #  - wiki markup (replace ../wiki_gen)
        #  - reStructured text, CI build to readthedocs.org...
        #  - reStructured text, with sphinx/breathe
        #  - markdown -> github
        #  - LaTex (why? :)
        #  - rulebases for logic programming
        #
        self.templates = {
            'modules': {
                'Doxygen':'modules_overview.dox'}}

    @classmethod
    def default_output_dir(self):
        return os.path.join(
            get_paparazzi_home(),
            self.DEFAULT_OUTPUT_PATH)

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
            modules = self.parser.modules,
            module_dirs = self.parser.module_dirs)
        
        ### bad stuff ###
        # TODO: this should be a function of the output_format
        # i.e. this is BAD
        outfile_name = os.path.join(
            self.output_dir,
            "onboard_modules.dox")
        # Are we it's always exactly 1 file? No
        with open(outfile_name, 'w') as outfile:
            outfile.write(outstring)
        ### end of bad stuff ###
        
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
