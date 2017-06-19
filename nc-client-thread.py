import argparse
import sys
import socket
import threading
import queue
from contextlib import contextmanager

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


def receiver(sock):
    while True:
        from_server = sock.recv(1024)
        sys.stdout.buffer.write(from_server)
        sys.stdout.flush()


def main():
    args = parse_args()

    with connect_to_host(args.host, args.port) as sock:

        th_r = threading.Thread(target=receiver, args=[sock])
        th_r.setDaemon(True)
        th_r.start()

        try:
            for line in sys.stdin.buffer:
                sock.send(line)
        except KeyboardInterrupt:
            sock.close()



if __name__ == "__main__":
    main()

