from multiprocessing import Process

import redis_ipc

from redis_ipc import RedisServer as rs
from redis_ipc import RedisClient as rc

import pytest


# common data
components = ['printer']
channels = ['main', 'debug']


def echo_msg():
    """ Simple message bus listener to echo the result msg  """

    listener = rs(component=components[0])
    result = listener.redis_ipc_receive_command()
    listener.redis_ipc_send_reply(result, result)


def test_ipc_send_receive():
    """ Test message bus using pytest and multiprocessing """

    # Start "server" process
    proc = Process(target=echo_msg)
    proc.start()

    # Create client
    client = rc(components[0])

    # Test
    res = client.redis_ipc_send_and_receive(components[0], {}, 1)

    assert isinstance(res, dict)
    assert res["component"] == components[0]
    assert res["thread"] == channels[0]
    proc.terminate()

    printer1_dbg = rc(components[0], channels[1])

    with pytest.raises(redis_ipc.RedisIpcExc) as excinfo:
        res_dbg = printer1_dbg.redis_ipc_send_and_receive(components[0], {}, 1)
    assert "redis message request timed out" in str(excinfo.value)
