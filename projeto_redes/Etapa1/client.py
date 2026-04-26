import socket
import os
import random

def client(host = 'localhost', port = 5000):

    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    endereco_servidor = (host, port)

    while True: 
        with open('/home/mhab/redes/Fundamentos-de-Redes/projeto_redes/Etapa1/Arquivos/Client/ola_mundo.txt', 'rb') as f:
            dados = f.read()
        
        socket_cliente.sendto(dados, endereco_servidor)
        break
    socket_cliente.close()