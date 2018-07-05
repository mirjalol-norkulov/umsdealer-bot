#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from emoji import emojize
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import config
import markups
import gettext
from urllib.parse import urljoin, quote

import strings


def _(language, s):
    if language == 'ru':
        ru = gettext.translation('base', localedir='locales', languages=['ru'])
        ru.install()
        return ru.gettext(s)
    else:
        return s


from models import DialogItemTypes, Rates, Services, News, CollectionModes, CollectionTypes, Collections, TelegramUsers, \
    Buttons, TelegramChannels

bot = TeleBot(config.TOKEN)


# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user, created = TelegramUsers.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'username': message.from_user.username,
            'language_code': 'ru'
        }
    )

    help_text = strings.HELP_TEXT_RU if user.language_code == 'ru' else strings.HELP_TEXT_UZ

    text = f"{_(user.language_code, strings.MAIN_PAGE)}\n{help_text}"
    msg = bot.send_message(message.chat.id, text=text,
                           reply_markup=markups.main_page_keyboard(message))
    bot.register_next_step_handler(msg, main_page_handler)


# Help command
@bot.message_handler(commands=['help'])
def help(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)

    if user.language_code == 'ru':
        msg = bot.send_message(message.chat.id, text=strings.HELP_TEXT_RU,
                               reply_markup=markups.main_page_keyboard(message))
    else:
        msg = bot.send_message(message.chat.id, text=strings.HELP_TEXT_UZ,
                               reply_markup=markups.main_page_keyboard(message))

    bot.register_next_step_handler(msg, main_page_handler)


# Main page handler
# ---------------------------------------------------------------------------------------------------------------
def main_page_handler(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    main_page_keyboard = markups.main_page_keyboard(message)

    if message.text == main_page_keyboard.btn_useful.text:
        useful = DialogItemTypes.get(DialogItemTypes.id == 1)
        text = useful.title(user.language_code)
        keyboard = markups.useful_page_keyboard(message)
        msg = bot.send_message(message.chat.id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, main_page_handler)
    elif message.text == main_page_keyboard.btn_rates.text:
        handler = lambda m: rates_page_handler(m, page=2)
        text = _(user.language_code, strings.RATES)
        keyboard = markups.rates_page_keyboard(message)
        msg = bot.send_message(message.chat.id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(msg, handler)
        send_rates(bot, message)
    elif message.text == main_page_keyboard.btn_services.text:
        handler = lambda m: services_page_handler(m, page=2)
        bot.send_message(message.chat.id, text=_(user.language_code, strings.SERVICES),
                         reply_markup=markups.pagination_keyboard(message))
        msg = send_services(bot, message)
        bot.register_next_step_handler(msg, handler)
    elif message.text == main_page_keyboard.btn_news.text:
        bot.send_message(message.chat.id, text=_(user.language_code, strings.NEWS),
                         reply_markup=markups.pagination_keyboard(message))
        handler = lambda m: news_page_handler(m, page=2)
        msg = send_news(bot, message, page=1)
        bot.register_next_step_handler(msg, handler)
    elif message.text == main_page_keyboard.btn_internet.text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.INTERNET),
                               reply_markup=markups.internet_page_keyboard(message))

        bot.register_next_step_handler(msg, internet_page_handler)

    elif message.text == main_page_keyboard.btn_communication.text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.COMMUNICATION),
                               reply_markup=markups.communication_page_keyboard(message))
        bot.register_next_step_handler(msg, communication_page_handler)
    elif message.text == main_page_keyboard.btn_russian.text:
        user.language_code = 'ru'
        user.save()
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)
    elif message.text == main_page_keyboard.btn_uzbek.text:
        user.language_code = 'uz'
        user.save()
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)

    elif message.text == main_page_keyboard.btn_android_app.text:
        text = f"<a href='{config.ANDROID_APP_URL}'>{_(user.language_code, strings.ANDROID_APP)}</a>"
        msg = bot.send_message(message.chat.id, text=text, parse_mode='html')
        bot.register_next_step_handler(msg, main_page_handler)


    elif main_page_keyboard.btn_telegram_channels and message.text == main_page_keyboard.btn_telegram_channels.text:
        telegram_channels = TelegramChannels.select()
        msg = bot.send_message(message.chat.id, text = _(user.language_code))
        for channel in telegram_channels:
            text = f"<a href='{channel.url}'>{channel.title}</a>"
            msg = bot.send_message(message.chat.id, text=text, parse_mode='html')

        bot.register_next_step_handler(msg, main_page_handler)

    elif message.text not in config.COMMANDS:
        handle_unknown_command(message, main_page_handler)
        return

    handle_commands(message)


