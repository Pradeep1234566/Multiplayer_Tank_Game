import socket
import pickle


class Network:
    SERVER = "127.0.0.1"
    PORT   = 5555

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.player_id   = None
        self.player_data = None
        self._connect()

    def _connect(self):
        self.client.connect((self.SERVER, self.PORT))
        raw = self._recv()
        self.player_id, self.player_data = pickle.loads(raw)
        print(f"[Network] player_id={self.player_id}")

    def send(self, data: dict) -> dict | None:
        try:
            self.client.sendall(pickle.dumps(data))
            raw = self._recv()
            return pickle.loads(raw) if raw else None
        except Exception as e:
            print(f"[Network] error: {e}")
            return None

    def _recv(self, buf=8192) -> bytes:
        data = b""
        while True:
            try:
                chunk = self.client.recv(buf)
                if not chunk:
                    return b""
                data += chunk
                pickle.loads(data)
                return data
            except (pickle.UnpicklingError, EOFError):
                continue
            except Exception:
                return data