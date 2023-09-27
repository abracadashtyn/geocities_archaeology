"""
This script is used to relocate the blogs and neighborhoods from the unzipped geocities torrent directory structure
"""
import logging
import os
import shutil
from py_code.config.config import Config

dirs_to_process = [
    #"uppercase",
    "lowercase",
    #"numbers"
]
neighborhoods = ["Area51", "Vault", "Athens", "Acropolis", "Augusta", "Baja", "BourbonStreet", "Broadway", "CapeCanaveral",
                 "Lab", "CapitolHill", "CollegePark", "Quad", "Colosseum", "Field", "Loge", "EnchantedForest", "Eureka",
                 "FashionAvenue", "Fashion Avenue", "Heartland", "Plains", "Hollywood", "Hills", "HotSprings",
                 "MadisonAvenue", "MotorCity", "NapaValley", "Nashville", "Paris", "Rue", "LeftBank", "Pentagon",
                 "Petsburgh", "PicketFence", "Pipeline", "RainForest", "RodeoDrive", "ResearchTriangle", "SiliconValley",
                 "Heights", "Park", "Pines", "SoHo", "Lofts", "SouthBeach", "Marina", "SunsetStrip", "Vine", "Alley",
                 "Palms", "Studio", "Towers", "TheTropics", "Shores", "TelevisionCity", "TimesSquare", "Arcade", "Tokyo",
                 "Vienna", "WallStreet", "Wellesley", "WestHollywood", "Yosemite"]

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    config = Config()
    geocities_config = config.get_geocities_config()
    blog_base_dir = geocities_config['blog_base_dir']
    blog_backup_dir = geocities_config['blog_backup_dir']

    for dir in dirs_to_process:
        # location should follow pattern \{dir}7zip\geocities\YAHOOIDS\{first_letter}\{second_letter}
        input_location = os.path.join(geocities_config['original_torrent_base_dir'], "{0}_7zip".format(dir.lower()))
        geocities_base_dir = os.path.join(input_location, "geocities\\")
        if not os.path.isdir(geocities_base_dir):
            logging.error("ERROR: {0} is not a directory".format(geocities_base_dir))
            exit(1)

        for l0_dir in os.listdir(geocities_base_dir):
            # in l0 we're looking for the YAHOOIDS directory. I don't know what the other dirs might be if any
            fq_l0_dir = os.path.join(geocities_base_dir, l0_dir)

            if l0_dir == "YAHOOIDS":
                logging.debug("Fully qualified l0 dir: {0}".format(fq_l0_dir))
                if not os.path.isdir(fq_l0_dir):
                    logging.error("ERROR: '{0}' should be a directory!!".format(fq_l0_dir))
                    exit(10)

                for l1_dir in os.listdir(fq_l0_dir):
                    # l1 contains the first letter of the yahoo id
                    fq_l1_dir = os.path.join(fq_l0_dir, l1_dir)
                    if os.path.isdir(fq_l1_dir):
                        for l2_dir in os.listdir(fq_l1_dir):
                            # l2 contains the second letter of the yahoo id
                            fq_l2_dir = os.path.join(fq_l1_dir, l2_dir)
                            if os.path.isdir(fq_l2_dir):
                                logging.info("examining content of {0}".format(fq_l2_dir))
                                for l3_dir in os.listdir(fq_l2_dir):
                                    # l3 dir should be the yahoo id itself as the dir name (or, in the uppercase directory, it could
                                    # be the neighborhood, which will then have a bunch of id numbers nested underneath it. We check
                                    # for that here and move neighborhoods to a separate directory.
                                    fq_l3_dir = os.path.join(fq_l2_dir, l3_dir)
                                    logging.info("found dir '{0}'".format(l3_dir))
                                    if os.path.isdir(fq_l3_dir):
                                        # check if this is a neighborhood
                                        if l3_dir in neighborhoods:
                                            l3_end_destination = os.path.join(geocities_config['neighborhood_base_dir'], l3_dir)
                                            logging.info(f"Moving Neighborhood to '{l3_end_destination}' from '{fq_l3_dir}'")
                                            shutil.move(fq_l3_dir, geocities_config['neighborhood_base_dir'])
                                        else:
                                            l3_end_destination = os.path.join(blog_base_dir, l3_dir)
                                            logging.info("regular blog, moving {0} to {1}".format(fq_l3_dir, l3_end_destination))

                                            try:
                                                shutil.move(fq_l3_dir, blog_backup_dir)
                                            except shutil.Error as e:
                                                if "already exists" in str(e):
                                                    logging.warning("blog directory '{0}' already exists!".format(l3_end_destination))
                                                    shutil.move(l3_end_destination, blog_backup_dir)
                                                else:
                                                    logging.error(e)
                                                    exit(40)

                                    else:
                                        logging.debug("!!!Found file at l3".format(l3_dir))
                            else:
                                # not a breaking condition; just would be interesting to know if there are files at this level
                                logging.debug("!!!Found file at l2: {0}".format(fq_l2_dir))
                    else:
                        # not a breaking condition; just would be interesting to know if there are files at this level
                        logging.debug("!!!Found file at l1: {0}".format(fq_l1_dir))

            else:
                logging.debug("!!!Found some other non-YAHOOIDS dir: {0}".format(fq_l0_dir))
