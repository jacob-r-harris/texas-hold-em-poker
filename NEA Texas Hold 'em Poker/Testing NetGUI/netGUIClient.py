import socket
import json
import tkinter as tk

HOST = "192.168.0.16"

PORT = 52002

name = input("Name: ")


def GUI():
    def send(event):
        nput = entry.get()

        entry.delete(0, len(nput))

        label["text"] += nput + "\n"

        message(nput)

    root = tk.Tk()

    HEIGHT = 500

    WIDTH = 500

    canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    frame1 = tk.Frame(canvas, bg="black")
    frame1.place(relheight=1, relwidth=1)

    label = tk.Label(frame1, fg="white", bg="black", anchor="nw", justify="left")
    label.place(relheight=1, relwidth=1)

    frame2 = tk.Frame(canvas, bg="white")
    frame2.place(relheight=0.05, relwidth=1, rely=0.95)

    entry = tk.Entry(frame2, bg="white")
    entry.bind("<Return>", send)
    entry.pack(side="left", fill="x", expand=True)

    button = tk.Button(frame2, text="send", command=send)
    button.pack(side="left")

    root.mainloop()


def message(text):
    count = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        if count == 0:
            msg = {"name": name, "msg": "%name%"}

            json_msg = json.dumps(msg)

            s.sendall(str.encode(json_msg))

            count += 1

        while True:
            msg = {"name": name, "msg": text}

            json_msg = json.dumps(msg)

            s.sendall(str.encode(json_msg))

            data = s.recv(1024)

            # out = json.loads(data.decode())

            # print(out["name"]+": "+out["msg"])

            print(data.decode())


def main():
    GUI()


main()
