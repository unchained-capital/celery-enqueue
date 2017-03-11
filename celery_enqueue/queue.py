from sys import stderr

from celery import Celery

from .config import *

def validate_authentication():
    """Validates current authentication configuration.

    Checks for BOTH user name and password or NEITHER."""
    username, password = get_config('user'), get_config('password')
    if (username or password) and not (username and password):
        stderr.write("ERROR: Must provide BOTH username and password or NEITHER.\n")
        exit(2)

def broker_url(masked=False):
    """Return the URL for the RabbitMQ broker.

    Setting 'masked' will cause the password to be masked (useful for printing)."""
    username, password = get_config('user'), get_config('password')
    if masked:
        password = "xxxxxxxx"
    authentication = "{}:{}@".format(username, password) if (username and password) else ""
    return "amqp://{}{}:{}{}".format(authentication, get_config('host'), get_config('port'), get_config('vhost'))

def enqueue(task, args):
    """Enqueue the given 'task' with the given 'args'."""
    if get_config('verbose'):
        stderr.write("Enqueuing task {}({}) at broker {}\n".format(
            task, 
            ','.join(args), 
            broker_url(masked=True)))
    return _queue().send_task(task, args=args)

def _queue():
    class celery_config(object):
        BROKER_URL             = broker_url()
        CELERY_ENABLE_UTC      = True
        CELERY_TASK_SERIALIZER = 'yaml'
        CELERY_ACCEPT_CONTENT  = ['yaml']
    queue = Celery(get_config('queue'))
    queue.config_from_object(celery_config)
    return queue
