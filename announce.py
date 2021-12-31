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
Dear TSMS Bot user,

Blessed New Year! Join us this year as we bring you daily devotions every morning from the book of Romans, <b>by subscribing to the Daily Manna telegram channel at t.me/edailymanna</b>

<i>This message is brought to you by the B-P Youth e-ministry - bpilgrims.com</i>
'''

specialmessage = '''

'''


def main():
    for user in users:
        try:
            bot.send_message(chat_id=user, text=message,
                             parse_mode=telegram.ParseMode.HTML)
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
