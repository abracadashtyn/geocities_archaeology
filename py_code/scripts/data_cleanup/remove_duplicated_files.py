"""
There are quite a few sites that contain duplicate files with the same name, but _1 appended - like 'index.html' versus
'index_1.html'. This script finds those instances and deletes the duplicated '_1' file.
"""
import logging
import os

from py_code.config.config import Config
from py_code.scripts.data_cleanup.comparison_helper_functions import diff_files
from py_code.scripts.stubs.helper_functions import get_site_id


def dedup_site_contents(site_base_dir):
    for root, dirs, files in os.walk(site_base_dir):
        for file in files:
            file_name, file_ending = os.path.splitext(file)
            if "_1" in file_name:
                file_path = os.path.join(root, file)

                regularized_filename = file_name.replace("_1", "")
                regularized_file_path = os.path.join(root, regularized_filename + file_ending)

                logging.debug(f"found {file_path} - might be a duplicate of {regularized_file_path}")
                if not os.path.exists(regularized_file_path):
                    logging.debug("Regularized file path does not exist! false positive")
                    continue
                if not os.path.isfile(regularized_file_path):
                    logging.debug("Regularized path exists but is not a file")
                    continue

                try:
                    file_diff = diff_files(file_path, regularized_file_path)
                    if file_diff and len(file_diff) > 0:
                        logging.debug("Files have differences; will not delete anything.")
                    else:
                        logging.info(
                            f"Files '{file_path}' and '{regularized_file_path}' are identical; deleting '{file}'")
                        os.remove(file_path)
                except Exception:
                    logging.exception(f"Exception while comparing files '{file_path}' and '{regularized_file_path}'")
                    # do nothing


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    blog_base_dir = config.get_geocities_config()['blog_base_dir']

    # handle blogs
    '''for blog in os.listdir(blog_base_dir):
        logging.debug("processing blog '{0}'".format(blog))
        current_blog_dir = os.path.join(blog_base_dir, blog)
        dedup_site_contents(current_blog_dir)'''

    # handle neighborhoods
    neighborhood_base_dir = config.get_geocities_config()['neighborhood_base_dir']
    for neighborhood in os.listdir(neighborhood_base_dir)[20:]:
        logging.info(f"Looking at {neighborhood}")
        current_neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)

        for subdir in os.listdir(current_neighborhood_dir):
            fq_subdir = os.path.join(current_neighborhood_dir, subdir)

            # check that this is a directory - any files at this level are corrupt data and can be disregarded
            if not os.path.isdir(fq_subdir):
                logging.warning(f"Found file {subdir} in neighborhood {neighborhood} - skipping")
                continue

            # directories at this level can be named for the 4 digit site id, a corrupted site id with arbitrary chars
            # appended at the end, or a subneighborhood
            possible_site_id = get_site_id(subdir)

            # if we match the regex above, we found a 4 digit site id -like string
            if possible_site_id is not None:
                logging.debug(f"Suspect '{subdir}' is a site id in neighborhood '{neighborhood}'")
                if str(possible_site_id) != subdir:
                    logging.warning("Site id string is likely corrupted!")
                dedup_site_contents(fq_subdir)

            # if we can't parse an int from the subdir string, it's probably a subneighborhood
            else:
                logging.debug(f"Suspect '{subdir}' is a subneighborhood of '{neighborhood}'")
                for subsubdir in os.listdir(fq_subdir):
                    fq_subsubdir = os.path.join(fq_subdir, subsubdir)

                    # check again that this is a directory - any files at this level are corrupt data
                    if not os.path.isdir(fq_subsubdir):
                        logging.warning(f"Found file '{subsubdir}' in neighborhood '{neighborhood}' subneighborhood "
                                        f"'{subdir}' - skipping")
                        continue

                    # check again if this is a site id - at this level it should be (or a corruption of one)
                    possible_site_id = get_site_id(subsubdir)
                    if possible_site_id is None:
                        logging.error(f"Found non-numeric directory name '{subsubdir}' where site id should be! "
                                      f"neighborhood '{neighborhood}' subneighborhood '{subdir}'")
                        exit(4)
                    else:
                        logging.debug(
                            f"Suspect '{subsubdir}' is a site id in neighborhood '{neighborhood}' subneighborhood '{subdir}'")
                        if str(possible_site_id) != subsubdir:
                            logging.warning("Site id string is likely corrupted!")

                        dedup_site_contents(fq_subsubdir)
