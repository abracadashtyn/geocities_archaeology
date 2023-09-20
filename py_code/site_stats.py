import os


class SiteStats:
    yahoo_id = None
    neighborhood = None
    subneighborhood = None
    neighborhood_id = None
    site_stats = {
        "site_size": 0,
        "file_count": 0,
        "subdirectory_count": 0,
        "html_file_count": 0,
        "html_file_size": 0,
        "gif_file_count": 0,
        "image_file_count": 0,
        "video_file_count": 0,
        "sound_file_count": 0,
        "other_file_count": 0
    }
    boolean_stats = {
        "suspected_empty_site": False,
        "reviewed": False
    }

    def __init__(self, yahoo_id=None, neighborhood=None, subneighborhood=None, neighborhood_id=None, site_stats=None,
                 boolean_stats=None):
        self.yahoo_id = yahoo_id
        self.neighborhood = neighborhood
        self.subneighborhood = subneighborhood
        self.neighborhood_id = neighborhood_id
        if site_stats is not None:
            for key in site_stats:
                self.site_stats[key] = site_stats[key]
        if boolean_stats is not None:
            for key in boolean_stats:
                self.boolean_stats[key] = boolean_stats[key]

    def generate_numeric_stats_from_dir(self, fq_dir):
        for root, dirs, files in os.walk(fq_dir):
            for file in files:
                self.site_stats['file_count'] += 1
                self.site_stats['site_size'] += os.path.getsize(os.path.join(root, file))

                filename, file_extension = os.path.splitext(file)
                if file_extension.lower() in [".html", ".htm"]:
                    self.site_stats['html_file_count'] += 1
                    self.site_stats['html_file_size'] += os.path.getsize(os.path.join(root, file))
                elif file_extension.lower() in [".gif"]:
                    self.site_stats['gif_file_count'] += 1
                elif file_extension.lower() in [".jpg", ".jpeg", ".png"]:
                    self.site_stats['image_file_count'] += 1
                elif file_extension.lower() in [".wav", ".midi", ".mp3", ".mp4"]:
                    self.site_stats['audio_file_count'] += 1
                elif file_extension.lower() in [".avi", ".mov", ".mpg", ".mpeg", ".wmv"]:
                    self.site_stats['video_file_count'] += 1
                else:
                    self.site_stats['other_file_count'] += 1

            self.site_stats['subdirectory_count'] += len(dirs)

    def generate_create_table_statement(self):
        columns = [
            "yahoo_id varchar(100)"
            "neighborhood varchar(50)"
            "subneighborhood varchar(50)"
            "neighborhood_id int"
            ]
        columns += ["{0} int NOT NULL".format(key) for key in self.site_stats]
        columns += ["{0} boolean".format(key) for key in self.boolean_stats]
        return "CREATE TABLE IF NOT EXISTS site_stats ({0});".format(",".join(columns))

    def generate_insert_statement(self):
        columns = ["yahoo_id", "neighborhood", "subneighborhood", "neighborhood_id"]
        values = [self.yahoo_id, self.neighborhood, self.subneighborhood, self.neighborhood_id]
        for key, value in self.site_stats.items():
            columns.append(key)
            values.append(value)
        for key, value in self.boolean_stats.items():
            columns.append(key)
            values.append(value)

        statement = "INSERT INTO site_stats ({0}) VALUES ({1});".format(",".join(columns), ",".join(["%s"] * len(columns)))
        return statement, values

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
