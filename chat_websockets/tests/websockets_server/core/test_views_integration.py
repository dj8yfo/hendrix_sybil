import pytest
from unittest.mock import ANY, patch
from aiohttp import WSMsgType
from websockets_server.core.server import HXApplication
from websockets_server.core.message_proto_handler import MessageProtoHandler
from utils.log_helper import setup_logger
import json
logger = setup_logger(__name__)


@pytest.fixture
def cli(loop, aiohttp_client):
    # from pytest_aiohttp import aiohttp_client - this fixture is somehow used automatically
    app = HXApplication()
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def patched_nyms_cli(loop, aiohttp_client):
    # from pytest_aiohttp import aiohttp_client - this fixture is somehow used automatically
    new_nyms = ['unique_nym']
    with patch('websockets_server.core.server.nyms', new_nyms):
        app = HXApplication()
        return loop.run_until_complete(aiohttp_client(app))


def log_decorate(method):
    async def decorated():
        result = await method()
        logger.debug('[%s] received [%s]', method.__name__, result)
        return result
    return decorated


async def test_send_multiple_messages(cli):
    ws_resp = await cli.ws_connect("/ws")

    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    for test_mes in [{'action': f'authenticate', 'client_token': 'dsffdsjsdf X$%3534232Xdfs'},
                     {'action': 'select_room', 'destination_room': 'quiet_place',
                      'client_token': 'dsffdsjsdf X$%3534232Xdfs'}]:
        await ws_resp.send_str(json.dumps(test_mes))
        await ws_resp.receive_str()
    await ws_resp.receive_str()  # self join announce

    for i in range(10):
        test_mes = {'action': f'send_message',
                    'content': f'control {i} relinquish',
                    'room': 'illegally_set_on_client'}
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()
        exp_msg = dict(test_mes)
        exp_msg.update(from_nym=ANY, room='quiet_place',
                       date_created=ANY, seq=ANY)
        exp_res = {
            'status': 'success',
            'msg': exp_msg
        }
        assert json.loads(ws_mes) == exp_res
    await ws_resp.close()


async def test_authenticate(patched_nyms_cli):
    ws_resp = await patched_nyms_cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    for test_mes in [{'action': f'authenticate'}]:
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()

    test_mes.update(from_nym='unique_nym', room=None)
    exp_res = {
        "status": "success",
        "msg": test_mes
    }
    assert json.loads(ws_mes) == exp_res


async def test_close(cli):
    ws_resp = await cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    for test_mes in [{'action': f'close'}]:
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()

    test_mes.update(from_nym=None, room=None)
    exp_res = {
        "status": "success",
        "msg": test_mes
    }
    assert json.loads(ws_mes) == exp_res


async def test_select_room(patched_nyms_cli):
    ws_resp = await patched_nyms_cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    test_mes = {'action': f'authenticate'}
    await ws_resp.send_str(json.dumps(test_mes))
    ws_mes = await ws_resp.receive_str()

    test_mes.update(from_nym=ANY, room=None)
    exp_res = {
        "status": "success",
        "msg": test_mes
    }
    assert json.loads(ws_mes) == exp_res
    test_mes = {'action': 'select_room', 'destination_room': 'custom_quiet_room'}
    await ws_resp.send_str(json.dumps(test_mes))
    ws_mes = await ws_resp.receive_str()

    test_mes.update(from_nym=ANY, room='custom_quiet_room', last_message=ANY,
                    page=MessageProtoHandler.PAGE, prev_room=None)
    exp_res = {
        "status": "success",
        "msg": test_mes
    }
    assert json.loads(ws_mes) == exp_res

    exp_join_announce = {
        'status': 'success',
        'msg': {
            'action': 'send_message',
            'content': '[unique_nym] has entered custom_quiet_room',
            'room': 'custom_quiet_room',
            'from_nym': 'hendrix',
            'date_created': ANY,
            'seq': -1
        }
    }
    announce_mes = await ws_resp.receive_str()
    assert json.loads(announce_mes) == exp_join_announce


