import argparse
import sys
import socket
import threading
from contextlib import contextmanager
import select
import queue
def main():
    args = parse_args()

    with connect_to_host(args.host, args.port) as sock:

        disconnected = threading.Event()

        try:
            th_r = threading.Thread(target=receiver, args=(sock,disconnected))
            th_r.setDaemon(True)
            th_r.start()

            # server側から先に切断されても標準入力readがblockされたままでexitしない
            # 標準入力になにか書き込めば停止する
            for buff in sys.stdin.buffer:
                if not buff:
                    disconnected.set()
                    break
                if disconnected.is_set():
                    break

                sock.send(buff)

            print("finish")

        except KeyboardInterrupt:
            pass

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)

    return parser.parse_args()

@contextmanager
def connect_to_host(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        yield s

def receiver(sock,disconnected):
    while True:

        if disconnected.is_set():
            break

        from_server = sock.recv(1024)
        if not from_server:
            break

        sys.stdout.buffer.write(from_server)
        sys.stdout.flush()

    print("disconnect")
    disconnected.set()
    sys.exit()


if __name__ == "__main__":
    main()

