# -*- coding: utf-8 -*-

import socket
import os
import json
import threading
import struct


class Server:

    def __init__(self, port, limit=5):
        self.port = port
        self.limit = limit
        self.host = 'localhost'
        self.sock = socket.socket()
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.limit)

        self.current_d = os.getcwd()
        self.running = True
        self.clients = []
        self.stop_event = threading.Event()

    def receive(self, client_conn):
        # Receive the length of the command first
        length_data = client_conn.recv(4)
        length = struct.unpack('!I', length_data)[0]
        # Receive the actual command
        data = bytearray()
        while len(data) < length:
            chunk = client_conn.recv(min(1024, length - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        return data.decode()

    def pwd(self):
        return {'status': 'Success', 'message': os.getcwd()}

    def help(self):
        a = '\n help - Show this info \n pwd - Get current directory \n ls - Get file tree without hidden files/folders \n lsi - Get file tree with hidden files/folders \n cd <directory> - Change directory \n exit - Stop client connection \n stop_server - Stop the server and all clients'
        return {'status': 'Success', 'message': a}

    def get_file_tree(self, d, hidden=False):
        def get_size(path):
            try:
                if os.path.isfile(path):
                    return os.path.getsize(path)
                return 0
            except (OSError, AttributeError):
                return 0

        def build_tree(current_d):
            tree = {}
            for item in os.listdir(current_d):
                full_path = os.path.join(current_d, item)
                if not hidden and item.startswith('.'):
                    continue
                if os.path.isdir(full_path):
                    tree[item] = build_tree(full_path)
                else:
                    tree[item] = self.convert_size(get_size(full_path))
            return tree

        return {os.path.basename(d): build_tree(d)}

    def convert_size(self, size_bytes):
        if size_bytes in (None, 0):
            return "0B"
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        index = 0
        while size_bytes >= 1024 and index < len(units) - 1:
            size_bytes /= 1024
            index += 1
        return f"{round(size_bytes, 1)}{units[index]}"

    def ls(self):
        tree = self.get_file_tree(self.current_d, False)
        return {'status': 'Success', 'tree': tree}

    def lsi(self):
        tree = self.get_file_tree(self.current_d, True)
        return {'status': 'Success', 'tree': tree}

    def cd(self, d):
        if os.path.isdir(d):
            os.chdir(d)
            self.current_d = os.getcwd()
            return {'status': 'Success', 'message': f'Directory has been successfully changed to {self.current_d}'}
        else:
            return {'status': 'Failure', 'message': 'There is no such directory or you do not have access to it'}

    def exit(self, client_conn):
        return {'status': 'Success', 'message': 'Client thread has been stopped', 'stop': True}

    def stop_server(self):
        self.running = False
        self.stop_event.set()
        for client_conn in self.clients:
            try:
                client_conn.send(struct.pack('!I', len(json.dumps({'status': 'Success', 'message': 'Server is stopping', 'stop': True}).encode())))
                client_conn.send(json.dumps({'status': 'Success', 'message': 'Server is stopping', 'stop': True}).encode())
            except:
                pass
        return {'status': 'Success', 'message': 'Server has been stopped'}

    def handle_client(self, client_conn, client_addr):
        self.clients.append(client_conn)
        try:
            while not self.stop_event.is_set():
                data = self.receive(client_conn)
                if not data:
                    break
                response = None
                if data == 'ls':
                    response = self.ls()
                elif data == 'lsi':
                    response = self.lsi()
                elif data == 'pwd':
                    response = self.pwd()
                elif data == 'help':
                    response = self.help()
                elif data == 'exit':
                    response = self.exit(client_conn)
                elif data == 'stop_server':
                    response = self.stop_server()
                    os._exit(os.EX_OK)
                elif 'cd ' in data:
                    d = data.replace('cd ', '', 1)
                    response = self.cd(d)
                response_bytes = json.dumps(response).encode()
                client_conn.send(struct.pack('!I', len(response_bytes)))
                client_conn.send(response_bytes)
                if response.get('stop', False):
                    break
        finally:
            self.clients.remove(client_conn)
            client_conn.close()

    def start(self):
        while not self.stop_event.is_set():
            client_conn, client_addr = self.sock.accept()
            client_handler = threading.Thread(
                target=self.handle_client, args=(client_conn, client_addr))
            client_handler.start()
        self.sock.close()


if __name__ == "__main__":
    try:
        server = Server(6666)
        server.start()
    except OSError:
<<<<<<< HEAD
        print('Address already in use !')
=======
        print('!!Address already in use!!!')
>>>>>>> a
