
import os
import yaml


DEFAULT_CONFIG = {
    "scheduler": {
        "data": "./data.yml",
    },
}


def load_config(config_filepath):
    with open(config_filepath) as file:
        config = yaml.safe_load(file)
    return DEFAULT_CONFIG.update(config)
