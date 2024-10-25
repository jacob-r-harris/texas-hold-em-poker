import socket
import json


HOST = "127.0.0.1"

PORT = 52002

name = input("Name: ")

count = 0


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    if count == 0:
        msg = {"name": name, "msg": "%name%"}

        json_msg = json.dumps(msg)

        s.sendall(str.encode(json_msg))

        count += 1

    while True:
        data = s.recv(1024)

        # out = json.loads(data.decode())

        # print(out["name"]+": "+out["msg"])

        try:
            server_message = json.loads(data.decode())

        except json.decoder.JSONDecodeError:
            print(data.decode())

        if type(server_message) is list:
            temp = ""

            for i in server_message:
                temp = temp + " " + str(i)

            server_message = temp[:]

        if server_message[0] == " ":  # Sometimes a message will be given a space at the beginning which affects the "%" marking
            server_message = server_message[1:]  # This removes the space

        if server_message[0] == "%":  # If a message is marked with a "%" at the beginning it allows the client to respond
            print(server_message[1:])  # Print the message without "%"

            msg = {"name": name, "msg": input(name + ": ")}

            json_msg = json.dumps(msg)

            s.sendall(str.encode(json_msg))

        else:
            print(server_message)

            print("")
