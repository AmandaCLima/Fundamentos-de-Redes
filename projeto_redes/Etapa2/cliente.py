import socket
import os
import random

BUFFER_SIZE = 1024
PROBABILIDADE_PERDA = 0.2

def sendto_com_perda(sock, pkt, addr):
    if random.random() >= PROBABILIDADE_PERDA:
        sock.sendto(pkt, addr)
    else:
        print("   [!] PERDA SIMULADA (Cliente -> Servidor).")

def make_ack(seq):
    return b"ACK" + bytes([seq])

def extrair_ack(resposta):
    if len(resposta) == 4 and resposta[:3] == b"ACK":
        return resposta[3]
    return -1

def rdt_send(sock, dados, seq, endereco, timeout_threshold):
    pkt = bytes([seq]) + dados
    sendto_com_perda(sock, pkt, endereco)
    sock.settimeout(timeout_threshold)
    
    while True:
        try:
            resposta, _ = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print(f"[TIMEOUT] Retransmitindo pkt seq={seq}...")
            sendto_com_perda(sock, pkt, endereco)
            sock.settimeout(timeout_threshold)
            continue

        ack_seq = extrair_ack(resposta)
        if ack_seq == seq:
            sock.settimeout(None)
            return 1 - seq

def rdt_rcv(sock, seq_esperado):
    sock.settimeout(None)
    while True:
        pkt, addr = sock.recvfrom(BUFFER_SIZE + 1)
        seq = pkt[0]
        payload = pkt[1:]

        if seq == seq_esperado:
            sendto_com_perda(sock, make_ack(seq), addr)
            return payload, addr, 1 - seq_esperado

        sendto_com_perda(sock, make_ack(seq), addr)

def client(host="localhost", port=5000, buffer_size=BUFFER_SIZE, timeout_threshold=2):
    endereco_servidor = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
    seq = rdt_send(sock, nome_alvo.encode(), seq, endereco_servidor, timeout_threshold)

    with open(caminho_origem, "rb") as f:
        chunk = f.read(buffer_size)
        while chunk:
            seq = rdt_send(sock, chunk, seq, endereco_servidor, timeout_threshold)
            chunk = f.read(buffer_size)

    seq = rdt_send(sock, b"", seq, endereco_servidor, timeout_threshold)
    print("Envio concluído. Aguardando a devolução do servidor...")

    # ==========================================
    # ETAPA 2: CLIENTE RECEBE A DEVOLUÇÃO
    # ==========================================
    seq_esperado = 0
    print(f"\n--- INICIANDO RECEBIMENTO DA DEVOLUÇÃO ---")
    
    # Recebe o novo nome criado pelo servidor
    nome_devolvido_bytes, addr, seq_esperado = rdt_rcv(sock, seq_esperado)
    nome_devolvido = nome_devolvido_bytes.decode()
    
    caminho_salvamento = os.path.join(DIRETORIO_CLIENTE, nome_devolvido)
    print(f"Salvando devolução como: {caminho_salvamento}")

    with open(caminho_salvamento, "wb") as f:
        bytes_recebidos = 0
        while True:
            chunk, addr, seq_esperado = rdt_rcv(sock, seq_esperado)
            if not chunk:
                break
            f.write(chunk)
            bytes_recebidos += len(chunk)

    print(f"Processo completo! Arquivo devolvido salvo ({bytes_recebidos} bytes).")

if __name__ == "__main__":
    client()