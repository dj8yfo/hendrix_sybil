from .settings import NYMS_KEY, ROUNDTRIP_CHANNEL, HENDRIX_CHANNEL
import re
import time
import os
import sys
from django import setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_websockets.settings')
setup()
import json
from collections import Mapping
from .worker_template import AioredisWorker
from ..models import Room, Message, MessageOrder
from ..serializers import ChatMessageSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from utils.log_helper import setup_logger
import traceback


logger = setup_logger(__name__)


class MessageProtoHandler(AioredisWorker):
    REQ_MSG_KEYS = ['action']
    SUCCESS = 'success'
    ERROR = 'error'
    MAX_MESSAGES = 123
    MAX_RETRIES = 13
    PAGE = 10

    message_sequence_pattern = re.compile(r'''
        ^
        (
            (
                A
                (
                    C|
                    (
                        S(S|M|H|Q)*C?
                    )
                )?
            )|
            C
        )
        $
        ''', re.VERBOSE)
    message_actions = {
        'authenticate': {
            'symbol': 'A',
            'required_args': [],
            'handler': 'handle_authenticate'
        },
        'close': {
            'symbol': 'C',
            'required_args': [],
            'handler': 'handle_close',
        },
        'select_room': {
            'symbol': 'S',
            'required_args': [('destination_room', str), ('from_nym', str)],
            'handler': 'handle_select_room',
        },
        'send_message': {
            'symbol': 'M',
            'required_args': [('room', str), ('content', str), ('from_nym', str)],
            'handler': 'handle_send_message',
        },
        'history_retrieve': {
            'symbol': 'H',
            'required_args': [('room', str), ('last_message', int)],
            'handler': 'handle_history_retrieve',
        },
        'query': {
            'symbol': 'Q',
            'required_args': [('query_name', str), ('parameters', dict)],
            'handler': 'handle_query'
        }

    }

    rooms_specifics = {  # nesting dicts infinetely is a beautiful design
        'Lobby': {
            'personal_tip': f'<p>type <a id="menu" href="#" onclick="substituteLinkCotent(this.text)">/menu</a> - to see what\'s on the hotel menu</p>',
            'queries': {
                '/menu': {
                    'required_args': [],
                    'handler': 'handle_menu_lobby'
                    # here users will eventually upload their own evm compiled code
                }
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def send_message_layout(content, room, from_nym, ws_id='broadcast',
                            date_created=time.time, seq=-1, channel=ROUNDTRIP_CHANNEL,
                            token=None):
        if callable(date_created):
            date_created = date_created()
        template = {
            "ws_id": ws_id,
            "status": "success",
            "msg": {
                "action": "send_message",
                "content": content,
                "from_nym": from_nym,
                "date_created": date_created,
                "room": room,
                "seq": seq,
                "token": token,
            }
        }

        if ws_id is None:
            template.pop("ws_id")
        return template, channel

    @classmethod
    def validate_raw_input(cls, msg_raw):
        try:
            msg = json.loads(msg_raw)
        except json.JSONDecodeError as jse:
            logger.debug("msg_raw: [%s]", msg_raw)
            raise ValueError('invalid json encoding of incoming message') from jse
        if not isinstance(msg, Mapping):
            logger.debug("msg_raw: [%s]", msg_raw)
            raise ValueError(f'the {msg} has to be a mapping')
        if not all(msg.get(key) for key in cls.REQ_MSG_KEYS):
            logger.debug("msg_raw: [%s]", msg_raw)
            raise ValueError(f'not all keys present in incoming message: {msg} |'
                             f'{cls.REQ_MSG_KEYS}')
        return msg

    @classmethod
    def pack_input(cls, msg, ws_id, message_types, identity_nym, room, **kwargs):
        msg.update(from_nym=identity_nym, room=room)
        data_out = {}
        data_out['message_types'] = message_types
        data_out['ws_id'] = ws_id
        data_out['msg'] = msg
        return data_out

    def map_sequence(self, sequence):
        string_sequence = ''.join(map(lambda x: self.message_actions[x]['symbol'],
                                      sequence))
        return string_sequence

    def validate_msg_sequence(self, msg, sequence):
        str_seq = self.map_sequence(sequence)
        action = msg['action']
        action_char = self.message_actions[action]['symbol']
        candidate_seq = str_seq + action_char
        if self.message_sequence_pattern.search(candidate_seq) is None:
            raise ValueError(f'{action} not allowed after sequence: {sequence} of actions')

    def validate_msg_params(self, msg):
        action = msg['action']
        required_args = self.message_actions[action]['required_args']
        for arg_name, arg_type in required_args:
            value = msg.get(arg_name)
            if value is None:
                raise ValueError(f'missing required parameter [ {arg_name} ] in {msg}')
            if not isinstance(value, arg_type):
                raise ValueError(
                    f'[ {arg_name} ] parameter {value} not of required type {arg_type}')

    def grab_message(self, msg_raw):
        msg = json.loads(msg_raw)
        ws_id = msg['ws_id']
        sequence = msg['message_types']
        msg = msg['msg']
        return msg, ws_id, sequence

    def validate_msg(self, msg, sequence):
        self.validate_msg_sequence(msg, sequence)
        self.validate_msg_params(msg)

    async def process_message(self, msg_raw):
        try:
            msg, ws_id, sequence = self.grab_message(msg_raw)
            if len(sequence) > self.MAX_MESSAGES:
                msg['action'] = 'close'  # unfair implicit connection cut
            self.validate_msg(msg, sequence)
            action = msg['action']
            handler = self.message_actions[action]['handler']
            meth = getattr(self, handler)
            return await meth(msg, ws_id) or [self.success_response(msg, ws_id)]
        except (KeyError, AttributeError) as ke:
            logger.error('\n%s', traceback.format_exc())
            return [self.error_response(msg, ws_id, f'missing handler for action {ke}')]
        except ValueError as ve:
            logger.error('\n%s', traceback.format_exc())
            return [self.error_response(msg, ws_id, ve)]
        except ValidationError as ve:
            logger.error('\n%s', traceback.format_exc())
            return [self.error_response(msg, ws_id, ve)]
        except Exception as gene:
            logger.error('\n%s', traceback.format_exc())
            return [self.error_response(msg, ws_id, f'unexpected generic expection {gene}')]

    async def handle_authenticate(self, msg, ws_id):
        nym = await self.redis_pub.spop(NYMS_KEY)
        if nym is None:
            raise ValueError('out of available nyms')
        msg['from_nym'] = nym.decode(encoding='utf-8')
        return [self.success_response(msg, ws_id)]

    async def handle_close(self, msg, ws_id):
        pass

    async def handle_select_room(self, msg, ws_id):

        dikt = {'title': msg['destination_room']}
        # import threading
        # logger.info('current thread: [%s]', threading.get_native_id())
        room, _ = Room.objects.get_or_create(**dikt)
        msg['last_message'] = room.messages_of.count() - 1

        # https://stackoverflow.com/questions/59503825/django-async-to-sync-vs-asyncio-run
        # from asgiref.sync import sync_to_async
        # await sync_to_async(self.handle_room_db, thread_sensitive=True)(dikt)

        prev_room = msg['room']
        new_room = msg['destination_room']
        msg['prev_room'] = prev_room
        msg['room'] = new_room
        msg['page'] = self.PAGE

        result = [self.success_response(msg, ws_id)]

        if prev_room is not None and new_room != prev_room:
            content = f"[{msg['from_nym']}] has left {prev_room}"
            announce_left = self.send_message_layout(
                content, prev_room, from_nym='hendrix')
            result.append(announce_left)


        content = f"[{msg['from_nym']}] has entered {msg['room']}"
        announce = self.send_message_layout(
            content, new_room, from_nym='hendrix')
        result.append(announce)

        room_info = self.rooms_specifics.get(msg['room'])
        if room_info:
            personal_tip = room_info['personal_tip']
            personal_msg = self.send_message_layout(
                content=personal_tip, room=None, from_nym=None,
                ws_id=ws_id, channel=HENDRIX_CHANNEL)
            result.append(personal_msg)
        return result

    # def handle_room_db(self, dikt):

    #     import threading
    #     logger.info('current thread: [%s]', threading.get_native_id())
    #     room, _ = Room.objects.get_or_create(**dikt)
    #     logger.info('current thread: [%s]', threading.get_native_id())

    async def handle_send_message(self, msg, ws_id):
        dikt = {'title': msg['room']}
        room = Room.objects.get(**dikt)
        data = {'content': msg['content'],
                'from_nym': msg['from_nym'],
                }
        for retry in range(self.MAX_RETRIES + 1):
            try:
                with transaction.atomic():
                    message = Message(**data)
                    message.save()
                    message_order = MessageOrder(room=room, message=message,
                                                 order=room.messages_of.count())
                    message_order.save()
                    break
            except IntegrityError as inte:
                self.logger.debug('STAGING RETRY:[%d] - [%s]', retry, inte)
                if retry == self.MAX_RETRIES:
                    raise
        # msg_id = message.id
        # newmsg = Message
        mser = ChatMessageSerializer(message)
        msg.update(mser.data)
        return [self.success_response(msg, ws_id)]

    async def handle_history_retrieve(self, msg, ws_id):
        dikt = {'title': msg['room']}
        room = Room.objects.get(**dikt)
        last = msg['last_message']
        first = last - self.PAGE
        orders = room.messages_of.filter(order__lte=last).filter(order__gt=first).\
            order_by('order')

        def mapper(order):
            datum = ChatMessageSerializer(order.message).data
            datum.pop('room')
            return datum
        msgs = map(mapper, orders)
        msg['result'] = list(msgs)
        return [self.success_response(msg, ws_id)]

    async def handle_query(self, msg, ws_id):
        query = msg['query_name']
        room = msg['room']
        query_parameters = msg['parameters']

        query_info = self.rooms_specifics[room]['queries'][query]
        req_args = query_info['required_args']
        self.validate_query_params(query_parameters, req_args)
        query_handler = query_info['handler']
        meth = getattr(self, query_handler)
        return await meth(msg, query_parameters, ws_id)

    def validate_query_params(self, query_params, req_args):
        for arg_name, arg_type in req_args:
            value = query_params.get(arg_name)
            if value is None:
                raise ValueError(f'missing required parameter [ {arg_name} ] in {query_params}')
            if not isinstance(value, arg_type):
                raise ValueError(
                    f'[ {arg_name} ] parameter {value} not of required type {arg_type}')

    async def handle_menu_lobby(self, msg, query_parameters, ws_id):
        from .queries.lobby_help import messages
        res = []
        content = f"Perfect!"
        res.append(self.send_message_layout(content, ws_id=ws_id, room='loopback_secret_room', from_nym='hendrix'))
        for message in messages:
            personal_msg = self.send_message_layout(
                content=message, room=None, from_nym=None,
                ws_id=ws_id, channel=HENDRIX_CHANNEL, token=msg.get('token'))
            res.append(personal_msg)
        return res

    def success_response(self, msg, ws_id, channel=ROUNDTRIP_CHANNEL):
        return {
            'ws_id': ws_id,
            'status': self.SUCCESS,
            'msg': msg
        }, channel

    def error_response(self, msg, ws_id, ve, channel=ROUNDTRIP_CHANNEL):
        return {
            'ws_id': ws_id,
            'status': self.ERROR,
            'error_reason': str(ve),
            'msg': msg,
        }, channel
