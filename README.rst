==============
 redis-ipc-py
==============

A small python module implementing redis-ipc concepts.

|ci| |pylint| |bandit| |cov| |python|

|tag| |license| |style|

redis-ipc is an example of how redis_ can be used as an advanced IPC 
mechanism on an embedded Linux system, for instance as a substitute for the
more common choice of dbus. 

redis-ipc is intended to make communication among different logical components
of a system convenient. It is not intended to replace shared memory for high 
data-rate transfers between processes, where lowest possible overhead is key,
but to provide a convenient and reliable way to implement the following
IPC mechanisms:

* command queues 
* settings 
* status 
* event channels

redis-ipc comes in 2 flavors, a python module (this repo) and a lightweight
C library implementation. See the (original) `redis-ipc C library`_ repo for
a more detailed description.

.. _redis-ipc C library: https://github.com/VCTLabs/redis-ipc


redis_ipc.py
============

A python module implementation of redis-ipc client/server classes.  Requires
`redis-py` and a running `redis` server.  From the repository directory, you
should either add "." to your PYTHON_PATH or copy the python module to
`site-packages`.

To start a local redis server first, run the following *before* you start
the python interpreter::

    $ redis-server --port 0 --pidfile /tmp/redis.pid --unixsocket /tmp/redis-ipc/socket --unixsocketperm 600 &

The above will background the redis server, but you may need to hit
<Enter> once to get the prompt back. Then type `python` in the source
directory in *2 separate terminal windows* and continue below.

For example, to run from the source directory, start a server from the
first terminal::

    >>> import sys
    >>> sys.path.append('.')
    >>> from redis_ipc import RedisServer as rs
    >>> myServer = rs("my_component")
    >>> result = myServer.redis_ipc_receive_command()  # doctest: +SKIP
    >>> myServer.redis_ipc_send_reply(result, result)  # doctest: +SKIP

Then from a second terminal, start a client::

    >>> import sys
    >>> sys.path.append('.')
    >>> from redis_ipc import RedisClient as rc
    >>> myClient = rc("my_component")
    >>> myClient.redis_ipc_send_and_receive("my_component", {}, 30)  # doctest: +SKIP
    {'timestamp': '1627166512.0108066', 'component': 'my_component', 'thread': 'main', 'tid': 24544, 'results_queue': 'queues.results.my_component.main', 'command_id': 'my_component:24544:1627166512.0108066'}


Note that both of the above will block for the timeout period (30 sec in
this example) if they're waiting for the other side to send/reply.

If there is no running redis server, then you will get the following::

    >>> import sys
    >>> sys.path.append('.')
    >>> from redis_ipc import RedisServer as rs
    >>> myServer = rs("my_component")
    >>> result = myServer.redis_ipc_receive_command()  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    redis.exceptions.ConnectionError: Error 2 connecting to unix socket: /tmp/redis-ipc/socket. No such file or directory.

When finished with the above, don't forget to kill the redis server::

    $ cat /tmp/redis.pid | xargs kill


Testing/troubleshooting with redis-ipc
======================================

One of the great features of using redis for system-wide IPC is the ability
to watch the interactions between components using the **monitor** command
from redis-cli utility. Another great use is in unit testing of a single
component, where a test script can push commands, update settings, check
status and so forth. For both reasons it is useful to understand how each
feature is implemented as redis data structures.

@@@TODO

Since redis-ipc requires the redis server to use a unix socket rather than tcp,
remember to specify the socket path when running redis-cli ::

  redis-cli -s /tmp/redis-ipc/socket


.. _redis: http://redis.io/


.. |ci| image:: https://github.com/VCTLabs/redis-ipc/actions/workflows/smoke.yml/badge.svg
    :target: https://github.com/VCTLabs/redis-ipc/actions/workflows/smoke.yml
    :alt: GitHub CI Smoke Test Status

.. |pylint| image:: https://github.com/VCTLabs/redis-ipc/actions/workflows/pylint.yml/badge.svg
    :target: https://github.com/VCTLabs/redis-ipc/actions/workflows/pylint.yml
    :alt: GitHub CI Pylint Status

.. |cov| image:: https://img.shields.io/codecov/c/github/VCTLabs/redis-ipc
    :target: https://codecov.io/gh/VCTLabs/redis-ipc
    :alt: Codecov test coverage

.. |bandit| image:: https://github.com/VCTLabs/redis-ipc/actions/workflows/bandit.yml/badge.svg
    :target: https://github.com/VCTLabs/redis-ipc/actions/workflows/bandit.yml
    :alt: Security check - Bandit

.. |license| image:: https://badges.frapsoft.com/os/gpl/gpl.png?v=103
    :target: https://opensource.org/licenses/GPL-2.0/
    :alt: License

.. |tag| image:: https://img.shields.io/github/v/tag/VCTLabs/redis-ipc?color=green&include_prereleases&label=latest%20release
    :target: https://github.com/VCTLabs/redis-ipc/releases
    :alt: GitHub tag (latest SemVer, including pre-release)

.. |python| image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :target: https://www.python.org/downloads/
    :alt: Python

.. |style| image:: https://img.shields.io/badge/Py%20code%20style-pylint-00000.svg
    :target: https://github.com/pycqa/pylint/
    :alt: Python Style
