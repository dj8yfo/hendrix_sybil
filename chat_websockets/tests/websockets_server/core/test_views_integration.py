import pytest
from websockets_server.core.app import app as App
from utils.log_helper import setup_logger
logger = setup_logger(__name__)


@pytest.fixture
def cli(loop, aiohttp_client):
    # from pytest_aiohttp import aiohttp_client - this fixture is somehow used automatically
    app = App
    return loop.run_until_complete(aiohttp_client(app))


test_mes = 'travel to Mecca'


async def test_get_ws_route(cli):
    ws_resp = await cli.ws_connect("/ws")
    await ws_resp.send_str(test_mes)
    ws_mes = await ws_resp.receive_str()
    assert ws_mes == test_mes + '/answer'
    await ws_resp.send_str('close')
    await ws_resp.receive()
    assert ws_resp.closed
