import threading
import json
import os
import re
import socket
import time

from client import Client
from server import Server


def start_server_in_background():
    try:
        server = Server(6666)
        server.start()
    except OSError:
        print('Address already in use')
        os._exit(os.EX_OK)


def main():
    server_thread = threading.Thread(target=start_server_in_background)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)
    client = Client(6666)
    client.start()


if __name__ == "__main__":
    main()
