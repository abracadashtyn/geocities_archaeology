"""
Helper script to examine all sites and determine all unique file types present in the collection. Used to determine
what site stats I want to capture in the database.
"""
import os

from py_code.config.config import Config


def update_dict(file_type_dict, blog_dir):
    for root, dirs, files in os.walk(blog_dir):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension not in file_type_dict:
                file_type_dict[file_extension] = 1
                print("Added extension {0} to dict".format(file_extension))
            else:
                file_type_dict[file_extension] += 1

    return file_type_dict


if __name__ == "__main__":
    config = Config()
    geocities_config = config.get_geocities_config()

    file_type_dict = {}

    # process blogs
    blog_base_dir = geocities_config['blog_base_dir']
    for blog in os.listdir(blog_base_dir):
        print("processing blog {0}".format(blog))
        blog_dir = os.path.join(blog_base_dir, blog)
        update_dict(file_type_dict, blog_dir)
        print("---------")

    # process neighborhoods
    neighborhood_base_dir = geocities_config['neighborhood_base_dir']
    for neighborhood in os.listdir(neighborhood_base_dir):
        print("processing neighborhood {0}".format(neighborhood))
        neighborhood_dir = os.path.join(neighborhood_base_dir, neighborhood)
        for subdirectory in os.listdir(neighborhood_dir):
            # 2 possibilities - this could be a site (identified by 4 digit id) or subneighborhood (string)
            try:
                neighborhood_id = int(subdirectory)
                print("Found site id {0}, neighborhood {1}".format(neighborhood_id, neighborhood))
                blog_dir = os.path.join(neighborhood_dir, subdirectory)
                update_dict(file_type_dict, blog_dir)
                print('---------')

            except ValueError:
                print("subdirectory {0} is suspected sub-neighborhood".format(subdirectory))
                subneighborhood_dir = os.path.join(neighborhood_dir, subdirectory)
                for subdirectory_2 in os.listdir(subneighborhood_dir):
                    neighborhood_id = int(subdirectory_2)  # this should cast now; if not, throw
                    print("Found site id {0}, neighborhood {1}, subneighborhood {2}".format(neighborhood_id,
                                                                                            neighborhood, subdirectory))
                    blog_dir = os.path.join(subneighborhood_dir, subdirectory_2)
                    update_dict(file_type_dict, blog_dir)
                    print('---------')

    print("Total File Types Found")
    sorted_file_types = sorted(file_type_dict.items(), key=lambda x: x[1], reverse=True)
    for key, value in sorted_file_types:
        print("{0}: {1}".format(key, value))
