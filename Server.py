import threading
import socket
import os

from numpy import long


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
            size_server = long(os.path.getsize(filename))
            NumS = int(size_server / 4096)
            NumS = NumS + 1
            fileExists = "EXISTS " + str(NumS)
            sock.sendto(fileExists.encode(), addr)
            check = int(NumS)
            GetRunS = open(filename, "rb")
            c = 0
            while check != 0:
                RunS = GetRunS.read(4096)
                sock.sendto(RunS, addr)
                c += 1
                check -= 1
                print("Packet number:" + str(c))
                print("Data sending in process:")
            GetRunS.close()
            print("Sent from Server - Get function")
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
            data, addr = sock.recvfrom(4096)
            print("client connedted ip:<" + str(addr) + ">")
            self.run_server(data, addr, sock)
            # Thread is created for each incoming connection