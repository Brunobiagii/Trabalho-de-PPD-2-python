from typing import Any
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random
import argparse

class Server(DatagramProtocol):
    def __init__(self, host, superA, superP, port):
        self.host = host
        self.port = port
        self.addr_ = host, port

        self.superNodes = {}
        self.address = superA, superP
        self.id = -1
        print("Server ligado: ", self.addr_)


    def startProtocol(self):
        print("Pedido de conexão para super nó...")
        self.transport.write("-1:ready:".encode("utf-8"), self.address)

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
        match command:
            # recebe seu id
            case "id":
                aux = int(arg)
                print(f"id {aux}({arg}) recebido...")
                self.id = aux
                
                ret = f"{self.id}:ACK:"
                self.transport.write(ret.encode('utf-8'), addr)
            # inútil?
            case "Finalizado":
                print("cadastro finalizado")
                ret = f"{self.id}:Roteamento:"
                self.transport.write(ret.encode('utf-8'), addr)
            # inútil?
            case "SuperNode":
                print("Informação sobre outros super nós recebidas:")
                aux = arg.split("|")
                for addn in aux:
                    nodeID, nodeAddr = addn.split(";")
                    nodeID = int(nodeID)
                    self.superNodes[nodeID] = {"addr": nodeAddr}
                print(self.superNodes)



    # inútil?
    def send_mensage(self):
        while True:
            self.transport.write(input(">").encode('utf-8'), self.address)

if __name__ == '__main__':
    # argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--SuperNo", help = "IP do super nó")
    parser.add_argument("-sp", "--SuperNoPort", help = "Porta do super nó")
    parser.add_argument("-p", "--Port", help = "Porta que será usada")
    parser.add_argument("-ip", "--Host", help = "IP do host")
    args = parser.parse_args()

    if args.Port:
        port = int(args.Port)
    else:
        port = random.randint(1000, 5000)

    if args.Host:
        host = args.Host
    else:
        host = '127.0.0.1'

    if args.SuperNo:
        ip = args.SuperNo
    else:
        ip = '127.0.0.1'

    if args.SuperNoPort:
        supPort = int(args.SuperNoPort)
    else:
        supPort = 5555

    reactor.listenUDP(port, Server(host, ip, supPort, port))
    reactor.run()