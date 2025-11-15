import json
from typing import List


base_path = "./StoredContents/"
def load_parsed_material(filename):
    with open(base_path+filename, "r", encoding="utf-8") as f:
        parsed_content_file = json.load(f)


    return parsed_content_file

