import socket
import os

def cliente(host='localhost', port=5000):
    BUFFER_SIZE = 1024
    endereco_servidor = (host, port)
    # Pasta onde estão seus arquivos
    DIRETORIO_CLIENTE = os.path.join("Arquivos", "Client")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Listar arquivos disponíveis 
    arquivos_disponiveis = os.listdir(DIRETORIO_CLIENTE)
    print(f"Arquivos disponíveis em {DIRETORIO_CLIENTE}: {arquivos_disponiveis}")
    
    nome_alvo = input("Digite o nome do arquivo que deseja enviar: ")
    caminho_origem = os.path.join(DIRETORIO_CLIENTE, nome_alvo)

    if not os.path.exists(caminho_origem):
        print("Erro: Arquivo não encontrado na pasta Arquivos/Client.")
        return

    # Envia nome do arquivo
    sock.sendto(nome_alvo.encode(), endereco_servidor)

    # Envia conteúdo fragmentado
    with open(caminho_origem, 'rb') as f:
        print("Enviando pacotes...")
        chunk = f.read(BUFFER_SIZE)
        while chunk:
            sock.sendto(chunk, endereco_servidor)
            chunk = f.read(BUFFER_SIZE)
        sock.sendto(b"EOF", endereco_servidor)

    # Recebe o arquivo devolvido pelo servidor
    caminho_retorno = os.path.join(DIRETORIO_CLIENTE, f"recebido_do_servidor_{nome_alvo}")
    
    print("Aguardando devolução do servidor...")
    with open(caminho_retorno, 'wb') as f:
        while True:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            if data == b"EOF":
                break
            f.write(data)

    print(f"Sucesso! Confira o arquivo em: {caminho_retorno}")
    sock.close()

if __name__ == "__main__":
    cliente()