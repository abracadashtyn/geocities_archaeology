"""
The directory 'GEOCITIES' in the torrent root contains many partial 7z files that unpack into 1 mega-file. This file
unpacks into a different directory structure than LOWERCASE, UPPERCASE, and NUMBERS did. This script transfers only the
blogs in that directory and ignores the symlinks
"""
import logging
import os
import shutil

from py_code.config.config import Config
from py_code.scripts.data_cleanup.relocate_blogs_and_neighborhoods import neighborhoods

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    geocities_config = config.get_geocities_config()

    # hardcoding this rather than putting in settings since this is a 1 off operation and no other unpacked directories
    # follow this same structure anyway
    dir_to_migrate = os.path.join(geocities_config['original_torrent_base_dir'], "www.geocities.com\www.geocities\geocities\www.geocities.com")

    missing_blogs = []
    for item in os.listdir(dir_to_migrate):
        path = os.path.join(dir_to_migrate, item)
        if os.path.isdir(path):
            logging.info("Found blog {0}".format(path))

            # I don't think there are any neighborhoods in here, but check just in case (and exit if so, I want to know)
            # after running this, there were not any neighborhoods in the directory
            if item in neighborhoods:
                logging.info(f"Migrating neighborhood {item}")
                shutil.move(path, geocities_config['neighborhood_base_dir'])
                exit(1)
            else:
                logging.info(f"Migrating blog {item}")
                try:
                    shutil.move(path, geocities_config['blog_base_dir'])
                except shutil.Error as e:
                    if "already exists" in str(e):
                        logging.warning("blog directory '{0}' already exists!".format(item))
                        shutil.move(path, geocities_config['backup_dir'])
                    else:
                        logging.error(e)
                        exit(40)
        else:
            existing_blog = os.path.join(geocities_config['blog_base_dir'], item)
            if os.path.exists(existing_blog):
                logging.info(f"Found symlink {item} that already exists in {geocities_config['blog_base_dir']}")
            else:
                logging.info(f"found symlink {item} to blog that does not already exist in {geocities_config['blog_base_dir']}")
                missing_blogs.append(item)

    logging.warning(f"found{len(missing_blogs)} symlinks for missing blogs: ")
    for missing_blog in missing_blogs:
        logging.warning(missing_blog)
