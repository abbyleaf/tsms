import os
import re
import secrets

existingname = set()
with open('filestore.txt', 'a+', encoding='UTF8') as filestore:

    for filename in (x.name for x in os.scandir('./oldfiles') if x.is_file()):
        filepath = './oldfiles/' + filename
        filename = filename.lstrip('0')
        filename = re.sub('_', ':', filename)
        filename = filename.split('.')
        fileformat = filename[-1]
        oldname = filename[-2]

        newname = secrets.token_hex(4)
        while newname in existingname:
            newname = secrets.token_hex(4)
        existingname.add(newname)
        newname += '.{}'.format(fileformat)

        line = oldname + '@###' + newname + '\n'
        filestore.write(line)

        os.rename(filepath, "./newfiles/{}".format(newname))
