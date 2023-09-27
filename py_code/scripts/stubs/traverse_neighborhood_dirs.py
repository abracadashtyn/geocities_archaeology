"""
Stub function that traverses through all neighborhood directories.
"""
import logging
import os

from py_code.config.config import Config
from py_code.scripts.stubs.helper_functions import get_site_id

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    geocities_config = config.get_geocities_config()
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']

    for neighborhood in os.listdir(neighborhood_base_dir):
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
                logging.info(f"Suspect '{subdir}' is a site id in neighborhood '{neighborhood}'")
                if str(possible_site_id) != subdir:
                    logging.warning("Site id string is likely corrupted!")

                # TODO - site directory located, do something with it

            # if we can't parse an int from the subdir string, it's probably a subneighborhood
            else:
                logging.info(f"Suspect '{subdir}' is a subneighborhood of '{neighborhood}'")
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
                        logging.info(f"Suspect '{subsubdir}' is a site id in neighborhood '{neighborhood}' subneighborhood '{subdir}'")
                        if str(possible_site_id) != subsubdir:
                            logging.warning("Site id string is likely corrupted!")

                        # TODO - site directory located, do something with it
