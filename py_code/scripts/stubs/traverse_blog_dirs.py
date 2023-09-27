"""
Stub script that traverses through all blog directories.
"""
import logging
import os

from py_code.config.config import Config

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    blog_base_dir = config.get_geocities_config()['blog_base_dir']

    # db handle if needed
    # conn = MysqlConnection(config.get_mysql_config())

    for blog in os.listdir(blog_base_dir):
        print("processing blog {0}".format(blog))
        # TODO - blog directory located, do something with it
