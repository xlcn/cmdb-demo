import yaml
import os

config_file = os.path.join(os.path.dirname(__file__), 'config.yml')
with open(config_file) as f:
    config_yml = yaml.load(f.read())
