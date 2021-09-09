import os
import time

from enum import Enum
from multiprocessing import Process
from unittest import mock

import pytest

import redis
import redis_ipc

from redis_ipc import get_serveraddr

from redis_ipc import jdic2pdic as fromJson
from redis_ipc import pdic2jdic as toJson
from redis_ipc import redis_connect as rconn
from redis_ipc import RedisServer as rs
from redis_ipc import RedisClient as rc


# bogus things
class Bogus(Enum):
    FOO = 0x00
    BAR = 0x01
    BAZ = 0x02


# common data
components = ['printer', 'turbo-charger']
channels = ['main', 'debug']

# default server/listener using "main" channel
echo_listener = rs(component=components[0])

# default client using "main" channel
client = rc(components[0])

# client using debug channel
client_dbg = rc(components[0], channels[1])

# bogus client using another component
other = rc(components[1])

msgs_json = [
    "{\"msg_body\": \"Printer on fire!!\", \"severity\": 10}",
]

msgs_dict = [
    {'msg_body': 'Printer on fire!!', 'severity': 10},
]

test_msg = {
    'timestamp': '1631125926.771478',
    'component': 'printer',
    'thread': 'main',
    'tid': 21969,
    'results_queue': 'queues.results.printer.main',
    'command_id': 'printer:22386:1631125926.771478',
    'msg_body': 'Printer on fire!!'
}

bad_things = [
    ("bad", "stuff"),
    "{\"msg\": \"This is tricky\", \"severity\": float('nan')}",
    {'really_bogus': True, 'extra_bogus': [Bogus['FOO'], Bogus['BAZ']]},
]

sock_paths = [
    "/tmp/redis-ipc/socket",
    "/run/redis-ipc/socket",
    "/run/sudo",
]

net_env_vars = {
    'RIPC_TEST_ENV': 'true',
    'RIPC_SERVER_ADDR': 'localhost'
}

test_only = {'RIPC_TEST_ENV': 'true'}

addr_only = {'RIPC_SERVER_ADDR': 'localhost'}

def test_get_serveraddr():
    """ monkeypatch env test """
    with mock.patch.dict(os.environ, test_only):
        assert get_serveraddr() is None

    with mock.patch.dict(os.environ, addr_only):
        assert get_serveraddr() is None

    with mock.patch.dict(os.environ, net_env_vars):
        assert get_serveraddr() == "localhost"


def test_redis_connect_no_socket():
    """ exception tests for bad socket path """

    with pytest.raises(redis_ipc.RedisIpcExc) as excinfo:
        redis_connection = rconn(sock_paths[1])
    assert "socket is not a valid socket" in str(excinfo.value)


def test_redis_connect_with_addr():
    """ monkeypatch env vars and test with localhost """
    with mock.patch.dict(os.environ, net_env_vars):
        redis_connection = rconn(sock_paths[0], server_addr=get_serveraddr())
        assert "localhost" in get_serveraddr()

        # this will generate Connection refused error
        with pytest.raises(redis.exceptions.ConnectionError) as excinfo:
            redis_connection.info()
        assert "Error 111 connecting to localhost" in str(excinfo.value)


def test_jdic2pdic_excs():
    """ exception tests for from-JSON function """

    res = fromJson(msgs_json[0])
    assert res == msgs_dict[0]

    with pytest.raises(redis_ipc.RedisIpcExc) as excinfo:
        res = fromJson(bad_things[1])
    assert "redis message was not a Python dictionary" in str(excinfo.value)


def test_pdic2jdic_excs():
    """ exception tests for to-JSON function """

    res = toJson(msgs_dict[0])
    assert res == msgs_json[0]

    with pytest.raises(redis_ipc.RedisIpcExc) as excinfo:
        res = toJson(bad_things[2])
    assert "redis message not a recognizable message" in str(excinfo.value)


def inject_side_msg_and_result(msg):
    """ Generate ID and queue a side message for the client to ignore """

    timestamp = str(time.time())
    pid = str(os.getpid())
    msg_id = components[0] + ":" + pid + ":" + timestamp

    msg["tid"] = pid
    msg["timestamp"] = timestamp
    msg["command_id"] = msg_id

    res_queue = "queues.results.{}.{}".format(components[0], channels[0])
    msg_queue = "queues.commands.{}".format(components[0])

    new_msg = toJson(msg)
    rconn(sock_paths[0]).rpush(msg_queue, new_msg)
    time.sleep(0.01)
    rconn(sock_paths[0]).rpush(res_queue, new_msg)


def echo_msg():
    """
    Simple message bus listener to echo the result msg after injection
    another (different) msg and result.
    """

    inject_side_msg_and_result(test_msg)  # push msg to ignore

    cmd = echo_listener.redis_ipc_receive_command()
    result = cmd  # echo original msg
    echo_listener.redis_ipc_send_reply(cmd, result)


def test_ipc_send_receive():
    """ Test message bus using pytest and multiprocessing """

    # Start "server" process
    proc = Process(target=echo_msg)
    proc.start()

    # Test
    res = client.redis_ipc_send_and_receive(components[0], {}, 1)

    assert isinstance(res, dict)
    assert res["component"] == components[0]
    assert res["thread"] == channels[0]

    with pytest.raises(redis_ipc.RedisIpcExc) as excinfo:
        res_dbg = other.redis_ipc_send_and_receive(components[1], {}, 1)
    assert "redis message request timed out" in str(excinfo.value)

    # cleanup stale msgs
    for component in components[1], components[0]:
        cmd_queue = "queues.commands.{}".format(component)
        rconn(sock_paths[0]).blpop(cmd_queue, 1)

    proc.join()
