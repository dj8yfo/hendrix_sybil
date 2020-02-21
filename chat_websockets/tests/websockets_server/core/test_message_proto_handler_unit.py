from websockets_server.core.message_proto_handler import MessageProtoHandler
import pytest
from utils.log_helper import setup_logger

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


def test_pack_input():
    packer = MessageProtoHandler.pack_input
    msg = {'action': 'send_message',
           'content': 'snx snx snx',
           'from_nym': None,
           'room': 'ambiguous'}
    data = packer(msg, ['authenticate', 'select_room'], 'host_far_away',
                  'Alexander the Great', 'system_message_room4234234')
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
