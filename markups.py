#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from emoji import emojize
from peewee import DoesNotExist

import config
import strings
import main
from urllib.parse import quote, urljoin

from models import DialogItemTypes, CollectionModes, TelegramUsers, Infos, TelegramChannels

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

_ = main._


# Common buttons
# Back button
def back_button(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    return KeyboardButton(emojize(f":arrow_left: {_(user.language_code, strings.BACK)}", use_aliases=True))


def next_button(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    return KeyboardButton(emojize(f":arrow_right: {_(user.language_code, strings.NEXT)}", use_aliases=True))


#  Main page keyboard

def main_page_keyboard(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    keyboard = ReplyKeyboardMarkup()

    btn_useful = KeyboardButton(emojize(f":high_brightness: {_(user.language_code, strings.USEFUL)}", use_aliases=True))
    btn_internet = KeyboardButton(
        emojize(f":globe_with_meridians: {_(user.language_code, strings.INTERNET)}", use_aliases=True))
    btn_communication = KeyboardButton(
        emojize(f":speech_balloon: {_(user.language_code, strings.COMMUNICATION)}", use_aliases=True))
    btn_news = KeyboardButton(emojize(f":loudspeaker: {_(user.language_code, strings.NEWS)}"))
    btn_services = KeyboardButton(emojize(f":computer: {_(user.language_code, strings.SERVICES)}", use_aliases=True))
    btn_rates = KeyboardButton(emojize(f":clipboard: {_(user.language_code, strings.RATES)}", use_aliases=True))
    btn_balance = KeyboardButton(emojize(f":moneybag: {_(user.language_code, strings.BALANCE)}", use_aliases=True))

    btn_russian = KeyboardButton(text=emojize('🇷🇺 Русский', use_aliases=True))
    btn_uzbek = KeyboardButton('🇺🇿 O\'zbekcha')
    btn_android_app = KeyboardButton(text=_(user.language_code, strings.ANDROID_APP))

    keyboard.row(btn_internet, btn_useful, btn_rates)
    keyboard.row(btn_communication, btn_news, btn_services)
    keyboard.row(btn_russian, btn_uzbek)
    keyboard.row(btn_android_app)

    keyboard.btn_useful = btn_useful
    keyboard.btn_internet = btn_internet
    keyboard.btn_communication = btn_communication
    keyboard.btn_news = btn_news
    keyboard.btn_services = btn_services
    keyboard.btn_rates = btn_rates
    keyboard.btn_balance = btn_balance
    keyboard.btn_russian = btn_russian
    keyboard.btn_uzbek = btn_uzbek
    keyboard.btn_android_app = btn_android_app

    if TelegramChannels.select().count() > 0:
        btn_telegram_channels = KeyboardButton(text=_(user.language_code, strings.TELEGRAM_CHANNELS))
        keyboard.row(btn_telegram_channels)
        keyboard.btn_telegram_channels = btn_telegram_channels

    return keyboard


# -----------------------------------------------------------------------------------------------------------------------
#  Useful page keyboard
def useful_page_keyboard(message):
    infos = Infos.get_or_none(Infos.id == 1)
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    keyboard = InlineKeyboardMarkup(row_width=2)
    useful = DialogItemTypes.get(DialogItemTypes.id == 1)

    if infos is not None:
        btn_meta = InlineKeyboardButton(text=infos.meta_title(user.language_code),
                                        url=infos.meta_url(user.language_code))
        btn_helper = InlineKeyboardButton(text=infos.helper_title(user.language_code),
                                          url=infos.helper_url(user.language_code))
        btn_call_center = InlineKeyboardButton(text="CALL CENTER",
                                               url=urljoin(config.USSD_URL, quote(infos.call_center)))

        keyboard.add(btn_meta, btn_helper)
    buttons = []
    for dialog_item in useful.dialog_items:
        btn = InlineKeyboardButton(text=dialog_item.title(user.language_code),
                                   url=f"https://umsdealer.uz/ussd/{quote(dialog_item.ussd)}",
                                   callback_data=dialog_item.ussd)
        buttons.append(btn)

    keyboard.add(*buttons)
    keyboard.buttons = buttons
    return keyboard


# -----------------------------------------------------------------------------------------------------------------------
#  Rates page keyboard
def rates_page_keyboard(message):
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(next_button(message))
    keyboard.add(back_button(message))
    return keyboard


# Pagination Keyboard
def pagination_keyboard(message):
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(next_button(message))
    keyboard.row(back_button(message))
    return keyboard


# Internet page keyboard
def internet_page_keyboard(message):
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    keyboard = ReplyKeyboardMarkup()

    dialog_item_type_internet = DialogItemTypes.get(DialogItemTypes.id == 2)
    btn = KeyboardButton(text=dialog_item_type_internet.title(user.language_code))
    keyboard.row(btn)
    collection_modes_internet = CollectionModes.select().where(CollectionModes.type == 1)

    for collection_mode in collection_modes_internet:
        btn = KeyboardButton(text=collection_mode.title(user.language_code))
        keyboard.add(btn)

    keyboard.add(back_button(message))
    return keyboard


# Collection mode keyboard
def collection_mode_keyboard(collection_mode, message):
    keyboard = ReplyKeyboardMarkup()
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    buttons = []
    for collection_type in collection_mode.collection_types:
        btn = KeyboardButton(text=collection_type.title(user.language_code))
        buttons.append(btn)

    keyboard.add(*buttons)
    keyboard.add(back_button(message))

    return keyboard


# Communication page keyboard
def communication_page_keyboard(message):
    keyboard = ReplyKeyboardMarkup()
    dialog_item_type_communication = DialogItemTypes.get(DialogItemTypes.id == 3)
    user = TelegramUsers.get(TelegramUsers.telegram_id == message.from_user.id)
    btn = KeyboardButton(text=dialog_item_type_communication.title(user.language_code))
    keyboard.add(btn)

    collection_modes_communication = CollectionModes.select().where(CollectionModes.type == 0)

    for collection_mode in collection_modes_communication:
        btn = KeyboardButton(text=collection_mode.title(user.language_code))
        keyboard.add(btn)

    keyboard.add(back_button(message))
    return keyboard
