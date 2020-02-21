import os
import sys

sys.path.append(os.getcwd())
import telebot
import tlgrm_secrets

from websockets_server.core.settings import HENDRIX_CHANNEL
from utils.log_helper import setup_logger

import redis
import json

bot = telebot.AsyncTeleBot(tlgrm_secrets.token2)
r = redis.Redis(host='localhost', port=6379, db=0)
logger = setup_logger(__name__, filename_arg='tlgrm_listen_hendrix')

command = 'send'


@bot.message_handler(content_types=["text"], commands=['send'])
def forward_messages(message):
    if message.from_user.id == tlgrm_secrets.chat_id:
        logger.info('[%s]: [%s]', HENDRIX_CHANNEL, message.text)
        try:
            suffix = message.text[len(command) + 1:]
            ws_id, text = suffix.split('|')[:2]
        except Exception as e:
            print(f'excpetion {e} happened')
            return
        msg = {
            'ws_id': ws_id.strip(),
            'message': text.strip()
        }
        msg_json = json.dumps(msg)
        r.publish(HENDRIX_CHANNEL, msg_json)


if __name__ == '__main__':
    bot.polling(none_stop=False, interval=10, timeout=20)
