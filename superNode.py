from typing import Any
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random

class Super(DatagramProtocol):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr_ = host, port

        self.master = '127.0.0.1', 9999

        self.superNodes = {}
        self.address = None
        self.id = -1

        self.serverNodeID = -1
        self.serverNodes = {}

    def startProtocol(self):
        print("Pedido de conexão para mestre...")
        self.transport.write("-1:ready:".encode("utf-8"), self.master)

    def datagramReceived(self, datagram: bytes, addr: Any):
        print("mensagem recebida")
        # decodifica a mensagem
        datagram = datagram.decode("utf-8")
        # separa a mensagem em:
        # ID do super nó : comando : argumentos
        splits = datagram.split(":")
        id, command, arg = splits
        id = int(id)
        # verifica o comando
        if id == 0:
            match command:
                case "id":
                    aux = int(arg)
                    print(f"id {aux}({arg}) recebido...")
                    self.id = aux
                    self.serverNodeID = self.id * 100
                    ret = f"{self.id}:ACK:"
                    self.transport.write(ret.encode('utf-8'), addr)
                case "Finalizado":
                    print("cadastro finalizado")
                    ret = f"{self.id}:Roteamento:"
                    self.transport.write(ret.encode('utf-8'), addr)
                case "SuperNode":
                    print("Informação sobre outros super nós recebidas:")
                    aux = arg.split("|")
                    for addn in aux:
                        nodeID, nodeAddr = addn.split(";")
                        nodeID = int(nodeID)
                        self.superNodes[nodeID] = {"addr": nodeAddr}
                    print(self.superNodes)
        else:
            match command:
                case "ready":
                    servId = self.serverNodeID
                    self.serverNodes[servId] = {"addr": addr, "reg": False}
                    self.serverNodeID += 1
                    
                    ret = f"{self.id}:id:{servId}"
                    self.transport.write(ret.encode('utf-8'), addr)

                #case "ACK":
                    




    def send_mensage(self):
        while True:
            self.transport.write(input(">").encode('utf-8'), self.address)

if __name__ == '__main__':
    port = random.randint(1000, 5000)
    reactor.listenUDP(port, Super('127.0.0.1', port))
    reactor.run()