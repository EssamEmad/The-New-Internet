from abc import ABC, abstractmethod

class SenderPacketManager (ABC):


    def __init__(self,window_size, max_sqn, send_callback, timeout = 6):
        """send_callback is the callback used to actually transmit the pckt over
        the internet"""
        self.size = window_size
        self.max_sqn = max_sqn
        self.send_callback = send_callback
        self.buffer = [None] * window_size
        self.base_seqn = 0
        self.timeout_length = timeout
    @abstractmethod
    def send_pkt(self,pkt):
        """Returns whether or not the packet was buffered to be sent"""
        pass

    @abstractmethod
    def can_buffer_pkts(self):
        pass

    @abstractmethod
    def receive_ack(self,pkt):
        """Receive a control packet (NAK or ACK)"""
        pass
class SelectiveRepeatPacketManager(SenderPacketManager):

    def __init__(self,window_size, max_sqn, send_callback):
        super(window_size, max_sqn, send_callback).__init__()
        self.timers_dict = {}
    def send_pkt(self,pkt):
        """If the window is not full, we put the pkt in the window and call the
        send callback immediately without checking if a send request has already been made"""
        if self.can_buffer_pkts():
            index = abs(self.base_seqn - pkt.seqn)
            if index < self.window_size:
                self.buffer[index] = pkt
                self.send_callback(pkt)
                return True
        else:
            return False

    def can_buffer_pkts(self):
        return len(filter(lambda x: x == None, self.buffer))

    def receive_ack(self,pkt):
        index = abs(pkt.seqn - self.base_seqn)
        self.buffer[index] = None
        # stop the timer
        if timers_dict[pkt.seqn]:
            timers_dict[pkt.seqn].stop()
            del timers_dict[pkt.seqn]
        #re-organize the buffer if there were a continuous stream of ack'd packets
        for i in range(len(self.buffer)):
            if self.buffer[i] != None:
                pkts = self.buffer.remove(0:i)
                self.buffer.extend([None] * i)
                self.base_seqn += i
                self.base_seqn %= self.max_sqn
                return
    def start_timer_for_pkt(self,pkt):
        self.timers_dict[pkt.seqn] = Timer(self.timeout_length,self.send_callback, [pkt])
