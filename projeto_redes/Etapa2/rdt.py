import socket 
import random

class RDT:
    """
    Classe RDT que agrupa as funções de envio e recebimento confiável, simulando perdas de pacotes.
    """

    BUFFER_SIZE = 1024

    def __init__(self, sock, timeout_threshold=2, probabilidade_perda=0.2):
        self.sock = sock
        self.timeout_threshold = timeout_threshold
        self.probabilidade_perda = probabilidade_perda


    def sendto_com_perda(self, pkt, addr):
        if random.random() >= self.probabilidade_perda:
            self.sock.sendto(pkt, addr)
        else:
            print("   [!] PERDA SIMULADA (Servidor -> Cliente).")

    def make_ack(self, seq):
        return b"ACK" + bytes([seq])

    def extrair_ack(self, resposta):
        if len(resposta) == 4 and resposta[:3] == b"ACK":
            return resposta[3]
        return -1

    def rdt_send(self, dados, seq, endereco, timeout_threshold):
        pkt = bytes([seq]) + dados
        self.sendto_com_perda(pkt, endereco)
        self.sock.settimeout(timeout_threshold)

        while True:
            try:
                resposta, _ = self.sock.recvfrom(self.BUFFER_SIZE)
            except socket.timeout:
                print(f"[TIMEOUT] Retransmitindo pkt seq={seq}...")
                self.sendto_com_perda(pkt, endereco)
                self.sock.settimeout(timeout_threshold)
                continue

            ack_seq = self.extrair_ack(resposta)
            if ack_seq == seq:
                self.sock.settimeout(None)
                return 1 - seq

    def rdt_rcv(self, seq_esperado):
        self.sock.settimeout(None)
        while True:
            pkt, addr = self.sock.recvfrom(self.BUFFER_SIZE + 1)
            seq = pkt[0]
            payload = pkt[1:]

            if seq == seq_esperado:
                self.sendto_com_perda(self.make_ack(seq), addr)
                return payload, addr, 1 - seq_esperado

            self.sendto_com_perda(self.make_ack(seq), addr)
