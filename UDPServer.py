
import socket
import os
import threading

import time


def run(data, addr, sock):
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

def Main():
    host = '127.0.0.1'
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print("Server Started.")
    while True:
        #try:
        data, addr = sock.recvfrom(1024)
        #except:
            #print("An existing connection was forcibly closed by the remote host")
        print("client connedted ip:<" + str(addr) + ">")
        # Thread is created for each incoming connection
        t = threading.Thread(target=run, args=(data, addr, sock))
        t.start()
    sock.close()

if __name__ == '__main__':
    Main()