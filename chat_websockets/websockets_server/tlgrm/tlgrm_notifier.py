import telebot
from utils.log_helper import setup_logger
from ..core.worker_template import AioredisWorker
from . import tlgrm_secrets
import json


class HendrixTelegramNotify(AioredisWorker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(__name__)
        self.bot = telebot.TeleBot(tlgrm_secrets.token)
        self.chat_id = tlgrm_secrets.chat_id

    async def process_msg_inbound(self, chann_name, msg_raw):
        await super().process_msg_inbound(chann_name, msg_raw)
        load = json.loads(msg_raw)
        dump = json.dumps(load, ensure_ascii=False).encode('utf8')
        self.bot.send_message(self.chat_id, dump)
