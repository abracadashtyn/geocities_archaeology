import logging
import os
import spacy

from bs4 import BeautifulSoup
from py_code.config.config import Config

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    config = Config()
    blog_base_dir = config.get_geocities_config()['blog_base_dir']
    nlp = spacy.load("en_core_web_lg")
    count = 0

    # db handle if needed
    # conn = MysqlConnection(config.get_mysql_config())

    for blog in os.listdir(blog_base_dir):
        print("processing blog {0}".format(blog))
        # TODO - blog directory located, do something with it

        for root, dirs, files in os.walk(os.path.join(blog_base_dir, blog)):
            for file in files:
                filepath = os.path.join(root, file)
                filename, ext = os.path.splitext(file)
                if ext.lower() in [".html", ".htm"]:
                    print(f"found html file to process: {filepath}")
                    with open(filepath, 'r') as f:
                        soup = BeautifulSoup(f, 'html.parser')
                        text = [text for text in soup.stripped_strings]
                        print("TEXT:")
                        for n in text:
                            print(n)
                        doc = nlp('\n'.join(text))
                        print("ENTITIES:")
                        for ent in doc.ents:
                            print(ent.text, ent.start_char, ent.end_char, ent.label_)
                        print('------')
        if count > 20:
            break
        print("--------------------------------------")
