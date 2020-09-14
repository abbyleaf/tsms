import telegram
import logging
import time
from cred import bottoken
import json


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open('users.json') as userfile:
    users = json.load(userfile)
bot = telegram.Bot(token=bottoken)


message = '''
<b>Bot Announcement</b>
'''

specialmessage = '''

'''


def main():
    for user in users:
        try:
            bot.send_message(chat_id=user, text=message,
                             parse_mode=telegram.ParseMode.HTML, disable_notification=True)
        except:
            print(user)
        time.sleep(0.1)


def special():
    for (key, value) in users.items():
        try:
            if value['rtl'] == True:
                bot.send_message(chat_id=key, text=specialmessage,
                                 parse_mode=telegram.ParseMode.HTML, disable_notification=True)
        except:
            print(value['name'])
        time.sleep(0.1)


if __name__ == '__main__':
    main()
