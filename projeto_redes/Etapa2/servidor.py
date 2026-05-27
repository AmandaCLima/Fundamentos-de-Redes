import socket
import os
import random
from rdt import RDT

BUFFER_SIZE = 1024

def servidor(host="localhost", port=5000, buffer_size=BUFFER_SIZE, timeout_threshold=2):
    DIRETORIO_STORAGE = os.path.join("Arquivos", "Servidor")
    os.makedirs(DIRETORIO_STORAGE, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    rdt = RDT(sock, timeout_threshold=timeout_threshold, origem="Servidor", destino="Cliente")

    print(f"Servidor iniciado em {host}:{port}")

    while True:
        print("\n=========================================")
        print("Pronto para atender novo cliente...")
        
        # ==========================================
        # ETAPA 1: SERVIDOR RECEBE O ARQUIVO
        # ==========================================
        seq_esperado = 0
        
        # Recebe o nome do arquivo
        nome_bytes, addr_cliente, seq_esperado = rdt.rdt_rcv(seq_esperado)
        nome_original = nome_bytes.decode().strip()
        
        if not nome_original:
            continue
            
        nome_final = f"leilao_{nome_original}"
        caminho_salvamento = os.path.join(DIRETORIO_STORAGE, nome_final)
        print(f"Recebendo: '{nome_original}' -> Salvando no servidor como: '{nome_final}'")

        with open(caminho_salvamento, "wb") as f:
            bytes_recebidos = 0
            while True:
                chunk, addr_cliente, seq_esperado = rdt.rdt_rcv(seq_esperado)
                if not chunk: 
                    break
                f.write(chunk)
                bytes_recebidos += len(chunk)
                
        print(f"Arquivo armazenado com sucesso ({bytes_recebidos} bytes).")

        # ==========================================
        # ETAPA 2: SERVIDOR DEVOLVE O ARQUIVO RENOMEADO
        # ==========================================
        seq_envio = 0
        print(f"Iniciando devolução para o cliente...")
        
        # Avisa o cliente qual será o novo nome do arquivo
        seq_envio = rdt.rdt_send(nome_final.encode(), seq_envio, addr_cliente)

        # Envia o conteúdo do arquivo renomeado de volta
        with open(caminho_salvamento, "rb") as f:
            chunk = f.read(buffer_size)
            while chunk:
                seq_envio = rdt.rdt_send(chunk, seq_envio, addr_cliente)
                chunk = f.read(buffer_size)

        # Pacote vazio indicando o fim da devolução
        rdt.rdt_send(b"", seq_envio, addr_cliente)
        print("Devolução concluída! Ciclo encerrado.")

if __name__ == "__main__":
    servidor()