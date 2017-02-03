# Bitcoind Celery Notifier

The `bitcoind` program has three notification settings in its
configuration file which trigger system commands upon certain
conditions:

* `blocknotify`
  * fires whenever there is a new block
  * passes the new block's hash
* `walletnotify`
  * fires whenever
    * a new transaction appears in the mempool
	* a transaction is mined
  * passes the transaction's ID
* `alertnotify`
  * fires whenever there is an alert
  * passes the alert's text
  
This repository contains three corresponding scripts (`blocknotify`,
`walletnotify`, and `alertnotify`) which, when run by `bitcoind`,
simply deposit their arguments onto RabbitMQ queues.

Celery tasks (defined by you, somewhere else) can then process these
queues appropriately, likely by turning around and querying `bitcoind`
for more details on the new block, transaction, alert, &c.

# Installation

For now, simply clone this repository somewhere:

```
$ git clone https://github.com/unchained-capital/bitcoind-celery-notifier
```

# Configuration

Some configuration is needed to find your RabbitMQ server and to
ensure data is enqueued so your Celery tasks will find it.

The default configuration file read by the notify scripts is
`/etc/bitcoind/notifiers.celery.yml`.  You can also specify your own
configuration file with the `-c` or `--config` arguments to any of the
scripts.

## RabbitMQ

By default, the scripts will attempt to connect to the vhost `bitcoin`
on a local RabbitMQ server on the default port (5672) with no
authentication.

To change any of these settings globally, set `broker_url` your
configuration file:

```yaml
---
# in /etc/bitcoind/notifiers.celery.yml

# Use a more complex RabbitMQ broker URL globally.
broker_url: "amqp://username@password:rabbitmq.example.com:5672/my/vhost"
```

## Celery

### Queue

Celery listens on a particular queue, taken by default to be `celery`.

To change this globally, set `queue` in your configuration file:

```yaml
---
# in /etc/bitcoind/notifiers.celery.yml

# Use this Celery queue globally.
queue: bitcoin_tasks
```

### Tasks

The actual tasks Celery runs are named as strings.  Configure them as
follows:

```yaml
---
# in /etc/bitcoind/notifiers.celery.yml

# Define tasks for blocknotify
blocknotify:
  - tasks:
      - stats.track_block
	  - accounting.update_accounts
	  - security.scan_transactions
	  ...

# Similar settings apply for walletnotify and alertnotify
walletnotify:
  ...
alertnotify
  ...
```

By default, no tasks are run for any of the scripts (you'll see a
warning message in this case).

Note that the `tasks` key is nested within an array within the
`blocknotify` key above (and the same for `walletnotify` and
`alertnotify`).  This seems redundant, but is useful when different
tasks need to be routed to different RabbitMQ servers or vhosts or
different Celery queues.

Here is a more complex example:

```yaml
---
# in /etc/bitcoind/notifiers.celery.yml

# Define tasks for blocknotify
blocknotify:
  # These tasks use global settings. 
  - tasks:
	  - accounting.update_accounts
	  ...
  # These tasks have a different broker.
  - broker_url: amqp://localhost:5672/operations
    tasks:
      - stats.track_block
	  ...
  # These tasks have a different broker and queue name.
  - broker_url: amqp://localhost:5672/security
    queue:      bitcoind
	tasks:
	  - security.scan_transactions
	  ...
```

# Usage

## Manually

You can run any of these scripts yourself:

```
$ ./blocknotify 000000000000056563c65cdd0b6f361aba84271eb33bac11f926ff627dc32361
$ ./walletnotify 7ab7852c6fde880651e751e4fc8151015614aa24a0547e5db96e08387423c44a
$ ./alertnotify 'Blockchain has begun eating itself.  Have a nice day!'
```

They all accept the following options:

* `-c` or `--config` to provide the path to a configuration file other than `/etc/bitcoind/notifiers.celery.yml`.
* `-h` or `--help` to see these options

## Automatically

To get `bitcoin` to run these scripts for you you'll need to configure
it:

```
# in /etc/bitcoind/bitcoind.conf
blocknotify=/path/to/bitcoind-celery-notifier/blocknotify %s
walletnotify=/path/to/bitcoind-celery-notifier/walletnotify %s
alertnotify=/path/to/bitcoind-celery-notifier/alertnotify %s
```

Don't forget to add the `-c` option to the above lines if you want
`bitcoind` to use a configuration file other than
`/etc/bitcoind/notifiers.celery.yml`.  In either case, the user
running `bitcoin` will need permissions to be able to read the
configuration file.
