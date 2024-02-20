import telegram.bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
import logging
from functools import wraps
import re
from cred import bottoken, port
from templates import login, welcome, examples, defaultbook
import json
from unidecode import unidecode
from fuzzywuzzy import fuzz
from requests import get
import time
from cache import titles, songs, chords, scores, mp3, piano

ip = get("https://api.ipify.org").text
try:
    certfile = open("cert.pem")
    keyfile = open("private.key")
    certfile.close()
    keyfile.close()
except IOError:
    from OpenSSL import crypto

    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    cert.get_subject().CN = ip
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, "sha256")
    with open("cert.pem", "wt") as certfile:
        certfile.write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("ascii")
        )
    with open("private.key", "wt") as keyfile:
        keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("ascii"))

logging.basicConfig(
    filename="debug.log",
    filemode="a+",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


def verifieduser(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id in users:
            return func(update, context, *args, **kwargs)
        else:
            update.message.reply_text("Press /start to continue")

    return wrapped


def loader():
    global users
    try:
        with open("users.json") as userfile:
            users = json.load(userfile)
    except:
        with open("users.json", "w+") as userfile:
            users = {}


def start(update, context):
    contact_keyboard = telegram.KeyboardButton(text="REGISTER", request_contact=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[contact_keyboard]])
    update.message.reply_text(
        login, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN
    )


def contact(update, context):
    user_id = str(update.effective_user.id)
    contact = update.message.contact
    phone = contact.phone_number
    if user_id != str(contact.user_id):
        update.message.reply_text(
            "Verification failed. Your ID does not match.",
            reply_markup=telegram.ReplyKeyboardRemove(),
        )
    elif (
        phone.startswith("+65")
        or phone.startswith("65")
        or phone.startswith("+61")
        or phone.startswith("61")
        or phone.startswith("+60")
        or phone.startswith("60")
    ):
        first_name = contact.first_name
        last_name = contact.last_name
        full_name = (str(first_name or "") + " " + str(last_name or "")).strip()
        users[user_id] = {"phone": phone, "name": full_name}
        with open("users.json", "w") as userfile:
            json.dump(users, userfile)
        update.message.reply_text(
            welcome,
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=telegram.ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_text(
            "Sorry, you are not permitted to enter at this time.",
            reply_markup=telegram.ReplyKeyboardRemove(),
        )


@verifieduser
def helptext(update, context):
    update.message.reply_text(examples, parse_mode=telegram.ParseMode.MARKDOWN)


@verifieduser
def go(update, context):
    message = update.message.text
    if re.search("[\u4e00-\u9FFF]", message):
        update.message.reply_text(
            "_Error: Chinese characters not supported. Search using han yu pin yin instead._",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        return
    message = message.strip().upper()
    tempflag = True
    if message.isnumeric():
        message = int(message)
        message = defaultbook + " " + str(message)
        tempflag = False
    titlematches = []
    if message in songs:
        reply_header = message
        reply = songs[reply_header]
        if message.startswith(defaultbook) and tempflag:
            update.message.reply_text(
                "_Hint: Get to songs faster by typing the number without '{}' :)_".format(
                    defaultbook
                ),
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            time.sleep(2)
    else:
        context.bot.send_chat_action(
            chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING
        )
        alpha = re.compile("[^a-zA-Z ]")
        message = unidecode(message)
        message = alpha.sub("", message)
        results = []
        titleresults = set()
        titlefound = False
        hold = None
        for number, title in titles.items():
            title = unidecode(title)
            title = alpha.sub("", title)
            title = title.upper()
            if message == title and " " in message:
                titlematches.append(number)
                titlefound = True
                if number.startswith(defaultbook):
                    hold = number
            similarity = fuzz.partial_ratio(title, message)
            if similarity > 75:
                results.append((number, -similarity))
                titleresults.add(number)
        if titlefound:
            if hold:
                number = hold
            else:
                number = titlematches[-1]
            titlematches.remove(number)
            reply_header = number
            reply = songs[number]
        else:
            for number, lyrics in songs.items():
                lyrics = unidecode(lyrics)
                lyrics = alpha.sub("", lyrics)
                lyrics = lyrics.upper()
                similarity = fuzz.partial_ratio(lyrics, message)
                if similarity > 75 and number not in titleresults:
                    results.append((number, -similarity))
            results = sorted(results, key=lambda x: (x[1], x[0]))
            if len(results) == 0:
                update.message.reply_text(
                    "_No matches found_", parse_mode=telegram.ParseMode.MARKDOWN
                )
                update.message.reply_text(
                    examples, parse_mode=telegram.ParseMode.MARKDOWN
                )
                return
            search_return = "<u>SONG SEARCH</u>\n\n"
            countresult = 0
            for result in results:
                countresult += 1
                number = result[0]
                search_return += "<b>{}</b> {}\n".format(number, titles[number])
                if countresult == 100:
                    search_return += "\n<i>{} results (showing top 100)</i>".format(
                        str(len(results))
                    )
                    update.message.reply_text(
                        search_return, parse_mode=telegram.ParseMode.HTML
                    )
                    return
                elif countresult % 100 == 0:
                    update.message.reply_text(
                        search_return, parse_mode=telegram.ParseMode.HTML
                    )
                    search_return = ""
            search_return += "\n<i>{} results</i>".format(str(len(results)))
            update.message.reply_text(search_return, parse_mode=telegram.ParseMode.HTML)
            return
    keyboard = []
    if reply_header in chords:
        data = "CHORDS {}".format(reply_header)
        keyboard.append([InlineKeyboardButton("🎸  Guitar Chords", callback_data=data)])
    if reply_header in scores:
        data = "SCORE {}".format(reply_header)
        keyboard.append([InlineKeyboardButton("🎼  Piano Score", callback_data=data)])
    if reply_header in mp3:
        data = "MP3 {}".format(reply_header)
        keyboard.append(
            [InlineKeyboardButton("🔊  MIDI Soundtrack", callback_data=data)]
        )
    if titles[reply_header] in piano:
        data = "PIANO {}".format(titles[reply_header])
        keyboard.append(
            [InlineKeyboardButton("🎹  Piano Recording (Wilds)", callback_data=data)]
        )
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        reply,
        reply_markup=reply_markup,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )
    if len(titlematches) > 0:
        reply = "Also available in:\n"
        for i in titlematches:
            reply += "*{}*\n".format(i)
        reply += "\n_Other books may contain more content such as Guitar Chords, Piano Scores, etc._"
        update.message.reply_text(
            reply, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True
        )


def callbackquery(update, context):
    query = update.callback_query
    data = query.data
    errors = False
    if data.startswith("CHORDS "):
        data = data.replace("CHORDS ", "")
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=chords[data],
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif data.startswith("SCORE "):
        data = data.replace("SCORE ", "")
        counter = 1
        for i in range(len(scores[data])):
            reference = scores[data][i]
            title = data + " " + titles[data]
            if len(scores[data]) > 1:
                title += " " + str(counter)
            try:
                context.bot.send_photo(
                    chat_id=query.message.chat_id, photo=reference, caption=title
                )
            except:
                errors = True
            counter += 1
    elif data.startswith("MP3"):
        data = data.replace("MP3 ", "")
        counter = 1
        for i in range(len(mp3[data])):
            reference = mp3[data][i]
            title = title = data + " " + titles[data]
            if len(mp3[data]) > 1:
                title += " " + str(counter)
            try:
                context.bot.send_audio(
                    chat_id=query.message.chat_id, audio=reference, caption=title
                )
            except:
                errors = True
            counter += 1
    elif data.startswith("PIANO"):
        data = data.replace("PIANO ", "")
        reference = piano[data]
        try:
            context.bot.send_audio(
                chat_id=query.message.chat_id, audio=reference, caption=data
            )
        except:
            errors = True
    if errors:
        context.bot.answer_callback_query(
            query.id,
            text="An Error Occurred: one or more files were unable to send. Please notify an admin.",
            show_alert=True,
        )
    else:
        context.bot.answer_callback_query(query.id)


def main():
    updater = Updater(token=bottoken, workers=32, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helptext))
    dp.add_handler(MessageHandler(Filters.contact, contact))
    dp.add_handler(MessageHandler(Filters.text, go, run_async=True))
    dp.add_handler(CallbackQueryHandler(callbackquery, run_async=True))

    loader()

    # updater.start_polling()
    updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=bottoken,
        key="private.key",
        cert="cert.pem",
        webhook_url="https://{}:{}/{}".format(ip, port, bottoken),
    )

    print("Bot is running. Press Ctrl+C to stop.")
    updater.idle()
    print("Bot stopped.")


if __name__ == "__main__":
    main()
