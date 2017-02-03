from sys  import stderr
from yaml import load

DEFAULT_CONFIG_PATH = "/etc/bitcoind/notifiers.celery.yml"

_CONFIG = {
    'broker_url': 'amqp://localhost:5672/bitcoin',
    'queue':      'celery',
    'blocknotify':  [],
    'walletnotify': [],
    'alertnotify':  [],
}

def load_config(path):
    try:
        _CONFIG.update(load(open(path)))
    except Exception as e:
        stderr.write("ERROR: Could not load configuration file at {}. ({})\n".format(path, type(e).__name__))
        return {}

def get_config(key, default=None):
    return _CONFIG.get(key, default)
