from unittest.mock import patch, Mock, AsyncMock, call, MagicMock, ANY
from websockets_server.core.server import HXApplication, nyms, HXApplicationState
import websockets_server
from websockets_server.core import message_proto_handler
from websockets_server.core.settings import ROUNDTRIP_CHANNEL, HENDRIX_CHANNEL, NYMS_KEY
from utils.log_helper import setup_logger
from aioredis.commands import Redis
from aiohttp import WSCloseCode
import pytest
import asyncio

logger = setup_logger(__name__)
logger_state = setup_logger(__name__ + HXApplicationState.__name__)


redis_spec = dir(Redis)
redis_spec.remove('__await__')


# redis_mock_conf = AsyncMock(return_value=Mock(name='redis_mock',
#                                               spec=redis_spec))
# with patch('aioredis.create_redis', redis_mock_conf) as aiored:

@pytest.fixture
def app():
    return HXApplication()


@pytest.fixture
def appstate():
    return HXApplicationState(logger_state)


class TestHXApplicationSState():
    def test_init(self, appstate):
        assert appstate.websockets == {}
        assert appstate.rooms == {}
        assert appstate.logger == logger_state

    def test___iter__(self, appstate):
        for i in range(10):
            appstate.websockets[f'key{i}'] = Mock(name=f'{i}')

        actual_keys = set(iter(appstate))
        exp_keys = set(f'key{i}' for i in range(10))
        assert actual_keys == exp_keys

    def test_store_new_connection(self, appstate):
        ws_id_mock = Mock(name='ws_id_mock')
        ws_mock = Mock(name='ws_mock')

        appstate.store_new_connection(ws_id_mock, ws_mock)
        assert appstate.websockets[ws_id_mock] == {
            'ws': ws_mock,
            'message_types': [],
            'identity_nym': None,
            'room': None,
            'processing_blocked': False,
            'closed': False
        }

    def test_proxy_get_values_through_proxy(self, appstate):
        ws_id_mock = Mock(name='ws_id_mock')
        ws_mock = Mock(name='ws_mock')
        appstate.websockets[ws_id_mock] = {
            'ws': ws_mock,
            'message_types': ['authenticate', 'close'],
            'identity_nym': 'some_beautiful_person',
            'room': None,
            'processing_blocked': False,
            'closed': False
        }
        assert appstate.msg_types[ws_id_mock] == ['authenticate', 'close']
        assert appstate.conn[ws_id_mock] == ws_mock
        assert appstate.identities[ws_id_mock] == 'some_beautiful_person'
        assert appstate.closed[ws_id_mock] is False

    def test_proxy_set_values_through_proxy(self, appstate):
        ws_id_mock = Mock(name='ws_id_mock')
        ws_mock = Mock(name='ws_mock')
        appstate.websockets[ws_id_mock] = {
            'ws': ws_mock,
            'message_types': ['authenticate', 'close'],
            'identity_nym': None,
            'room': None,
            'processing_blocked': False,
            'closed': False
        }
        replace_ws_mock = Mock(name='replace_ws_mock')
        appstate.msg_types[ws_id_mock] = ['select_room', 'invalid']
        appstate.conn[ws_id_mock] = replace_ws_mock
        appstate.identities[ws_id_mock] = 'other_person'
        appstate.closed[ws_id_mock] = 'godfather'
        assert appstate.websockets[ws_id_mock]['message_types'] == ['select_room', 'invalid']
        assert appstate.websockets[ws_id_mock]['ws'] == replace_ws_mock
        assert appstate.identities[ws_id_mock] == 'other_person'
        assert appstate.closed[ws_id_mock] == 'godfather'

    def test_store_new_connection_no_accept(self, appstate):
        ws_id_mock = Mock(name='ws_id_mock')
        ws_mock = Mock(name='ws_mock')
        appstate.accept = False

        appstate.store_new_connection(ws_id_mock, ws_mock)
        assert ws_id_mock not in appstate.websockets.keys()

    async def test_close_connection(self, appstate):
        ws_id_mock = Mock(name='ws_id_mock')
        code_mock = Mock(name='code_mock')
        message_mock = Mock(name='message_mock')

        info_mock = MagicMock(name='info_mock')
        room_mock = MagicMock(name='room_mock')
        room_left = info_mock['room']

        appstate.redis_pub = Mock(name='redis_pub_mock')
        appstate.redis_pub.sadd = AsyncMock(name='redis_pub_sadd_mock')
        appstate.websockets[ws_id_mock] = info_mock
        appstate.rooms = room_mock
        stored_ws_mock = info_mock['ws']
        nym_freed = info_mock['identity_nym']
        stored_ws_mock.close = AsyncMock(name='stored_ws_close_mock')
        await appstate.close_connection(ws_id_mock, code=code_mock,
                                        message=message_mock)

        room_mock[room_left].remove.assert_called_with(ws_id_mock)
        room_mock.pop.assert_called_with(room_left)

        appstate.redis_pub.sadd.assert_awaited_with(NYMS_KEY,
                                                    nym_freed.encode(encoding='utf-8'))

        assert ws_id_mock not in appstate.websockets.keys()
        stored_ws_mock.close.assert_awaited_with(code=code_mock, message=message_mock)

    async def test_drop_all_connections(self, appstate):
        ws_ids = [Mock(name=f'i') for i in range(10)]
        for ws_id in ws_ids:
            appstate.websockets[ws_id] = Mock()
        appstate.websockets = MagicMock(name='websockets')
        appstate.close_connection = AsyncMock(name='close_connection_mock')
        appstate.websockets.__iter__.return_value = ws_ids

        await appstate.drop_all_connections()
        for ws_id in ws_ids:
            appstate.close_connection.assert_any_await(ws_id, code=WSCloseCode.GOING_AWAY,
                                                       message='servo_shutdown')


