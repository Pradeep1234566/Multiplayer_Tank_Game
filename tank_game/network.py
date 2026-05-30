import socket
import pickle


class Network:

    def __init__(self):

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server = "127.0.0.1"
        self.port = 5555

        self.addr = (
            self.server,
            self.port
        )

        self.player_id = None
        self.player_data = None

        self.connect()

    def connect(self):

        try:

            self.client.connect(
                self.addr
            )

            data = pickle.loads(
                self.client.recv(
                    2048
                )
            )

            self.player_id = (
                data[0]
            )

            self.player_data = (
                data[1]
            )

        except Exception as e:
            print(e)

    def send(
        self,
        data
    ):

        try:

            self.client.send(
                pickle.dumps(data)
            )

            return pickle.loads(
                self.client.recv(
                    2048
                )
            )

        except socket.error as e:
            print(e)