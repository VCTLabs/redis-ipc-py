# Copyright (c) 2011-2021 Vanguard Computer Technology Labs <answers@vctlabs.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""
This is a Python module to provide 'thin' client/server classes implementing
a light-weight IPC mechanism using JSON formatting and the Redis server as
'message bus'.
"""

import json
import os
import tempfile
import time
from importlib.metadata import version
from pathlib import Path

import redis
from redis import ConnectionPool, StrictRedis

# instead of global pdb import, add this where you want to start debugger:
# import pdb; pdb.set_trace()


__version__ = version('redis_ipc')


# exceptions
class RedisIpcExc(Exception):
    """
    Generic redis-ipc error, used with one of the exception definitions
    defined below.
    """


NoRedis = RedisIpcExc('redis server not available')
NotDict = RedisIpcExc('redis message was not a Python dictionary')
BadMessage = RedisIpcExc('redis message not a recognizable message')
MsgTimeout = RedisIpcExc('redis message request timed out')


# module-level functions and variables
def is_jsonable(obj):
    """
    Test if an object can be dumped as JSON.

    :param obj: object to test
    :return: True if dumpable else False
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def is_unjsonable(obj):
    """
    Test if an object can be loaded as JSON.

    :param obj: object to test
    :return: True if loadable else False
    """
    try:
        json.loads(obj)
        return True
    except (TypeError, ValueError):
        return False


def pdic2jdic(pdic):
    """
    Covert an object to JSON.

    :param pdic: a dictionary
    :return: a JSON string
    """
    if not (is_jsonable(pdic) and isinstance(pdic, dict)):
        raise BadMessage
    return json.dumps(pdic)


def jdic2pdic(jstr):
    """
    Convert JSON to a dictionary, list, etc.

    :param jstr: a JSON string
    :return: an object
    """
    if not is_unjsonable(jstr):
        raise NotDict
    return json.loads(jstr)


# default socket path or address should only be used in a trusted/isolated
# environment
def get_runtimepath():
    """
    Get the runtime socket path.

    :return: socket path string
    """
    temp_dir = tempfile.gettempdir()
    run_dir = os.getenv('RIPC_RUNTIME_DIR', temp_dir)
    return os.path.join(run_dir, 'redis-ipc', 'socket')


def get_serveraddr():
    """
    Get the redis server address if defined in ENV (should be either
    a resolvable hostname or ``localhost``).

    :return: address or None
    """
    if os.getenv('RIPC_TEST_ENV'):
        return os.getenv('RIPC_SERVER_ADDR')
    return None


ripc_socket_path = get_runtimepath()
ripc_server_address = get_serveraddr()


def redis_connect(socket_path=ripc_socket_path, server_addr=ripc_server_address):
    """
    Attempt to open a connection to the Redis server, and raise an exception
    if this does not work. Return the connection object if successful.

    :param socket_path: path to redis socket
    :param server_addr: address of redis server
    :return: client object
    :raises: NoRedis
    """

    if not Path(socket_path).is_socket():
        raise_msg = f'Socket path {socket_path} is not a valid socket'
        raise RedisIpcExc(raise_msg)

    try:
        if not server_addr:
            pool = ConnectionPool.from_url(f'unix://{socket_path}')
        else:
            pool = ConnectionPool.from_url(f'redis://{socket_path}')
        client = StrictRedis(connection_pool=pool)

    except redis.exceptions.ConnectionError as exc:
        raise NoRedis from exc
    return client


