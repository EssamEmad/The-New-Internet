class FileWriter:

    def __init__(self, fileName):
        self.file = open('new_' + fileName, 'w')
        self.data = ''
    def appendPackets(self, packets):
        for packet in packets:
            self.data += str(packet.data)
        print('Filewriter packets appended: {}'.format(packets))
    def write(self):
        self.file.write(self.data)
    def close(self):
        self.file.close()
