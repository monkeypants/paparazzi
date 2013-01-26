import os, sys, glob, re
import xml.etree.ElementTree as ET
import lxml, lxml.etree # for DTD processing

import logging
try:
    import jinja2
except:
    # I don't have any idea if this will work
    # but i'm forced to try as I currently don't have an internet connection
    import jinja as jinja2

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
    """Paparazzi artefact parser relating to a module.

    Current implementation has hardcoced knowledge about the expected
    structure of a paparazzi module. This is a duplicate of the dtd,
    and it should also be possible to inferr it from the xml. In other
    words, this is largely redundant code.

    Another problem with this module is that it should provide a pythonic
    interface to the parsed module. In other words, something (the template
    rendering context) should be able to access information about the module
    from attributes of this representation of it.

    I thought that I should rewrite this as some sort of metaclass hack,
    that created a class with the relevant members, then instantiated
    it with the contents of a parsed module. That was some interesting reading,
    but it turn's out someone already made the lxml.objectify module which
    does thiS. Oh well.

    """
   
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
                        if desc is None or not hasattr(desc, 'text') \
                                or desc.text is None:
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
            # removed a whold bunch of commented out stuff here
            # it shouldn't need replacing when I start using lxml.objectify

class PaparazziParser(object):
    """Inspects the paparazzi sources and generate representations of it.

    Currently only knows about modules, but should obviously be extended to
    know about airframes, subsystems, etc.

    The more that's added to it, the more that it should be responsible for
    discovering linkages between code and configuration artefacts. Eventually,
    it should probably be replaced with some logic programming. I.e. evolve
    into three parts:

     * A true parser, that populates a graph of convenience objects representing
       the paparazzi tree
     * a "knowledge harvester" that generates logical assertions about those
       representations, using an ontology.
     * an reasoner that decorates the object graph with inferencially derived
       information.

    That way, the templates would be able to render semanic links between
    objects (not just structual ones). Increasing the semantic richness of
    generated docs would have three parts. 

     1. Add new concepts to the ontology
     2. Teach the knowledge harvester to pick them up
     3. Use the new information in the templates

    Well, that's a fine theory :)

    """
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

