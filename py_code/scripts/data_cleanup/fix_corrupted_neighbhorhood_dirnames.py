"""Some of the neighborhood blogs unpacked with directories like 1234_ or 1234%A0 - I checked some of these and it's
clear their contents are intended to be with the base 4 digit blog (1234 in the example above). This script checks
those directories discards the contents of the corrupted one if they already exist in the actual one, copies missing
files, and allows the user to choose whether or not to copy diffed files over depending on their content. """
import filecmp
import logging
import os
import shutil

from py_code.config.config import Config
from py_code.scripts.data_cleanup.comparison_helper_functions import diff_files
from py_code.scripts.stubs.helper_functions import get_site_id


def fix_corrupted_site(dir, original_string, regex_match):
    current_dir = os.path.join(dir, original_string)
    potential_matching_dir = os.path.join(dir, regex_match)
    print(f"Comparing {current_dir} to {potential_matching_dir}")
    comparison = filecmp.dircmp(current_dir, potential_matching_dir)
    if len(comparison.left_only) == 0 and len(comparison.diff_files) == 0:
        print("Existing directory already contains all content of corrupted directory")
        shutil.rmtree(current_dir)
    else:
        comparison.report_full_closure()
        # if there are files in the corrupted directory that are not in the existing directory, we need to copy them
        if len(comparison.left_only) > 0:
            print("Some content in corrupted directory is not in existing directory")
            for file in comparison.left_only:
                print(f"Copying {file} from {current_dir} to {potential_matching_dir}")
                shutil.copy(os.path.join(current_dir, file), potential_matching_dir)

        # if there are differences in files that exist in both, print them, then ask user what to do
        if len(comparison.diff_files) > 0:
            print("Some content in corrupted directory is different from content in existing directory")
            for diff_file in comparison.diff_files:
                print(f"Diffing {diff_file}")
                diff_files(os.path.join(current_dir, diff_file), os.path.join(potential_matching_dir, diff_file))
                discard = None
                while discard not in ['y', 'n']:
                    discard = input("Discard file from corrupted dir? (y/n)")

                if discard == 'y':
                    print(f"Deleting {diff_file} from {current_dir}")
                    os.remove(os.path.join(current_dir, diff_file))
                else:
                    name, ext = os.path.splitext(diff_file)
                    new_name = f"{name}_from{original_string}{ext}"
                    print(f"Renaming file to {new_name} and relocating")
                    shutil.copy(os.path.join(current_dir, diff_file), os.path.join(potential_matching_dir, new_name))
                    os.remove(os.path.join(current_dir, diff_file))


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    geocities_config = config.get_geocities_config()
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']

    for neighborhood in os.listdir(neighborhood_base_dir):
        print(f"Looking at {neighborhood}")
        current_neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)

        for subdir in os.listdir(current_neighborhood_dir):
            # check that this is a directory - any files at this level are corrupt data and can be deleted
            fq_subdir = os.path.join(current_neighborhood_dir, subdir)
            if not os.path.isdir(fq_subdir):
                logging.warning(f"Found file {subdir} in neighborhood {neighborhood} - deleting")
                os.remove(fq_subdir)
                continue

            # at this level, could either be 4 digit site id, corrupted 4 digit site id (chars appended to end),
            # or subneighborhood
            possible_site_id = get_site_id(subdir)

            # if we match the regex above, we found a 4 digit site id -like string
            if possible_site_id is not None:
                print(f"Suspect {subdir} is a site id, neighborhood {neighborhood}")
                if str(possible_site_id) != subdir:
                    print("Site id is corrupted")
                    fix_corrupted_site(current_neighborhood_dir, subdir, possible_site_id)

            # otherwise this is probably a subneighborhood
            else:
                print(f"Suspect {subdir} is a subneighborhood")
                current_subneighborhood_dir = os.path.join(current_neighborhood_dir, subdir)
                for subsubdir in os.listdir(current_subneighborhood_dir):
                    # check that this is a directory - any files at this level are corrupt data and can be deleted
                    fq_subsubdir = os.path.join(fq_subdir, subsubdir)
                    if not os.path.isdir(fq_subdir):
                        logging.warning(f"Found file {subdir} in neighborhood {neighborhood} - deleting")
                        os.remove(fq_subdir)
                        continue

                    # check again if this is a site id - at this level it should be (or a corruption of one)
                    possible_site_id = get_site_id(subsubdir)
                    if possible_site_id is None:
                        print("SHOULD NOT BE POSSIBLE!")
                        exit(4)
                    else:
                        print(f"Suspect {subsubdir} is a site id, neighborhood {neighborhood}, subneighborhood {subdir}")
                        if str(possible_site_id) != subsubdir:
                            print("Site id is corrupted")
                            fix_corrupted_site(current_subneighborhood_dir, subsubdir, possible_site_id)

