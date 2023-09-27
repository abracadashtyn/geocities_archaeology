import os
import re

from py_code.config.config import Config
from py_code.classes.mysql_connection import MysqlConnection
from py_code.classes.site_info import SiteInfo, query_site_stats_by_neighborhood_info


def check_is_blog_id(string):
    try:
        int(string)
        return True
    except ValueError:
        regex_try = re.match("([0-9]{4})", string)
        if regex_try is not None:
            return True
    return False


if __name__ == "__main__":
    config = Config()
    conn = MysqlConnection(config.get_mysql_config())
    neighborhood_base_dir = config.get_geocities_config()['neighborhood_base_dir']
    endings = {}

    for neighborhood in os.listdir(neighborhood_base_dir):
        print("processing neighborhood {0}".format(neighborhood))
        neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)

        for subdir in os.listdir(neighborhood_dir):
            # at this level, could either be 4 digit site id or all alphabetical subneighborhood
            if check_is_blog_id(subdir):
                print(f"Suspect '{subdir}' is a site id, neighborhood {neighborhood}")
                existing_site_data = conn.execute_sql_query(*query_site_stats_by_neighborhood_info(subdir, neighborhood, None))
                if existing_site_data is None or len(existing_site_data) == 0:
                    print("No existing data found for site - need to create a record")
                    site = SiteInfo(neighborhood=neighborhood, subneighborhood=None, neighborhood_id=subdir)
                    file_endings = site.generate_numeric_stats_from_dir(neighborhood_dir)
                    for file_ending, count in file_endings.items():
                        file_ending = file_ending.lower()
                        if file_ending not in endings:
                            endings[file_ending] = 0
                        endings[file_ending] += count

                    conn.execute_sql_statement(*site.generate_insert_statement())
                    print("Inserted record for site.")

                else:
                    print("Found existing data for site {0} - do nothing".format(subdir))
                    # assume if it's in the database it's already been processed and we don't need to calculate stats again

            else:
                print(f"Suspect '{subdir}' is a subneighborhood")
                subneighborhood_dir = os.path.join(neighborhood_dir, subdir)
                for subsubdir in os.listdir(subneighborhood_dir):
                    # check again if this is a site id - at this level it should be
                    if check_is_blog_id(subsubdir):
                        print(f"Suspect {subsubdir} is a site id, neighborhood {neighborhood}, subneighborhood {subdir}")
                        existing_site_data = conn.execute_sql_query(
                            *query_site_stats_by_neighborhood_info(subdir, neighborhood, subsubdir))
                        if existing_site_data is None or len(existing_site_data) == 0:
                            print("No existing data found for site - need to create a record")
                            site = SiteInfo(neighborhood=neighborhood, subneighborhood=subdir, neighborhood_id=subsubdir)
                            file_endings = site.generate_numeric_stats_from_dir(subneighborhood_dir)
                            for file_ending, count in file_endings.items():
                                file_ending = file_ending.lower()
                                if file_ending not in endings:
                                    endings[file_ending] = 0
                                endings[file_ending] += count

                            conn.execute_sql_statement(*site.generate_insert_statement())
                            print("Inserted record for site.")
                    else:
                        print(f"{subsubdir} is not an int - SHOULD NOT BE POSSIBLE! (neighborhood {neighborhood}, subneighborhood {subdir})")
                        exit(4)
        print("-----")

    print("File endings:")
    for file_ending, count in sorted(endings.items(), key=lambda x: x[1], reverse=True):
        print("{0}: {1}".format(file_ending, count))