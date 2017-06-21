import argparse
import sys
import socket
import threading
from contextlib import contextmanager
import select

def main():
    args = parse_args()

    with listen(args.host, args.port) as sock:
        disconnected = threading.Event()

        try:
            client_socket, address = sock.accept()

            th_r = threading.Thread(target=receiver, args=(client_socket, disconnected))
            th_r.setDaemon(True)
            th_r.start()

            # client側から先に切断されても標準入力readがblockされたままでexitしない
            # 標準入力になにか書き込めば停止する
            for data in sys.stdin.buffer:
                if data:
                    client_socket.send(data)
                else:
                    break
                if disconnected.is_set():
                    break
        except KeyboardInterrupt:
            pass


        disconnected.set()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)

    return parser.parse_args()

@contextmanager
def listen(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        yield s

def receiver(client_sock, disconnected):
    while True:
        from_client = client_sock.recv(1024)
        if not from_client:
            break

        if disconnected.is_set():
            break

        sys.stdout.buffer.write(from_client)
        sys.stdout.flush()

    disconnected.set()


if __name__ == "__main__":
    main()

