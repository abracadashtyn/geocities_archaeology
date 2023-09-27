import os

from py_code.config.config import Config
from py_code.classes.mysql_connection import MysqlConnection
from py_code.classes.site_info import query_site_stats_by_yahoo_id, SiteInfo


if __name__ == "__main__":
    config = Config()
    conn = MysqlConnection(config.get_mysql_config())
    blog_base_dir = config.get_geocities_config()['blog_base_dir']
    endings = {}

    for blog in os.listdir(blog_base_dir):
        print("processing blog {0}".format(blog))

        # check if a record for this site already exists in the database;
        existing_site_data = conn.execute_sql_query(*query_site_stats_by_yahoo_id(blog))
        if existing_site_data is None or len(existing_site_data) == 0:
            print("No existing data found for site {0} - need to create a record".format(blog))
            site = SiteInfo(yahoo_id=blog)
            file_endings = site.generate_numeric_stats_from_dir(blog_base_dir)
            for file_ending, count in file_endings.items():
                if file_ending not in endings:
                    endings[file_ending] = 0
                endings[file_ending] += count

            conn.execute_sql_statement(*site.generate_insert_statement())
            print("Inserted record for site.")

        else:
            print("Found existing data for site {0} - do nothing".format(blog))
            # assume if it's in the database it's already been processed and we don't need to calculate stats again

        print("-----")

    print("File endings:")
    for file_ending, count in sorted(endings.items(), key=lambda x: x[1], reverse=True):
        print("{0}: {1}".format(file_ending, count))