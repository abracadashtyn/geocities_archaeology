"""
This script assumes that none of the site data has been loaded yet. It will insert records for each site into the database,
along with basic numeric stats that can be easily calculated, like number of files, size of files, number of subdirectories, etc.
More advanced exploration of the site content will be done in other scripts.
"""
import os

from py_code.config.config import Config
from py_code.mysql_connection import MysqlConnection
from py_code.site_stats import SiteStats


def process_and_insert(blog_dir, site_stats, conn):
    site_stats.generate_numeric_stats_from_dir(blog_dir)

    # validation will throw errors, but we don't want to stop processing the rest of the sites.
    # Just log the error and move on.
    try:
        site_stats.validate()
    except Exception as e:
        print("Error processing site: {0}\nRecord was not inserted".format(e))
        return False

    # insertion outside of try-catch - if this fails I probably need to make some changes to the table structure, so I
    # want the program to throw & halt.
    conn.execute_sql_statement(site_stats.generate_insert_statement())
    return True


if __name__ == "__main__":
    config = Config()
    conn = MysqlConnection(config.get_mysql_config())
    geocities_config = config.get_geocities_config()

    print("BEGIN PROCESSING BLOGS")
    blog_base_dir = geocities_config['blog_base_dir']
    for blog in os.listdir(blog_base_dir):
        print("processing blog {0}".format(blog))
        site = SiteStats(yahoo_id=blog)
        blog_dir = os.path.join(blog_base_dir, blog)
        process_and_insert(blog_dir, site, conn)
        print("-----")

    print("END PROCESSING BLOGS\n======\nBEGIN PROCESSING NEIGHBORHOODS")
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']
    for neighborhood in os.listdir(neighborhood_base_dir):
        print("processing neighborhood {0}".format(neighborhood))
        neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)
        for subdirectory in os.listdir(neighborhood_dir):
            # 2 possibilities - this could be a site (identified by 4 digit id) or subneighborhood (string)
            try:
                neighborhood_id = int(subdirectory)
                print("Found site id {0}, neighborhood {1}".format(neighborhood_id, neighborhood))
                site = SiteStats(neighborhood=neighborhood, neighborhood_id=neighborhood_id)
                blog_dir = os.path.join(neighborhood_dir, subdirectory)
                process_and_insert(blog_dir, site, conn)
                print("-----")

            except ValueError:
                print("subdirectory {0} is suspected sub-neighborhood".format(subdirectory))
                subneighborhood_dir = os.path.join(neighborhood_dir, subdirectory)
                for subdirectory_2 in os.listdir(os.path.join(subneighborhood_dir)):
                    neighborhood_id = int(subdirectory_2)   # this should cast now; if not, throw
                    print("Found site id {0}, neighborhood {1}, subneighborhood {2}".format(neighborhood_id,
                                                                                            neighborhood, subdirectory))
                    site = SiteStats(neighborhood=neighborhood, subneighborhood=subdirectory, neighborhood_id=neighborhood_id)
                    blog_dir = os.path.join(subneighborhood_dir, subdirectory_2)
                    process_and_insert(blog_dir, site, conn)
                    print("-----")
