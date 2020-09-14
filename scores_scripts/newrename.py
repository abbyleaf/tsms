import os
import re

for filename in (x.name for x in os.scandir('./png') if x.is_file()):
    filepath = './png/' + filename
    filename = filename.replace("0001-", "_")
    filename = filename.replace("_1", "")
    os.rename(filepath, "./png/{}".format(filename))
