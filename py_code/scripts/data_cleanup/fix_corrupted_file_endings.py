"""There are some file endings that were corrupted when I unzipped them from the main torrent. The two instances I
particularly care about are:
- html files that end with .htm{something} or .html{something} where something is just
garbled text. The ones I spot checked are valid html files, so fixing their extensions to .html means our ingestion
script will properly count the number of html files in the site.
- jpg files that end with .jpe,{something} or .jpeg,{something} where something is just garbled text. I havent gotten
to one of these yet though
TODO update docs here when you figure out if those are corrupt and need to be tossed or can be renamed"""
import logging
import os
import re

from py_code.config.config import Config
from py_code.scripts.data_cleanup.comparison_helper_functions import diff_files


def fix_corrupted_file_endings(site_base_dir):
    for root, dirs, files in os.walk(site_base_dir):
        for file in files:
            filename, ext = os.path.splitext(file)
            ext = ext.lower()

            # fix up corrupted html file endings
            html_match = re.match("\.html?(.+)", ext)
            if html_match and ext not in [".html", ".htm"]:
                print(f"Found corrupted html file ending {ext} for {file}")
                # special case where the filename is like 'index.html_A=D' - these are all index files that differ
                # slightly in which index file they link to next, but none of them are that interesting, so we can just
                # delete all but the original
                special_case_match = re.match("\.html_[a-z]=[a-z]", ext)
                if special_case_match:
                    print(f"Deleting {file} since it's a special case index file")
                    os.remove(os.path.join(root, file))

                else:
                    original_path = os.path.join(root, file)
                    fixed_filename = filename + ".html"
                    fixed_path = os.path.join(root, fixed_filename)
                    if os.path.exists(fixed_path):
                        print(f"Trying to fix up {original_path} to {fixed_path}, but it already exists!")

                        # get the differences between the two files. If they're identical, delete the corrupt file ending one
                        differences = diff_files(original_path, fixed_path)
                        if len(differences) == 0:
                            print(f"Deleting {original_path} since it's identical to {fixed_path}")
                            os.remove(original_path)

                        else:
                            deduped_filename = filename + html_match.group(1) + ".html"
                            deduped_path = os.path.join(root, deduped_filename)
                            print(f"Renaming {original_path} to {deduped_path}")
                            # throw here if we can't rename because deduped_path already exists - highly unlikely there
                            # will be a name collision, but if there is, we'll need to fix it up manually
                            os.rename(original_path, deduped_path)
                    else:
                        print(f"Fixing up {original_path} to {fixed_filename}")
                        os.rename(original_path, fixed_path)

            # fix up corrupted image file endings
            jpg_match = re.match("\.jpe?g,", ext)
            if jpg_match:
                print(f"Found corrupted jpg file ending {ext} for {file}")
                fixed_filename = filename + ".jpg"
                fixed_path = os.path.join(root, fixed_filename)
                if os.path.exists(fixed_path):
                    print(f"Trying to fix up {file} to {fixed_filename}, but it already exists!")
                    exit(3)
                else:
                    print(f"Fixing up {file} to {fixed_filename}")
                    exit(4)
                    os.rename(os.path.join(root, file), fixed_path)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    blog_base_dir = config.get_geocities_config()['blog_base_dir']

    # db handle if needed
    # conn = MysqlConnection(config.get_mysql_config())

    # some of these blogs have weird file endings that are intentional - skip and manually fix up later
    #  - bill_dietrich: those '_' in the html need converted to '?', idk what to do with the jpegs yet there
    skip_blogs = ['bill_dietrich']

    for blog in os.listdir(blog_base_dir):
        if blog not in skip_blogs:
            print("processing blog {0}".format(blog))
            fix_corrupted_file_endings(os.path.join(blog_base_dir, blog))