async def test_select_room_personal_timp(patched_nyms_cli):
    ws_resp = await patched_nyms_cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    test_mes = {'action': f'authenticate'}
    await ws_resp.send_str(json.dumps(test_mes))
    _ = await ws_resp.receive_str()

    test_mes = {'action': 'select_room', 'destination_room': 'Lobby'}
    await ws_resp.send_str(json.dumps(test_mes))
    _ = await ws_resp.receive_str()

    another_msg = await ws_resp.receive_str()
    personal_msg = await ws_resp.receive_str()
    exp_personal_msg = {
        'status': 'success',
        'msg': {
            'action': 'send_message',
            'content': MessageProtoHandler.rooms_specifics['Lobby']['personal_tip'],
            'room': 'Lobby',
            'from_nym': 'hendrix',
            'date_created': ANY,
            'seq': -1
        }
    }
    assert json.loads(personal_msg) == exp_personal_msg or\
        json.loads(another_msg) == exp_personal_msg  # there is no guarantee of the order


async def test_handle_history_retrieve(patched_nyms_cli):
    ws_resp = await patched_nyms_cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    test_mes = {'action': f'authenticate'}
    await ws_resp.send_str(json.dumps(test_mes))
    ws_mes = await ws_resp.receive_str()

    test_mes = {'action': 'select_room', 'destination_room': 'quiet_place'}
    await ws_resp.send_str(json.dumps(test_mes))
    join_room_raw_conf = await ws_resp.receive_str()
    _ = await ws_resp.receive_str()
    join_room = json.loads(join_room_raw_conf)
    test_mes = {'action': 'history_retrieve', 'room': 'quiet_place',
                'last_message': join_room['msg']['last_message']}
    await ws_resp.send_str(json.dumps(test_mes))
    history_raw = await ws_resp.receive_str()
    history = json.loads(history_raw)
    assert len(history['msg']['result']) == MessageProtoHandler.PAGE


async def test_select_room_error(cli):
    ws_resp = await cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    test_mes = {'action': f'authenticate'}
    await ws_resp.send_str(json.dumps(test_mes))
    ws_mes = await ws_resp.receive_str()

    test_mes.update(from_nym=ANY, room=None)
    exp_res = {
        "status": "success",
        "msg": test_mes
    }
    assert json.loads(ws_mes) == exp_res

    for test_mes in [{'action': 'select_room', 'destination_room': None},
                     {'action': 'select_room', 'destination_room':
                      'fdsssssssssssssssssssssssssssssssssssssssssssssssverylongverylong'}]:
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()

        test_mes.update(from_nym=ANY, room=None)
        exp_res = {
            "status": "error",
            "error_reason": ANY,
            "msg": test_mes
        }
        assert json.loads(ws_mes) == exp_res


async def test_authenticate_send_message_sequence_error(cli):
    ws_resp = await cli.ws_connect("/ws")
    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    for test_mes in [{'action': f'authenticate'},
                     {'action': f'send_message', 'content': f'control 23 relinquish'}]:
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()

    test_mes.update(from_nym=ANY, room=None)
    exp_res = {
        "status": "error",
        "error_reason": ANY,
        "msg": test_mes
    }
    assert json.loads(ws_mes) == exp_res


async def test_get_ws_block_duplicate(cli):
    ws_resp = await cli.ws_connect("/ws")
    ws_resp.receive = log_decorate(ws_resp.receive)
    for i in range(2):
        test_mes = {'action': f'authenticate'}
        await ws_resp.send_str(json.dumps(test_mes))

    result = await ws_resp.receive()
    assert result.type == WSMsgType.CLOSE
    assert 'blocked by another message' in result.extra
    assert ws_resp.closed


async def test_get_ws_error_not_json(cli):
    ws_resp = await cli.ws_connect("/ws")
    ws_resp.receive = log_decorate(ws_resp.receive)
    await ws_resp.send_str('invalid_input: failure')

    result = await ws_resp.receive()
    assert result.type == WSMsgType.CLOSE
    assert 'invalid json encoding' in result.extra
    assert ws_resp.closed


async def test_get_ws_error_required_keys(cli):
    ws_resp = await cli.ws_connect("/ws")
    ws_resp.receive = log_decorate(ws_resp.receive)
    await ws_resp.send_str('{"toxicity": 45454}')

    result = await ws_resp.receive()
    assert result.type == WSMsgType.CLOSE
    assert 'not all keys' in result.extra
    assert ws_resp.closed
