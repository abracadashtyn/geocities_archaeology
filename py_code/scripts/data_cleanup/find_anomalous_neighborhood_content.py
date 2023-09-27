"""
Traverses through all neighborhoods and subneighborhoods. If files or non-site-id directories are found in locations
they should not be - log a warning. For instance, the contents of the directory 'Area51' should only be directories
named for 4-digit site ids or subneighborhoods of Area51, and the contents of subneighborhoods like 'Area51\\Alien'
should only be directories named for 4-digit site ids. This script only logs and waits for me to manually fix, as
these are all contents that should be placed within some subsite directory, but I have to manually identify which site,
or shift to another location if I cannot.
"""

import logging
import os

from py_code.config.config import Config

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    geocities_config = config.get_geocities_config()
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']
    neighborhood_json = config.get_neighborhood_json()

    for neighborhood in os.listdir(neighborhood_base_dir):
        # print instead of log to wait for user input
        print("Neighborhood: {0}".format(neighborhood))
        current_neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)

        for subdir in os.listdir(current_neighborhood_dir):
            fq_subdir = os.path.join(current_neighborhood_dir, subdir)

            # check that this is a directory - any files at this level are corrupt data and can be disregarded
            if not os.path.isdir(fq_subdir):
                print(f"\tERR: File {subdir}")
                continue

            try:
                possible_site_id = int(subdir)
            except ValueError:
                # if this subneighborhood does not exist in the JSON, it's not a valid subneighborhood
                from_json = neighborhood_json['neighborhoods'][subdir]
                if from_json is None:
                    print(f"\tERR: Invalid subneighborhood {subdir}")
                    continue

                # otherwise it's a valid subneighborhood and we need to check its contents
                print("\tSubneighborhood: {0}".format(subdir))
                for subsubdir in os.listdir(fq_subdir):
                    fq_subsubdir = os.path.join(fq_subdir, subsubdir)

                    # check again that this is a directory - any files at this level are corrupt data
                    if not os.path.isdir(fq_subsubdir):
                        print(f"\t\tERR: File {subsubdir}")
                        continue

                    # if it is a directory but the name does not parse to an int, it's not a valid site ID.
                    try:
                        possible_site_id = int(subsubdir)
                    except ValueError:
                        print(f"\t\tERR: Other dir {subsubdir}")

        input("Press Enter to continue...")
