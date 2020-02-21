from aiohttp import WSMsgType
from aiohttp.test_utils import TestClient, TestServer, loop_context
from unittest.mock import patch
import os
import sys
import json
import pytest
sys.path.append(os.getcwd())
from websockets_server.core.server import HXApplication, nyms
from utils.log_helper import setup_logger

logger = setup_logger(__file__.replace(os.path.sep, '_'))


def log_decorate(method):
    async def decorated():
        result = await method()
        logger.debug('[%s] received [%s]', method.__name__, result)
        return result
    return decorated


def clients_context(routine, patch_nyms=nyms):
    with patch('websockets_server.core.server.nyms', patch_nyms):
        with loop_context() as loopext:
            app = HXApplication()
            server = TestServer(app)
            client1 = TestClient(server, loop=loopext)
            loopext.run_until_complete(client1.start_server())
            client2 = TestClient(server, loop=loopext)

            try:
                loopext.run_until_complete(routine(client2, client2))
            finally:
                loopext.run_until_complete(client1._server.close())
                loopext.run_until_complete(client1.close())
                loopext.run_until_complete(client2.close())


async def multi_clients_test_one(client1, client2):
    try:
        ws_resp1 = await client1.ws_connect("/ws")
        ws_resp2 = await client2.ws_connect("/ws")
        result = await ws_resp1.receive()
        assert result.type == WSMsgType.CLOSE
        assert 'replacing_conn' in result.extra
    finally:
        await ws_resp2.close()


# clients_context(multi_clients_test_one)
    # only expected to pass if extract_websockets_id
    # returns str(remote_host_prefix)

async def test_authenticate_out_of_nyms(client1, client2):
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        test_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(test_mes))

        resp1 = await ws_resp1.receive_str()
        error_mes = dict(test_mes)
        test_mes.update(from_nym='unique_nym', room=None)
        exp_res = {
            "status": "success",
            "msg": test_mes
        }
        assert json.loads(resp1) == exp_res
        resp2 = await ws_resp2.receive_str()

        error_mes.update(from_nym=None, room=None)
        exp_res = {
            "status": "error",
            "error_reason": "out of available nyms",
            "msg": error_mes
        }
        assert json.loads(resp2) == exp_res
    finally:
        await ws_resp1.close()
        await ws_resp2.close()

clients_context(test_authenticate_out_of_nyms, patch_nyms=['unique_nym'])
