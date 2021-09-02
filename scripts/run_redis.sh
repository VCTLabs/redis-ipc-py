#! /bin/sh
#
# this runs a local redis-server and accepts start|stop|status args;
# we use this in tox pre/post commands to run tests that require
# a redis server listening on the redis-ipc socket
# note: the default command is status


failures=0
trap 'failures=$((failures+1))' ERR

CMD_ARG=${1:-status}

if [[ "${CMD_ARG}" = "status" ]]; then
    [[ -n $VERBOSE ]]  && echo "pinging redis-server on local socket..."
    redis-cli -s /tmp/redis-ipc/socket ping
fi

if [[ "${CMD_ARG}" = "start" ]]; then
    [[ -n $VERBOSE ]]  && echo "starting redis-server on local socket..."
    mkdir -p /tmp/redis-ipc/
    redis-server --port 0 --pidfile /tmp/redis.pid --unixsocket /tmp/redis-ipc/socket --unixsocketperm 600 &
    sleep 1
    redis-cli -s /tmp/redis-ipc/socket config set save ""
fi

if [[ "${CMD_ARG}" = "stop" ]]; then
    [[ -n $VERBOSE ]]  && echo "killing redis-server on local socket in 1 sec..."
    sleep 1
    cat /tmp/redis.pid | xargs kill
fi

if ((failures == 0)); then
    echo "Success"
else
    echo "Something went wrong"
    exit 1
fi
