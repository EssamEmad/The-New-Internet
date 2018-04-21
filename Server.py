import threading
import socket
import os

from numpy import long

# Class of thread creation of the server
class Server(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        # Creating lock
        lock = threading.Lock()
        # Get lock to synchronize threads
        lock.acquire()
        self.serverSide()
        # Free lock to release next thread
        lock.release()


    def run_server(self, data, addr, sock):
        # Get the filename requested from the client and the address of the client
        filename, addr = data, addr
        filename = str(filename)
        # To Get rid of the 'b' and the 2 single quotes at the beginning and ending i.e. extracting the file name
        filename = filename[2:-1]
        if os.path.isfile(filename):
            # Get the file's size
            size_server = long(os.path.getsize(filename))
            # Divide the size by the buffer's size
            number_of_packets = int(size_server / 4096)
            # Adding extra 1 for safety
            number_of_packets = number_of_packets + 1
            # Confirming that the file exists at the server
            fileExists = "EXISTS " + str(number_of_packets)
            # Sending the message of confirmation
            sock.sendto(fileExists.encode(), addr)
            # Opening the file in binary format
            f = open(filename, "rb")
            # number of chunks
            c = 0
            while number_of_packets != 0:
                # Reading the file in the buffer
                file = f.read(4096)
                # Send it to the client packet by packet
                sock.sendto(file, addr)
                # Incrementing the number of chunks sent
                c += 1
                # Decrementing number of chunks received
                number_of_packets -= 1
                print("Packet number:" + str(c))
                print("Data sending in process:")
            f.close()
            print("Sent from Server - Get function")
        # Outputting an error in case the file isn't found
        else:
            error = "ERROR"
            sock.sendto(error.encode('utf-8'), addr)
            sock.close()


    def serverSide(self):
        # Host IP
        host = '127.0.0.1'
        # Port number
        port = 5000
        # Creating UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Binding the host with the port number
        sock.bind((host, port))
        print("Server Started.")
        while True:
            # Receiving the file's name
            data, addr = sock.recvfrom(4096)
            # Conforming connection with the client
            print("client connedted ip:<" + str(addr) + ">")
            # Calling the running function for sending the file
            self.run_server(data, addr, sock)
            # Thread is created for each incoming connection