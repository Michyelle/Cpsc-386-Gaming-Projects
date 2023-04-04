import socket
from _thread import *
import pickle
from game import Game

# change the server address to your IPv4 Address
server = "192.168.1.222"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# checks if server will work
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# allows only 2 people in the connection
s.listen()
print("Waiting for a connection, Server Started")

connected = set()   # stores IP address of clients
games = {}          # stores game
idCount = 0         # don't override games

def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()

            if gameId in games:         # checks if game still exists
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()
                    elif data != "get":
                        game.play(p, data)

                    reply = game                        #TAKE THIS OUT OR LEAVE IN
                    conn.sendall(pickle.dumps(reply))
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game ", gameId)
    except:
        pass
    idCount -= 1
    conn.close()

# continuously listens for connection
# when connected, will check if you have even/odd amount of players
# even = create a new game
# odd = assign to a game
while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2   # add new game for 2 players
    if idCount % 2 == 1:        # checks
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:
        games[gameId].ready = True
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))