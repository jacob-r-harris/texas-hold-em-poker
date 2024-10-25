import socket
import threading
import json

# HOST = "192.168.0.16"
HOST = "127.0.0.1"

PORT = 52002

messages = []

disconnect_msg = "/disconnect"


def thread_receive(conn, id):
    with conn:
        print("Connected by", addr)

        while True:
            json_msg = conn.recv(1024)

            msg = {"msg": ""}

            if json_msg:
                msg = json.loads(json_msg)

            if msg["msg"] == disconnect_msg:
                print(msg["name"], "has disconnected")
                break

            elif msg["recipient"] is not None:
                j_msg = json.dumps(msg)
                data = j_msg.encode()
                list_of_clients[msg["recipient"]].sendall(data)

            elif msg:
                # do something if we have some data
                print(msg)
                print(messages)

        conn.close()


def thread_send(conn, id):
    j_msg = json.dumps(msg)
    data = j_msg.encode()
    list_of_clients[id].sendall(data)


CLIENT_ID = 1
list_of_clients = {}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        req = conn.recv(1024)
        if req:
            msg = json.loads(req)
            if msg["msg"] == "GetClientID":
                response = {"ID": CLIENT_ID, "name": msg["name"]}
                resp_json = json.dumps(response)
                conn.send(resp_json.encode())

        list_of_clients[CLIENT_ID] = conn
        # threads run programs at the same time
        send_thread = threading.Thread(target=thread_send, args=(conn, CLIENT_ID))
        send_thread.start()
        threading.Thread(target=thread_receive, args=(conn, CLIENT_ID)).start()

        CLIENT_ID += 1
