from threading import *
import socket
import os

from numpy import long

# Class of thread creation of the server
class Server:
    def __init__(self, counter, max_sqn,window_size):
        threading.Thread.__init__(self)
        self.counter = counter
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.last_child_id = 0 #last generated id of a child UDPSender that handles a client
        #(client id basically)
        self.num_children = 0 #number of clients being serviced at the moment

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
            # # Get the file's size
            size_server = long(os.path.getsize(filename))
            # Divide the size by the buffer's size
            number_of_packets = int(size_server / 4096)
            # Adding extra 1 for safety
            number_of_packets = number_of_packets + 1
            # Confirming that the file exists at the server
            fileExists = "EXISTS " + str(number_of_packets)
            # Sending the message of confirmation
            sock.sendto(fileExists.encode(), addr)
            self.num_children += 1
            self.last_child_id += 1
            sender = UDPSender(self.last_child_id,str(filename),addr,new_socket,self.max_sqn,self.window_size)
            sender.start()#Starting the thread implicitly starts sending data
            #No need to reference or track the thread, we jus leave the baby fly .. high
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



class UDPSender(Thread):
    #UDPSender is a class that sends a certain file to a certain socket.
    #The class is synchronous and Thread safe. So, it's assumed to be forked off
    #on a different thread.

    def __init__(self,threadID,filename,dest_addr, socket,max_seqn, window_size):
        self.num_pkts = self.num_pkts(filename)
        self.threadID = threadID
        self.file = open(filename, "rb")
        self.dest = dest_addr
        self.socket = socket
        self.window_manager = SelectiveRepeatPacketManager(window_size,max_seqn,send_pkt)
        self.max_seqn = max_seqn


    def __start_transfer__(self):
        """Assumes a connection has been oriented, and the client is expecting
        data. Should be run on a different thread"""
        number_of_packets = self.num_pkts
        seqn = 0
        while number_of_packets != 0:
            # Reading the file in the buffer
            byte = self.file.read(4096)
            while not window_manager.can_buffer_pkts():
                #TODO receive acccckkkkkkss
            # Send it to the client packet by packet
            pkt = Packet(4096,seqn,byte,0,0)
            self.window_manager.send_pkt(pkt)
            # Decrementing number of chunks received
            number_of_packets -= 1
            seqn = (seqn + 1) % self.max_seqn
            print("Packet number:" + str(self.num_pkts - number_of_packets))
            # print("Data sending in process:")
        self.file.close()
        print("Sent from Server - Get function")

    def run(self):
        self.__start_transfer__()
    def num_pkts(self,filename):
        # Get the file's size
        size_server = long(os.path.getsize(filename))
        # Divide the size by the buffer's size
        number_of_packets = int(size_server / 4096)
        # Adding extra 1 for safety
        number_of_packets = number_of_packets + 1
        return number_of_packets

    def send_pkt(self,pkt):
        """Callback for the window manager to prompt the sender to actually transmit
        the data over the new internet"""
        self.socket.sendto(pkt.data, self.dest)
