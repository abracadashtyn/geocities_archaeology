import json
from pathlib import Path


class Config:
    def __init__(self):
        self.config_file = "config.json"
        with open("{0}\\{1}".format(Path(__file__).parent.absolute(), self.config_file), "r") as config_file:
            self.config = json.load(config_file)

    def get_mysql_config(self):
        return self.config['mysql']

    def get_geocities_config(self):
        return self.config['geocities']
