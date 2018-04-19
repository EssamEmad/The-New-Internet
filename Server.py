import threading
import socket

import os


class Server(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        # Get lock to synchronize threads
        lock = threading.Lock()
        lock.acquire()
        self.serverSide()
        # Free lock to release next thread
        lock.release()


    def run_server(self, data, addr, sock):
        filename, addr = data, addr
        filename = str(filename)
        filename = filename[2:-1]
        if os.path.isfile(filename):
            fileExists = "EXISTS " + str(os.path.getsize(filename))
            sock.sendto(fileExists.encode('utf-8'), addr)
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                sock.sendto(str(bytesToSend).encode('utf-8'), addr)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    sock.sendto(str(bytesToSend).encode('utf-8'), addr)
        else:
            error = "ERROR"
            sock.sendto(error.encode('utf-8'), addr)
            sock.close()


    def serverSide(self):
        host = '127.0.0.1'
        port = 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        print("Server Started.")
        while True:
            # try:
            data, addr = sock.recvfrom(1024)
            # except:
            # print("An existing connection was forcibly closed by the remote host")
            print("client connedted ip:<" + str(addr) + ">")
            self.run_server(data, addr, sock)
            # Thread is created for each incoming connection