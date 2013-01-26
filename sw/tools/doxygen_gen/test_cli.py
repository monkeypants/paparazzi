import unittest
import subprocess
from autodoc import *

class CLITestCase(unittest.TestCase):
    """Base class for TestCases that validate the CLI program.

    Defines  methods for interacting with the CLI. Consolidates assuptions
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
        """The CLI program should run from anywhere.

        This is a silly test because it takes so long. Maybe the CLI program
        should get a "don't actually generate anything" option that's very 
        quick, just so tests like this are faster to run.

        """
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

if __name__ == "__main__":
    unittest.main()
