import logging
import csv
from lib.AWS_SSH import AWS_SSH
from paramiko import SSHClient, AutoAddPolicy

class Main():
    def main(self):
        ssh_info = {
            "Host": None,
            "Username": None,
            "Public Key Path File": None
        }
        # C:/Users/ryann/Desktop/ssh_key/ssh_key_info.csv
        # D:/ssh_key/ssh_key_info.csv
        # Open .csv file containing AWS host, Linux username, and public key directory
        with open("D:/ssh_key/ssh_key_info.csv", 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                row_type = row[0]
                row_content = row[1]
                if row_type == "host":
                    ssh_info["Host"] = row_content
                if row_type == "username":
                    ssh_info["Username"] = row_content
                if row_type == "public key path directory":
                    ssh_info["Public Key Path File"] = row_content

        print("Host:", ssh_info["Host"])
        print("Username:", ssh_info["Username"])
        print("Public Key Path File:", ssh_info["Public Key Path File"])
        server = AWS_SSH(client=SSHClient(), host=ssh_info["Host"], username=ssh_info["Username"], public_key_file_path=ssh_info["Public Key Path File"])
        server.connect()
        print("Output:", server.exec_command(command="pwd").decode().rstrip("\n"))
        server.disconnect()

if __name__ == "__main__":
    test = Main()
    test.main()