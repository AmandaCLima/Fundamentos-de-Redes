import socket
import os
import time
import select
from rdt import RDT

BUFFER_SIZE = 1024

usuarios_online = {}   
itens_leilao = {}
leilao_ativo = False
seqs_envio = {} 

fila_itens = []           
indice_item_atual = 0     

clientes_cadastrados = {
    "Diego": ("127.0.0.1", 5001),
    "Amanda": ("127.0.0.1", 5002),
    "Silvano": ("127.0.0.1", 5003),
    "Jaubert": ("127.0.0.1", 5004)
}



def rdt_rcv_servidor(sock, seq_esperado_clientes):
    try:
        pkt, addr_cliente = sock.recvfrom(BUFFER_SIZE + 1)
    except Exception: return None, None
    if not pkt or pkt.startswith(b"ACK") or pkt[0] not in (0, 1): return None, None

    seq = pkt[0]
    payload = pkt[1:]
    if addr_cliente not in seq_esperado_clientes:
        seq_esperado_clientes[addr_cliente] = 0

    esperado = seq_esperado_clientes[addr_cliente]
    if seq == esperado:
        sock.sendto(b"ACK" + bytes([seq]), addr_cliente)
        seq_esperado_clientes[addr_cliente] = 1 - esperado
        return payload, addr_cliente
    else:
        sock.sendto(b"ACK" + bytes([1 - esperado]), addr_cliente)
        return None, None

def inicializar_itens():
    global itens_leilao, fila_itens
    DIRETORIO_STORAGE = os.path.join("Arquivos", "Servidor")
    os.makedirs(DIRETORIO_STORAGE, exist_ok=True)
    arquivos_na_pasta = sorted(os.listdir(DIRETORIO_STORAGE))
    
    id_contador = 1
    for nome_arquivo in arquivos_na_pasta:
        if os.path.isfile(os.path.join(DIRETORIO_STORAGE, nome_arquivo)):
            id_item = str(id_contador)
            itens_leilao[id_item] = {"arquivo": nome_arquivo, "lance_atual": 0.0, "vencedor": None, "qtd_lances": 0, "tempo_inicio": None}
            fila_itens.append(id_item)
            id_contador += 1

def enviar_mensagem_rdt(rdt, mensagem, endereco):
    global seqs_envio
    if endereco not in seqs_envio: seqs_envio[endereco] = 0
    seqs_envio[endereco] = rdt.rdt_send(mensagem.encode(), seqs_envio[endereco], endereco)


