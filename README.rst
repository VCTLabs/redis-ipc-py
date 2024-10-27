====================================
 Python implementation of redis-ipc
====================================

A small python module implementing redis-ipc concepts.

|ci| |pylint| |bandit|

|pre| |cov| |contributors|

|python| |tag| |license| |style|

redis-ipc (the concept) comes in 2 flavors, a python module (this repo)
and a lightweight C library implementation. See the (original)
`redis-ipc C library`_ repo for a more detailed description.

``redis_ipc`` (the Python module) is an example of how redis_ can be used
as an advanced IPC mechanism on an embedded Linux system, for instance
as a substitute for the more common choice of dbus.

``redis_ipc`` is intended to make communication among different logical
components of a system convenient. It is not intended to replace shared
memory for high data-rate transfers between processes, where lowest
possible overhead is key, but to provide a convenient and reliable way
to implement the following IPC mechanisms:

* command queues
* settings
* status
* event channels

.. _redis-ipc C library: https://github.com/VCTLabs/redis-ipc


Quick Start Dev Environment
===========================

As there are not any Pypi packages available yet, you'll need to first
clone this repository and then install locally (see below).

.. note:: All dependencies are optional except ``redis-py``.


Dev Install
-----------

As long as you have git and at least Python 3.6, then the "easy" dev
install is to clone this repository and install `tox`_.

After cloning the repository, you can run the current tests with the
``tox`` command.  It will build a virtual python environment for each
installed version of python with all the python dependencies and run
the tests (including style checkers and test coverage).

::

  $ git clone https://github.com/VCTLabs/redis-ipc-py
  $ cd redis-ipc-py
  $ tox -e py<NN>-<platform>

where <NN> is your local version of python, and <platform> is one of either
``linux`` or ``macos``, eg::

  $ tox -e py38-linux

The above will run the default tox testenv, which includes the following:

* pre_test - install redis_ipc in tox env via ``pip`` and start the redis server
* test - run the simple msg bus send/receive tests with coverage
* post_test - stop the redis server

.. important:: The command above **requires** the installation of the full
  ``redis`` package (or at least ``redis-server``).  See the `Usage Example`_
  below for install instructions; you can still run the other tox commands
  without a full ``redis`` install.

Other tox environment arguments you can pass include:

* ``tox -e build,check`` will build the python packages and run package checks
* ``tox -e style`` will run the ``flake8`` and ``pycodestyle`` (PEP8) style checks
* ``tox -e lint`` will run ``pylint`` (somewhat less permissive than PEP8/flake8 checks)
* ``tox -e black`` will run the ``black`` formatter
* ``tox -e mypy`` will run ``mypy`` type checking


.. _tox: https://github.com/tox-dev/tox


Standards and Coding Style
--------------------------

Black style and both pep8 and flake8 are part of the above test suite.  There are also
some CI pylint and bandit code analysis checks for complexity and security issues
(we try to keep the "cognitive complexity" low when possible).


Usage Example
=============

This repository contains a python module implementation of redis-ipc client/server
classes, and requires ``redis-py`` and a running ``redis`` server for full
functionality. The easiest way to get started is really just "Try it and see..."
so you'll need to install and start a redis server first.

Using your system package manager, install the redis server package for your
platform:

* on Gentoo: ``sudo emerge dev-db/redis dev-python/tox``
* on Ubuntu: ``sudo apt-get install redis-server``
* on CentOS::

    sudo yum install epel-release
    sudo yum update
    sudo yum install redis

On almost everything except Gentoo you should stop the system service
before proceeding::

  sudo systemctl stop redis

If your distro doesn't currently package ``tox``, first complain (consider filing
a "missing package" bug) and then use ``pip`` to install it into your usual python
environment.


Testing With Tox
----------------

Once you have a ``redis-server`` installed, you can simply run the above
``tox`` command to manage the redis server component and run the tests
for your local python version and OS platform, ie::

  $ tox -e py38-cov-macos

The following section illustrates the (approximate) manual test steps run
by the above command.

Developer Mode
--------------

To manually control ``redis-server`` and monitor the traffic on redis, use
a workflow something like this. starting from the project source directory::

  $ ./scripts/run_redis.sh start

Open another terminal window and start the monitor::

  $ redis-cli -s /tmp/redis-ipc/socket monitor

From the first terminal window, run the (alternate) tests target::

  $  tox -e tests

Observe both terminals; the tests should complete successfully with the
test data cleared from redis, so executing the tests several times should
all succeed.  To manually clear all data from redis, simply stop and
start the server::

  $ ./scripts/run_redis.sh stop
  $ ./scripts/run_redis.sh start


