# dp.add_handler(InlineQueryHandler(inlinequery))

@run_async
def inlinequery(update, context):
    query = update.inline_query.query
    query = query.strip()
    query = query.upper()
    if query.isnumeric():
        query = int(query)
        query = defaultbook + ' ' + str(query)
    if 'SCORE ' in query:
        query = query[6:]
        query = query.lstrip('0')
        if query == '':
            query = 'SCORE '
        if query not in scores_lookup:
            if (query.lstrip('C').isnumeric()):
                results = [telegram.InlineQueryResultArticle(
                    id=99, title="Score Not Available", description="No scores with this number", input_message_content=telegram.InputTextMessageContent('_Nothing Selected_', parse_mode=telegram.ParseMode.MARKDOWN))]
            else:
                query_parsed = ' ' + query + ' '
                query_parsed = re.sub("[:\-',!?();\".“”ʼ]", '', query_parsed)
                found = False
                for number, title in scores_lookup.items():
                    title_parsed = title + ' '
                    title_parsed = re.sub(
                        "[:\-',!?();\".“”ʼ]", '', title_parsed)
                    if query_parsed in title_parsed:
                        query = number
                        found = True
                        break
                if not found:
                    results = [telegram.InlineQueryResultArticle(
                        id=99, title="No Match Found",  description="No scores with this title", input_message_content=telegram.InputTextMessageContent('_Nothing Selected_', parse_mode=telegram.ParseMode.MARKDOWN))]
        if query in scores_lookup:
            results = [telegram.InlineQueryResultArticle(
                id=99, title=scores_lookup[query], description='Tap image(s) below to send...', input_message_content=telegram.InputTextMessageContent('_Nothing Selected_', parse_mode=telegram.ParseMode.MARKDOWN))]
            counter = 1
            for reference in scores[query]:
                title = 'TSMS ' + scores_lookup[query]
                if len(scores[query]) > 1:
                    title += ' ' + str(counter)
                results.append(telegram.InlineQueryResultCachedPhoto(
                    id=counter, photo_file_id=reference, caption=title))
                counter += 1
    elif query in songs:
        results = [telegram.InlineQueryResultArticle(
            id=1, title=query, description=titles[query], input_message_content=telegram.InputTextMessageContent(songs[query], parse_mode=telegram.ParseMode.MARKDOWN))]
    else:
        search_count = 0
        results = []
        message_parsed = ' ' + query + ' '
        message_parsed = re.sub("[:\-',!?();\".“”ʼ]", '', message_parsed)
        for number, title in titles.items():
            title_parsed = ' ' + title + ' '
            title_parsed = re.sub("[:\-',!?();\".“”ʼ]", '', title_parsed)
            if message_parsed in title_parsed:
                search_count += 1
                results.append(telegram.InlineQueryResultArticle(
                    id=search_count, title=number, description=title, input_message_content=telegram.InputTextMessageContent(songs[number], parse_mode=telegram.ParseMode.MARKDOWN)))
                if search_count == 50:
                    break
        if search_count == 0:
            results = [telegram.InlineQueryResultArticle(
                id=1, title="No Results", description="No songs with this title/number", input_message_content=telegram.InputTextMessageContent('_Nothing Selected_', parse_mode=telegram.ParseMode.MARKDOWN))]
    try:
        update.inline_query.answer(results)
    except:
        results = [telegram.InlineQueryResultArticle(
            id=1, title="An Error Occurred", description="This feature is currently unavailable", input_message_content=telegram.InputTextMessageContent('_Nothing Selected_', parse_mode=telegram.ParseMode.MARKDOWN))]
        update.inline_query.answer(results)

# dp.add_handler(conv_handler)


conv_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^http://|^https://'), polr)],
    states={
        LINK: [MessageHandler(Filters.text, shorten)]
    },
    fallbacks=[MessageHandler(Filters.all, invalid)]
)


def polr(update, context):
    message = update.message.text
    context.user_data['link'] = message
    update.message.reply_text(
        "*What should I shorten your link to?*\n\nE.g. Type _something_ to shorten to lifebpc.cc/something", parse_mode=telegram.ParseMode.MARKDOWN)
    return LINK


def shorten(update, context):
    message = update.message.text.lower().strip()
    link = context.user_data['link']
    context.user_data.clear()
    params = {'key': apikey, 'url': link, 'custom_ending': message}
    try:
        r = get(url=url, params=params)
        success = True
        if r.status_code != 200:
            raise ValueError
            success = False
    except:
        update.message.reply_text(
            "_Something went wrong :( That link might already exist._", parse_mode=telegram.ParseMode.MARKDOWN)
        success = False
    if success:
        response = r.content.decode()
        response = response.replace('https://', '')
        update.message.reply_text(
            "Link {} created successfully!".format(response), parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END


def invalid(update, context):
    update.message.reply_text(
        "_Unable to process this message_", parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END
