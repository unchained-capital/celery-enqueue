from sys import stderr

from celery import Celery

from config import *

def _queue(broker_url, name):
    class celery_config(object):
        BROKER_URL             = broker_url
        CELERY_ENABLE_UTC      = True
        CELERY_TASK_SERIALIZER = 'yaml'
        CELERY_ACCEPT_CONTENT  = ['yaml']
    queue = Celery(name)
    queue.config_from_object(celery_config)
    return queue

def _enqueue_task(broker_url, queue_name, task_name, arg):
    _queue(broker_url, queue_name).send_task(task_name, args=[arg])

def enqueue_tasks(notify_type, arg):
    brokers = get_config(notify_type, [])
    for broker in brokers:
        broker_url = broker.get('broker_url', get_config('broker_url'))
        queue      = broker.get('queue',      get_config('queue'))
        tasks      = broker.get('tasks', [])
        if len(tasks) == 0:
            stderr.write("WARNING: No Celery tasks defined for '{}'\n".format(notify_type))
        for task_name in tasks:
            _enqueue_task(broker_url, queue, task_name, arg)
