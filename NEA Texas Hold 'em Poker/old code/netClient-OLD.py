import socket
import json


def start(name):
    HOST = "192.168.0.16"
    HOST = "127.0.0.1"

    PORT = 52002

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = {"name": name, "msg": "GetClientID"}
        json_msg = json.dumps(msg)
        s.sendall(str.encode(json_msg))
        data = json.loads(s.recv(1024).decode())

        ID = data["ID"]

        while True:
            if name == "game.server.connection":
                msg = {"ID": ID, "name": name, "msg": input(name + ": "), "recipient": int(input("ID of recipient: "))}

            else:
                msg = {"ID": ID, "name": name, "msg": input(name + ": "), "recipient": None}

            json_msg = json.dumps(msg)

            s.sendall(str.encode(json_msg))

            data = s.recv(1024)

            out = json.loads(data.decode())

            print(out["name"] + ": " + out["msg"])


start(input("Name: "))
