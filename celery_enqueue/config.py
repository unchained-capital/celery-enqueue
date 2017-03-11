from yaml import load

_CONFIG = {
    'host':  'localhost',
    'port':  5672,
    'vhost': '/',
    'queue': 'celery',

    # 'error_command': """echo 'ERROR: Failed to enqueue task %t(%a) at broker %u. (%e)'""",
}

def get_config(key, default=None):
    """Return the current value of the configuration 'key' (or 'default', if not found)."""
    return _CONFIG.get(key, default)

def load_config(options):
    """Load configuration based on the given command-line `options`.

    If the `options` contain a `config_path` then the YAML file at
    that path will be loaded.

    Additional data in `options` will be used to further load
    configuration."""
    if options.config_path:
        _CONFIG.update(_load_yaml_config_file(options.config_path))

    # Basically all options except config_path
    for attr in ['success', 'error_command', 'verbose',
                 'user', 'password', 'host', 'port', 'vhost', 'queue']:
        value = getattr(options, attr)
        if value:
            _CONFIG[attr] = value

def set_config(config):
    """Update the configuration."""
    _CONFIG.update(config)

def _load_yaml_config_file(path):
    data = (load(open(path)) or {})
    if not isinstance(data, dict):
        raise ValueError("YAML configuration in {} must map to a Python dict, not a {}.".format(path, type(data).__name__))
    return data