class TestHXApplicationS():

    def test_init(self, app):
        assert len(app.tasks) == 0
        assert app.tasks == []
        assert isinstance(app.state, HXApplicationState)
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
        room_mock = Mock(name=f'room_mock')
        app.state.rooms[room_mock] = set()
        app.state.redis_pub = Mock(name='redis_pub_mock')
        app.state.redis_pub.sadd = AsyncMock(name='redis_pub_sadd_mock')
        app.state.redis_pub.publish_json = AsyncMock(name='redis_pub_publish_json_mock')
        test_data = {}
        for i in range(5):
            ws_id_mock = Mock(name=f'ws_id mock {i}')
            ws_mock = Mock(name=f'ws_mock {i}')
            nym_mock = Mock(name=f'nym_mock {i}')
            ws_mock.close = AsyncMock()
            app.state.websockets[ws_id_mock] = {
                'ws': ws_mock,
                'identity_nym': nym_mock,
                'room': room_mock
            }
            test_data[ws_id_mock] = {
                'ws': ws_mock,
                'identity_nym': nym_mock,
                'room': room_mock
            }
            app.state.rooms[room_mock].add(ws_id_mock)

        num_nyms = len(nyms)

        with patch.object(websockets_server.core.server,
                          'MessageProtoHandler') as protohandler:
            announce_mock = Mock(name='announce_mock')
            protohandler.send_message_layout.return_value = (announce_mock, Mock())

            await app._on_shutdown_handler(Mock())

            app.redis_pub.spop.assert_has_awaits([call(NYMS_KEY, num_nyms)])
            for ws_id_mock in test_data.keys():
                ws_mock = test_data[ws_id_mock]['ws']
                nym_mock = test_data[ws_id_mock]['identity_nym']
                room_mock = test_data[ws_id_mock]['room']

                app.state.redis_pub.sadd.assert_any_await(NYMS_KEY,
                                                          nym_mock.encode(encoding='utf-8'))
                protohandler.send_message_layout.assert_called_with(
                    ANY, room_mock, from_nym='hendrix')
                app.state.redis_pub.publish_json.assert_any_await(ROUNDTRIP_CHANNEL,
                                                                  announce_mock)
                assert room_mock not in app.state.rooms.keys()
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
        app.state = MagicMock(name='state_mock')

        app.state.close_connection = AsyncMock(name='state_mock_close')
        app.state.store_new_connection = Mock(name='state_mock_close')

        await app.handle_ws_connect(ws_id_mock, ws_mock)

        app.state.close_connection.assert_awaited_with(ws_id_mock)
        app.state.store_new_connection.assert_called_with(ws_id_mock, ws_mock)

    async def test_handle_ws_disconnect(self, app):
        ws_id_mock = Mock(name=f'ws_id mock')

        code_mock = Mock(name='code_mock')
        message_mock = Mock(name='message_mock')

        app.state = MagicMock(name='state_mock')
        app.state.close_connection = AsyncMock(name='state_mock_close')

        await app.handle_ws_disconnect(ws_id_mock, code_mock, message_mock)

        app.state.close_connection.assert_awaited_with(ws_id_mock, code=code_mock,
                                                       message=message_mock)

    async def test_process_msg_outbound(self, app):
        app.redis_pub = Mock(name='redis_pub')
        app.redis_pub.publish_json = AsyncMock(name='redis_pub.publish_json')
        app.state = MagicMock(name='app_state_mock')
        ws_id = Mock(name='ws_id_mock')
        ws_id_state = MagicMock(name='ws_id_state_dict_mock')
        app.state[ws_id] = ws_id_state
        msg_mock = Mock(name='msg_mock')
        valid_msg_mock = Mock(name='valid_msg_mock')

        with patch.object(websockets_server.core.server.random, 'choice',
                          return_value='some_random_pub'):
            with patch.object(websockets_server.core.server,
                              'MessageProtoHandler') as protohandler:
                protohandler.validate_raw_input.return_value = valid_msg_mock
                data_out = protohandler.pack_input.return_value
                await app.process_msg_outbound(msg_mock, ws_id)

                app.state.aquire_lock.assert_called_with(ws_id)
                protohandler.validate_raw_input.assert_called_with(msg_mock)
                protohandler.pack_input.assert_called_with(valid_msg_mock, ws_id, **ws_id_state)
        app.redis_pub.publish_json.assert_awaited_with('some_random_pub', data_out)
