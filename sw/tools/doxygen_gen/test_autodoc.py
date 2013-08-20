import unittest
import tempfile

from autodoc import *

class GetPaparazziHomeTestCase(unittest.TestCase):
    """This should work regardless if PAPARAZZI_HOME is actually set."""

    def setUp(self):
        """Prepare to undo changes to the environment.
        
        Should I be using PAPARAZZI_SRC for any of this?

        Also, populate "expected" here because we use it more than once.

        """
        hardcode_path = '../../../'
        self.orig_home = os.getenv('PAPARAZZI_HOME',None)
        self.expected = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                hardcode_path))

    def tearDown(self):
        """Restore the environment if the test may have mangled it."""
        if self.orig_home:
            # we found it set, so restore it
            os.putenv('PAPARAZZI_HOME', self.orig_home)
        else:
            # we did not find it set
            if os.getenv('PAPARAZZI_HOME', None):
                # so, if it's set now, then unset it
                os.unsetenv('PAPARAZZI_HOME')

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


class PaparazziParserModuleTestCases(unittest.TestCase):

    def test_module_dir_validation_non_existant(self):
        """Raise InvalidModuleInputDirError if  modules_dir doesn't exist.

        The PaparazziParser can (optionally) be passed a modules_dir parameter.
        If it is, it must be the path of a directory that exist.
        """
        bogus_name = '/delme'
        # humerously pad hardcoded bogus directory name, as required to
        # ensure that it doesn't exist.
        while os.path.exists(bogus_name):
            bogus_name += "ROASTBEEF"
        self.assertRaises(
            InvalidModuleInputDirError,
            PaparazziParser,
            modules_dir=bogus_name)

    def test_module_dir_validation_non_dir(self):
        """Raise InvalidModuleInputDirError if modules_dir isn't a dir"""
        # create an empty, non-directory file
        tmpfp, tmpfname = tempfile.mkstemp()
        # it's not a dir, therefore invalid as a modules_dir
        self.assertRaises(
            InvalidModuleInputDirError,
            PaparazziParser,
            modules_dir=tmpfname)
        # clean up after yourself
        os.unlink(tmpfname)


# is initialised with a non-default modules_dir, expect the
# specified modules dir to be used

# after parsing the paparazzi tree, the present working directory must
# be is it was found

# solitary module.dirs should be aggregated into "misc" dir.

# default_modules_dir should return $PAPARAZZI_HOME/conf/modules"


#
### Module
#

# pass init a malformed XML, expect MalformedModuleXMLError

# when do I actually want to raise UnableToParseModuleError?

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



#
## Generator
#

### what's the point of non-PaparazziParser parsers?
### if different parsers can be used, what's the API?

## create_parents option
# true:
# false:

## output_dir option
# None (default):
# * InvalidOutputDirectoryAndNotCreatingItError
# Specified:

# default_output_path returns $PAPARAZZI_HOME/doc/manual/generated

# if no output_format specified, default to Doxygen

# if valid output format specified, use it

# if invalid output format specified, raise MissingTemplateError
# n.b. valid is defined as a coresponding template exists

# actual rendereing happens...

if __name__ == "__main__":
    unittest.main()
