import os

# these statements/queries are stored outside the class so you don't have to instantiate a SiteStats object to use them
table_name = "site_info"
create_site_info_table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (" \
                                   "id int NOT NULL AUTO_INCREMENT PRIMARY KEY, " \
                                   "yahoo_id varchar(100), " \
                                   "neighborhood varchar(50), " \
                                   "subneighborhood varchar(50), " \
                                   "neighborhood_id int, " \
                                   "file_count int, " \
                                   "site_size bigint, " \
                                   "html_file_count int, " \
                                   "html_file_size int, " \
                                   "css_file_count int, " \
                                   "image_file_count int, " \
                                   "audio_file_count int, " \
                                   "gif_file_count int, " \
                                   "video_file_count int, " \
                                   "other_file_count int, " \
                                   "subdirectory_count int" \
                                   ");"


def query_site_stats_by_yahoo_id(id):
    return f"SELECT * FROM {table_name} WHERE yahoo_id = %s", (id,)


def query_site_stats_by_neighborhood_info(site_id, neighborhood, subneighborhood=None):
    query = f"SELECT * FROM {table_name} WHERE yahoo_id = %s AND neighborhood = %s"
    values = (site_id, neighborhood)
    if subneighborhood is not None:
        query += " AND subneighborhood = %s"
        values += (subneighborhood,)
    return query, values


class SiteInfo:
    def __init__(self, yahoo_id=None, neighborhood=None, subneighborhood=None, neighborhood_id=None):
        self.yahoo_id = yahoo_id
        self.neighborhood = neighborhood
        self.subneighborhood = subneighborhood
        self.neighborhood_id = neighborhood_id
        self.sql_id = None

        # site stats to calculate
        self.file_count = 0
        self.site_size = 0
        self.html_file_count = 0
        self.html_file_size = 0
        self.css_file_count = 0
        self.image_file_count = 0
        self.audio_file_count = 0
        self.gif_file_count = 0
        self.video_file_count = 0
        self.other_file_count = 0
        self.subdirectory_count = 0

        # TODO - more?

        self.validate()

    def generate_insert_statement(self):
        col_val_pairs = {
            "yahoo_id": self.yahoo_id,
            "neighborhood": self.neighborhood,
            "subneighborhood": self.subneighborhood,
            "neighborhood_id": self.neighborhood_id,
            "file_count": self.file_count,
            "site_size": self.site_size,
            "html_file_count": self.html_file_count,
            "html_file_size": self.html_file_size,
            "css_file_count": self.css_file_count,
            "image_file_count": self.image_file_count,
            "audio_file_count": self.audio_file_count,
            "gif_file_count": self.gif_file_count,
            "video_file_count": self.video_file_count,
            "other_file_count": self.other_file_count,
            "subdirectory_count": self.subdirectory_count
        }
        columns = []
        values = []
        for k, v in col_val_pairs.items():
            columns.append(k)
            values.append(v)
        statement = "INSERT INTO {2} ({0}) VALUES ({1});".format(",".join(columns), ",".join(["%s"] * len(columns)),
                                                                 table_name)
        return statement, values

    def insert_and_update_id(self, db_conn):
        statement, values = self.generate_insert_statement()
        cursor = db_conn.cursor()
        cursor.execute(statement, values)
        self.sql_id = cursor.lastrowid
        cursor.close()
        db_conn.commit()

    def validate(self):
        if self.yahoo_id is None:
            if self.neighborhood is None:
                raise ValueError("Site must have either a YahooID or neighborhood specified!")

            if self.neighborhood_id is None:
                raise ValueError("Site with neighborhood specified must also specify neighborhood_id!")
        else:
            if not isinstance(self.yahoo_id, str):
                print("WARNING: YahooID is not a string! Converting to string.")
                self.yahoo_id = str(self.yahoo_id)

    def generate_numeric_stats_from_dir(self, root_dir):
        location = None
        filetype_map = {}
        if self.yahoo_id is not None:
            location = os.path.join(root_dir, self.yahoo_id)
        else:
            location = os.path.join(root_dir, self.neighborhood)
            if self.subneighborhood is not None:
                location = os.path.join(location, self.subneighborhood)
            location = os.path.join(location, str(self.neighborhood_id))

        for root, dirs, files in os.walk(location):
            self.subdirectory_count += len(dirs)

            for file in files:
                self.file_count += 1
                self.site_size += os.path.getsize(os.path.join(root, file))

                filename, file_extension = os.path.splitext(file)
                if file_extension not in filetype_map:
                    filetype_map[file_extension] = 0
                filetype_map[file_extension] += 1

                file_extension = file_extension.lower()
                if file_extension in [".html", ".htm"]:
                    if not filename.endswith('_1') and not filename.endswith("_FROMBACKUP"):
                        self.html_file_count += 1
                        self.html_file_size + os.path.getsize(os.path.join(root, file))
                elif file_extension in [".css"]:
                    self.css_file_count += 1
                elif file_extension in [".gif"]:
                    self.gif_file_count += 1
                elif file_extension in [".jpg", ".jpeg", ".png"]:
                    self.image_file_count += 1
                elif file_extension in [".wav", ".midi", ".mid", ".mp3", ".mp4"]:
                    self.audio_file_count += 1
                elif file_extension in [".avi", ".mov", ".mpg", ".mpeg", ".wmv"]:
                    self.video_file_count += 1
                else:
                    self.other_file_count += 1

        return filetype_map
