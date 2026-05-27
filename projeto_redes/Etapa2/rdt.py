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

    def rdt_send(self, dados, seq, endereco, timeout_threshold, timeout_last_pkt_coef=3):
        pkt = bytes([seq]) + dados
        self.sendto_com_perda(pkt, endereco)
        self.sock.settimeout(timeout_threshold)
        
        if dados == b"":  # Se for o pacote de finalização, aumenta o timeout para garantir a entrega
            timeout_threshold *= timeout_last_pkt_coef

        last_pkt_count = 0

        while True:
            try:
                resposta, _ = self.sock.recvfrom(self.BUFFER_SIZE)
            except socket.timeout:
                print(f"[TIMEOUT] Retransmitindo pkt seq={seq}...")
                self.sendto_com_perda(pkt, endereco)
                self.sock.settimeout(timeout_threshold)
                if dados == b"":  
                    # Se for o pacote de finalização, conta as tentativas e encerra após um número definido de vezes.
                    # Isso evita que o servidor fique preso tentando enviar um pacote final que pode ter sido perdido ou
                    # cliente pode ter fechado a conexão ou não estar mais esperando, então é razoável encerrar após algumas tentativas.
                    last_pkt_count += 1
                    if last_pkt_count >= timeout_last_pkt_coef:
                        print(f"[TIMEOUT] Pacote de finalização seq={seq} não foi reconhecido após {timeout_last_pkt_coef} tentativas. Encerrando tentativa.")
                        return None
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
