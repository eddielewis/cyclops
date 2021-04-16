from pssh.clients import ParallelSSHClient

hosts = ["cyclops1.local", "cyclops0.local"]
client = ParallelSSHClient(hosts, user='pi', password='corsairk100')

output = client.run_command(
    "./home/pi/ce301_lewis_edward_f/cyclops/run &")

for host_output in output:
    for line in host_output.stdout:
        print(line)
    exit_code = host_output.exit_code
