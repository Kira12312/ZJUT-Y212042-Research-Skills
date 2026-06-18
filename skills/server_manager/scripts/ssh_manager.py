import paramiko
import sys

HOST = "10.12.54.200"
PORT = 22
USERNAME = "wzq"
PASSWORD = "wzq666888"

command = sys.argv[1]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(
    HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD
)

stdin, stdout, stderr = ssh.exec_command(command)

print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()