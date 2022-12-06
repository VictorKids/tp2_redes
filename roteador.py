import sys
import socket
import json
import threading

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Classe que encapsula infos dos roteadores conhecidos
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
class Router:
    def __init__(self, name, ip, port, dist, next):
        self.enlace  = (name, ip, port)
        self.dist    = dist
        self.next    = next

    def get_enlace(self):
        return self.enlace

    def get_dist(self):
        return self.dist

    def get_next(self):
        return self.next

    def set_enlace(self, name, ip, port):
        self.enlace  = (name, ip, port)

    def set_dist(self, valor):
        self.dist = valor

    def set_next(self, next):
        self.next = next

class DistanceVector:

    def __init__(self,routerList):
        self.table = {}
        for router in routerList:
            self.table[router] = (router.next,router.dist)
        self.origin = routerList[0]

    def update(self, other):
        self.table[other.origin] = (other.origin,1)
        for key in other.table.keys():
            if key in self.table.keys():
                if self.table[key][1] > other.table[key][1]+1:
                     self.table[key] = (other.origin,other.table[key][1]+1)
            else:
                self.table[key] = (other.origin,other.table[key][1]+1)

    def toRouterList(self):
        routerList = []
        routerList.append(self.table[self.origin()]) #adiciona primeiro elemento da lista
        del self.table[self.origin]
        for router in self.table.keys():
            routerList.append(router)
        return routerList

    def appendRouter(self,newRouter):
        router = DistanceVector([newRouter])
        self.update(router)
        
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Variaveis globais importantes
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
mapa = []
flag = False

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funções que lidam com cada ação entre roteadores
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def seguir_msg_adiante(text, origin, name, destin, next):
    try:
        msg = {
            "id": 9999,
            "name": name,
            "text": text,
            "origin": origin,
            "destin": destin,
            "next": next
        }
        for i in mapa:
            if i.get_enlace()[0] == next:
                h = i.get_enlace()[1]
                p = i.get_enlace()[2]
            s.sendto(json.dumps(msg).encode(), 0, (h, int(p)))
    except:
        return

def enviar_atualizacao():
    pass

def enviar_msg():
    pass

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funções que lidam com cada comando da interface
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def conectar(ip, port, name):
    mapa.append(Router(name,ip, port, 1, name)) 
    flag = True

def desconectar(ip, port):
    for i in mapa:
        if i.get_enlace()[1] == ip and i.get_enlace()[2] == port:
            mapa.pop(i)
            break

def rodar_alg():
    pass

def finalizar():
    pass

def print_tabela():
    print(str(mapa[0].get_enlace()[0]) + "\n")
    for i in mapa[1:]:
        print(str(i.get_enlace()[0]) + " " + str(i.get_dist()) + " " + str(i.get_next()) + "\n")
    print("\n")

def repassar_msg(text, destino):
    r_atual = mapa[0].get_enlace()[0]
    for i in mapa:
        if i.get_enlace()[0] == destino:
            # caso onde sabe-se a existencia de 'destin'
            print("E" + text + "de" + r_atual + "para" + destino + "\n")
            print("\n")
            seguir_msg_adiante(text, r_atual, r_atual, destino, i.get_next())
            return
    # caso onde não se sabe da existencia de 'destin'
    print("X" + text + "de" + r_atual + "para" + destino + "\n")
    print("\n") 

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Função que lida com o recebimento de msgs
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def receber_msgs_interface(msg):
    ident = msg["comando"]
    if   ident == "C":
        conectar(msg["param1"], msg["param2"], msg["param3"])
    elif ident == "D":
        desconectar(msg["param1"], msg["param2"])
    elif ident == "I":
        rodar_alg()
    elif ident == "F":
        finalizar()
    elif ident == "T":
        print_tabela()
    elif ident == "E":
        repassar_msg(msg["param1"], msg["param2"])

 
def receber_msgs_roteadores(msg, addr):                                                  ##### NÃO TERMINEI
    r_name  = msg["name"]
    r_atual = mapa[0].get_enlace()[0]
    isIn    = False
    for i in mapa:
        if i.get_enlace()[0] == r_name:
            isIn = True
            break
    if isIn == False:
        mapa.append(Router(r_name,addr[0], addr[1], 1, r_name))

    # msgs do protocolo de vetor de dist.
    if int(msg["id"]) == 11111: # FALTA ISSO AQ!!!!
        distVec = DistanceVector(mapa)
        distVec.appendRouter(Router()) # criar roteador de onde vem a mensagem
        mapa = distVec.toRouterList()
    

    # msgs de encaminhamento de msgs
    elif int(msg["id"]) == 9999:
        # a msg é pra mim
        if msg["destin"] == r_atual:
            print("R" + msg["text"] + "de" + msg["origin"] + "para" + msg["destin"] + "\n")
            print("\n")
        else:
            isIn2 = False
            for i in mapa:
                # a msg n é pra mim mas conheço o alvo
                if i.get_enlace()[0] == msg["destin"]:
                    print("E" + msg["text"] + "de" + msg["origin"] + "para" +  msg["destin"] + "através de" + i.get_next() + "\n")
                    isIn2 = True
                    seguir_msg_adiante(msg["text"], msg["origin"], r_atual, msg["destin"], i.get_next())
                    break
            # a msg não é pra mim e não sei pra quem é
            if isIn2 == False:
                print("X" + msg["text"] + "de" + msg["origin"] + "para" +  msg["destin"] + "\n")
                print("\n")  

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Main e Loop de recebimento de novas conexões
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
HOST = sys.argv[1]
PORT = int(sys.argv[2])

mapa.append(Router(HOST,"127.0.0.1", PORT, 0, HOST)) 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

try:
    while True:
        msg, addr = json.loads(s.recvfrom(1024).decode('utf-8'))
        if int(msg["id"]) < 7:
            t0 = threading.Thread(target = receber_msgs_interface, args=[msg])
            t0.daemon = True
            t0.start()
        elif flag:
            t1 = threading.Thread(target = receber_msgs_roteadores, args=[msg, addr])
            t1.daemon = True
            t1.start()      
except:
    pass   
