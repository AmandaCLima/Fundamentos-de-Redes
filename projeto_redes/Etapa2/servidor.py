import socket
import os
import random

BUFFER_SIZE = 1024
PROBABILIDADE_PERDA = 0.2

def sendto_com_perda(sock, pkt, addr):
    if random.random() >= PROBABILIDADE_PERDA:
        sock.sendto(pkt, addr)
    else:
        print("   [!] PERDA SIMULADA (Servidor -> Cliente).")

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

def servidor(host="localhost", port=5000, buffer_size=BUFFER_SIZE, timeout_threshold=2):
    DIRETORIO_STORAGE = os.path.join("Arquivos", "Servidor")
    os.makedirs(DIRETORIO_STORAGE, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Servidor iniciado em {host}:{port}")

    while True:
        print("\n=========================================")
        print("Pronto para atender novo cliente...")
        
        # ==========================================
        # ETAPA 1: SERVIDOR RECEBE O ARQUIVO
        # ==========================================
        seq_esperado = 0
        
        # Recebe o nome do arquivo
        nome_bytes, addr_cliente, seq_esperado = rdt_rcv(sock, seq_esperado)
        nome_original = nome_bytes.decode().strip()
        
        if not nome_original:
            continue
            
        nome_final = f"leilao_{nome_original}"
        caminho_salvamento = os.path.join(DIRETORIO_STORAGE, nome_final)
        print(f"Recebendo: '{nome_original}' -> Salvando no servidor como: '{nome_final}'")

        with open(caminho_salvamento, "wb") as f:
            bytes_recebidos = 0
            while True:
                chunk, addr_cliente, seq_esperado = rdt_rcv(sock, seq_esperado)
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
        seq_envio = rdt_send(sock, nome_final.encode(), seq_envio, addr_cliente, timeout_threshold)

        # Envia o conteúdo do arquivo renomeado de volta
        with open(caminho_salvamento, "rb") as f:
            chunk = f.read(buffer_size)
            while chunk:
                seq_envio = rdt_send(sock, chunk, seq_envio, addr_cliente, timeout_threshold)
                chunk = f.read(buffer_size)

        # Pacote vazio indicando o fim da devolução
        rdt_send(sock, b"", seq_envio, addr_cliente, timeout_threshold)
        print("Devolução concluída! Ciclo encerrado.")

if __name__ == "__main__":
    servidor()