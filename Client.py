import socket
import threading
from numpy import long
from pip._vendor.distlib.compat import raw_input

class Client (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print ("Starting " + self.name)
        # Get lock to synchronize threads
        lock = threading.Lock()
        lock.acquire()
        self.clientSide()
        # Free lock to release next thread
        lock.release()


    def clientSide(self):
        host = '127.0.0.1'
        port = 5001

        server = ('127.0.0.1', 5000)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.bind((host, port))

        filename = raw_input("Filename? -> ")
        if filename != 'q':
            s.sendto(filename.encode(), server)
            data, addr = s.recvfrom(4096)
            data = str(data)
            print(data[2:8])
            if data[2:8] == "EXISTS":
                filesize = long(data[8:-1])
                size_client = int(filesize)
                print("File exists, " + str(filesize) + " Bytes")
                f = open('new_' + filename, 'wb')
                print("Receiving packets will start now if file exists.")
                # print(
                #   "Timeout is 15 seconds so please wait for timeout at the end.")
                d = 0
                while size_client != 0:
                    ClientBData, clientbAddr = s.recvfrom(4096)
                    f.write(ClientBData)
                    d += 1
                    print("Received packet number:" + str(d))
                    size_client = size_client - 1
                    print(size_client)

                f.close()
                print(
                    "New Received file closed. Check contents in your directory.")
            else:
                print("File Does Not Exist!")

        s.close()
