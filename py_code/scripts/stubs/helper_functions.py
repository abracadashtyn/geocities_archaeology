
import difflib
import re


# Sometimes the 4 digit neighborhood site ids get corrupted when unzipped - they might be something like '12340' or
# '1234_' where the actual site id is '1234'. This function checks if the string is a 4 digit site id or a corruption of
# one, and returns the site ID found
def get_site_id(string):
    try:
        int(string)
        return int(string)
    except ValueError:
        regex_try = re.match("([0-9]{4})", string)
        if regex_try is not None:
            return int(regex_try.group(1))
    return None


def construct_geocities_neighborhood_url(site_id, neighborhood, subneighborhood=None):
    url = f"https://www.geocities.com/{neighborhood}/"
    if subneighborhood is not None:
        url += f"{subneighborhood}/"
    url += f"{site_id}"
    return url
