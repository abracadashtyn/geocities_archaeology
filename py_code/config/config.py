import json
import os
from pathlib import Path


class Config:
    def __init__(self):
        self.config_file = "config.json"
        fq_path = os.path.join(Path(__file__).parent.absolute(), self.config_file)
        print(f"Config fq path: {fq_path}")
        with open(fq_path, "r") as config_file:
            self.config = json.load(config_file)

    def get_mysql_config(self):
        return self.config["mysql"]

    def get_geocities_config(self):
        return self.config["geocities_directories"]

    def get_neighborhood_json(self):
        fq_path = os.path.join(Path(__file__).parent.absolute(), self.config["neighborhood_json_filename"])
        print(f"JSON fq path: {fq_path}")
        with open(fq_path, "r") as f:
            return json.load(f)
