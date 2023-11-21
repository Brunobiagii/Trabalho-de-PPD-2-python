import string
from typing import Any
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random
from dataclasses import dataclass

#classe do nó mestre
class Master(DatagramProtocol):
    def __init__(self, host, port):
        #host e porta do nó
        self.host = host
        self.port = port
        self.id = host, port
        #Super nós conectados
        self.superNodes = {}
        #ID do super nó
        self.superNodeID = 0

    #Recebe mensagem
    def datagramReceived(self, datagram: bytes, addr: Any):
        # decodifica a mensagem
        datagram = datagram.decode("utf-8")
        # separa a mensagem em:
        # ID do super nó : comando : argumentos
        splits = datagram.split(":")
        id, command, arg = splits
        id = int(id)
        # verifica o comando
        match command:
            # super nó quer se conectar
            case "ready":
                # escolhe um id para o super nó
                id = self.superNodeID
                # guarda as informações do super nó
                self.superNodes[id] = {"addr": addr, "reg": False}
                # avança o id do nó
                self.superNodeID += 1
                # retorna uma mensagem para o super nó
                ret = f"id:{id}"
                self.transport.write(ret.encode('utf-8'), addr)

            # super nó recebeu seu id
            case "ACK":
                # super nó é registrado
                self.superNodes[id]["reg"] = True
                # caso todos os super nós se registraram o mestre manda um broadcast
                if len(self.superNodes) >= 5:
                    aux = True
                    for node in self.superNodes.values():
                        if not node["reg"]:
                            aux = False
                            break
                    if aux:
                        self.broadCast("finalizado")

            # retorna os dados de endereço de todos os super nós
            case "Roteamento":
                super_nodes = "|".join(str(x["addr"]) for x in self.superNodes.values())
                self.transport.write(ret.encode('utf-8'), addr)


    def broadCast(self, msg):
        for node in self.superNodes.values():
            self.transport.write(msg.encode('utf-8'), node["addr"])

if __name__ == '__main__':
    port = random.randint(1000, 5000)
    reactor.listenUDP(port, Master('127.0.0.1', port))