def servidor(host="127.0.0.1", port=5000, timeout_threshold=2):
    global leilao_ativo, indice_item_atual, usuarios_online

    inicializar_itens()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    rdt = RDT(sock, timeout_threshold=timeout_threshold, origem="Servidor", destino="Cliente")
    
    print(f"Servidor AuctionCIn online ({host}:{port})")
    print("Aguardando conexões... O leilão inicia automaticamente no primeiro login.")

    seq_esperado_clientes = {}

    # =========================================================
    # O LOOP DE EVENTOS DO SERVIDOR 
    # =========================================================
    while True:
        # 1. CHECA A REDE COM SELECT (Espera 0.1s para não sobrecarregar a CPU)
        pronto, _, _ = select.select([sock], [], [], 0.1)
        
        if pronto:
            dado_bytes, addr_cliente = rdt_rcv_servidor(sock, seq_esperado_clientes)
            
            if dado_bytes:
                mensagem = dado_bytes.decode(errors="ignore").strip()
                partes = mensagem.split()
                comando = partes[0].lower()

                if comando == "login" and len(partes) >= 2:
                    nome = partes[1]
                    if nome in clientes_cadastrados and nome not in usuarios_online and addr_cliente == clientes_cadastrados[nome]:
                        usuarios_online[nome] = addr_cliente
                        print(f"[LOGIN] {nome} conectou.")
                        enviar_mensagem_rdt(rdt, "você está online", addr_cliente)

                        # Auto-start do leilão quando o primeiro logar
                        if not leilao_ativo and len(fila_itens) > 0:
                            leilao_ativo = True
                            indice_item_atual = 0
                            id_primeiro = fila_itens[0]
                            itens_leilao[id_primeiro]["tempo_inicio"] = time.time()
                            print(f"\n[!] LEILÃO INICIADO AUTO! Item: {id_primeiro}")
                            enviar_mensagem_rdt(rdt, f"[!] LEILÃO COMEÇOU! Item da vez: {itens_leilao[id_primeiro]['arquivo']}.", addr_cliente)

                elif comando == "bid" and len(partes) >= 3:
                    id_item = partes[1]
                    try: valor = float(partes[2])
                    except ValueError: continue
                    
                    id_item_ativo = fila_itens[indice_item_atual] if (leilao_ativo and indice_item_atual < len(fila_itens)) else None
                    remetente = next((n for n, a in usuarios_online.items() if a == addr_cliente), None)
                    
                    if remetente and id_item == id_item_ativo and valor > itens_leilao[id_item]["lance_atual"]:
                        itens_leilao[id_item]["lance_atual"] = valor
                        itens_leilao[id_item]["vencedor"] = remetente
                        itens_leilao[id_item]["qtd_lances"] += 1
                        msg_broadcast = f"Novo lance! {remetente} ofereceu R$ {valor:.2f} no item {id_item}."
                        print(f"[BID] {msg_broadcast}")
                        for usr_addr in usuarios_online.values():
                            enviar_mensagem_rdt(rdt, msg_broadcast, usr_addr)
                            
                elif comando == "list":
                    resposta = "Itens em leilão:\n"
                    if not itens_leilao:
                        resposta += "Nenhum item disponível no momento."
                    else:
                        for i_id, i_dados in itens_leilao.items():
                            # Destaca qual item está sendo leiloado agora
                            status_str = "[ATIVO AGORA]" if (leilao_ativo and i_id == fila_itens[indice_item_atual]) else "[EM ESPERA]"
                            resposta += f"ID: {i_id} | {i_dados['arquivo']} | Preço Atual: R$ {i_dados['lance_atual']:.2f} {status_str}\n"
                    enviar_mensagem_rdt(rdt, resposta, addr_cliente)
                    
                elif comando == "status":
                    resposta = "Status atual do Leilão:\n"
                    if not itens_leilao:
                        resposta += "Nenhum item disponível no momento."
                    else:
                        for i_id, i_dados in itens_leilao.items():
                            vencedor = i_dados["vencedor"] if i_dados["vencedor"] else "Nenhum lance"
                            status_str = "[ATIVO AGORA]" if (leilao_ativo and i_id == fila_itens[indice_item_atual]) else ""
                            resposta += f"ID: {i_id} | {i_dados['arquivo']} | Ganhando: {vencedor} (R$ {i_dados['lance_atual']:.2f}) {status_str}\n"
                    enviar_mensagem_rdt(rdt, resposta, addr_cliente)
           
                elif comando == "logout":
                    remetente = next((n for n, a in usuarios_online.items() if a == addr_cliente), None)
                    if remetente:
                        del usuarios_online[remetente]
                        enviar_mensagem_rdt(rdt, "Você saiu.", addr_cliente)

        # 2. CHECA OS RELÓGIOS DOS LEILÕES
        if leilao_ativo and indice_item_atual < len(fila_itens):
            id_item = fila_itens[indice_item_atual]
            dados = itens_leilao[id_item]
            
            if dados["tempo_inicio"] is not None:
                tempo_decorrido = time.time() - dados["tempo_inicio"]
                
                # O item fica disponível por 60 segundos ou até 5 lances 
                if tempo_decorrido >= 60 or dados["qtd_lances"] >= 5:
                    print(f"\n[LEILÃO ENCERRADO] O item {id_item} acabou!")
                    vencedor = dados["vencedor"]

                    if vencedor and vencedor in usuarios_online:
                        addr_vencedor = usuarios_online[vencedor]
                        nome_arquivo = dados["arquivo"]
                        caminho_arquivo = os.path.join("Arquivos", "Servidor", nome_arquivo)
                        
                        # O item é enviado ao usuário com o lance mais alto 
                        seq_atual = seqs_envio.get(addr_vencedor, 0)
                        seq_atual = rdt.rdt_send(f"WINNER {nome_arquivo}".encode(), seq_atual, addr_vencedor)

                        with open(caminho_arquivo, "rb") as f:
                            chunk = f.read(BUFFER_SIZE)
                            while chunk:
                                seq_atual = rdt.rdt_send(chunk, seq_atual, addr_vencedor)
                                chunk = f.read(BUFFER_SIZE)

                        seq_atual = rdt.rdt_send(b"", seq_atual, addr_vencedor)
                        seqs_envio[addr_vencedor] = seq_atual
                        print(f"Prêmio enviado para {vencedor}!")

                    del itens_leilao[id_item]
                    indice_item_atual += 1
                    
                    if indice_item_atual < len(fila_itens):
                        prox_id = fila_itens[indice_item_atual]
                        itens_leilao[prox_id]["tempo_inicio"] = time.time()
                        for addr in usuarios_online.values():
                            enviar_mensagem_rdt(rdt, f"\n[!] Próximo leilão começou: {itens_leilao[prox_id]['arquivo']} (ID: {prox_id})", addr)

if __name__ == "__main__":
    servidor()