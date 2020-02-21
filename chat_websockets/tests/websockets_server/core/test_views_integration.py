import pytest
from unittest.mock import ANY, patch
from aiohttp import WSMsgType
from websockets_server.core.server import HXApplication
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


@pytest.mark.xfail(reason='not implemented select room yet')
async def test_get_ws_route(cli):
    ws_resp = await cli.ws_connect("/ws")

    ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    for test_mes in [{'action': f'authenticate', 'client_token': 'dsffdsjsdf X$%3534232Xdfs'},
                     {'action': 'select_room', 'destination_room': 'default',
                      'client_token': 'dsffdsjsdf X$%3534232Xdfs'}]:
        await ws_resp.send_str(json.dumps(test_mes))
        await ws_resp.receive_str()

    for i in range(10):
        test_mes = {'action': f'send_message',
                    'content': f'control {i} relinquish',
                    'room': 'illegally_set_on_client'}
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()
        exp_msg = dict(test_mes)
        exp_msg.update(from_nym=None, room=None)
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
