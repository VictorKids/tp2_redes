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

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Variaveis globais importantes
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
mapa = []
flag = False

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funções que lidam com cada ação entre roteadores
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def seguir_msg_adiante(text, origin, destin, next):
    try:
        msg = {
            "id": 9999,
            "text": text,
            "origin": origin,
            "destin": destin,
            "next": next
        }
        # gambiarra -> pega ip e porta do próximo roteador no caminho até 'destin' 
        for i in mapa:
            if i.get_enlace()[0] == next:
                h = i.get_enlace()[1]
                p = i.get_enlace()[2]
            s.connect((h, p))
            s.send(json.dumps(msg))
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
        print(str(i.get_enlace()[0]) + " " + str(i.getdist()) + " " + str(i.get_next()) + "\n")
    print("\n")

def repassar_msg(text, destino):
    for i in mapa:
        if i.get_enlace()[0] == destino:
            # caso onde sabe-se a existencia de 'destin'
            print("E" + text + "de" + mapa[0].get_enlace()[0] + "para" + destino + "\n")
            print("\n")
            seguir_msg_adiante(text, mapa[0].get_enlace()[0], destino, i.get_next())
            return
    # caso onde não se sabe da existencia de 'destin'
    print("X" + text + "de" + mapa[0].get_enlace()[0] + "para" + destino + "\n")
    print("\n") 

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Função que lida com o recebimento de msgs
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def receber_msgs_interface(cliente):
    try:
        while True:
            msg = json.loads(cliente.recv(1024).decode('utf-8'))
            if int(msg["id"]) < 7: # 7 pq são ao todo 6 msgs, isso aq é codigo vestigial de outras versões
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
    except:
        return
 
def receber_msgs_roteadores(rot, addr):                                                  ##### NÃO TERMINEI
    try:
        while True:
            msg    = json.loads(rot.recv(1024).decode('utf-8'))
            # conferir se não é um roteador desconhecido, se for, add ele na tabela
            r_name = msg["name"]
            isIn   = False
            for i in mapa:
                if i.get_enlace()[0] == r_name:
                    isIn = True
                    break
            if isIn == False:
                mapa.append(Router(r_name,addr[0], addr[1], 1, r_name)) 

            # msgs do protocolo de vetor de dist.
            if int(msg["id"]) == 11111: # FALTA ISSO AQ!!!!
                pass

            # msgs de encaminhamento de msgs
            elif int(msg["id"]) == 9999:
                # a msg é pra mim
                if msg["destin"] == mapa[0].get_enlace()[0]:
                    print("R" + msg["text"] + "de" + msg["origin"] + "para" + msg["destin"] + "\n")
                    print("\n")
                else:
                    isIn2 = False
                    for i in mapa:
                        # a msg n é pra mim mas conheço o alvo
                        if i.get_enlace[0] == msg["destin"]:
                            print("E" + msg["text"] + "de" + msg["origin"] + "para" +  msg["destin"] + "através de" + i.get_next() + "\n")
                            isIn2 = True
                            seguir_msg_adiante(msg["text"], msg["origin"], msg["destin"], i.get_next())
                            break
                    # a msg não é pra mim e não sei pra quem é
                    if isIn2 == False:
                        print("X" + msg["text"] + "de" + msg["origin"] + "para" +  msg["destin"] + "\n")
                        print("\n")  
    except:
        return

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Main e Loop de recebimento de novas conexões
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
HOST = sys.argv[0]
PORT = int(sys.argv[1])

# o proprio roteador
mapa.append(Router(HOST,"127.0.0.1", PORT, 0, HOST)) 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
# esperando alguém querer se conectar
s.listen()

try:
    client, addr = s.accept()
    # a única thread relativa a interface
    t0 = threading.Thread(target = receber_msgs_interface, args=[client])
    t0.daemon = True
    t0.start()

    # Loop de leitura de mensagens
    while True:
        conn, addr = s.accept()
        # só recebe msgs de roteadores após a interface flipar a flag
        if flag:
            t1 = threading.Thread(target = receber_msgs_roteadores, args=[conn, addr])
            t1.daemon = True
            t1.start()      
except:
    pass   
