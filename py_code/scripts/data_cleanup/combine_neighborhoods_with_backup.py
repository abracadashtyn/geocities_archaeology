"""Traverses through all backup neighborhood directories combines them with the existing contents of the neighborhood
directory. I saw some instances when unpacking each directory in the torrent where neighborhoods appeared multiple
times - for instance, 'Athens' would be included in the upppercase directory and 'athens' would be included in the
lowercase directory - having some overlap in the site IDs appearing within each. This script copies over any site
that does not exist in the neighborhood already, and for sites that do already exist, compares their contents and
copies over anything missing or different. Then, it deletes the backup site. """
import logging
import os
import shutil

from py_code.config.config import Config
from py_code.scripts.data_cleanup.comparison_helper_functions import compare_site_to_backup
from py_code.scripts.stubs.helper_functions import get_site_id

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    config = Config()
    geocities_config = config.get_geocities_config()
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']
    backup_base_dir = geocities_config['neighborhood_backup_dir']

    for neighborhood in os.listdir(backup_base_dir):
        # printing instead of logging in this file so output won't be out of order when combined with comparision
        # printouts from filecmp
        print(f"Deduplicating backup of '{neighborhood}' from {backup_base_dir}")
        backup_neighborhood_dir = os.path.join(backup_base_dir, neighborhood)
        original_neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)

        for subdir in os.listdir():
            for subdir in os.listdir(backup_neighborhood_dir):
                # check that this is a directory - any files at this level are corrupt data and can be disregarded
                if not os.path.isdir(os.path.join(backup_neighborhood_dir, subdir)):
                    logging.warning(f"Found file {subdir} in neighborhood {neighborhood} - skipping")
                    continue

                # directories at this level can be named for the 4 digit site id, a corrupted site id with arbitrary
                # chars appended at the end, or a subneighborhood
                possible_site_id = get_site_id(subdir)

                # if we match the regex above, we found a 4 digit site id -like string
                if possible_site_id is not None:
                    if str(possible_site_id) != subdir:
                        logging.warning(f"Site id string '{subdir}' in neighborhood '{neighborhood}' is likely "
                                        f"corrupted!")

                    print(f"Processing site id '{subdir}' in neighborhood '{neighborhood}' from backup")
                    compare_site_to_backup(original_neighborhood_dir, backup_neighborhood_dir, subdir)

                # if we can't parse an int from the subdir string, it's probably a subneighborhood
                else:
                    backup_subneighborhood_dir = os.path.join(backup_neighborhood_dir, subdir)
                    original_subneighborhood_dir = os.path.join(original_neighborhood_dir, subdir)

                    for subsubdir in os.listdir(backup_subneighborhood_dir):
                        # check again that this is a directory - any files at this level are corrupt data
                        if not os.path.isdir(os.path.join(backup_subneighborhood_dir, subsubdir)):
                            logging.warning(
                                f"Found file '{subsubdir}' in neighborhood '{neighborhood}' subneighborhood "
                                f"'{subdir}' - skipping")
                            continue

                        # check again if this is a site id - at this level it should be (or a corruption of one)
                        possible_site_id = get_site_id(subsubdir)
                        if possible_site_id is None:
                            logging.error(f"Found non-numeric directory name '{subsubdir}' where site id should be! "
                                          f"neighborhood '{neighborhood}' subneighborhood '{subdir}'")
                            exit(4)
                        else:
                            if str(possible_site_id) != subsubdir:
                                logging.warning("Site id string is likely corrupted!")

                            print(f"Processing site id '{subsubdir}' in neighborhood '{neighborhood}' subneighborhood "
                                  f"'{subdir}' from backup")
                            compare_site_to_backup(original_subneighborhood_dir, backup_subneighborhood_dir, subsubdir)
