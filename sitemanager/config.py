
import os
import yaml


DEFAULT_CONFIG = {
    "scheduler": {
        "data": "./data.yml",
    },
}


def load_config(filepath):
    """
    Load config, falling back to default values where possible.

    Params:
        filepath: the path to the config YAML file.

    Returns:
        The config dictionary.
    """
    with open(filepath) as file:
        config = yaml.safe_load(file)
    return DEFAULT_CONFIG.update(config)
