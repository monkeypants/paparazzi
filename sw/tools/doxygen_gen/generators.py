import os
import jinja2
import generators

class BaseGenerator(object):
    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(
                    os.path.dirname(__file__),
                    'templates')))


class DoxygenGenerator(BaseGenerator):
    def __init__(
            self, options,
            module_parser, output_dir):
        self.options = options
        self.module_parser = module_parser
        self.output_dir = output_dir
        self.validate_output_dir()
        super(DoxygenGenerator, self).__init__()
        
    def validate_output_dir(self):
        if not os.path.isdir(self.output_dir):
            msg = "Output directory " + self.output_dir
            if not self.options.create_parent_dirs:
                print(msg + " not valid.")
                sys.exit(1)
            else:
                msg += " doesn't exit yet. Creating it." 
                print(msg)
                os.makedirs(self.output_dir)
