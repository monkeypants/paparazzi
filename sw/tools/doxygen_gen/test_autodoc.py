import unittest
from autodoc import *

class GetPaparazziHomeTestCase(unittest.TestCase):
    """This should work regardless if PAPARAZZI_HOME is actually set."""

    def setUp(self):
        hardcode_path = '../../../'
        self.orig_home = os.getenv('PAPARAZZI_HOME',None)
        self.expected = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                hardcode_path))

    def tearDown(self):
        if self.orig_home:
            os.putenv('PAPARAZZI_HOME', self.orig_home)

    def test_without_PAPARAZZI_HOME(self):
        # we expect/assume this file is in a specific place, relative
        # to the sensible default PAPARAZZI_HOME
        os.unsetenv('PAPARAZZI_HOME')
        found = get_paparazzi_home()
        self.assertEqual(found, self.expected)

    def test_with_PAPARAZZI_HOME(self):
        os.putenv('PAPARAZZI_HOME', self.expected) 
        found = get_paparazzi_home()
        self.assertEqual(found, self.expected)

'''
# todo: test these errors are raised as required
* InvalidModuleInputDirError
* InvalidOutputDirectoryAndNotCreatingItError
* InvalidModuleXMLError
* MalformedModuleXMLError
* MissingTemplateError
* UnableToParseModuleError
'''


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


#
### Module
#

# pass init a malformed XML, expect MalformedModuleXMLError

# pass init well formed XML but without a root node "module",
# expect InvalidModuleXMLError

# pass init well formed XML with "module" root node, that does not
# conform to the DTD, and expect InvalidModuleXMLError

# pass init valid XML with empty 'name' attribute, name should be 
# 'mystery_module'

# pass init valid XML with name atttribute set to some arbitrary values,
# expect the name should be the appropriate value

# pass init valid XML with dir attribute not set, dir should be "misc"

# do some shit with the doc element...

'''
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
'''



if __name__ == "__main__":
    unittest.main()
