import socket
import os
import random

def server(host = 'localhost', port = 5000):

    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_servidor.bind((host, port))

    Limit_Tam_Dados = 1024
    while True:

        print('Servidor aguardando conexões...')
        dados, endereco = socket_servidor.recvfrom(Limit_Tam_Dados)
        print(f'Conexão estabelecida com {endereco}')
        
        print(f'Dados recebidos: {dados.decode()}')
        if dados:
            os.makedirs("Arquivos/Servidor", exist_ok=True)
            caminho_arquivo = os.path.join("Arquivos/Servidor", f"dados_recebidos{random.randint(0, 1000)}")
            with open(caminho_arquivo, 'wb') as arquivo:
                arquivo.write(dados)

            
