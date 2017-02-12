from sys      import stderr
from os       import system
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
    
def _run(program_name, arg_name, notify_type, help_text):
    parser        = _command_line_parser(program_name, arg_name, help_text)
    options, args = parser.parse_args()
    
    if len(args) == 0:
        stderr.write(parser.get_usage().split("\n")[0] + "\n")
        exit(1)
    else:
        load_config(options.config_path)
        enqueue_tasks(notify_type, args[0])
        exit(0)

def _handle_error(program_name, e):
    error_command = get_config('error_command')
    if error_command:
        error_message = "{}: {}".format(type(e).__name__, str(e))
        error_command = error_command.replace('%p', program_name)
        error_command = error_command.replace('%e', error_message)
        system(error_command)
    else:
        raise e

def run(program_name, arg_name, notify_type, help_text):
    try:
        _run(program_name, arg_name, notify_type, help_text)
    except Exception as e:
        _handle_error(program_name, e)
        exit(2)
