import os
import errno
class FileWriter:

    def __init__(self, name, client_id):
        path = 'Clients/{}/'.format(client_id)
        # if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
        self.file = open( '{}/{}'.format(path,name), 'wb')
        self.data = b''
    def appendPackets(self, packets):
        testing_appended_packets = b''
        for packet in packets:
            self.data += packet.data#.decode('utf-8')
            testing_appended_packets += packet.data#packet.data.decode('utf-8')
        # print('Filewriter packets appended: {}'.format(packets))
        # print('Packet after decoding:{}'.format(testing_appended_packets))
    def write(self):
        # print('Writing pakckets with length:{} them packets:\n{}'.format(len(self.data),self.data))
        # self.data = self.data.replace("\\r\\n", "")
        # self.data = self.data.replace("\n", "")
        # self.data = self.data.replace("b'", "")
        # self.data = self.data.replace('b"', "")
        self.file.write(self.data)
    def close(self):
        self.file.close()
