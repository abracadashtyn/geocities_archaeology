"""Traverses through all backup blog directories combines them with the existing contents of the blog directory. I
saw some instances when unpacking each directory in the torrent where blogs appeared multiple times - for instance,
a blog would be included in both the uppercase and lowercase directories - so you might see a blog dir with the name
'Yahooid' in the uppercase directory and another named 'yahooid' in the lowercase directory. The relocation script
just chucks these duplicate named blogs into a backup directory so I could examine them. When I did, it's clear
they're intended to be combined with their lowercase counterparts. This script does that, then deletes the backup
directory. """
import os
import shutil

from py_code.config.config import Config
from py_code.scripts.data_cleanup.comparison_helper_functions import compare_site_to_backup

if __name__ == "__main__":
    config = Config()
    geocities_config = config.get_geocities_config()
    blog_base_dir = geocities_config['blog_base_dir']
    blog_backup_dir = geocities_config['blog_backup_dir']

    if blog_backup_dir is None or blog_backup_dir == "":
        raise Exception("blog_backup_dir is not set in config.json")

    if not os.path.exists(blog_backup_dir):
        raise Exception("blog_backup_dir {0} does not exist".format(blog_backup_dir))

    for blogname in os.listdir(blog_backup_dir):
        # printing instead of logging in this file so output won't be out of order when combined with comparision
        # printouts from filecmp
        print(f"Processing blog '{blogname}' from backup")
        compare_site_to_backup(blog_base_dir, blog_backup_dir, blogname)
        print(f"Finished processing blog '{blogname}' and removed backup\n--------------------------------------")