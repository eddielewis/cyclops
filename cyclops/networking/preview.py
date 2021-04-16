import time
from pssh.clients import ParallelSSHClient

# PI_HOSTNAMES = ["cyclops0.local", "cyclops1.local"]
PI_HOSTNAMES = ["cyclops0.local"]
USER = "pi"
PASSWORD = "corsairk100"
ENV = "source /home/pi/.virtualenvs/cv/bin/activate &&"
PROJECT_ROOT = "/home/pi/ce301_lewis_edward_f/cyclops"

client = ParallelSSHClient(PI_HOSTNAMES, user=USER, password=PASSWORD)


def send_command(command):
    output = client.run_command(command)
    for host_output in output:
        for line in host_output.stdout:
            print(line)
        exit_code = host_output.exit_code


send_command("cd /home/pi/ce301_lewis_edward_f/cyclops/ && ./receive.py")


# send_command("%s %s/run_server.sh &" % (ENV, PROJECT_ROOT))
# time.sleep(2.0)
# send_command("pkill receive.py")
