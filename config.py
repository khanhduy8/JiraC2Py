import json

def parse_config(json_config_path):
    """Parse JSON configuration and return a configparser.ConfigParser object."""

    config_data = json.load(open(json_config_path, "rt"))

    return config_data