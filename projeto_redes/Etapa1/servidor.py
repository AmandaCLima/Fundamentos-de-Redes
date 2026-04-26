import socket
import os
import random

def server(host = 'localhost', port = 23):

    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_servidor.bind((host, port))

    Limit_Tam_Dados = 1024
    socket_servidor.listen(1)
    while True:

        print('Servidor aguardando conexões...')
        conexao, endereco = socket_servidor.accept()
        print(f'Conexão estabelecida com {endereco}')

        dados = conexao.recv(Limit_Tam_Dados).decode()
        print(f'Dados recebidos: {dados}')
        if dados:
            os.makedirs("Arquivos/Servidor", exist_ok=True)
            caminho_arquivo = os.path.join("Arquivos/Servidor", f"dados_recebidos{random.randint(0, 1000)}.txt")
            with open(caminho_arquivo, 'w') as arquivo:
                arquivo.write(dados)

            
