from flask import Flask
from flask import request
from json import loads
from simple_settings import settings
import vk_bot
import discord_bot
import tele_bot

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400


class GetError(Exception):
    text = 'Ошибка входных данных'


@app.route("/")
def index():
    return 'Flask is running'


@app.route("/send", methods=['POST'])
def send():

    ending = '\nДля отписки от рассылки напиши /unsub'
    message = request.data.decode('utf-8')
    message = loads(message)

    text = message['message'] + ending
    link = message['link']

    if 'discord' in message['dispatchers']:
        discord_bot.main(text, link)
    if 'telegram' in message['dispatchers']:
        tele_bot.main(text, link)
    if 'vk' in message['dispatchers']:
        vk_bot.main(text, link)
    return 'ok'


@app.route("/get", methods=['POST'])
def get():
    message = request.data.decode('utf-8')
    message = loads(message)

    if message['type'] == 'confirmation':
        return settings.confirmation_token

    message = message['object']
    members = [message['user_id']]
    text = None
    if message['body'] == '/sub':
        text = vk_bot.subscribe(message['user_id'])
    elif message['body'] == '/unsub':
        text = vk_bot.unsubscribe(message['user_id'])
    elif message['body'] == '/help':
        text = '/sub для подписки\n' \
               '/unsub для отписки\n' \
               'На этом мои полномочия все'
    if text:
        vk_bot.main(message=text, members=members)
    return 'ok'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888)
