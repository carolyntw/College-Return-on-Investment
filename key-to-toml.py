# *-* coding:utf8 *_*
# @Time: 2/25/22 20:57
# @Author: Yan
# @File: key-to-toml.py
# @Software: PyCharm

import toml

output_file = ".streamlit/secrets.toml"

with open("firestore-key.json") as json_file:
    json_text = json_file.read()

config = {"textkey": json_text}
toml_config = toml.dumps(config)

with open(output_file, "w") as target:
    target.write(toml_config)