import socket
import os
from rdt import RDT

BUFFER_SIZE = 1024



def client(host="localhost", port=5000, buffer_size=BUFFER_SIZE, timeout_threshold=2):
    endereco_servidor = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    rdt = RDT(sock, timeout_threshold=timeout_threshold)

    DIRETORIO_CLIENTE = os.path.join("Arquivos", "Cliente")
    os.makedirs(DIRETORIO_CLIENTE, exist_ok=True)

    print(f"Arquivos na pasta: {os.listdir(DIRETORIO_CLIENTE)}")
    nome_alvo = input("Digite o nome do arquivo que deseja enviar: ")
    caminho_origem = os.path.join(DIRETORIO_CLIENTE, nome_alvo)

    if not os.path.exists(caminho_origem):
        print("Erro: Arquivo não encontrado.")
        return

    # ==========================================
    # ETAPA 1: CLIENTE ENVIA O ARQUIVO (UPLOAD)
    # ==========================================
    seq = 0
    print(f"\n--- INICIANDO ENVIO DO ARQUIVO '{nome_alvo}' ---")
    seq = rdt.rdt_send(nome_alvo.encode(), seq, endereco_servidor, timeout_threshold)

    with open(caminho_origem, "rb") as f:
        chunk = f.read(buffer_size)
        while chunk:
            seq = rdt.rdt_send(chunk, seq, endereco_servidor, timeout_threshold)
            chunk = f.read(buffer_size)

    seq = rdt.rdt_send(b"", seq, endereco_servidor, timeout_threshold)
    print("Envio concluído. Aguardando a devolução do servidor...")

    # ==========================================
    # ETAPA 2: CLIENTE RECEBE A DEVOLUÇÃO
    # ==========================================
    seq_esperado = 0
    print(f"\n--- INICIANDO RECEBIMENTO DA DEVOLUÇÃO ---")
    
    # Recebe o novo nome criado pelo servidor
    nome_devolvido_bytes, addr, seq_esperado = rdt.rdt_rcv(seq_esperado)
    nome_devolvido = nome_devolvido_bytes.decode()
    
    caminho_salvamento = os.path.join(DIRETORIO_CLIENTE, nome_devolvido)
    print(f"Salvando devolução como: {caminho_salvamento}")

    with open(caminho_salvamento, "wb") as f:
        bytes_recebidos = 0
        while True:
            chunk, addr, seq_esperado = rdt.rdt_rcv(seq_esperado)
            if not chunk:
                break
            f.write(chunk)
            bytes_recebidos += len(chunk)

    print(f"Processo completo! Arquivo devolvido salvo ({bytes_recebidos} bytes).")

if __name__ == "__main__":
    client()