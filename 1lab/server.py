# -*- coding: utf-8 -*-

import socket
import os
import json


class Server:

    def __init__(self,port,limit=1):

        self.port=port
        self.limit=limit
        self.host='localhost'
        self.sock=socket.socket()
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.limit)

        self.current_d=os.getcwd()
        self.running=True
        self.conn, self.addr = None,None

    def receive(self):
        data = bytearray()
        while True:
            chunk = self.conn.recv(1024)
            if not chunk:
                break
            if b'\0' in chunk:
                data.extend(chunk.split(b'\0')[0])
                break
            data.extend(chunk)
        return data.decode()


    def pwd(self):
        return {'status':'Success','message':os.getcwd()}

    def help(self):
        a='\n help - Show this info \n pwd - Get current directory \n ls - Get file tree without hidden files/folders \n lsi - Get file tree with hidden files/folders \n cd <directory> - Change directory \n exit - Stop server and client \n draw - Draws a file tree'
        return {'status':'Success','message':a}

    def get_file_tree(self,d,hidden=False):
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

    def convert_size(self,size_bytes):
        if size_bytes in (None, 0):
            return "0B"
        units = ["B", "KB", "MB", "GB", "TB"]
        index = 0
        while size_bytes >= 1024 and index < len(units) - 1:
            size_bytes /= 1024
            index += 1
        if index == len(units) - 1 and size_bytes >= 1024:
            size_bytes /= 1024
            return f"{round(size_bytes, 1)}PB"
        return f"{round(size_bytes, 1)}{units[index]}"


    def ls(self):
        tree=self.get_file_tree(self.current_d,False)
        return {'status':'Success','tree':tree}
    def lsi(self):
        tree = self.get_file_tree(self.current_d, True)
        return {'status': 'Success', 'tree': tree}


    def cd(self,d):
        if os.path.isdir(d):
            os.chdir(d)
            self.current_d=os.getcwd()
            return {'status':'Success','message':f'Directory has been successfully changed to {self.current_d}'}
        else:
            return {'status': 'Failure', 'message': 'There is no such directory or you do not have access to it'}

    def exit(self):
        self.running=False
        return {'status': 'Success', 'message': 'Server has been stopped','stop':True}

    def start(self,):
        self.conn, self.addr=self.sock.accept()
        while self.running:
            data=self.receive()
            if not data:
                pass
            else:
                if data=='ls':
                    response=self.ls()
                elif data=='lsi':
                    response=self.lsi()
                elif data=='pwd':
                    response=self.pwd()
                elif data=='help':
                    response=self.help()
                elif data=='exit':
                    response=self.exit()
                elif 'cd ' in data:
                    d=data.replace('cd ','',1)
                    response=self.cd(d)
                self.conn.send((json.dumps(response)+'\0').encode())
        self.conn.close()

server=Server(6666)
server.start()
