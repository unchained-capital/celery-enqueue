from yaml import load

DEFAULT_CONFIG_PATH = "/etc/bitcoind/notifiers.celery.yml"

_CONFIG = {
    # 'error_command': """echo 'ERROR: Failed to %p (%e)'""",
    'broker_url':    'amqp://localhost:5672/bitcoin',
    'queue':         'celery',
    'blocknotify':   [],
    'walletnotify':  [],
    'alertnotify':   [],
}

def load_config(path):
    _CONFIG.update(load(open(path)))

def get_config(key, default=None):
    return _CONFIG.get(key, default)
