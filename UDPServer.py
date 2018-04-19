# import socket
#
# def Main():
#     host = '127.0.0.1'
#     port = 5000
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.bind((host, port))
#
#     print ("Server Started.")
#     while True:
#         data, addr = s.recvfrom(1024)
#         print("message from: " + str(addr))
#         print("from connected user: "+ str(data))
#         data = str(data).upper()
#         print("sending: "+str(data))
#         s.sendto(data.encode('utf-8'), addr)
#     s.close()
#
# if __name__ == '__main__':
#     Main()

import socket
import os



def Main():
    host = '127.0.0.1'
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print ("Server Started.")
    while True:
        filename, addr = s.recvfrom(1024)
        filename = str(filename)
        filename = filename[2:-1]
        # t = "minion"
        # print(t)
        # print(filename[2:-1])
        if os.path.isfile(filename):
            fileExists = "EXISTS " + str(os.path.getsize(filename))
            s.sendto(fileExists.encode('utf-8'), addr)
            userResponse, addr = s.recvfrom(1024)
            userResponse = str(userResponse)
            print(userResponse[2:4])
            if userResponse[2:4] == 'OK':
                with open(filename, 'rb') as f:
                    bytesToSend = f.read(1024)
                    s.sendto(str(bytesToSend).encode('utf-8'), addr)
                    while bytesToSend != "":
                        bytesToSend = f.read(1024)
                        s.sendto(str(bytesToSend).encode('utf-8'), addr)
        else:
            error = "ERROR"
            s.sendto(error.encode('utf-8'), addr)

    s.close()

if __name__ == '__main__':
    Main()