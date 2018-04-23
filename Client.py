import socket
import threading
from numpy import long
from pip._vendor.distlib.compat import raw_input

# Class of thread creation of the client
class Client (threading.Thread):
    def __init__(self, threadID, name, counter, max_sqn,plp,pcorruption, window_manager):
        """window_manager is one of the 3 subclasses of the abstract class ReceiverWindowManager"""
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.max_sqn = max_sqn
        self.plp = plp
        self.pcorruption = pcorruption
        self.window_manager = window_manager
    def run(self):
        print ("Starting " + self.name)
        # Creating lock
        lock = threading.Lock()
        # Get lock to synchronize threads
        lock.acquire()
        self.clientSide()
        # Free lock to release next thread
        lock.release()


    def clientSide(self):
        # Host IP
        host = '127.0.0.1'
        # Port number
        port = 5001
        # Pointing to the server's host and port number
        server = ('127.0.0.1', 5000)
        # Creating UDP sockets
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Binding the host with the port numbers
        s.bind((host, port))
        # Asking for the desired file's name
        filename = raw_input("Filename? -> ")
        # Checking if the user isn't requesting quitting
        if filename != 'q':
            # Sending the file's name to the server
            s.sendto(filename.encode(), server)
            # Receive the server's address and confirmation whether the file exists or not
            data, addr = s.recvfrom(4096)
            data = str(data)
            # Extracting the word EXISTs
            if data[2:8] == "EXISTS":
                # Extracting the file's size divided by the buffer's size
                filesize = long(data[8:-1])
                size_client = int(filesize)
                # Outputting the information relieved
                print("File exists, " + str(filesize) + " Bytes")
                # Creating a new file with the same file's name preceded by the word 'new_' for distinguishing
                writer = FileWriter(filename)
                print("Receiving packets will start now if file exists.")
                # Packets received
                seqn = 0
                while size_client != 0:
                    # Getting chunks of the file and its address
                    # TODO Change port/socket receiving from
                    ClientBData, clientbAddr = s.recvfrom(4096)
                    pkt = Packet(len(ClientBData),seqn,ClientBData,self.plp, self.pcorruption)
                    delivered_pkts = self.window_manager.receive_pkt(pkt) #Marks the pkt as received
                    #in the window manager
                    # Write the data in the new file
                    if delivered_pkts:
                        writer.appendPackets(delivered_pkts)
                    # Incrementing numbers of packets recieved
                    seqn = (seqn + 1) % self.max_sqn
                    print("Received packet number:" + str(d))
                    # Decrementing number of packets of the file itself we got before receiving
                    size_client = size_client - 1
                    print(size_client)
                # Closing the file
                writer.write()
                writer.close()
                print("New Received file closed. Check contents in your directory.")
            else:
                print("File Does Not Exist!")
        # Closing the socket
        s.close()
