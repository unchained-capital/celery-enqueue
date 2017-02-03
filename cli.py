from sys      import stderr
from optparse import OptionParser

from config import *
from queue  import *

def _command_line_parser(program_name, arg_name, help_text):
    usage = """usage: %prog [OPTIONS] {}

{}""".format(arg_name, help_text)
    parser = OptionParser(usage=usage)
    
    parser.add_option("-c", "--config",
                      dest="config_path",
                      help="path to YAML configuration file [default: {}]".format(DEFAULT_CONFIG_PATH),
                      metavar="FILE", default=DEFAULT_CONFIG_PATH)
    
    return parser
    
def run(program_name, arg_name, notify_type, help_text):
    parser        = _command_line_parser(program_name, arg_name, help_text)
    options, args = parser.parse_args()
    
    if len(args) == 0:
        stderr.write(parser.get_usage().split("\n")[0] + "\n")
        exit(1)
    else:
        load_config(options.config_path)
        enqueue_tasks(notify_type, args[0])
        exit(0)
