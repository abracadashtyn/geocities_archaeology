"""
Some of the neighborhoods have incorrect capitalization on their directory names, depending on whether the data came
from the lowercase category of the Geocities torrent or the uppercase category, or somewhere else. This script renames
the incorrectly cased directories and creates empty subdirectiories for neighborhoods/subneighborhoods I have no data
for. This is all to prepare to get missing data from the Wayback Machine, where these neighborhoods will require correct
capitalization to hit the right URL. Rather than look it up every time I'm just correcting it once.
"""

import json
import logging
import os

from py_code.config.config import Config

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    geocities_config = config.get_geocities_config()
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']
    neighborhoods = config.get_neighborhood_json()

    # fix top level neighborhoods:
    neighborhood_keys = neighborhoods.keys()
    neighborhood_base_dir_contents = os.listdir(neighborhood_base_dir)
    for dirname in neighborhood_base_dir_contents:
        case_insensitive_match = [n for n in neighborhood_keys if n.lower() == dirname.lower()]
        if len(case_insensitive_match) == 1:
            if dirname == case_insensitive_match[0]:
                logging.debug(f"Exact match for {dirname} with {case_insensitive_match[0]}")
                neighborhood_keys = [n for n in neighborhood_keys if n != case_insensitive_match[0]]
                continue
            else:
                original_path = os.path.join(neighborhood_base_dir, dirname)
                new_path = os.path.join(neighborhood_base_dir, case_insensitive_match[0])
                logging.info(f"Case insensitive match; will rename {original_path} to {new_path}")
                os.rename(original_path, new_path)
                neighborhood_keys = [n for n in neighborhood_keys if n != case_insensitive_match[0]]
                continue

        elif len(case_insensitive_match) > 1:
            raise ValueError(f"Multiple matches for {dirname}: {case_insensitive_match}")

    for missing_neighborhood in neighborhood_keys:
        mn_path = os.path.join(neighborhood_base_dir, missing_neighborhood)
        logging.info(f"Creating missing neighborhood {missing_neighborhood} at {mn_path}")
        os.mkdir(mn_path)

    # fix subneighborhoods:
    for name, subneighborhood_list in neighborhoods.items():
        logging.info(f"Processing neighborhood {name}")

        neighborhood_path = os.path.join(neighborhood_base_dir, name)
        if not os.path.exists(neighborhood_path):
            raise ValueError(f"Neighborhood path {neighborhood_path} does not exist")
        if not os.path.isdir(neighborhood_path):
            raise ValueError(f"Neighborhood path {neighborhood_path} is not a directory")

        neighborhood_path_contents = os.listdir(neighborhood_path)
        for subdir_name in neighborhood_path_contents:
            # by this point, the data has been cleaned such that all remaining subdirectories are 4 digit site ids or
            # subneighborhoods.
            try:
                possible_site_id = int(subdir_name)
                continue
            except ValueError:
                logging.info(f"Comparing subneighborhood {subdir_name}")
                case_insensitive_match = [n for n in subneighborhood_list if n.lower() == subdir_name.lower()]
                if len(case_insensitive_match) == 1:
                    if subdir_name == case_insensitive_match[0]:
                        logging.debug(f"Exact match for {subdir_name} with {case_insensitive_match[0]}")
                        subneighborhood_list = [n for n in subneighborhood_list if n != case_insensitive_match[0]]
                        continue
                    else:
                        original_path = os.path.join(neighborhood_path, subdir_name)
                        new_path = os.path.join(neighborhood_path, case_insensitive_match[0])
                        logging.info(f"Case insensitive match; will rename {original_path} to {new_path}")
                        os.rename(original_path, new_path)
                        subneighborhood_list = [n for n in subneighborhood_list if n != case_insensitive_match[0]]
                        continue

        for missing_subneighborhood in subneighborhood_list:
            ms_path = os.path.join(neighborhood_path, missing_subneighborhood)
            logging.info(f"Creating missing subneighborhood {missing_subneighborhood} at {ms_path}")
            os.mkdir(ms_path)


