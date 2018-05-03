class FileWriter:

    def __init__(self, fileName):
        self.file = open('new_' + fileName, 'w')
        self.data = ''
    def appendPackets(self, packets):
        for packet in packets:
            self.data += packet.data.decode('utf-8')
        print('Filewriter packets appended: {}'.format(packets))
    def write(self):
        print('Writing pakckets with length:{}'.format(len(self.data)))
        self.data = self.data.replace("\\r\\n", "")
        self.data = self.data.replace("\n", "")
        self.data = self.data.replace("b'", "")
        self.data = self.data.replace('b"', "")
        self.file.write(self.data)
    def close(self):
        self.file.close()