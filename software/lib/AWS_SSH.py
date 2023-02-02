from paramiko import SSHClient, AutoAddPolicy
import time

class AWS_SSH:
    def __init__(self, client, host, username, public_key_file_path, timeout=5):
        self.client = client
        self.host = host
        self.username = username
        self.public_key_file_path = public_key_file_path
        self.timeout = timeout

    # This function connects to the AWS host
    def connect(self):
        print("Connecting to \'{}\'...".format(self.host))
        self.client.set_missing_host_key_policy(AutoAddPolicy())  # If the server's hostname is not found in either set of host keys, the missing host key policy is used
        try:
            self.client.connect(self.host, username=self.username, key_filename=self.public_key_file_path, timeout=self.timeout)  # Connects to host with the given username and public key
        except TimeoutError:
            raise Exception("Unable to connect to \'{}\' within the given timeout frame time ({} seconds).".format(self.host, self.timeout))
        print("Connected to \'{}\'".format(self.host))

    # This function connects to the AWS host (Linux OS) AND executes command to the Linux terminal of that host.
    def exec_command(self, command: str):
        print("Sending command to {}: \'{}\'".format(self.host, command))
        stdin, stdout, stderr = self.client.exec_command(command)  # sends command to Linux Terminal in the host
        stdin.close()  # closes input for output to properly function
        return stdout.read()  # returns output command sent to the Terminal
    
    # This function disconnects from the AWS host
    def disconnect(self):
        self.client.close()
        print("Disconnected from \'{}\'".format(self.host))
        
# client.connect('ec2-54-176-150-189.us-west-1.compute.amazonaws.com', username='ubuntu', key_filename="C:\\Users\\ryann\\Downloads\\CMPE195.pem")