import os

print("Welcome To Poker!")
print("Enter the letters listed below to perform their functions:")
print("(P): Creates a host server")
print("(C): Creates a client to join the game")
print("(A): Creates an ai to join the game")
print("===================================================================\n")

while True:
    comm = input()

    if comm.lower().startswith("p"):
        os.system("main_with_nethost.py")

    elif comm.lower().startswith("c"):
        import netClient

    elif comm.lower().startswith("a"):
        import AI
