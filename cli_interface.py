import sys
import socket
import json
import time

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        entradas = input().split()
        if (entradas[0] != "0") and (entradas[1] != "0") and (entradas[2] != "S"):
            roteador   = entradas[0]
            porto      = entradas[1]
            comando    = entradas[2]
            if comando == "C":
                param1 = entradas[3]
                param2 = entradas[4]
                param3 = entradas[5]
                id     = 1
            elif comando == "D":
                param1 = entradas[3]
                param2 = entradas[4]
                param3 = ""
                id     = 2
            elif comando == "E":
                param1 = entradas[3] #texto
                param2 = entradas[4]
                param3 = ""
                id     = 6
            else:
                param1 = ""
                param2 = ""
                param3 = ""
                if   comando == "I":
                    id = 3
                elif comando == "F":
                    id = 4
                else:
                    id = 5
            msg = {
                "id": id,
                "comando": comando,
                "param1": param1,
                "param2": param2,
                "param3": param3
            }
#            s.connect((roteador, int(porto)))
            s.sendto(json.dumps(msg).encode('utf-8'), 0, (roteador,int(porto)))

        else:
            time.sleep(int(entradas[4]))

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")