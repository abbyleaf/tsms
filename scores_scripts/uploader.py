import telegram
from telegram.ext import (Updater)
import logging
import os
from cred import bottoken

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bot = telegram.Bot(token=bottoken)


def dophoto():
    with open('photouploads.txt', 'a+', encoding='UTF8') as ids:
        for filename in (x.name for x in os.scandir('./photouploads') if x.is_file()):
            filepath = './photouploads/' + filename
            update = bot.send_photo(
                chat_id=647102635, photo=open(filepath, 'rb'))
            filename = filename.split('.')[0]
            print(filename)
            ids.write(filename + '@' + update['photo'][-1]['file_id'] + '\n')


def doaudio():
    with open('audiouploads.txt', 'a+', encoding='UTF8') as uploads:
        for filename in (x.name for x in os.scandir('./audiouploads') if x.is_file()):
            filepath = './audiouploads/' + filename
            update = bot.send_audio(
                chat_id=647102635, audio=open(filepath, 'rb'))
            filename = filename.split('.')[0]
            filename = filename
            print(filename)
            uploads.write(filename + '@' + update['audio']['file_id'] + '\n')


def main():
    dophoto()
    doaudio()


if __name__ == '__main__':
    main()
