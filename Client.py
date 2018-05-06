import re
import socket
import shutil
import datetime
from numpy import long
from Packet import *
from FileWriter import *
from Defaults import *
from time import sleep
from threading import *
import time
from pip._vendor.distlib.compat import raw_input
from NetworkFlowAlgorithm import *
import atexit
# Class of thread creation of the client
class Client:
    def __init__(self,  max_sqn, window_manager, id):
        """window_manager is one of the 3 subclasses of the abstract class ReceiverWindowManager"""
        self.max_sqn = max_sqn
        self.window_manager = window_manager
        atexit.register(self.close_sockets)
        self.sockets = []
        self.id = id
    def start_client(self):
        # print ("Starting " + self.name)
        self.clientSide()

    def clientSide(self):
        # Host IP
        host = '127.0.0.1'
        # Port number
        # Pointing to the server's host and port number
        server = ('127.0.0.1', 5000)
        # Creating UDP sockets
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Binding the host with the port numbers
        s.bind((host, 0))
        self.sockets.append(s)
        # Asking for the desired file's name
        filename = 'TestingFile-1984.txt'#raw_input("Filename? -> ")
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
                print("File exists with size: " + str(filesize) + " Bytes")
                # Creating a new file with the same file's name preceded by the word 'new_' for distinguishing
                writer = FileWriter(filename,self.id)
                print()
                print('########################################################')
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                print(st, '--- Beginning of receiving packets #')
                print('########################################################')
                print()
                # Packets received
                ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ack_socket.bind(('', 0))
                delivered_pkts_count = 0
                data_bytes = b''
                while size_client != delivered_pkts_count:
                    # Getting chunks of the file and its address
                    # print('Willl wait for them packets')
                    ClientBData = s.recv(8196)
                    # print('Got them packets')
                    # print(ClientBData.decode('utf-8'))
                    seqn = re.search('seq#(.+?)seq#', str(ClientBData)).group(1)
                    seqn = int(seqn)
                    #ClientBData = ClientBData.decode('utf-8')
                    pkt = Packet(len(ClientBData), seqn, ClientBData, Defaults.PLP, Defaults.P_CORRUPTION,
                                 hashlib.md5())
                    if pkt.isCorrupt():
                        pkt.data += b'Me want a banana!'
                    data_bytes += ClientBData
                    ClientBData = ClientBData.split(b"seq#")[0]
                    # if Defaults.P_CORRUPTION == 1:
                    #     ClientBData += b'Me want a banana!'
                    # data_bytes += ClientBData
                    #ClientBData = ClientBData.encode()
                    # print(ClientBData)
                    # pkt = Packet(len(ClientBData),seqn,ClientBData,Defaults.PLP, Defaults.P_CORRUPTION, hashlib.md5())
                    pkt.update_checksum(ClientBData)
                    print("Received packet with seqn:{}".format(str(seqn)))
                    delivered_pkts = self.window_manager.receive_pkt(pkt) #Marks the pkt as received
                    #send an ack
                    if self.window_manager.should_ack_pkt(pkt):
                        ack_socket.sendto("ACK{}".format(seqn).encode(), addr)
                        print('ACK with sequence#: {}, sent from the client'.format(seqn))
                    else:
                        print("Won't ack sequence#:{}".format(seqn))
                        raise Exception('We just ran into a dead lock because of a big difference between client and '
                                        'server windows')
                    # In the window manager
                    # Write the data in the new file
                    if delivered_pkts:
                        writer.appendPackets(delivered_pkts)
                        delivered_pkts_count += len(delivered_pkts)
                # Closing the file
                writer.write()
                writer.close()
                print()
                print('#####################################################')
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                print(st, '--- Ending of receiving packets #')
                print('#####################################################')
                print()
                print(" ---> New Received file closed. Check contents in your directory.  <--- ")
                print()
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("The hashed checksum is " + str(pkt.return_checksum()))
                print("The regular checksum is ", pkt.checksum1(data_bytes))
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print()
            else:
                raise Exception("File Does Not Exist!")
        # Closing the socket
        s.close()
        self.sockets.remove(s)
    def close_sockets(self):
        if self.sockets:
            for socket in self.sockets:
                socket.close()
                self.sockets.remove(socket)

def fire_up_client(id):
    window = SelectiveRepeatReceiver(Defaults.WINDOW_SIZE,
                                     Defaults.MAX_SEQN) if Defaults.SELECTIVE_REPEAT else GoBkNReceiver(
        Defaults.MAX_SEQN)
    if Defaults.STOP_WAIT:
        window = StopWaitReceiver()
    client = Client(Defaults.MAX_SEQN, window, id)
    client.start_client()

path = 'Clients/'
if os.path.exists(os.path.dirname(path)):
    shutil.rmtree(path) #clear the output folder
for i in range(5):
    t = Thread(target=fire_up_client,args=[i])
    t.start()
    sleep(0.5)
# ti = 0
# for j in range(5):
#     start_time = time.time()
#     for i in range(1):
#         t = Thread(target=fire_up_client,args=[i])
#         t.start()
#         time.sleep(0.5)
#     ti = ti + time.time() - start_time
# print("---  seconds Selective repeate---", ti)