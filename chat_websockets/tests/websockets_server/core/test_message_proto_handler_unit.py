from websockets_server.core.message_proto_handler import MessageProtoHandler
import pytest
from utils.log_helper import setup_logger
from unittest.mock import Mock, ANY
from websockets_server.models import Room
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

logger = setup_logger(__name__)


@pytest.fixture
def seq_pattern():
    return MessageProtoHandler.message_sequence_pattern


def test_seq_mapper():
    mapper = MessageProtoHandler().map_sequence
    assert mapper([]) == ''
    assert mapper(['authenticate', 'select_room',
                   'history_retrieve', 'send_message']) == 'ASHM'
    assert mapper(['authenticate', 'select_room',
                   'select_room', 'send_message', 'history_retrieve']) == 'ASSMH'


def test_seq_mapper_error():
    mapper = MessageProtoHandler().map_sequence
    with pytest.raises(KeyError, match='invalid_action'):
        mapper(['authenticate', 'invalid_action', 'send_message'])


def test_validate_raw_input_error():
    arg = 'invalid_input: failure'
    with pytest.raises(ValueError, match='invalid json encoding'):
        MessageProtoHandler.validate_raw_input(arg)


def test_validate_raw_input_error_not_mapping():
    arg = '[5435, 345345 ,345345 ,34535 ,34535]'
    with pytest.raises(ValueError, match='has to be a mapping'):
        MessageProtoHandler.validate_raw_input(arg)


def test_validate_raw_input_error_keys():
    arg = '{"toxicity": 45454}'
    with pytest.raises(ValueError, match='not all keys'):
        MessageProtoHandler.validate_raw_input(arg)


def test_pack_input():
    packer = MessageProtoHandler.pack_input
    msg = {'action': 'send_message',
           'content': 'snx snx snx',
           'from_nym': None,
           'room': 'ambiguous'}
    data = packer(msg, message_types=['authenticate', 'select_room'],
                  ws_id='host_far_away',
                  identity_nym='Alexander the Great',
                  room='system_message_room4234234')
    assert data == {
        'message_types': ['authenticate', 'select_room'],
        'ws_id': 'host_far_away',
        'msg': {
            'action': 'send_message',
            'content': 'snx snx snx',
            'from_nym': 'Alexander the Great',
            'room': 'system_message_room4234234'
        }
    }


def test_pattern(seq_pattern):
    assert seq_pattern.search('AC') is not None
    assert seq_pattern.search('A') is not None
    assert seq_pattern.search('C') is not None
    assert seq_pattern.search('AM') is None
    assert seq_pattern.search('AAC') is None
    assert seq_pattern.search('ACC') is None
    assert seq_pattern.search('ACA') is None
    assert seq_pattern.search('ASMMMHC') is not None
    assert seq_pattern.search('ASMMMH') is not None
    assert seq_pattern.search('ASMMMSC') is not None
    assert seq_pattern.search('ASMMMSCC') is None
    assert seq_pattern.search('ASHHHSMMHSC') is not None
    assert seq_pattern.search('ASHHHSMMHS') is not None
    assert seq_pattern.search('AMMMH') is None
    assert seq_pattern.search('SMMM') is None


async def test_handle_select_room():
    proto = MessageProtoHandler()
    msg = {'destination_room': 'illegally_set_on_client',
           'from_nym': 'a nym',
           'room': 'previous_room'}
    rslt = await proto.handle_select_room(msg, Mock())
    logger.debug(rslt)
    assert len(rslt) == 3
    status, _ = rslt[0]
    exp_mes = {
            "destination_room": "illegally_set_on_client",
            "from_nym": "a nym",
            "room": "illegally_set_on_client",
            "last_message": ANY,
            "prev_room": "previous_room",
            "page": MessageProtoHandler.PAGE
        }
    assert status['msg'] == exp_mes


async def test_handle_send_message():
    proto = MessageProtoHandler()
    test_room = 'illegally_set_on_client'
    start_count = Room.objects.get(title=test_room).messages_of.count()
    for i in range(10):
        msg = {'content': f'control {i} relinquish',
               'room': test_room,
               'from_nym': 'a unique nym'}
        rslt = await proto.handle_send_message(msg, Mock())
        logger.debug(rslt)
    end_count = Room.objects.get(title=test_room).messages_of.count()
    assert (end_count - start_count) == 10


async def test_handle_history_retrieve():
    proto = MessageProtoHandler()
    test_room = 'illegally_set_on_client'
    test_range = MessageProtoHandler.PAGE
    for i in range(test_range):
        msg = {'content': f'control {i} relinquish',
               'room': test_room,
               'from_nym': 'a unique nym'}
        rslt = await proto.handle_send_message(msg, Mock())
        logger.debug(rslt)

    last_msg = Room.objects.get(title=test_room).messages_of.count() - 1
    hist = {'last_message': last_msg,
            'room': test_room}
    rslt = await proto.handle_history_retrieve(hist, Mock())
    logger.debug(rslt)

    resp = rslt[0]
    act_msg, _ = resp
    results = act_msg['msg']['result']

    assert len(results) == test_range
    for i in range(test_range):
        exp = {'content': f'control {i} relinquish',
               'from_nym': 'a unique nym',
               'date_created': ANY,
               'seq': (last_msg - (test_range - 1) + i)
               }
        assert results[i] == exp
