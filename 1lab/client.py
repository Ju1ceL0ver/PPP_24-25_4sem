# -*- coding: utf-8 -*-

import socket
import re
import json


class Client:

    def __init__(self, port):
        self.port = port
        self.host = 'localhost'
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.allowed = ['ls', 'pwd', 'exit', 'help', 'lsi', 'stop_server']
        self.running = True
        self.last_command = None

    def rms(self, text):
        return re.sub(r'\s+', ' ', text)

    def input_command(self):
        command = input('-->').strip()
        if command in self.allowed or command.startswith('cd '):
            self.sock.send((command + '\0').encode())
            self.last_command = command
            return True
        if command == 'draw':
            self.sock.send('ls\0'.encode())
            self.last_command = 'draw'
            return True
        else:
            print('Unknown command. Use "help" to see all commands')
            return False

    def receive(self):
        data = bytearray()
        while True:
            chunk = self.sock.recv(1024)
            if not chunk:
                break
            if b'\0' in chunk:
                data.extend(chunk.split(b'\0')[0])
                break
            data.extend(chunk)
        return data.decode()

    def save_file_tree(self, tree):
        with open('file_tree.json', 'w', encoding='utf-8') as f:
            json.dump(tree, f, ensure_ascii=False, indent=4)

    def draw(self, data, prefix=""):
        for key, value in data.items():
            if isinstance(value, dict):
                print(prefix + "├── " + key)
                self.draw(value, prefix + "│   ")
            else:
                print(prefix + "├── " + f"{key} ({value})")

    def handle(self, response):
        response = json.loads(response)
        status = response.get('status', None)
        message = response.get('message', None)
        tree = response.get('tree', None)
        if message is not None:
            print(message)
        if tree:
            self.save_file_tree(tree)
            print('File tree has been saved')
            if self.last_command == 'draw':
                self.draw(tree)
        if response.get('stop', None) is not None:
            self.running = False
            print('Stopping client')

    def start(self):
        print('Working')
        while self.running:
            f = self.input_command()
            if f:
                response = self.receive()
                self.handle(response)


if __name__ == '__main__':
    try:
        client = Client(6666)
        client.start()
    except ConnectionRefusedError:
        print('Server has not been started or refused connection')
