from aiohttp import WSMsgType
from aiohttp.test_utils import TestClient, TestServer, loop_context
import asyncio
from unittest.mock import patch, ANY
import time
import os
import sys
import json
import re
import pytest
sys.path.append(os.getcwd())
from websockets_server.core.server import HXApplication, nyms
from websockets_server.core.queries import lobby_help
from utils.log_helper import setup_logger

logger = setup_logger(__file__.replace(os.path.sep, '_'))


def log_decorate(method):
    async def decorated():
        result = await method()
        instance = str(method.__self__)
        pat = re.compile('.*at(.*)')
        inst = pat.search(instance).groups()[0]
        logger.debug('[%s][%s] received [%s]', inst,
                     method.__name__, result)
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
                loopext.run_until_complete(routine(client2, client2, app))
            finally:
                loopext.run_until_complete(client1._server.close())
                loopext.run_until_complete(client1.close())
                loopext.run_until_complete(client2.close())


def clients_context_num(routine, num=2, patch_nyms=nyms):
    with patch('websockets_server.core.server.nyms', patch_nyms):
        with loop_context() as loopext:
            app = HXApplication()
            server = TestServer(app)
            clients = []
            for i in range(num):
                client = TestClient(server, loop=loopext)
                if i == 0:
                    loopext.run_until_complete(client.start_server())
                clients.append(client)

            try:
                loopext.run_until_complete(routine(app, *clients))
            finally:
                loopext.run_until_complete(clients[0]._server.close())
                for client in clients:
                    loopext.run_until_complete(client.close())


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

async def test_authenticate_out_of_nyms(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        test_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(test_mes))
            time.sleep(0.2)

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


