import socket
import json

HOST = "192.168.0.16"

PORT = 52002

name = input("Name: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        msg = {"name": name, "msg": input(">")}

        json_msg = json.dumps(msg)

        s.sendall(str.encode(json_msg))

        data = s.recv(1024)

        print("Received", str(data.decode()))