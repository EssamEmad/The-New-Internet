import socket

from numpy import long
from pip._vendor.distlib.compat import raw_input


def Main():
    host = '127.0.0.1'
    port = 5001

    server = ('127.0.0.1', 5000)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.bind((host, port))

    filename = raw_input("Filename? -> ")
    if filename != 'q':
        s.sendto(filename.encode('utf-8'), server)
        data, addr = s.recvfrom(1024)
        data = str(data)
        print(data[2:8])
        if data[2:8] == "EXISTS":
            filesize = long(data[8:-1])
            print("File exists, " + str(filesize) + " Bytes")
            f = open('new_' + filename, 'wb')
            data, addr = s.recvfrom(1024)
            totalRecv = len(data)
            f.write(data)
            print("Total Recieved " + str(totalRecv) + " file size " + str(filesize))
            while totalRecv < filesize:
                data, addr = s.recvfrom(1024)
                totalRecv += len(data)
                f.write(data)
                print("{0:.2f}".format((totalRecv / float(filesize)) * 100) + "% Done")
            print("Download Complete!")
            f.close()
        else:
            print("File Does Not Exist!")

    s.close()


if __name__ == '__main__':
    Main()