# ---------------------------------------------------------------------------------------------------------------
def handle_unknown_command(message, handler=None, markup=None):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    kwargs = {}
    if markup is not None:
        kwargs = {
            'markup': markup
        }

    msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.UNKNOWN_COMMAND), **kwargs)

    if handler is not None:
        bot.register_next_step_handler(msg, handler)


# ---------------------------------------------------------------------------------------------------------------
def send_rates(bot, message, page=1):
    rates = Rates.select().paginate(page, config.RATES_PER_PAGE)
    count = rates.count()

    if count == 0:
        return

    msg = None
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)

    for rate in rates:
        text = f"<b>{rate.title(user.language_code)}</b>\n" \
               f"{rate.description(user.language_code)}"

        rate_markup = InlineKeyboardMarkup()
        activate_button = InlineKeyboardButton(text=_(user.language_code, strings.ACTIVATE_RATE),
                                               url=f"http://umsdealer.uz/ussd/{quote(rate.ussd)}")
        activate_super_zero_button = None
        if rate.super_zero_ussd:
            activate_super_zero_button = InlineKeyboardButton(text=_(user.language_code, strings.ACTIVATE_SUPER_ZERO),
                                                              url=f"http://umsdealer.uz/ussd/{quote(rate.super_zero_ussd)}")
        share_ussd_button = InlineKeyboardButton(text=_(user.language_code, _(user.language_code, strings.SHARE_USSD)),
                                                 switch_inline_query=f"UMS | {_(user.language_code, strings.RATES)} | {rate.title(user.language_code)} - {rate.ussd}")

        if activate_super_zero_button:
            rate_markup.row(activate_button, activate_super_zero_button)
            rate_markup.row(share_ussd_button)
        else:
            rate_markup.row(activate_button, share_ussd_button)

        msg = bot.send_message(message.chat.id, text=text,
                               parse_mode='html', reply_markup=rate_markup)

    return msg


# ---------------------------------------------------------------------------------------------------------------
def rates_page_handler(message, page=1):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    if message.text == markups.next_button(message).text:
        msg = send_rates(bot, message, page)
        if msg is None:
            msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.RATES_LAST),
                                   reply_markup=markups.main_page_keyboard(message))
            bot.register_next_step_handler(msg, main_page_handler)
            return
        bot.register_next_step_handler(msg, lambda m: rates_page_handler(m, page=page + 1))
    elif message.text == markups.back_button(message).text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)

    elif message.text not in config.COMMANDS:
        handle_unknown_command(message, lambda m: rates_page_handler(m, page))

    handle_commands(message)


# ---------------------------------------------------------------------------------------------------------------
def send_services(bot, message, page=1):
    services = Services.select().join(Buttons).paginate(page, config.SERVICES_PER_PAGE)
    msg = None
    if services.count() == 0:
        return

    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)

    for service in services:
        inline_keyboard = None
        if service.buttons:
            inline_keyboard = InlineKeyboardMarkup()
            for button in service.buttons:
                btn = InlineKeyboardButton(text=button.title(user.language_code),
                                           url=urljoin(config.USSD_URL, quote(button.ussd)))
                inline_keyboard.add(btn)

        if inline_keyboard:
            kwargs = {
                'reply_markup': inline_keyboard
            }
        else:
            kwargs = None
        text = f"<b>{service.title(user.language_code)}</b>\n" \
               f"{service.description(user.language_code)}"
        msg = bot.send_message(message.chat.id, text=text, parse_mode='html', **kwargs)

    return msg


