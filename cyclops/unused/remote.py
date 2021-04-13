from fabric import Connection
from calibration.snap import snap


PASSWORD = "corsairk100"
PI_HOSTNAMES = ["cyclops0", "cyclops1"]

connections = []

env = "source /home/pi/.virtualenvs/cv/bin/activate &&"
project_root = "/home/pi/ce301_lewis_edward_f/cyclops"


def setup(hostname):
    connection = Connection('pi@%s.local' % hostname,
                            connect_kwargs={
                                "password": PASSWORD,
                            }, inline_ssh_env=True)

    connections.append(connection)
    # result = connection.run(
    # "nohup /home/pi/ce301_lewis_edward_f/cyclops/run_server.sh")
    # 'screen -d -m "/home/pi/ce301_lewis_edward_f/cyclops/run_server.sh; sleep 1"'
    # "screen -S jim"
    result = connection.run(
        "dtach -n udp_server `%s/run_server.sh`" % project_root
    )
    print(result)
    # result=connection.run("screen -ls")
    # print(result)


for hostname in PI_HOSTNAMES:
    print(hostname)
    setup(hostname)
