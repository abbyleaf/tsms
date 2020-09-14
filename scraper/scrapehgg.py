# pip install bs4
# pip install requests

from bs4 import BeautifulSoup
import requests
import re

full = ''
with open('links.txt', 'r', encoding='utf8') as links:
    for line in links:
        line = line.strip()
        line = '1' + line
        line = line.split('@')
        title = line[0]
        title = title.upper()
        print(title)
        url = line[1]
        response = requests.get(url, timeout=5)
        try:
            content = BeautifulSoup(response.content, "html.parser")
            content = content.find('font', attrs={"class": "ve5"}).p.p
            for child in content.find_all("p"):
                child.decompose()
            if '</a>' in str(content):
                raise ValueError
        except:
            content = BeautifulSoup(response.content, "html.parser")
            content = content.find('font', attrs={"class": "ve5"}).p
            for child in content.find_all("p"):
                child.decompose()
        content = str(content)
        content = re.sub('<p>|<\/p>', '', content)
        content = re.sub('<br/>', '\n', content)
        if full != '':
            full += '\n'
        full += title + '\n\n' + content

with open('hgg.txt', 'w+', encoding='utf8') as hgg:
    hgg.write(full)
