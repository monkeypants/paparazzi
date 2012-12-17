import os
from optparse import OptionParser

from generators import DoxygenGenerator
from parsers import ModulesParser

# TODO: refactor these away
from gen_modules_doc import *


def parse_args():
    usage = "Usage: %prog [options] modules/dir" + "\n" 
    usage += "Run %prog --help to list the options."
    parser = OptionParser(usage)
    parser.add_option(
        "-i", "--inputdir", dest="input_dir",
        help="read input from DIR [default: PAPARAZZI_HOME/conf/modules",
        metavar="DIR")
    parser.add_option(
        "-o", "--outputdir", dest="output_dir",
        help="write output to DIR [default: PAPARAZZI_HOME/doc/manual",
        metavar="DIR")
    parser.add_option(
        "-p", "--parents",
        action="store_true", dest="create_parent_dirs",
        help="Create parent dirs of output dir if they don't exist.")
    parser.add_option(
        "-v", "--verbose",
        action="store_true", dest="verbose")
    return parser.parse_args()    

def get_paparazzi_home():
    # if PAPARAZZI_HOME not set, then assume the tree containing this
    # file is a reasonable substitute
    return os.getenv(
        "PAPARAZZI_HOME",
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../../../')))

def get_modules_dir(options):
    if options.input_dir:
        return options.input_dir
    else:
        return os.path.join(
            get_paparazzi_home(),
            "conf/modules")

def get_output_dir(options):
    if options.output_dir:
        return options.output_dir
    else:
        return os.path.join(
            get_paparazzi_home(),
            "doc/manual/generated")


if __name__ == "__main__":
    print "Building Documentation"
    #dg = DoxygenGenerator(modules=mp.modules)
    #dg.write(outfile)
    
    (options, args) = parse_args()

    modules_dir = get_modules_dir(options)
    mp = ModulesParser(modules_dir)

    dg = DoxygenGenerator(
        module_parser = mp,
        options = options,
        output_dir = get_output_dir(options))

    if options.verbose:
        print("Generating module documentation in " + output_dir)
    
    modules = dg.module_parser.modules # HACK - refactor WIP
    output_dir = dg.output_dir # HACK - refactor WIP

    # generate overview
    outstring = modules_overview_page(modules)

    # generate each module subpage
    for (n, m) in modules.items():
        outstring += module_page(n, m)

    #print(outstring)

    outfile_name = os.path.join(output_dir, "onboard_modules.dox")
    with open(outfile_name, 'w') as outfile:
        outfile.write(outstring)
    if options.verbose:
        print("Done.")
