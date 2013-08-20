import os
import logging
from optparse import OptionParser
import autodoc 

def parse_args():
    usage = "Usage: %prog [options] modules/dir" + "\n" 
    usage += "Run %prog --help to list the options."
    parser = OptionParser(usage)
    
    idef = autodoc.PaparazziParser.default_modules_dir()
    ihelp = "read input from DIR [default: %s]" % idef
    parser.add_option(
        "-i", "--inputdir", dest="input_dir",
        help=ihelp, metavar="DIR")

    odef = autodoc.Generator.default_output_dir()
    ohelp = "write output to DIR [default: %s]" % odef
    parser.add_option(
        "-o", "--outputdir", dest="output_dir",
        help=ohelp, metavar="DIR")
    
    parser.add_option(
        "-p", "--parents",
        action="store_true", dest="create_parent_dirs",
        help="Create parent dirs of output dir if they don't exist.")
    parser.add_option(
        "-v", "--verbose",
        action="store_true", dest="verbose",
        help="Print info messages during normal operation")
    parser.add_option(
        "-d", action="store_true", dest="debug",
        help="Print lots of (typically useless) information." + \
        " Overrules -v and -q.")
    parser.add_option(
        "-q", action="store_true", dest="quiet",
        help="Supress all but the most critical output. " + \
        " Silence means success.")
    return parser.parse_args()    


if __name__ == "__main__":
    (options, args) = parse_args()

    logger = logging.getLogger('autodoc')
    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    
    if ((options.debug and (options.quiet or options.verbose))
        or (options.quiet and options.verbose)):
        msg = 'It doesnt make sense to use -v, -q or -d together.'
        logger.warning(msg)
    
    if options.debug:
        logger.setLevel(logging.DEBUG)
    elif options.quiet:
        logger.setLevel(logging.CRITICAL)
    elif options.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    logger.info("Building Documentation")

    if not options.input_dir:
        moddir=None
    else:
        moddir=options.input_dir

    psr = autodoc.PaparazziParser(modules_dir=moddir)

    if options.create_parent_dirs:
        mkparents = True
    else:
        mkparents = False
    if not options.output_dir:
        outdir = False
    else:
        outdir=options.output_dir

    try:
        gen = autodoc.Generator(
            parser=psr,
            create_parents=mkparents,
            output_dir=outdir)
    except autodoc.InvalidModuleInputDirError:
        msg = "Input directory with modules "
        msg += psr.modules_dir + " not found."
        logger.critical(msg)
        sys.exit(1)

    gen.modules_doc(output_format="Doxygen")
