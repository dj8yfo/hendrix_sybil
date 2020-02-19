from unittest.mock import patch, Mock, AsyncMock, call
from websockets_server.core.server import HXApplication
from websockets_server.core.settings import WORKER_TOPIC, ROUNDTRIP_CHANNEL
from utils.log_helper import setup_logger
from aioredis.commands import Redis
from aiohttp import WSCloseCode
import pytest
import asyncio
logger = setup_logger(__name__)


redis_spec = dir(Redis)
redis_spec.remove('__await__')


# redis_mock_conf = AsyncMock(return_value=Mock(name='redis_mock',
#                                               spec=redis_spec))
# with patch('aioredis.create_redis', redis_mock_conf) as aiored:

@pytest.fixture
def app():
    return HXApplication()


class TestHXApplicationS():

    def test_init(self, app):
        assert len(app.tasks) == 0
        assert len(app.websockets) == 0
        assert app.tasks == []
        assert app.websockets == {}
        assert app._setup in app.on_startup
        assert app._on_shutdown_handler in app.on_shutdown

    @patch('aioredis.create_redis')
    async def test__setup(self, aiored, app):
        with patch.object(app, '_loop') as ploop:
            with patch.object(app, 'channel_subscribe', Mock(name='chan_coro'))\
                    as chan_coro:
                exp_red_sub = Mock(name='redis_sub')
                exp_red_pub = Mock(name='redis_pub')
                aiored.side_effect = [exp_red_pub, exp_red_sub]
                coro = chan_coro.return_value
                chanel_exp = ploop.create_task.return_value

                await app._setup(Mock())

                assert app.tasks[0] == chanel_exp
                assert app.redis_sub == {
                    ROUNDTRIP_CHANNEL: exp_red_sub
                }
                assert app.redis_pub == exp_red_pub
                app.channel_subscribe.assert_called_with(ROUNDTRIP_CHANNEL,
                                                         app.process_msg_inbound)
                ploop.create_task.assert_called_with(coro, name=f'redis_{ROUNDTRIP_CHANNEL}_chan')

    async def test__on_shutdown_handler(self, app):
        real_redis_sub = Mock(name='redis_sub_connection')
        real_redis_sub.closed = False
        real_redis_sub.wait_closed = AsyncMock(name='redis_sub_close_wait')
        app.redis_sub = {
            'test_chan': real_redis_sub
        }

        app.redis_pub = Mock(name='redis_pub', spec=redis_spec)
        app.redis_pub.closed = False
        app.redis_pub.wait_closed = AsyncMock(name='redis_pub_close_wait')

        async def trivial(param):
            await asyncio.sleep(1)
            return 'trivial coro result'

        app.tasks = [asyncio.create_task(trivial(i), name=i) for i in range(10)]
        for i in range(5):
            ws_id_mock = Mock(name=f'ws_id mock {i}')
            ws_mock = Mock(name=f'ws_mock {i}')
            ws_mock.close = AsyncMock()
            app.websockets[ws_id_mock] = {
                'ws': ws_mock
            }

        await app._on_shutdown_handler(Mock())

        for ws_id_mock in app.websockets.keys():
            ws_mock = app.websockets[ws_id_mock]['ws']
            ws_mock.close.assert_called_with(code=WSCloseCode.GOING_AWAY,
                                             message='servo_shutdown')
            ws_mock.close.assert_awaited()

        for t in app.tasks:
            assert t.cancelled()
        real_redis_sub.wait_closed.assert_awaited()
        app.redis_pub.wait_closed.assert_awaited()

    async def test_channel_subscribe(self, app):
        app.process_msg_inbound = AsyncMock(name='app_process_msg_inbound_mock')

        redis_chan = AsyncMock(name='redis_chan_conn')
        real_redis_sub = Mock(name='redis_sub_connection')
        test_chan = 'test_channel'
        app.redis_sub = {
            test_chan: real_redis_sub
        }
        real_redis_sub.subscribe = AsyncMock(name='redis_sub_command')
        real_redis_sub.subscribe.return_value = [redis_chan]

        sidef = [f'test_mes {el}'.encode() for el in range(6)]

        redis_chan.wait_message = AsyncMock(name='redis_chan_conn_wait',
                                            side_effect=sidef)
        redis_chan.get = AsyncMock(name='redis_chan_conn_get', side_effect=sidef)
        try:
            await app.channel_subscribe(test_chan, app.process_msg_inbound)

        except RuntimeError as e:
            assert str(e) == 'coroutine raised StopIteration'
        real_redis_sub.subscribe.assert_called_with(test_chan)
        exp_calls = [call(test_chan, el) for el in sidef]
        app.process_msg_inbound.assert_has_awaits(exp_calls)

    async def test_handle_ws_connect(self, app):
        ws_id_mock = Mock(name=f'ws_id mock')
        ws_mock = Mock(name=f'ws_mock')

        await app.handle_ws_connect(ws_id_mock, ws_mock)

        assert app.websockets[ws_id_mock]['ws'] == ws_mock
        assert app.websockets[ws_id_mock]['message_tuples'] == []
        assert app.websockets[ws_id_mock]['room'] is None
        assert app.websockets[ws_id_mock]['identity_name'] == 'unauthenticated'

    async def test_handle_ws_connect_replace(self, app):
        ws_id_mock = Mock(name=f'ws_id mock')
        stored_ws_mock = Mock(name=f'stored_ws_mock')
        stored_ws_mock.close = AsyncMock('close_stored_conn')
        ws_mock = Mock(name=f'ws_mock')

        await app.handle_ws_connect(ws_id_mock, stored_ws_mock)
        await app.handle_ws_connect(ws_id_mock, ws_mock)

        stored_ws_mock.close.assert_awaited()
        assert app.websockets[ws_id_mock]['ws'] == ws_mock

    def test_handle_ws_disconnect(self, app):
        ws_id_mock = Mock(name=f'ws_id mock')
        ws_struct_mock = Mock(name=f'ws_struct_mock')

        app.websockets[ws_id_mock] = ws_struct_mock
        app.handle_ws_disconnect(ws_id_mock)

        assert ws_id_mock not in app.websockets.keys()

    async def test_process_msg_outbound(self, app):
        app.redis_pub = Mock(name='redis_pub')
        app.redis_pub.publish_json = AsyncMock(name='redis_pub.publish_json')
        ws_id = 'host_far_away'
        app.websockets[ws_id] = {}
        app.websockets[ws_id]['message_tuples'] = [('A', 30), ('S', 34), ('H', 100), ('M', 300)]
        msg = '{"action": 45454}'

        exp_data = {
            'message_types': ['A', 'S', 'H', 'M'],
            'ws_id': ws_id,
            'msg': {
                'action': 45454
            }
        }
        await app.process_msg_outbound(msg, ws_id)

        app.redis_pub.publish_json.assert_awaited()
        app.redis_pub.publish_json.assert_called_with(WORKER_TOPIC, exp_data)

    async def test_process_msg_outbound_error(self, app):
        arg = 'invalid_input: failure'
        with pytest.raises(ValueError, match='json encoding'):
            await app.process_msg_outbound(arg, 0)

    async def test_process_msg_outbound_error_keys(self, app):
        arg = '{"toxicity": 45454}'
        with pytest.raises(ValueError, match='not all keys'):
            await app.process_msg_outbound(arg, 0)
