class FileWriter:

    def __init__(self, fileName):
        self.file = open('new_' + fileName, 'wb')
        self.data = ''
    def appendPackets(self, packets):
        for packet in packets:
            self.data += packet.data
    def write(self):
        self.file.write(self.data)
    def close(self):
        self.file.close()