# ---------------------------------------------------------------------------------------------------------------
def services_page_handler(message, page=1):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    if message.text == markups.next_button(message).text:
        msg = send_services(bot, message, page)
        if msg is None:
            msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.SERVICES_LAST),
                                   reply_markup=markups.main_page_keyboard(message))
            bot.register_next_step_handler(msg, main_page_handler)

        bot.register_next_step_handler(msg, lambda m: services_page_handler(m, page=page + 1))
    elif message.text == markups.back_button(message).text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)

    elif message.text not in config.COMMANDS:
        handle_unknown_command(message, lambda m: services_page_handler(m, page))

    handle_commands(message)


# ---------------------------------------------------------------------------------------------------------------
def send_news(bot, message, page=1):
    news = News.select().paginate(page, config.NEWS_PER_PAGE)
    if news.count() == 0:
        return
    msg = None
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)

    bot.send_message(message.chat.id,
                     text=f'<b>{_(user.language_code, strings.NEWS)}</b>\n {(page - 1) * config.NEWS_PER_PAGE + 1} - {page * config.NEWS_PER_PAGE}',
                     parse_mode='html')
    for news_item in news:
        text = f"https://t.me/iv?url={quote(news_item.url(user.language_code))}&rhash=59e8c575dd4b4f"
        msg = bot.send_message(message.chat.id, text=text)
    return msg


# ---------------------------------------------------------------------------------------------------------------
def news_page_handler(message, page=1):
    print("News page handler")
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    if message.text == markups.next_button(message).text:
        msg = send_news(bot, message, page)
        if msg is None:
            msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.NEWS_LAST),
                                   reply_markup=markups.main_page_keyboard(message))
            bot.register_next_step_handler(msg, main_page_handler)
            return

        bot.register_next_step_handler(msg, lambda m: news_page_handler(m, page=page + 1))
    elif message.text == markups.back_button(message).text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)

    elif message.text not in config.COMMANDS:
        handle_unknown_command(message, lambda m: news_page_handler(m, page))

    handle_commands(message)


# ---------------------------------------------------------------------------------------------------------------
def internet_page_handler(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    if message.text == markups.back_button(message).text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)
        return

    dialog_item_type_internet = DialogItemTypes.get(DialogItemTypes.id == 2)
    if message.text == dialog_item_type_internet.title(user.language_code):
        internet_inline_keyboard = InlineKeyboardMarkup()
        for dialog_item in dialog_item_type_internet.dialog_items:
            btn = InlineKeyboardButton(text=dialog_item.title(user.language_code),
                                       url=f"{urljoin(config.USSD_URL,quote(dialog_item.ussd))}")
            internet_inline_keyboard.add(btn)

        msg = bot.send_message(message.chat.id,
                               text=dialog_item_type_internet.title(user.language_code),
                               reply_markup=internet_inline_keyboard)
        bot.register_next_step_handler(msg, internet_page_handler)
        return

    collection_mode = CollectionModes.get_by_title(message.text, user.language_code)

    if collection_mode is None:
        if message.text not in config.COMMANDS:
            handle_unknown_command(message, internet_page_handler)
            return
        else:
            handle_commands(message)
            return
    collection_mode_keyboard = ReplyKeyboardMarkup()
    buttons = []
    for collection_type in collection_mode.collection_types:
        btn = KeyboardButton(text=collection_type.title(user.language_code))
        buttons.append(btn)

    collection_mode_keyboard.add(*buttons)
    collection_mode_keyboard.add(markups.back_button(message))
    collection_mode_inline_keyboard = InlineKeyboardMarkup()
    btn_text = collection_mode.button_title(user.language_code)
    ussd_btn = InlineKeyboardButton(text=btn_text, url=urljoin(config.USSD_URL, quote(collection_mode.ussd)))
    collection_mode_inline_keyboard.add(ussd_btn)
    bot.send_message(message.chat.id, text=btn_text, reply_markup=collection_mode_inline_keyboard)
    msg = bot.send_message(message.chat.id, text=collection_mode.title(user.language_code),
                           reply_markup=collection_mode_keyboard)
    bot.register_next_step_handler(msg, lambda m: collection_mode_page_handler(m, collection_mode))


