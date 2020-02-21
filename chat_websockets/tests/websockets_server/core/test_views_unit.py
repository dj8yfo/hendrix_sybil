from websockets_server.core import views
import pytest
from unittest.mock import patch, AsyncMock, MagicMock, NonCallableMock, call
from utils.log_helper import setup_logger

logger = setup_logger(__name__)


@pytest.fixture
def aio_req():
    return MagicMock(name='aiohttp_request')


async def test_init(aio_req):
    view = views.WebSocketView(aio_req)
    assert view.app == aio_req.app


async def test_get(aio_req):
    view = views.WebSocketView(aio_req)
    ws = MagicMock(name='ws')
    ws_id_unique = 'host_far_away_id'
    with patch.object(views.web, 'WebSocketResponse', return_value=ws):
        view.app.extract_websockets_id.return_value = ws_id_unique
        view.app.process_msg_outbound = AsyncMock(name='process_out_mock')
        view.app.handle_ws_connect = AsyncMock(name='handle_ws_connect_mock')
        view.app.handle_ws_disconnect = AsyncMock(name='handle_ws_disconnect_mock')

        ws.prepare = AsyncMock(name='ws_prepare')
        test_msgs = [NonCallableMock(type=views.WSMsgType.TEXT,
                                     data=f'test_msg {el}')
                     for el in range(6)]
        ws.__aiter__.return_value = test_msgs

        await view.get()

        view.app.handle_ws_connect.assert_called_with(ws_id_unique, ws)
        ws.prepare.assert_called_with(aio_req)
        ws.prepare.assert_awaited()
        exp_calls = [call(el.data, ws_id_unique) for el in test_msgs]
        assert view.app.process_msg_outbound.mock_calls == exp_calls
        view.app.handle_ws_disconnect.assert_awaited_with(ws_id_unique)


async def test_get_errors(aio_req):
    view = views.WebSocketView(aio_req)
    ws = MagicMock(name='ws')
    ws.close = AsyncMock(name='close_ws')
    ws_id_unique = 'host_far_away_id'

    with patch.object(views.web, 'WebSocketResponse', return_value=ws):
        view.app.extract_websockets_id.return_value = ws_id_unique
        unused_data = [NonCallableMock(
            type=views.WSMsgType.TEXT, data='unused')]
        test_msgs = [NonCallableMock(type=views.WSMsgType.TEXT,
                                     data=f'test_msg')]
        sidef = [Exception('error_out')] + test_msgs

        ws.prepare = AsyncMock(name='ws_prepare')
        ws.__aiter__.return_value = unused_data + test_msgs
        view.app.handle_ws_connect = AsyncMock(name='handle_ws_connect_mock')
        view.app.handle_ws_disconnect = AsyncMock(name='handle_ws_disconnect_mock')
        view.app.process_msg_outbound = AsyncMock(name='process_out_mock',
                                                  side_effect=sidef)

        await view.get()

        exp_calls = [call(el.data, ws_id_unique) for el in unused_data]
        assert view.app.process_msg_outbound.mock_calls == exp_calls
        ws.close.assert_awaited()
        view.app.handle_ws_disconnect.assert_awaited_with(ws_id_unique)