Manual Example Steps
--------------------

From the repository directory, you should either add "." to your PYTHON_PATH
or copy the python module to ``site-packages``; for this example you can use
the command shown below.

To start a local redis server first, run the following *before* you start
the python interpreter::

  $ mkdir /tmp/redis-ipc
  $ redis-server --port 0 --pidfile /tmp/redis.pid --unixsocket /tmp/redis-ipc/socket --unixsocketperm 600 &
  $ redis-cli -s /tmp/redis-ipc/socket config set save ""  # disable dump.rdb saving

The above command will use your local temp directory and permissions for the
socket and PID files, and setting the ``port`` to zero disables listening on
any network interfaces.

The above will also background the redis server, but you may need to hit
<Enter> once to get the prompt back. Then type ``python`` in the source
directory in *2 separate terminal windows* and continue below.

For example, to run from the source directory, start a client process from
the first terminal::

    >>> import sys
    >>> sys.path.append('.')
    >>> from redis_ipc import RedisClient as rc
    >>> myClient = rc("my_component")
    >>> myClient.redis_ipc_send_and_receive("my_component", {}, 30)
    {'timestamp': '1627166512.0108066', 'component': 'my_component', 'thread': 'main', 'tid': 24544, 'results_queue': 'queues.results.my_component.main', 'command_id': 'my_component:24544:1627166512.0108066'}

Then from a second terminal, start a server process::

    >>> import sys
    >>> sys.path.append('.')
    >>> from redis_ipc import RedisServer as rs
    >>> myServer = rs("my_component")
    >>> result = myServer.redis_ipc_receive_command()
    >>> myServer.redis_ipc_send_reply(result, result)


Note that client side of the above will block for the timeout period (30 sec in
this example) while waiting for the other side to send/reply, so run the server
commands in less than 30 sec. or increase the timeout value on the client.

If there is no running redis server, then you will get the following::

    >>> import sys
    >>> sys.path.append('.')
    >>> from redis_ipc import RedisServer as rs
    >>> myServer = rs("my_component")
    >>> result = myServer.redis_ipc_receive_command()
    Traceback (most recent call last):
    ...
    redis.exceptions.ConnectionError: Error 2 connecting to unix socket: /tmp/redis-ipc/socket. No such file or directory.

When finished with the above, don't forget to kill the redis server::

    $ cat /tmp/redis.pid | xargs kill


Testing | Troubleshooting
=========================

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


.. |ci| image:: https://github.com/VCTLabs/redis-ipc-py/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/VCTLabs/redis-ipc-py/actions/workflows/ci.yml
    :alt: GitHub CI Smoke Test Status

.. |pylint| image:: https://github.com/VCTLabs/redis-ipc-py/actions/workflows/pylint.yml/badge.svg
    :target: https://github.com/VCTLabs/redis-ipc-py/actions/workflows/pylint.yml
    :alt: GitHub CI Pylint Status

.. |pre| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. |cov| image:: https://raw.githubusercontent.com/VCTLabs/redis-ipc-py/badges/develop/test-coverage.svg
    :target: https://github.com/VCTLabs/redis-ipc-py/
    :alt: Test coverage

.. |bandit| image:: https://github.com/VCTLabs/redis-ipc-py/actions/workflows/bandit.yml/badge.svg
    :target: https://github.com/VCTLabs/redis-ipc-py/actions/workflows/bandit.yml
    :alt: Security check - Bandit

.. |license| image:: https://badges.frapsoft.com/os/gpl/gpl.png?v=103
    :target: https://github.com/VCTLabs/redis-ipc-py/blob/master/COPYING
    :alt: License

.. |tag| image:: https://img.shields.io/github/v/tag/VCTLabs/redis-ipc-py?color=green&include_prereleases&label=latest%20release
    :target: https://github.com/VCTLabs/redis-ipc-py/releases
    :alt: GitHub tag (latest SemVer, including pre-release)

.. |python| image:: https://img.shields.io/badge/python-3.8+-blue.svg
    :target: https://www.python.org/downloads/
    :alt: Python

.. |style| image:: https://img.shields.io/badge/Py%20code%20style-pylint-00000.svg
    :target: https://github.com/pycqa/pylint/
    :alt: Python Style

.. |contributors| image:: https://img.shields.io/github/contributors/VCTLabs/redis-ipc-py
   :target: https://github.com/VCTLabs/redis-ipc-py/
   :alt: Contributors
