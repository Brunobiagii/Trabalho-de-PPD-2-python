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
        self.superNodeID = 1
        print("Mestre ligado: ", self.id)

    #Recebe mensagem
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
            # super nó quer se conectar
            case "ready":
                # escolhe um id para o super nó
                id = self.superNodeID
                # guarda as informações do super nó
                self.superNodes[id] = {"addr": addr, "reg": False}
                # avança o id do nó
                self.superNodeID += 1
                # retorna o id para o super nó
                ret = f"0:id:{id}"
                self.transport.write(ret.encode('utf-8'), addr)

            # super nó recebeu seu id
            case "ACK":
                # super nó é registrado
                self.superNodes[id]["reg"] = True
                print(f"super {id} conectado...")
                # caso todos os super nós se registraram o mestre manda um broadcast
                if len(self.superNodes) >= 2:
                    aux = True
                    # verifica se todos os nós estão registrados
                    for node in self.superNodes.values():
                        if not node["reg"]:
                            aux = False
                            break
                    if aux:
                        # broadcast para todos os super nós
                        print(f"Todos os supers conectados...")
                        self.broadCast("0:Finalizado:")

            # retorna os dados de endereço de todos os super nós
            case "Roteamento":
                print(f"Mandando informação de roteamento para o super {id}...")
                # Junta todos os super nós para mandar para o super nó
                super_nodes = "|".join([str(f"{key};{value['addr']}") for key, value in self.superNodes.items()])
                ret = f"0:SuperNode:{super_nodes}"
                self.transport.write(ret.encode('utf-8'), addr)

    #função para broadcast
    def broadCast(self, msg):
        for node in self.superNodes.values():
            print(node["addr"])
            self.transport.write(msg.encode('utf-8'), node["addr"])

if __name__ == '__main__':
    #port = random.randint(1000, 5000)
    reactor.listenUDP(9999, Master('127.0.0.1', 9999))
    reactor.run()