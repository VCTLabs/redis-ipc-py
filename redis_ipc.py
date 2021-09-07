# Copyright (c) 2011-2021 Vanguard Computer Technology Labs <answers@vctlabs.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""
This is a Python module to provide 'thin' client/server classes implementing
a light-weight IPC mechanism using JSON formatting and the Redis server as
'message bus'.
"""

import os
import time
import json
import tempfile

from pathlib import Path

import redis

from redis import ConnectionPool
from redis import StrictRedis


__version__ = "0.0.0.dev0"

# instead of global pdb import, add this where you want to start debugger:
# import pdb; pdb.set_trace()


# exceptions
class RedisIpcExc(Exception):
    pass


NoRedis = RedisIpcExc("redis server not available")
NotDict = RedisIpcExc("redis message was not a Python dictionary")
BadMessage = RedisIpcExc("redis message not a recognizable message")
MsgTimeout = RedisIpcExc("redis message request timed out")


# global functions
# default tmp path is only used in a trusted/isolated environment
def get_runtimepath():
    """
    Get the runtime socket path
    """
    temp_dir = tempfile.gettempdir()
    run_dir = os.getenv("RIPC_RUNTIME_DIR", temp_dir)
    return os.path.join(run_dir, "redis-ipc", "socket")


def is_jsonable(obj):
    """
    Test if obj can be dumped as JSON
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def is_unjsonable(obj):
    """
    Test if obj can be loaded as JSON
    """
    try:
        json.loads(obj)
        return True
    except (TypeError, ValueError):
        return False


def pdic2jdic(pdic):
    """
    pdic    -    a Python dictionary

    returns a JSON string
    """
    if not is_jsonable(pdic):
        raise BadMessage
    return json.dumps(pdic)


def jdic2pdic(jstr):
    """
    jstr    -    a JSON string which is a hash

    returns a Python dictionary
    """
    if not is_unjsonable(jstr):
        raise NotDict
    return json.loads(jstr)


def redis_connect(socket_path=get_runtimepath()):
    """
    attempt to open a connection to the Redis server
    raise an exception if this does not work
    return the connection object if it does work
    """

    if not Path(socket_path).is_socket():
        raise_msg = "Socket path {} is not a valid socket".format(socket_path)
        raise RedisIpcExc(raise_msg)
    try:
        pool = ConnectionPool.from_url("unix://{}".format(socket_path))
        client = StrictRedis(connection_pool=pool)
    except (
        redis.exceptions.ConnectionError,
        redis.ConnectionError,
        ConnectionError,
    ) as exc:
        raise NoRedis from exc
    return client


# the main feature here is a class which will provide the wanted access
class RedisClient:
    """
    component : friendly name for calling program
                (e.g. how it is labeled on system architecture diagrams
                 as opposed to exact executable name)
    thread: friendly name for specific thread of execution,
            allowing IPC from multiple threads in a multi-threaded program
    """

    def __init__(self, component, thread="main"):
        self.component = component
        self.thread = thread

        # process number of this component (a python program)
        self.process_number = os.getpid()

        # construct name of queue where replies to commands should arrive
        self.results_queue = "queues.results.%s.%s" % (component, thread)

        # initialize redis connection
        self.redis_conn = redis_connect()

    def __generate_msg_id(self):
        # unique id for message
        # component name, process number, timestamp
        timestamp = str(time.time())  # floating timestamp
        msg_id = self.component + ":" + str(self.process_number) + ":" + timestamp
        return msg_id, timestamp

    def redis_ipc_send_and_receive(self, dest, cmd, tmout):
        """
        dest     -   name of the component to handle this command (string)
        cmd      -   the command to send (must be a Python dictionary)
        tmout    -   timeout for receiving a response, floating seconds
        """
        # add standard fields to the command dictionary
        late_news = self.__generate_msg_id()  # id and timestamp
        cmd["timestamp"] = late_news[1]  # just the timestamp
        cmd["component"] = self.component
        cmd["thread"] = self.thread
        cmd["tid"] = self.process_number
        cmd["results_queue"] = self.results_queue
        cmd["command_id"] = late_news[0]  # the id includes the timestamp

        # calculate name of command queue
        dest_queue = "queues.commands.%s" % dest

        # send off the command message  # still a Python dictionary
        self.__redis_ipc_send_command(dest_queue, cmd)

        # wait on results queue for the answer
        # an exception is raised by the request function if it times out
        response = self.__redis_ipc_receive_reply(cmd, tmout)
        return response

    def __redis_ipc_send_command(self, dest_queue, cmd):
        """
        arguments are mandatory
        dest_queue -   command queue serviced by destination component
        cmd        -   a command known to the receiving component

        this routine does not block
        it just sends the command to the back of the queue
        """
        # turn command into a JSON dictionary before sending it
        msg = pdic2jdic(cmd)

        # send it via Redis
        self.redis_conn.rpush(dest_queue, msg)  # no waiting

    def __redis_ipc_receive_reply(self, cmd, tmout):
        """
        arguments are mandatory
        cmd           - command for which we await a reply
        tmout         - timeout for receiving a response, floating seconds

        a proper response is a JSON string (dictionary)
        turn it into a Python dictionary

        if the request timed out, the response is empty,
        and an exception will be raised if a non-empty value was received,
        if it is not the response to the specified command
           try again
        else
           return this result

        """

        # use self.results_queue as name of queue to wait on
        # throw out received messages until reply["command_id"] == cmd["command_id"]
        while True:
            redis_reply = self.redis_conn.blpop(self.results_queue, tmout)
            if redis_reply is None:
                raise MsgTimeout
            decoded_reply = jdic2pdic(redis_reply[1])
            if decoded_reply["command_id"] != cmd["command_id"]:
                continue  # skip this message, not our response
            # take it
            return decoded_reply  # good enough


class RedisServer:
    """
    component : friendly name for calling program
                (e.g. how it is labeled on system architecture diagrams
                as opposed to exact executable name)
    """

    def __init__(self, component):
        # global redis_connect
        self.component = component

        # process number of this component (a python program)
        self.process_number = os.getpid()

        # construct name of queue where commands should arrive
        self.command_queue = "queues.commands.%s" % component

        # initialize redis connection
        self.redis_conn = redis_connect()

    def redis_ipc_receive_command(self):
        """
        blocks for command to arrive in own command queue,
        return it as Python dictionary
        """
        # get serialized command message
        redis_reply = self.redis_conn.blpop(self.command_queue)
        decoded_reply = jdic2pdic(redis_reply[1])
        return decoded_reply

    def redis_ipc_send_reply(self, cmd, result):
        """
        arguments are mandatory
        cmd    - command that was processed so result is now available
        result - the generated result

        this routine does not block
        it just sends the reply to the back of the queue
        """

        # command contains name of reply queue
        dest_queue = cmd["results_queue"]

        # tie reply to its command with matching command_id
        result["command_id"] = cmd["command_id"]

        # turn result into a JSON string before sending it
        msg = pdic2jdic(result)

        # send it via Redis
        self.redis_conn.rpush(dest_queue, msg)