class RedisClient:
    """
    Provide a friendly component name for calling program (e.g. how it is
    labeled on system architecture diagrams as opposed to exact executable
    name). Allows IPC from multiple threads in a multi-threaded program.

    :param component: name of component
    :param thread: friendly name for specific thread of execution
    """

    def __init__(self, component, thread='main'):
        self.component = component
        self.thread = thread

        # process number of this component (a python program)
        self.process_number = os.getpid()

        # construct name of queue where replies to commands should arrive
        self.results_queue = f'queues.results.{component}.{thread}'

        # initialize redis connection
        self.redis_conn = redis_connect()

    def __generate_msg_id(self):
        # unique id for message
        # component name, process number, timestamp
        timestamp = str(time.time())  # floating timestamp
        msg_id = self.component + ':' + str(self.process_number) + ':' + timestamp
        return msg_id, timestamp

    def redis_ipc_send_and_receive(self, dest, cmd, tmout):
        """
        :param dest: name of the component to handle this command (string)
        :param cmd: the command to send (dictionary)
        :param tmout: timeout for receiving a response (float seconds)
        """
        # add standard fields to the command dictionary
        late_news = self.__generate_msg_id()  # id and timestamp
        cmd['timestamp'] = late_news[1]  # just the timestamp
        cmd['component'] = self.component
        cmd['thread'] = self.thread
        cmd['tid'] = self.process_number
        cmd['results_queue'] = self.results_queue
        cmd['command_id'] = late_news[0]  # the id includes the timestamp

        # calculate name of command queue
        dest_queue = f'queues.commands.{dest}'

        # send off the command message  # still a Python dictionary
        self.__redis_ipc_send_command(dest_queue, cmd)

        # wait on results queue for the answer
        # an exception is raised by the request function if it times out
        response = self.__redis_ipc_receive_reply(cmd, tmout)
        return response

    def __redis_ipc_send_command(self, dest_queue, cmd):
        """
        This routine does not block, it just sends the command to the back
        of the queue.

        :param dest_queue: command queue serviced by destination component
        :param cmd: command known to the receiving component
        """
        # turn command into a JSON dictionary before sending it
        msg = pdic2jdic(cmd)

        # send it via Redis
        self.redis_conn.rpush(dest_queue, msg)  # no waiting

    def __redis_ipc_receive_reply(self, cmd, tmout):
        """
        A proper response is a JSON string (dictionary), turn it back into
        a dictionary. If the request timed out, the response is empty,
        and an exception will be raised. if a non-empty value was received,
        then::

            if it is not the response to the specified command
               try again
            else
               return this result

        :param cmd: command for which we await a reply
        :param tmout: timeout for receiving a response (float seconds)
        """

        # use self.results_queue as name of queue to wait on
        # throw out received messages until reply["command_id"] == cmd["command_id"]
        while True:
            redis_reply = self.redis_conn.blpop(self.results_queue, tmout)
            if redis_reply is None:
                raise MsgTimeout
            decoded_reply = jdic2pdic(redis_reply[1])
            if decoded_reply['command_id'] != cmd['command_id']:
                continue  # skip this message, not our response
            # take it
            return decoded_reply  # good enough


class RedisServer:
    """
    Provide a friendly component name for calling program (e.g. how it is
    labeled on system architecture diagrams as opposed to exact executable
    name).

    :param component: name of component
    """

    def __init__(self, component):
        # global redis_connect
        self.component = component

        # process number of this component (a python program)
        self.process_number = os.getpid()

        # construct name of queue where commands should arrive
        self.command_queue = f'queues.commands.{component}'

        # initialize redis connection
        self.redis_conn = redis_connect()

    def redis_ipc_receive_command(self):
        """
        Blocks for command string to arrive in own command queue.

        :return: dictionary
        """
        # get serialized command message
        redis_reply = self.redis_conn.blpop(self.command_queue)
        decoded_reply = jdic2pdic(redis_reply[1])
        return decoded_reply

    def redis_ipc_send_reply(self, cmd, result):
        """
        This routine does not block, it just sends the reply to the back
        of the queue.

        :param cmd: command that was processed so result is now available
        :return result: the generated result
        """

        # command contains name of reply queue
        dest_queue = cmd['results_queue']

        # tie reply to its command with matching command_id
        result['command_id'] = cmd['command_id']

        # turn result into a JSON string before sending it
        msg = pdic2jdic(result)

        # send it via Redis
        self.redis_conn.rpush(dest_queue, msg)
