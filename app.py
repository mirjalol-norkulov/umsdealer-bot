import telebot
import os
import config
from flask import Flask, request
from main import bot

app = Flask(__name__)


@app.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://umsdealer-bot.herokuapp.com/bot")
    return "!", 200
