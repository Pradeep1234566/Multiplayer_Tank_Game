import socket
import pickle
from _thread import start_new_thread


# ---------------- SERVER ----------------
server = "127.0.0.1"
port = 5555

socket_server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

socket_server.bind(
    (server, port)
)

socket_server.listen(2)

print("Server Started")


# ---------------- PLAYER DATA ----------------
players = [

    {
        "x": 250,
        "y": 450,
        "angle": 0,
        "bullets": []
    },

    {
        "x": 1150,
        "y": 450,
        "angle": 0,
        "bullets": []
    }
]

current_players = 0


# ---------------- CLIENT THREAD ----------------
def threaded_client(
    conn,
    player
):

    global current_players

    try:

        conn.send(
            pickle.dumps(
                (
                    player,
                    players[player]
                )
            )
        )

        while True:

            data = pickle.loads(
                conn.recv(2048)
            )

            players[player] = data

            enemy_player = (
                1 - player
            )

            reply = players[
                enemy_player
            ]

            conn.sendall(
                pickle.dumps(reply)
            )

    except Exception as e:

        print(
            "Connection Lost:",
            e
        )

    finally:

        current_players -= 1
        conn.close()


# ---------------- CONNECTION LOOP ----------------
while True:

    conn, addr = (
        socket_server.accept()
    )

    print(
        "Connected to:",
        addr
    )

    # Only allow 2 players
    if current_players >= 2:

        print(
            "Server Full"
        )

        conn.close()
        continue

    player_id = current_players

    start_new_thread(
        threaded_client,
        (
            conn,
            player_id
        )
    )

    current_players += 1