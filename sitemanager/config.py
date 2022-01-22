
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

    # Create a new config from defaults.
    config = dict(DEFAULT_CONFIG)

    # Overwrite defaults with values from config file.
    with open(filepath) as file:
        config.update(yaml.safe_load(file))

    # Return the merged config.
    return config
