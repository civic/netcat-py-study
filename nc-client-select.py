import argparse
import sys
import socket
from contextlib import contextmanager
import fcntl
import os
import selectors
import threading

def main():
    args = parse_args()

    set_stdin_to_non_blocking()


    with connect_to_host(args.host, args.port) as sock:
        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ, stdin_read)
        sel.register(sock, selectors.EVENT_READ, sock_read)

        finished = threading.Event()

        while not finished.is_set():
            try:
                events = sel.select()
                if finished.is_set():
                    break
                for key, mask in events:
                    callback = key.data
                    callback(sock, finished)

            except KeyboardInterrupt:
                break

def stdin_read(sock, finished):
    buff = sys.stdin.buffer.read()
    if buff:
        sock.send(buff)
    else:
        finished.set()

def sock_read(sock, finished):
    from_server = sock.recv(1024)
    if from_server:
        sys.stdout.buffer.write(from_server)
        sys.stdout.flush()
    else:
        finished.set()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)

    return parser.parse_args()

def set_stdin_to_non_blocking():
    fd = sys.stdin.fileno()
    orig_fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

@contextmanager
def connect_to_host(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        yield s


if __name__ == "__main__":
    main()

