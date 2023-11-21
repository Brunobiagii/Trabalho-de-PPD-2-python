from typing import Any
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random

class Super(DatagramProtocol):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.master = "127.0.0.1", 9999
        self.id = host, port
        self.address = None

    def startProtocol(self):
        self.transport.write("0:ready:".encode("utf-8"), self.master)

    def datagramReceived(self, datagram: bytes, addr: Any):
        

    def send_mensage(self):
        while True:
            self.transport.write(input(">").encode('utf-8'), self.address)

if __name__ == '__main__':
    port = random.randint(1000, 5000)
    reactor.listenUDP(port, Super('127.0.0.1', port))