# ---------------------------------------------------------------------------------------------------------------
def send_collections(bot, message, collection_type, type='INTERNET', page=1):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    msg = None
    collections = Collections.select().where(Collections.collection_type_id == collection_type.id). \
        paginate(page, config.COLLECTIONS_PER_PAGE)

    if collections.count() == 0:
        return None

    collection_inline_keyboard = InlineKeyboardMarkup()
    buy_collection_btn = InlineKeyboardButton(text=_(user.language_code, strings.BUY_COLLECTION))
    share_ussd_button = InlineKeyboardButton(text=_(user.language_code, strings.SHARE_USSD))
    collection_inline_keyboard.add(buy_collection_btn, share_ussd_button)

    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)

    for collection in collections:
        text = f"UMS | {collection_type.title(message)} - {collection.title(user.language_code)} - {collection.ussd}"
        collection_inline_keyboard.keyboard[0][0]['url'] = urljoin(config.USSD_URL, quote(collection.ussd))
        collection_inline_keyboard.keyboard[0][1][
            'switch_inline_query'] = text

        text = f"{collection.title(user.language_code)} - {emojize(':moneybag:', use_aliases=True)} {collection.coast(user.language_code)}"
        msg = bot.send_message(message.chat.id, text=text, reply_markup=collection_inline_keyboard)

    return msg


def collection_mode_page_handler(message, collection_mode, type='INTERNET'):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    if message.text == markups.back_button(message).text:
        if type == 'INTERNET':
            markup = markups.internet_page_keyboard(message)
            handler = internet_page_handler
        else:
            markup = markups.communication_page_keyboard(message)
            handler = communication_page_handler
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.INTERNET), reply_markup=markup)
        bot.register_next_step_handler(msg, handler)
        return

    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    collection_type = CollectionTypes.get_by_title(message.text, user.language_code)

    if collection_type is None:
        if message.text not in config.COMMANDS:
            handle_unknown_command(message, lambda m: collection_mode_page_handler(m, collection_mode, 'INTERNET'))
            return
        else:
            handle_commands(message)
    bot.send_message(message.chat.id, text=collection_type.title(user.language_code),
                     reply_markup=markups.pagination_keyboard(message))
    msg = send_collections(bot, message, collection_type, type=type)

    if msg is None:
        msg = bot.send_message(message.chat.id,
                               text=_(user.language_code, strings.COLLECTIONS_DOES_NOT_EXIST),
                               reply_markup=markups.collection_mode_keyboard(collection_mode, message))
        bot.register_next_step_handler(msg, lambda m: collection_mode_page_handler(m, collection_mode, type))
        return

    bot.register_next_step_handler(msg,
                                   lambda m: collection_type_page_handler(m,
                                                                          collection_mode,
                                                                          collection_type,
                                                                          type,
                                                                          2))


