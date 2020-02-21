from .settings import NYMS_KEY
import re
import json
from collections import Mapping
from .worker_template import AioredisWorker


class MessageProtoHandler(AioredisWorker):
    REQ_MSG_KEYS = ['action']
    SUCCESS = 'success'
    ERROR = 'error'

    message_sequence_pattern = re.compile(r'''
        ^
        (
            (
                A
                (
                    C|
                    (
                        S(S|M|H)*C?
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
            'required_args': [('destination_room', str)],
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
        }

    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def validate_raw_input(cls, msg_raw):
        try:
            msg = json.loads(msg_raw)
        except json.JSONDecodeError as jse:
            raise ValueError('invalid json encoding of incoming message') from jse
        if not isinstance(msg, Mapping):
            raise ValueError(f'the {msg} has to be a mapping')
        if not all(msg.get(key) for key in cls.REQ_MSG_KEYS):
            raise ValueError(f'not all keys present in incoming message: {msg} |'
                             f'{cls.REQ_MSG_KEYS}')
        return msg

    @classmethod
    def pack_input(cls, msg, types, ws_id, from_nym, room):
        msg.update(from_nym=from_nym, room=room)
        data_out = {}
        data_out['message_types'] = types
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
            raise ValueError(f'{action} not allowed after {sequence} of actions')

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
            self.validate_msg(msg, sequence)
            action = msg['action']
            handler = self.message_actions[action]['handler']
            meth = getattr(self, handler)
            return await meth(msg, ws_id) or [self.success_response(msg, ws_id)]
        except (KeyError, AttributeError) as ke:
            return [self.error_response(msg, ws_id, f'missing handler for action {ke}')]
        except ValueError as ve:
            return [self.error_response(msg, ws_id, ve)]
        except Exception as gene:
            return [self.error_response(msg, ws_id, f'unexpected generic expection {gene}')]

    async def handle_authenticate(self, msg, ws_id):
        nym = await self.redis_pub.spop(NYMS_KEY)
        if nym is None:
            raise ValueError('out of available nyms')
        msg['from_nym'] = nym.decode(encoding='utf-8')
        return [self.success_response(msg, ws_id)]

    async def handle_select_room(self, msg, ws_id):
        pass

    async def handle_send_message(self, msg, ws_id):
        pass

    def success_response(self, msg, ws_id):
        return {
            'ws_id': ws_id,
            'status': self.SUCCESS,
            'msg': msg
        }

    def error_response(self, msg, ws_id, ve):
        return {
            'ws_id': ws_id,
            'status': self.ERROR,
            'error_reason': str(ve),
            'msg': msg,
        }
