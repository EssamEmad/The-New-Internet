import socket
import os
from SenderPacketManager import *
from numpy import long
from Packet import *
from threading import *
# Class of thread creation of the server
class Server:
    def __init__(self, max_sqn,window_size):
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.last_child_id = 0 #last generated id of a child UDPSender that handles a client
        #(client id basically)
        self.num_children = 0 #number of clients being serviced at the moment

    def start_server(self):
        self.__server_side__()

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
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            new_socket.bind((host, port + 2))
            new_socket.sendto(fileExists.encode(), addr)
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


    def __server_side__(self):
        # Host IP
        host = '127.0.0.1'
        # Port number
        port = 4000
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
        self.file = open(filename, "rb")
        self.dest = dest_addr
        self.socket = socket
        self.window_manager = SelectiveRepeatPacketManager(window_size,max_seqn,self.send_pkt)
        self.max_seqn = max_seqn
        self.threadID = threadID


    def run(self):
        self.__start_transfer__()
    def __start_transfer__(self):
        """Assumes a connection has been oriented, and the client is expecting
        data. Should be run on a different thread"""
        number_of_packets = self.num_pkts
        seqn = 0
        while number_of_packets != 0:
            # Reading the file in the buffer
            byte = self.file.read(4096)
            while not self.window_manager.can_buffer_pkts():
                ack = self.socket.recv(4096)
                if  "Ack" in ack:
                    ack_seqn = ack[3:]
                    pkt = Packet(8,ack_seqn,ack,0,0)
                    self.window_manager.receive_ack(pkt)
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


server = Server(1024, 10)
server.start_server()