def collection_type_page_handler(message, collection_mode, collection_type, type='INTERNET', page=1):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    if message.text == markups.back_button(message).text:
        collection_mode_keyboard = ReplyKeyboardMarkup()
        buttons = []
        for collection_type in collection_mode.collection_types:
            btn = KeyboardButton(text=collection_type.title(user.language_code))
            buttons.append(btn)

        collection_mode_keyboard.add(*buttons)
        collection_mode_keyboard.add(markups.back_button(message))
        msg = bot.send_message(message.chat.id, text=collection_mode.title(user.language_code),
                               reply_markup=collection_mode_keyboard)
        bot.register_next_step_handler(msg, lambda m: collection_mode_page_handler(m, collection_mode, type=type))
        return

    if message.text == markups.next_button(message).text:
        msg = send_collections(bot, message, collection_type, type, page)
        if msg is None:
            collection_mode_keyboard = ReplyKeyboardMarkup()
            buttons = []
            for collection_type in collection_mode.collection_types:
                btn = KeyboardButton(text=collection_type.title(user.language_code))
                buttons.append(btn)

            collection_mode_keyboard.add(*buttons)
            collection_mode_keyboard.add(markups.back_button(message))
            msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.PACKETS_LAST),
                                   reply_markup=collection_mode_keyboard)
            bot.register_next_step_handler(msg, lambda m: collection_mode_page_handler(m, collection_mode, type))
            return

        bot.register_next_step_handler(msg, lambda m: collection_type_page_handler(m,
                                                                                   collection_mode,
                                                                                   collection_type,
                                                                                   type, page + 1))
        return

    if message.text not in config.COMMANDS:
        handle_unknown_command(message,
                               lambda m: collection_type_page_handler(m,
                                                                      collection_mode,
                                                                      collection_type,
                                                                      'INTERNET',
                                                                      page))
        return

    handle_commands(message)


# ---------------------------------------------------------------------------------------------------------------
def communication_page_handler(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)

    if message.text == markups.back_button(message).text:
        msg = bot.send_message(message.chat.id, text=_(user.language_code, strings.MAIN_PAGE),
                               reply_markup=markups.main_page_keyboard(message))
        bot.register_next_step_handler(msg, main_page_handler)
        return
    dialog_item_type_communication = DialogItemTypes.get(DialogItemTypes.id == 3)

    if message.text == dialog_item_type_communication.title(user.language_code):
        inline_keyboard = InlineKeyboardMarkup()

        for dialog_item in dialog_item_type_communication.dialog_items:
            btn = InlineKeyboardButton(text=dialog_item.title(user.language_code),
                                       url=urljoin(config.USSD_URL, quote(dialog_item.ussd)))
            inline_keyboard.add(btn)

        msg = bot.send_message(message.chat.id, text=dialog_item_type_communication.title(user.language_code),
                               reply_markup=inline_keyboard)
        bot.register_next_step_handler(msg, communication_page_handler)
        return

    collection_mode = CollectionModes.get_by_title(message.text, user.language_code)
    if collection_mode is None:
        if message.text not in config.COMMANDS:
            handle_unknown_command(message, communication_page_handler)
            return
        else:
            handle_commands(message)
            return
    collection_mode_keyboard = ReplyKeyboardMarkup()
    buttons = []
    for collection_type in collection_mode.collection_types:
        btn = KeyboardButton(text=collection_type.title(user.language_code))
        buttons.append(btn)

    collection_mode_keyboard.add(*buttons)
    collection_mode_keyboard.add(markups.back_button(message))
    msg = bot.send_message(message.chat.id, text=collection_mode.title(user.language_code),
                           reply_markup=collection_mode_keyboard)
    bot.register_next_step_handler(msg, lambda m: collection_mode_page_handler(m, collection_mode,
                                                                               type='COMMUNICATION'))


# ---------------------------------------------------------------------------------------------------------------
# default handler for every other text
@bot.message_handler()
def command_default(message):
    handle_unknown_command(message)


def handle_commands(message):
    if message.text == '/start':
        start(message)
    elif message.text == '/help':
        help(message)


# if __name__ == '__main__':
#     print('Bot started...')
#     bot.polling(timeout=15)
# ---------------------------------------------------------------------------------------------------------------
