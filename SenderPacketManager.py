from abc import ABC, abstractmethod
from threading import Timer
class SenderPacketManager (ABC):


    @abstractmethod
    def __init__(self):
        """send_callback is the callback used to actually transmit the pckt over
        the internet"""
        pass
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

    def __init__(self,window_size, max_sqn, send_callback, timeout = 6):
        # super().__init__(window_size, max_sqn, send_callback)
        self.window_size = window_size
        self.max_sqn = max_sqn
        self.send_callback = send_callback
        self.buffer = [None] * window_size
        self.base_seqn = 0
        self.timeout_length = timeout
        self.timers_dict = {}

    def send_pkt(self,pkt):
        """If the window is not full, we put the pkt in the window and call the
        send callback immediately without checking if a send request has already been made"""
        if self.can_buffer_pkts():
            index = abs(self.base_seqn - pkt.seqn)
            if index < self.window_size:
                self.buffer[index] = pkt
                self.send_callback(pkt)
                self.start_timer_for_pkt(pkt)
                return True
            # else:
                # print('Base seqn:{}, where pkts index:{}'.format(self.base_seqn,pkt.seqn))

        return False

    def can_buffer_pkts(self):
        can_buffer = len(list(filter(lambda x: x is None, self.buffer)))
        # print('Sender can buffer packets: {}, buffer:{}'.format(can_buffer,self.buffer))
        return can_buffer

    def receive_ack(self,pkt):
        index = abs(pkt.seqn - self.base_seqn)
        self.buffer[index] = None
        # stop the timer
        if pkt.seqn in self.timers_dict and self.timers_dict[pkt.seqn]:
            self.timers_dict[pkt.seqn].stop()
            del self.timers_dict[pkt.seqn]
        #re-organize the buffer if there were a continuous stream of ack'd packets
        for i in range(len(self.buffer)):
            if self.buffer[i] != None:
                pkts = self.buffer[0:i]
                del self.buffer[0:i]
                self.buffer.extend([None] * i)
                self.base_seqn += i
                self.base_seqn %= self.max_sqn
                # print('Window manager receiving ack with seqn:{}'.format(pkt.seqn))
                return
    def start_timer_for_pkt(self,pkt):
        print('Starting Timer')
        timer =  Timer(self.timeout_length,self.send_pkt, [pkt])
        timer.start()
        self.timers_dict[pkt.seqn] = timer

class GoBackNWindowManager(SenderPacketManager):

    def __init__(self):
        pass