from typing import Any
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random
import argparse

class Super(DatagramProtocol):
    def __init__(self, master, host, port):
        # Informação de conexão do nó
        self.host = host
        self.port = port
        self.addr_ = host, port 
        # endereço nó mestre
        self.master = master, 9999
        # outros super nós
        self.superNodes = {}
        self.id = -1
        # nós servidores
        self.serverNodeID = -1 # id para criação do nó servidor
        self.serverNodes = {}
        self.serverNodeReg = False # se o nó servidor foi registrado
        self.serverEnd = False # finalização da criação dos nós servidores
        self.extServerNodes = {} # nós servidores dos outros super nós
        print("Super ligado: ", self.addr_)

    # se conecta ao mestre
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
                #recebe seu id
                case "id":
                    aux = int(arg)
                    print(f"id {aux}({arg}) recebido...")
                    self.id = aux
                    self.serverNodeID = self.id * 100
                    ret = f"{self.id}:ACK:"
                    self.transport.write(ret.encode('utf-8'), addr)
                # finalização da adição dos super nós
                case "Finalizado":
                    print("cadastro finalizado")
                    ret = f"{self.id}:Roteamento:"
                    self.transport.write(ret.encode('utf-8'), addr)
                # recebe os outros super nós
                case "SuperNode":
                    print("Informação sobre outros super nós recebidas:")
                    # separa os super nós
                    aux = arg.split("|")
                    for addn in aux:
                        # separa id e o endereço do super nó
                        nodeID, nodeAddr = addn.split(";")
                        nodeID = int(nodeID)
                        # guarda o super nó
                        if nodeID != self.id:
                            nodeAddr = nodeAddr.replace("'", '').replace('(', '').replace(')', '')
                            ip, port = nodeAddr.split(',')
                            port = int(port)
                            nodaddr = ip, port
                            self.superNodes[nodeID] = {"addr": nodaddr}
                    print(self.superNodes)
        else:
            match command:
                # nó servidor quer se conectar
                case "ready":
                    servId = self.serverNodeID
                    self.serverNodes[servId] = {"addr": addr, "reg": False}
                    self.serverNodeID += 1
                    
                    ret = f"{self.id}:id:{servId}"
                    self.transport.write(ret.encode('utf-8'), addr)
                # nó servidor se conectou
                case "ACK":
                    self.serverNodes[id]["reg"] = True
                    self.serverNodeReg = True
                    print(f"server {id} conectado...")
                    ret = f"{self.id}:ServerNode:{id}|{addr}"
                    self.broadCast(self.superNodes, ret)
                # adiciona os outros nós servidores
                case "ServerNode":
                    print("server recebido")
                    nodeID, nodeAddr = arg.split("|")
                    nodeID = int(nodeID)
                    nodeAddr = nodeAddr.replace("'", '').replace('(', '').replace(')', '')
                    ip, port = nodeAddr.split(',')
                    port = int(port)
                    nodaddr = ip, port
                    self.superNodes[nodeID] = {"addr": nodaddr}
                    self.extServerNodes[nodeID] = {"addr": nodeAddr}
                    minID = True
                    # verifica se é necessário terminar a operação
                    if len(self.extServerNodes) == len(self.superNodes) and self.serverNodeReg and not self.serverEnd:
                        print("entrado")
                        # verifica se é o super nó principal (com menor id)
                        for key in self.extServerNodes.keys():
                            if key < self.id * 100:
                                minID = False
                                break
                        
                        if minID:
                            print("broadcast")
                            ret = f"{self.id}:Finalizado:"
                            self.broadCast(self.superNodes, ret)
                            self.serverEnd = True
                
                case "Finalizado":
                    self.serverEnd = True





    # inútil
    def send_mensage(self):
        while True:
            self.transport.write(input(">").encode('utf-8'), self.address)

    # função de broadcast
    def broadCast(self, dests, msg):
        for node in dests.values():
            print(node["addr"])
            self.transport.write(msg.encode('utf-8'), node["addr"])
    

if __name__ == '__main__':
    # argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--Master", help = "IP do nó mestre")
    parser.add_argument("-p", "--Port", help = "Porta que será usada")
    parser.add_argument("-ip", "--Host", help = "IP do host")
    args = parser.parse_args()

    if args.Port:
        port = int(args.Port)
    else:
        port = random.randint(1000, 5000)

    if args.Master:
        master = args.Master
    else:
        master = '127.0.0.1'
    
    if args.Host:
        host = args.Host
    else:
        host = '127.0.0.1'
    
    reactor.listenUDP(port, Super(master, host, port))
    reactor.run()