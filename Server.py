import socket
import os
from SenderPacketManager import *
from numpy import long
from Packet import *
from threading import *
import atexit
# Class of thread creation of the server
class Server:
    def __init__(self, max_sqn,window_size):
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.last_child_id = 0 #last generated id of a child UDPSender that handles a client
        #(client id basically)
        self.num_children = 0 #number of clients being serviced at the moment
        self.sockets = []
        atexit.register(self.close_sockets)
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
            new_socket.bind(('', 0))
            self.sockets.append(new_socket)
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
            self.sockets.remove(sock)


    def __server_side__(self):
        # Host IP
        host = '127.0.0.1'
        # Port number
        port = 5000
        # Creating UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Binding the host with the port number
        sock.bind((host, port))
        self.sockets.append(sock)
        print("Server Started.")
        while True:
            # Receiving the file's name
            data, addr = sock.recvfrom(4096)
            # Conforming connection with the client
            print("client connedted ip:<" + str(addr) + ">")
            # Calling the running function for sending the file
            self.run_server(data, addr, sock)
            # Thread is created for each incoming connection

    def close_sockets(self):
        print('close got called sockets: {}'.format(self.sockets))
        for so in self.sockets:
            so.close()
            self.sockets.remove(so)
            print('Removing them sockets')


class UDPSender(Thread):
    #UDPSender is a class that sends a certain file to a certain socket.
    #The class is synchronous and Thread safe. So, it's assumed to be forked off
    #on a different thread.

    def __init__(self,threadID,filename,dest_addr, socket,max_seqn, window_size):
        Thread.__init__(self)
        self.num_pkts = self.num_pkts(filename)
        self.file = open(filename, "rb")
        self.dest = dest_addr
        self.socket = socket
        self.window_manager = GoBackNWindowManager(window_size,max_seqn,self.send_pkt)
        self.max_seqn = max_seqn
        self.threadID = threadID
        self.packet_sending_lock = Semaphore()#Lock used to make send_pkt callback thread safe; as the timer in window
        #manager doesn't guarrentee thread safety (It's actually run on a forked thread)


    def run(self):
        self.__start_transfer__()
    def __start_transfer__(self):
        """Assumes a connection has been oriented, and the client is expecting
        data. Should be run on a different thread"""
        number_of_packets = self.num_pkts
        seqn = 0
        lock = Semaphore()
        ack_listener_thread = Ack_Listener(lock,self.window_manager,self.socket)#Thread(target=UDPSender.receive_ack_listener,  args = (lock,self.window_manager,self.socket))
        ack_listener_thread.start()
        while number_of_packets != 0:
            # Reading the file in the buffer
            byte = self.file.read(4096)
            while True:
                #Wait for acks
                lock.acquire()
                can_buffer = self.window_manager.can_buffer_pkts()
                if can_buffer:
                    lock.release()
                    break
                lock.release()
            # Send it to the client packet by packet
            pkt = Packet(4096,seqn,byte,0,0)
            if not self.window_manager.send_pkt(pkt):
                continue #Keep trying
            # Decrementing number of chunks received
            number_of_packets -= 1
            seqn = (seqn + 1) % self.max_seqn
            print("Packet number:" + str(self.num_pkts - number_of_packets))
            # print("Data sending in process:")
        self.file.close()
        ack_listener_thread.stop() #implicitly closes the socket
        self.window_manager.close_connection()
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
        the data over the new internet
        The function is thread safe"""
        self.packet_sending_lock.acquire()
        print('Sending packet with seqn:{}'.format(pkt.seqn))
        self.socket.sendto(pkt.data, self.dest)
        self.packet_sending_lock.release()


class StoppableThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class Ack_Listener(StoppableThread):

    def __init__(self,lock,window_manager,socket):
        super().__init__()
        self.lock = lock
        self.window_manager = window_manager
        self.socket = socket
    def __receive_ack_listener__(self,lock, window_manager):
        """Listens to acks sent from the client, and updates the window_manager in a thread safe manner by
                using the lock provided. This method is expected to run asynchronously (be dispatched on a thread)"""
        # TODO If we were to remove the new socket for each client, we'd have to do mapping here as this socket would
        # intercept all calls, not only acks
        while not self.stopped():
            bytes = self.socket.recv(4096)
            ack = bytes.decode("utf-8")
            if 'ACK' in ack:
                ack_seqn = int(ack[3:])
                pkt = Packet(8, ack_seqn, ack, 0, 0)
                lock.acquire()
                # print('Receiving ack with seqn:{}'.format(pkt.seqn))
                window_manager.receive_ack(pkt)
                lock.release()
        self.socket.close()

    def run(self):
        self.__receive_ack_listener__(self.lock,self.window_manager)


server = Server(1024, 3)
server.start_server()
