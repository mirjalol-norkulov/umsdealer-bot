from main import bot

import markups


class Page(object):
    bot = bot

    def __init__(self):
        pass


class MainPage(Page):
    @staticmethod
    def invoke(message):
        MainPage.bot.send_message(message.chat.id, 'Welcome!', reply_markup=markups.MainMenuMarkup.keyboard)
