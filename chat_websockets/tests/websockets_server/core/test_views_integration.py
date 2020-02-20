import pytest
from websockets_server.core.app import app as App
from unittest.mock import ANY
from utils.log_helper import setup_logger
import json
logger = setup_logger(__name__)


@pytest.fixture
def cli(loop, aiohttp_client):
    # from pytest_aiohttp import aiohttp_client - this fixture is somehow used automatically
    app = App
    return loop.run_until_complete(aiohttp_client(app))


async def test_get_ws_route(cli):
    ws_resp = await cli.ws_connect("/ws")
    for i in range(10):
        test_mes = {'action': f'{i} привет привет 23'}
        await ws_resp.send_str(json.dumps(test_mes))
        ws_mes = await ws_resp.receive_str()
        logger.info(ws_mes)
        assert json.loads(ws_mes) == test_mes
    await ws_resp.close()
