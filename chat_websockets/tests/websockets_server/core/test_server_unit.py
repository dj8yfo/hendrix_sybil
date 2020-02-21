from unittest.mock import patch, Mock, AsyncMock, call
from websockets_server.core.server import HXApplication, nyms
import websockets_server
from websockets_server.core.settings import ROUNDTRIP_CHANNEL, HENDRIX_CHANNEL, NYMS_KEY
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
                exp_red_sub1 = Mock(name='redis_sub1')
                exp_red_pub = Mock(name='redis_pub')
                exp_red_pub.sadd = AsyncMock(name='redis_sadd_mock')
                aiored.side_effect = [exp_red_pub, exp_red_sub, exp_red_sub1]
                coro = Mock(name='redis_sub_coro')
                coro1 = Mock(name='redis_sub_coro')
                chan_coro.side_effect = [coro, coro1]
                chanel_exp = Mock(name='redis_sub_task')
                chanel_exp1 = Mock(name='redis_sub_task1')
                ploop.create_task.side_effect = [chanel_exp, chanel_exp1]

                await app._setup(Mock())

                assert app.tasks[0] == chanel_exp
                assert app.tasks[1] == chanel_exp1
                assert app.redis_sub == {
                    ROUNDTRIP_CHANNEL: exp_red_sub,
                    HENDRIX_CHANNEL: exp_red_sub1
                }
                assert app.redis_pub == exp_red_pub
                sub_exp_calls = [call(ROUNDTRIP_CHANNEL, app.process_msg_inbound),
                                 call(HENDRIX_CHANNEL, app.process_msg_admin)]
                app.channel_subscribe.assert_has_calls(sub_exp_calls)
                exp_calls = [call(coro, name=f'redis_{ROUNDTRIP_CHANNEL}_chan'),
                             call(coro1, name=f'redis_{HENDRIX_CHANNEL}_chan')]
                ploop.create_task.assert_has_calls(exp_calls)
                exp_calls = [call(NYMS_KEY, nym.encode(encoding='utf-8')) for nym in nyms]
                exp_red_pub.sadd.assert_has_awaits(exp_calls)

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
        app.redis_pub.spop = AsyncMock(name='redis_pub_spop')

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

        num_nyms = len(nyms)

        await app._on_shutdown_handler(Mock())

        app.redis_pub.spop.assert_has_awaits([call(NYMS_KEY, num_nyms)])
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
        assert app.websockets[ws_id_mock]['message_types'] == []
        assert app.websockets[ws_id_mock]['room'] is None
        assert app.websockets[ws_id_mock]['identity_nym'] == None
        assert app.websockets[ws_id_mock]['processing_blocked'] is False

    async def test_handle_ws_connect_replace(self, app):
        ws_id_mock = Mock(name=f'ws_id mock')
        stored_ws_mock = Mock(name=f'stored_ws_mock')
        stored_ws_mock.close = AsyncMock('close_stored_conn')
        ws_mock = Mock(name=f'ws_mock')

        await app.handle_ws_connect(ws_id_mock, stored_ws_mock)
        await app.handle_ws_connect(ws_id_mock, ws_mock)

        stored_ws_mock.close.assert_awaited()
        assert app.websockets[ws_id_mock]['ws'] == ws_mock

    async def test_handle_ws_disconnect(self, app):
        ws_id_mock = Mock(name=f'ws_id mock')
        ws_struct_mock = Mock(name=f'ws_struct_mock')

        app.websockets[ws_id_mock] = ws_struct_mock

        await app.handle_ws_disconnect(ws_id_mock)

        assert ws_id_mock not in app.websockets.keys()

    async def test_process_msg_outbound(self, app):
        app.redis_pub = Mock(name='redis_pub')
        app.redis_pub.publish_json = AsyncMock(name='redis_pub.publish_json')
        ws_id = 'host_far_away'
        app.websockets[ws_id] = {}
        app.websockets[ws_id]['message_types'] = ['authenticate', 'select_room',
                                                  'history_retrieve', 'send_message']
        app.websockets[ws_id]['room'] = None
        app.websockets[ws_id]['identity_nym'] = None
        app.websockets[ws_id]['processing_blocked'] = False
        msg = '{"action": 45454}'

        exp_data = {
            'message_types': ['authenticate', 'select_room',
                              'history_retrieve', 'send_message'],
            'ws_id': ws_id,
            'msg': {
                'action': 45454,
                'from_nym': None,
                'room': None,
            }
        }

        with patch.object(websockets_server.core.server.random, 'choice',
                          return_value='some_random_pub'):
            await app.process_msg_outbound(msg, ws_id)

        assert app.websockets[ws_id]['processing_blocked'] is True
        app.redis_pub.publish_json.assert_awaited()
        app.redis_pub.publish_json.assert_called_with('some_random_pub', exp_data)

    async def test_process_msg_outbound_error(self, app):
        arg = 'invalid_input: failure'
        with pytest.raises(ValueError, match='invalid json encoding'):
            await app.process_msg_outbound(arg, 0)

    async def test_process_msg_outbound_error_not_mapping(self, app):
        arg = '[5435, 345345 ,345345 ,34535 ,34535]'
        with pytest.raises(ValueError, match='has to be a mapping'):
            await app.process_msg_outbound(arg, 0)

    async def test_process_msg_outbound_error_keys(self, app):
        arg = '{"toxicity": 45454}'
        with pytest.raises(ValueError, match='not all keys'):
            await app.process_msg_outbound(arg, 0)

    async def test_process_msg_outbound_error_duplicate_msg(self, app):
        arg = '{"action": 45454}'
        ws_id = 'host_far_away'
        app.websockets[ws_id] = {}
        app.websockets[ws_id]['processing_blocked'] = True
        with pytest.raises(RuntimeError, match='blocked by another message'):
            await app.process_msg_outbound(arg, ws_id)
