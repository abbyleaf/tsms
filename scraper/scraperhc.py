# pip install bs4
# pip install requests

import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from titles import lines
lines = lines.split('\n')
titlelist = []
for line in lines:
    line = line[10:].strip()
    titlelist.append(line)

full = ''
for i in range(1, 568):
    num = str(i)
    padnum = num.zfill(3)
    url1 = 'https://intzone.com/Hymns/rhc/lyrics/rhc{}.htm'.format(padnum)
    url2 = 'https://hymnary.org/hymn/RHC/{}'.format(num)
    try:
        print(url1)
        response = requests.get(url1, timeout=5).text
        if '404 error' in response:
            raise ValueError
        response = re.sub('<br />', '\n', response)
        lines = response.split('\n')
        song = ''
        for line in lines:
            if len(line) > 0 and line[0].isalpha() and line[0].isupper():
                song += line + '\n'
            elif line == '':
                song += line + '\n'
        song = song.strip()
        full += num + ' ' + titlelist[i].upper() + '\n\n' + song + '\n\n'
    except:
        try:
            print(url2)
            response = requests.get(url2, timeout=5)
            content = BeautifulSoup(response.content, "html.parser")
            content = content.find('div', attrs={"id": "text"})
            song = ''
            for child in content.find_all("p"):
                text = child.get_text()
                text = text.strip()
                lines = text.split('\n')
                text = ''
                for line in lines:
                    line = line.strip()
                    text += line + '\n'
                text = text.replace(" [Chorus]", "")
                text = text.replace(" [Refrain]", "")
                if text[0].isnumeric():
                    text = text[2:]
                song += text + '\n'
            song = song.strip()
            full += num + ' ' + titlelist[i].upper() + '\n\n' + song + '\n\n'
        except:
            print("SKIP")
            full += num + ' ' + titlelist[i].upper() + '\n\n'

full = unidecode(full).strip()

with open('rhc.txt', 'w+', encoding='utf8') as rhc:
    rhc.write(full)
