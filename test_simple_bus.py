from enum import Enum
from multiprocessing import Process

import pytest

import redis_ipc

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
components = ['printer']
channels = ['main', 'debug']

# default server/listener is "main"
echo_listener = rs(component=components[0])

# default client using "main"
client = rc(components[0])

# client on "main" using debug channel
printer1_dbg = rc(components[0], channels[1])

msgs_json = [
    "{\"msg\": \"Printer on fire!!\", \"severity\": 10}",
]

msgs_dict = [
    {'msg': 'Printer on fire!!', 'severity': 10},
]

bad_things = [
    ("bad", "stuff"),
"{\"msg\": \"This is tricky\", \"severity\": float('nan')}",
    {'really_bogus': True, 'extra_bogus': [Bogus['FOO'], Bogus['BAZ']]}
]

sock_paths = [
    "/tmp/redis-ipc/socket",
    "/run/redis-ipc/socket",
    "/run/sudo",
]


def test_redis_connect_no_socket():
    """ exception tests for bad socket path """

    with pytest.raises(redis_ipc.RedisIpcExc) as excinfo:
        redis_connection = rconn(sock_paths[1])
    assert "redis server not available" in str(excinfo.value)


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


def echo_msg():
    """ Simple message bus listener to echo the result msg """

    cmd = echo_listener.redis_ipc_receive_command()
    result = cmd  # echo
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
        res_dbg = printer1_dbg.redis_ipc_send_and_receive(components[0], {}, 1)
    assert "redis message request timed out" in str(excinfo.value)

    proc.join()
