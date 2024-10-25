import socket
import threading
import json

HOST = "192.168.0.16"

PORT = 52002

messages = []

clients = {}

disconnect_msg = "/disconnect"


def thread_receive(conn, userNo):
    with conn:
        print("Connected by", addr)

        while True:

            json_msg = conn.recv(1024)

            print(json_msg)

            msg = {"msg": ""}

            if json_msg:
                try:
                    msg = json.loads(json_msg)

                except ValueError:
                    print("json decode error")
                    msg["msg"] = "Json Decode Error"

                print(msg)

                clients[str(userNo)] = conn

                print(clients)

            if msg["msg"] == disconnect_msg:
                print(msg["name"], "has disconnected")
                break

            elif msg["msg"] != "%ping%":
                messages.append(msg)

            elif msg:
                # do something if we have some data
                print(msg)
                print(messages)

        conn.close()


def thread_send():
    x = 0

    while True:

        print("test")

        out_msg = {"to": input("to: "), "msg": input("msg: ")}
        j_msg = json.dumps(out_msg["msg"])
        data = j_msg.encode()
        clients[out_msg["to"]].sendall(data)
        x += 1


userNo = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()

        if userNo > 1:
            threading.Thread(target=thread_receive, args=(conn, userNo,)).start()

        else:
            # threads run programs at the same time
            send_thread = threading.Thread(target=thread_send, args=())
            send_thread.start()
            threading.Thread(target=thread_receive, args=(conn, userNo,)).start()
            userNo += 1