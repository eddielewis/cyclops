from fabric import Connection
from calibration.snap import snap


PASSWORD = "corsairk100"
PIS = ["cyclops0", "cyclops1"]

connections = []

env = "source /home/pi/.virtualenvs/cv/bin/activate &&"
project_root = "/home/pi/ce301_lewis_edward_f/cyclops"


def setup(hostname):
    connection = Connection('pi@%s.local' % hostname,
                            connect_kwargs={
                                "password": PASSWORD,
                            }, inline_ssh_env=True)

    connections.append(connection)
    result = connection.run(
        "nohup /home/pi/ce301_lewis_edward_f/cyclops/run_server.sh")
    print(result)

    # "screen -dmS snap %s python %s/receive_multicast_snap.py &" % (env, project_root))
    # 'screen -d -m "/home/pi/ce301_lewis_edward_f/cyclops/snap.sh; sleep 1"')

    # result = connection.run(
    # "%s dtach `python %s/remote.py`" % (env, project_root))
    # connection.run("tmux new -d -s snap")
    # result = connection.run(
    # "tmux send -t snap %s python %s/receive_multicast_snap.py" % (env, project_root))


# setup("cyclops1")
# snap(connections[0])
for connection in connections:
    #     print("jim")
    snap(connection)

# connection.run('env echo $WORKON_HOME')
# connection.run("cd /home/pi/ce301_lewis_edward_f/cyclops/")

# connection.run(". /usr/local/bin/virtualenvwrapper.sh")
# connection.config.run.env = {
#     "WORKON_HOME": "/home/pi/.virtualenvs",
#     "VIRTUALENVWRAPPER_PYTHON": "/usr/bin/python3",
#     "VIRTUALENVWRAPPER_ENV_BIN_DIR": "bin"
# }

# connection.run("source /usr/local/bin/virtualenvwrapper.sh")
# connection.run("workon cv")

# connection.run("export WORKON_HOME=$HOME/.virtualenvs")
# connection.run("export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3")
# connection.run("export VIRTUALENVWRAPPER_ENV_BIN_DIR=bin")
# connection.run("source /home/pi/.bashrc")
