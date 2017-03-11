from sys      import stderr, stdout
from os       import system
from optparse import OptionParser

from .config import *
from .queue  import *

USAGE = "%prog [OPTIONS] TASK [ARG] ..."

HELP = """Enqueue data in RabbitMQ to create tasks for Celery workers.

Celery doesn't provide a simple way to append tasks to worker queues
from outside an application's Python context.  This program fixes
that.

Given you have written a Celery task in your Python application:

  # Example task in Python module myapp.tasks
  @task
  def some_task(color, width):
    ...

You can enqueue data for this task via:

  $ %prog myapp.tasks.some_task red 15

Which would be the equivalent of having run

  some_task.delay("red", "15")

from within your application.

You need to provide the full Python namespace of the task as it runs
in your worker ('myapp.tasks.some_task', in this case).

Positional command-line arguments will be passed directly to the task
without any conversion or parsing (in particular, the 'width' argument
above of '15' will remain a string when received by 'some_task').

Keyword arguments are not currently supported."""

def run():
    """The main function for the celery-enqueue command.

    Parses the command-line, loads configuration, and enqueues the
    task."""
    parser = _command_line_parser()
    options, all_args = parser.parse_args()
    _validate_args(all_args, parser)
    load_config(options)
    validate_authentication()

    task = all_args[0]
    args = all_args[1:] if len(all_args) > 1 else []

    if get_config('success'):
        try:
            result = enqueue(task, args)
        except Exception as e:
            result = None
            _run_error_command(task, args, e)
    else:
        result = enqueue(task, args)
    if result:
        stdout.write(str(result) + "\n")
    exit(0)
    
def _command_line_parser():
    usage = """usage: {}

{}""".format(USAGE, HELP)
    parser = OptionParser(usage=usage)

    #
    # Note: Each option's 'dest' should equal the corresponding config
    # key.
    #
    
    parser.add_option("-u", "--user",
                      dest="user",
                      help="RabbitMQ user name",
                      metavar="NAME")

    parser.add_option("-p", "--password",
                      dest="password",
                      help="RabbitMQ user password",
                      metavar="PASSWORD")

    parser.add_option("-H", "--host",
                      dest="host",
                      help="RabbitMQ host [default: '{}']".format(get_config('host')),
                      metavar="HOST")

    parser.add_option("-P", "--port",
                      dest="port",
                      help="RabbitMQ port [default: {}]".format(get_config('port')),
                      type='int',
                      metavar="PORT")

    parser.add_option("-V", "--vhost",
                      dest="vhost",
                      help="RabbitMQ virtual host [default: '{}']".format(get_config('vhost')),
                      metavar="VHOST")

    parser.add_option("-q", "--queue",
                      dest="queue",
                      help="Name of RabbitMQ queue used by Celery [default: '{}']".format(get_config('queue')),
                      metavar="NAME")

    parser.add_option("-s", "--success",
                      action="store_true",
                      dest="success",
                      help="Always exit successfuly, with a return code of 0")

    parser.add_option("-e", "--errors",
                      dest="error_command",
                      help="Run this (interpolated) command in case of an error",
                      metavar="COMMAND")

    parser.add_option("-v", "--verbose",
                      action="store_true",
                      dest="verbose",
                      help="Print details while running")

    parser.add_option("-c", "--config",
                      dest="config_path",
                      help="Path to YAML configuration file",
                      metavar="FILE")

    return parser

def _validate_args(args, parser):
    if len(args) == 0:
        stderr.write(parser.get_usage().split("\n")[0] + "\n")
        exit(1)

def _run_error_command(task, args, e):
    command = get_config('error_command')
    if command is None:
        return
    error_message = "{}: {}".format(type(e).__name__, str(e))
    command = command.replace('%e', error_message)
    command = command.replace('%t', task)
    command = command.replace('%a', ','.join(args))
    command = command.replace('%u', masked_broker_url())
    system(command)