async def test_close_free_nyms(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    assert len(app.state.websockets.keys()) == 1
    ws_resp2 = await client2.ws_connect("/ws")
    assert len(app.state.websockets.keys()) == 2
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        auth_mes = {'action': f'authenticate', 'token': 'dsfsjksdjfjjxojsdfjskfo0934'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(auth_mes))
            time.sleep(0.2)

        resp1 = await ws_resp1.receive_str()
        error_mes = dict(auth_mes)
        resp2 = await ws_resp2.receive_str()

        error_mes.update(from_nym=None, room=None)
        exp_res = {
            "status": "error",
            "error_reason": "out of available nyms",
            "msg": error_mes
        }
        assert json.loads(resp2) == exp_res

        close_mes = {'action': f'close', 'token': 'dsfsjksdjfjjxojsdfjskfo0934'}
        await ws_resp1.send_str(json.dumps(close_mes))
        resp1 = await ws_resp1.receive_str()
        close_mes.update(from_nym='unique_nym', room=None)
        exp_res = {
            "status": "success",
            "msg": close_mes
        }
        assert json.loads(resp1) == exp_res

        await ws_resp2.send_str(json.dumps(auth_mes))
        resp2 = await ws_resp2.receive_str()

        auth_mes.update(from_nym='unique_nym', room=None)
        exp_res = {
            "status": "success",
            "msg": auth_mes
        }
        assert json.loads(resp2) == exp_res
    finally:
        await ws_resp1.close()
        await ws_resp2.close()


async def test_select_room(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        join_room_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(join_room_mes))
            await conn.receive_str()

        assert 'custom_room' not in app.state.rooms
        join_room_mes = {'action': 'select_room', 'destination_room': 'custom_room'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()
        announce1 = await ws_resp1.receive_str()

        exp_join_announce = {
            'status': 'success',
            'msg': {
                'action': 'send_message',
                'content': ANY,
                'room': 'custom_room',
                'from_nym': 'hendrix',
                'date_created': ANY,
                'seq': -1,
                'token': ANY,
            }
        }
        assert json.loads(announce1) == exp_join_announce
        assert len(app.state.rooms['custom_room']) == 1

        await ws_resp2.send_str(json.dumps(join_room_mes))
        await ws_resp2.receive_str()
        announce2 = await ws_resp2.receive_str()
        announce3 = await ws_resp1.receive_str()

        assert json.loads(announce2) == exp_join_announce
        assert json.loads(announce3) == exp_join_announce

        assert len(app.state.rooms['custom_room']) == 2

        # ==============================
        join_room_mes = {'action': 'select_room', 'destination_room': 'swap_room'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()
        _ = await ws_resp1.receive_str()
        announce_change = await ws_resp2.receive_str()

        exp_join_announce = {
            'status': 'success',
            'msg': {
                'action': 'send_message',
                'content': ANY,
                'room': 'custom_room',
                'from_nym': 'hendrix',
                'date_created': ANY,
                'seq': -1,
                'token': ANY,
            }
        }
        assert json.loads(announce_change) == exp_join_announce
        assert len(app.state.rooms['custom_room']) == 1
        assert len(app.state.rooms['swap_room']) == 1
        # ==============================
        join_room_mes = {'action': 'select_room', 'destination_room': 'custom_room'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()
        announce1 = await ws_resp1.receive_str()
        announce2 = await ws_resp2.receive_str()

        assert len(app.state.rooms['custom_room']) == 2
        assert 'swap_room' not in app.state.rooms
        # ==============================
        close_mes = {'action': f'close', 'token': 'dsfsjksdjfjjxojsdfjskfo0934'}
        await ws_resp1.send_str(json.dumps(close_mes))
        await ws_resp1.receive_str()
        close_announce = await ws_resp2.receive_str()
        exp_close_announce = {
            'status': 'success',
            'msg': {
                'action': 'send_message',
                'content': ANY,
                'room': 'custom_room',
                'from_nym': 'hendrix',
                'date_created': ANY,
                'seq': -1,
                'token': ANY,
            }
        }
        assert json.loads(close_announce) == exp_close_announce
        assert len(app.state.rooms['custom_room']) == 1

        close_mes = {'action': f'close', 'token': 'dsfsjksdjfjjxojsdfjskfo0934'}
        await ws_resp2.send_str(json.dumps(close_mes))
        await ws_resp2.receive_str()

        assert 'custom_room' not in app.state.rooms
    finally:
        await ws_resp1.close()
        await ws_resp2.close()


async def test_select_room_personal_msg(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        join_room_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(join_room_mes))
            await conn.receive_str()

        assert 'custom_room' not in app.state.rooms
        join_room_mes = {'action': 'select_room', 'destination_room': 'Lobby'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()
        announce_or_personal = await ws_resp1.receive_str()
        announce_or_personal = await ws_resp1.receive_str()

        assert len(app.state.rooms['Lobby']) == 1

        await ws_resp2.send_str(json.dumps(join_room_mes))
        await ws_resp2.receive_str()
        announce_or_personal = await ws_resp2.receive_str()
        announce_or_personal = await ws_resp2.receive_str()

        announce3 = await ws_resp1.receive_str()

        assert len(app.state.rooms['Lobby']) == 2

    finally:
        await ws_resp1.close()
        await ws_resp2.close()


async def test_select_room_query_help(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        join_room_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(join_room_mes))
            await conn.receive_str()

        assert 'custom_room' not in app.state.rooms
        join_room_mes = {'action': 'select_room', 'destination_room': 'Lobby'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()
        announce_or_personal = await ws_resp1.receive_str()
        announce_or_personal = await ws_resp1.receive_str()

        assert len(app.state.rooms['Lobby']) == 1

        await ws_resp2.send_str(json.dumps(join_room_mes))
        await ws_resp2.receive_str()
        announce_or_personal = await ws_resp2.receive_str()
        announce_or_personal = await ws_resp2.receive_str()

        announce3 = await ws_resp1.receive_str()

        assert len(app.state.rooms['Lobby']) == 2
        query_msg = {'action': 'query', 'query_name': '/menu', 'parameters': {}}
        await ws_resp1.send_str(json.dumps(query_msg))
        for message in lobby_help.messages:
            query_resp1 = await ws_resp1.receive_str()

            query_resp_exp = {
                'status': 'success',
                'msg': {
                    'action': 'send_message',
                    'content': message,
                    'room': 'Lobby',
                    'from_nym': 'hendrix',
                    'date_created': ANY,
                    'seq': -1,
                    'token': ANY,
                }
            }
            assert json.loads(query_resp1) == query_resp_exp

    finally:
        await ws_resp1.close()
        await ws_resp2.close()



async def test_close_connection_with_room(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        join_room_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(join_room_mes))
            await conn.receive_str()

        assert 'custom_room' not in app.state.rooms
        join_room_mes = {'action': 'select_room', 'destination_room': 'custom_room'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()

        assert len(app.state.rooms['custom_room']) == 1

        await ws_resp2.send_str(json.dumps(join_room_mes))
        await ws_resp2.receive_str()

        assert len(app.state.rooms['custom_room']) == 2

        await ws_resp1.close()
        close_announce = await ws_resp2.receive_str()
        exp_close_announce = {
            'status': 'success',
            'msg': {
                'action': 'send_message',
                'content': ANY,
                'room': 'custom_room',
                'from_nym': 'hendrix',
                'date_created': ANY,
                'seq': -1,
                'token': ANY,
            }
        }
        assert json.loads(close_announce) == exp_close_announce
        assert len(app.state.rooms['custom_room']) == 1

        await ws_resp2.close()

        assert 'custom_room' not in app.state.rooms
    finally:
        await ws_resp1.close()
        await ws_resp2.close()


async def test_exchange_messages(client1, client2, app):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    ws_resp1 = await client1.ws_connect("/ws")
    ws_resp2 = await client2.ws_connect("/ws")
    try:
        ws_resp1.receive_str = log_decorate(ws_resp1.receive_str)
        ws_resp2.receive_str = log_decorate(ws_resp2.receive_str)
        join_room_mes = {'action': f'authenticate'}
        for conn in [ws_resp1, ws_resp2]:
            await conn.send_str(json.dumps(join_room_mes))
            await conn.receive_str()

        assert 'custom_room' not in app.state.rooms
        join_room_mes = {'action': 'select_room', 'destination_room': 'custom_room'}
        await ws_resp1.send_str(json.dumps(join_room_mes))
        await ws_resp1.receive_str()  # join conf
        await ws_resp1.receive_str()  # self join announce

        await ws_resp2.send_str(json.dumps(join_room_mes))
        await ws_resp2.receive_str()  # join conf
        await ws_resp2.receive_str()  # self join announce
        await ws_resp1.receive_str()  # to other join announce

        for conn in [ws_resp1, ws_resp2]:
            for i in range(10):
                test_mes = {'action': f'send_message',
                            'content': f'control {i} relinquish',
                            'room': 'illegally_set_on_client'}
                await conn.send_str(json.dumps(test_mes))
                ws_mes1 = await ws_resp1.receive_str()
                ws_mes2 = await ws_resp2.receive_str()
                exp_msg = dict(test_mes)
                exp_msg.update(from_nym=ANY, room='custom_room',
                               date_created=ANY, seq=ANY)

                exp_res = {
                    'status': 'success',
                    'msg': exp_msg
                }
                assert ws_mes1 == ws_mes2
                assert json.loads(ws_mes1) == exp_res
    finally:
        await ws_resp1.close()
        await ws_resp2.close()


async def test_exchange_messages_multi_clients(app, *clients):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    connections = []
    for client in clients:
        ws_resp = await client.ws_connect("/ws")
        connections.append(ws_resp)
        ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    try:
        auth_mess = {'action': f'authenticate'}
        join_room_mes = {'action': 'select_room', 'destination_room': 'custom_room'}
        for ind in range(len(connections)):
            conn = connections[ind]
            await conn.send_str(json.dumps(auth_mess))
            await conn.receive_str()

            await conn.send_str(json.dumps(join_room_mes))
            await conn.receive_str()
            for prev in range(ind + 1):
                prev_conn = connections[prev]
                announce = await prev_conn.receive_str()
                exp_join_announce = {
                    'status': 'success',
                    'msg': {
                        'action': 'send_message',
                        'content': ANY,
                        'room': 'custom_room',
                        'from_nym': 'hendrix',
                        'date_created': ANY,
                        'seq': -1,
                        'token': ANY,
                    }
                }
                assert json.loads(announce) == exp_join_announce

        for conn in connections:
            others = set(connections)
            others.remove(conn)
            for i in range(2):
                test_mes = {'action': f'send_message',
                            'content': f'control {i} relinquish',
                            'room': 'illegally_set_on_client'}
                await conn.send_str(json.dumps(test_mes))
                ws_mes0 = await conn.receive_str()

                for other in others:
                    ws_mes1 = await other.receive_str()
                    exp_msg = dict(test_mes)
                    exp_msg.update(from_nym=ANY, room='custom_room',
                                   date_created=ANY, seq=ANY)

                    exp_res = {
                        'status': 'success',
                        'msg': exp_msg
                    }
                    assert ws_mes0 == ws_mes1
                    assert json.loads(ws_mes1) == exp_res
        for ind in range(len(connections)):
            conn = connections[ind]
            await conn.close()

            for next in range(ind + 1, len(connections)):
                next_conn = connections[next]
                announce = await next_conn.receive_str()
                exp_join_announce = {
                    'status': 'success',
                    'msg': {
                        'action': 'send_message',
                        'content': ANY,
                        'room': 'custom_room',
                        'from_nym': 'hendrix',
                        'date_created': ANY,
                        'seq': -1,
                        'token': ANY,
                    }
                }
                assert json.loads(announce) == exp_join_announce
    finally:
        for conn in connections:
            await conn.close()


async def test_concurrent_messages_multi_client(app, *clients):
    logger.warning('context: %s', sys._getframe().f_code.co_name)
    connections = []
    for client in clients:
        ws_resp = await client.ws_connect("/ws")
        connections.append(ws_resp)
        ws_resp.receive_str = log_decorate(ws_resp.receive_str)
    try:
        auth_mess = {'action': f'authenticate'}
        join_room_mes = {'action': 'select_room', 'destination_room': 'custom_room'}
        for ind in range(len(connections)):
            conn = connections[ind]
            await conn.send_str(json.dumps(auth_mess))
            await conn.receive_str()

            await conn.send_str(json.dumps(join_room_mes))
            last_join = await conn.receive_str()
            for prev in range(ind + 1):
                prev_conn = connections[prev]
                announce = await prev_conn.receive_str()
        lst_join = json.loads(last_join)
        count = lst_join['msg']['last_message']
        logger.warn("number_of messages - 1 : %s", count)

        test_mes = {'action': f'send_message',
                    'content': f'control 23 relinquish',
                    'room': 'illegally_set_on_client'}

        json_mes = json.dumps(test_mes)

        coros = map(lambda conn: conn.send_str(json_mes), connections)
        res = await asyncio.gather(*coros, return_exceptions=True)

        for conn in connections:
            for i in range(len(connections)):
                await conn.receive_str()

        conn0 = connections[0]
        swap_room = {'action': 'select_room', 'destination_room': 'system_room'}
        for mess in [swap_room, join_room_mes]:
            await conn0.send_str(json.dumps(mess))
            last_join = await conn0.receive_str()
            _ = await conn0.receive_str()

        lst_join = json.loads(last_join)
        count_end = lst_join['msg']['last_message']
        logger.warn("number_of messages - 1 : %s", count_end)
        assert count_end - count == len(clients)

    finally:
        for conn in connections:
            await conn.close()

clients_context(test_authenticate_out_of_nyms, patch_nyms=['unique_nym'])
clients_context(test_close_free_nyms, patch_nyms=['unique_nym'])
clients_context(test_select_room)
clients_context(test_select_room_personal_msg)
clients_context(test_select_room_query_help)
clients_context(test_close_connection_with_room)
clients_context(test_exchange_messages)
clients_context_num(test_exchange_messages_multi_clients, num=4)
clients_context_num(test_concurrent_messages_multi_client, num=18)
