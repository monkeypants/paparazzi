import os
from optparse import OptionParser
import autodoc 

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


if __name__ == "__main__":
    print "Building Documentation"
    (options, args) = parse_args()
    
    if options.input_dir:
        moddir=None # use default
    else:
        moddir=options.input_dir
    # TODO: test/respect "-p", "-o", "-i" and "-v"
    # TODO: replace all the printing with logging
    psr = autodoc.PaparazziParser(modules_dir=moddir)

    d = autodoc.Generator(parser=psr)
    d.generate(output_format="Doxygen")

    if options.verbose:
        print("Generating module documentation in " + output_dir)
