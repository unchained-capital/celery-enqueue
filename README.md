# Celery Notifier

[Celery](http://www.celeryproject.org/) is a distributed task queue
for Python that uses [RabbitMQ](https://www.rabbitmq.com/) (or
[Redis](https://redis.io/)) for state.

The usual pattern in Celery is to have task implementations and the
code which enqueues/schedules tasks within the same application:

```python
# in tasks.py

def doit(arg):
	...
```

```python
# in app.py
from tasks import *
result = doit.delay(123)
```

Sometimes it is useful to be able to split these functions across
totally different hosts/applications, using Celery's state (e.g. -
RabbitMQ) to connect them.  Unfortunately, Celery doesn't make it as
easy as it could be to schedule the `doit` task without having the
`tasks.py` file available locally.

The `celery-enqueue` program included with this library makes this
easy.

# Installation

Via `pip`:

```
$ pip install celery-notifier
```

Via source:

```
$ git clone https://github.com/unchained-capital/celery-notifier
$ cd celery-notifier
$ make
```

# Usage

## Command-Line

Assuming you installed via `pip`, the `celery-enqueue` command should
be installed.  Try running it with the `-h` flag to see more details:

```
$ celery-enqueue -h
```

If you have a RabbitMQ server running locally at the default port with
no custom vhosts, users, or security, you can run:

```
$ celery-enqueue my_app.tasks.my_task arg1 arg2
```

to enqueue the task `my_app.tasks.my_task` with arguments `('arg1',
'arg2')` into the local RabbitMQ broker's `celery` queue.  This should
be identical to having run `my_app.tasks.my_task.delay("arg1",
"arg2")` from within your application.

This behavior can be configured on the command-line as well as via a
configuration file.

## Python

Assuming that your `PYTHONPATH` is properly set up (this is handled
for you if you installed using `pip`), and you have a RabbitMQ server
running locally at the default port with no custom vhosts, users, or
security, you can run:

```python
from celery_notifier import enqueue
enqueue("my_app.tasks.my_task", ["arg1", "arg2"])
```

to enqueue the task `my_app.tasks.my_task` with arguments `('arg1',
'arg2')` into the local RabbitMQ broker's `celery` queue.  This should
be identical to having run `my_app.tasks.my_task.delay("arg1",
"arg2")` from within your application.

This behavior can be configured at runtime:

```python
from celery_notifier import enqueue, set_config
set_config({'host': 'rabbitmq.internal'})
enqueue("my_app.tasks.my_task", ["arg1", "arg2"])
```

# Configuration

See `example/celery-notifier.yml` in this repository for an example
configuration file you can copy and modify.

## RabbitMQ

Some configuration is needed to find your RabbitMQ server and to
ensure data is enqueued so your Celery tasks will find it.

By default, the scripts will attempt to connect to the vhost `/` on a
local RabbitMQ server on the default port (5672) with no
authentication.

The following configuration settings affect this default behavior:

* `user` -- the name of the RabbitMQ user
* `password` -- the password of the RabbitMQ user
* `host` -- the hostname or IP of the RabbitMQ broker
* `port` -- the port of the RabbitMQ broker
* `vhost` -- the RabbitMQ vhost used by Celery
* `queue` -- the RabbitMQ queue used by Celery

These settings can be provided on the command-line, via a
configuration file, or by calling `set_config`.

## Error handling

In case of an uncaught exception, the default behavior is for
`celery-enqueue` to print a Python stacktrace and exit with a nonzero
return code.

The following configuration settings affect this default behavior:

* `success` -- make `celery-enqueue` always exit successfully with a return code of 0
* `error_command` -- run this command.  The following strings will be interpolated:
 * `%e` -- the error message of the exception
 * `%u` -- the (masked) URL of the RabbitMQ broker
 * `%t` -- the name of the task
 * `%a` -- the arguments to the task

(The `error_command` will only run if `success` is also set.)

A simple example, handled via a configuration file:

```yaml
# in config.yml
error_command: |	
	echo 'ERROR: Failed to enqueue task %t(%a) at broker %u. (%e)'
```

And invoked like this:

```
  $ celery-enqueue -c config.yml my_app.tasks.my_task arg1 arg2
```
