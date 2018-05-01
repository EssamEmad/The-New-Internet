class FileWriter:

    def __init__(self, fileName):
        self.file = open('new_' + fileName, 'wb')
        self.data = b''
    def appendPackets(self, packets):
        for packet in packets:
            self.data += packet.data
        print('Filewriter packets appended: {}'.format(packets))
    def write(self):
        print('Writing pakckets with length:{}'.format(len(self.data)))
        self.file.write(self.data)
    def close(self):
        self.file.close()
