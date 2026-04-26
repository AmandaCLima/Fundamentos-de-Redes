import socket
import os

def servidor(host='localhost', port=5000):
    BUFFER_SIZE = 1024
    # Caminho relativo baseado na sua imagem
    DIRETORIO_STORAGE = os.path.join("Arquivos", "Servidor")
    os.makedirs(DIRETORIO_STORAGE, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print(f"Servidor iniciado em {host}:{port}")

    while True:
        print("\nPronto para receber novo arquivo...")
        
        # Recebe o nome do arquivo
        data, addr = sock.recvfrom(BUFFER_SIZE)
        nome_arquivo = data.decode().strip()
        
        if not nome_arquivo: continue

        nome_final = f"leilao_{nome_arquivo}"
        caminho_salvamento = os.path.join(DIRETORIO_STORAGE, nome_final)

        print(f"Recebendo: {nome_arquivo} -> Salvando como: {nome_final}")

        # Loop de recebimento do conteúdo
        with open(caminho_salvamento, 'wb') as f:
            while True:
                packet, _ = sock.recvfrom(BUFFER_SIZE)
                if packet == b"EOF":
                    break
                f.write(packet)

        print(f"Arquivo {nome_final} armazenado. Iniciando devolução...")

        # Devolve o arquivo para o cliente
        with open(caminho_salvamento, 'rb') as f:
            chunk = f.read(BUFFER_SIZE)
            while chunk:
                sock.sendto(chunk, addr)
                chunk = f.read(BUFFER_SIZE)
            sock.sendto(b"EOF", addr)
        
        print("Devolução concluída.")

if __name__ == "__main__":
    servidor()