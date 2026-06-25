import socket
import os
import time
import select
import sys
import msvcrt  # Biblioteca nativa do Windows para ler teclado sem travar
from rdt import RDT

BUFFER_SIZE = 1024

PORTAS_CLIENTES = {
    "Diego": 5001,
    "Amanda": 5002,
    "Silvano": 5003,
    "Jaubert": 5004
}

def client(host="127.0.0.1", port_servidor=5000, timeout_threshold=2):
    DIRETORIO_CLIENTE = os.path.join("Arquivos", "Cliente")
    os.makedirs(DIRETORIO_CLIENTE, exist_ok=True)

    print("=========================================")
    print("        Bem-vindo ao AuctionCIn!         ")
    print("=========================================")
    print(" - login <nome>\n - list\n - status\n - bid <id_item> <valor>\n - logout")
    print("=========================================")
    print("Digite seu comando: ", end="", flush=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    endereco_servidor = (host, port_servidor)
    
    rdt = None
    seq_envio = 0
    seq_esperado = 0
    logado = False
    
    buffer_teclado = "" # Guarda o que você está digitando aos poucos

    # =========================================================
    # O LOOP DE EVENTOS
    # =========================================================
    while True:
        try:
            # 1. CHECA A REDE (Espera no máximo 0.1 segundos)
            if rdt:
                pronto, _, _ = select.select([sock], [], [], 0.1)
                if pronto:
                    # Temos pacote! O rdt_rcv não vai travar pois já sabemos que há dados
                    dado_bytes, addr_servidor, seq_esperado = rdt.rdt_rcv(seq_esperado)
                    
                    if dado_bytes:
                        mensagem = dado_bytes.decode(errors="ignore").strip()
                        
                        # Limpa a linha atual do terminal para não misturar com o que vc estava digitando
                        sys.stdout.write('\r' + ' ' * 50 + '\r') 
                        
                        if mensagem.startswith("WINNER "):
                            nome_arquivo = mensagem.split(" ", 1)[1]
                            caminho_salvamento = os.path.join(DIRETORIO_CLIENTE, nome_arquivo)
                            print(f"\n[!] VOCÊ VENCEU O LEILÃO! Baixando: {nome_arquivo}...")
                            
                            with open(caminho_salvamento, "wb") as f:
                                bytes_recebidos = 0
                                while True:
                                    rdt.sock.settimeout(2.0)
                                    chunk, addr_servidor, seq_esperado = rdt.rdt_rcv(seq_esperado)
                                    if not chunk: break
                                    f.write(chunk)
                                    bytes_recebidos += len(chunk)
                                    
                            print(f"[!] Sucesso! Arquivo '{nome_arquivo}' salvo ({bytes_recebidos} bytes).")
                        else:
                            print(f"\n{mensagem}")
                            
                        # Redesenha o que você estava digitando
                        print(f"Digite seu comando: {buffer_teclado}", end="", flush=True)


            # 2. CHECA O TECLADO (Sem bloquear o programa)
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                # Se apertou ENTER
                if char in (b'\r', b'\n'):
                    comando = buffer_teclado.strip()
                    buffer_teclado = ""
                    print() # Pula linha
                    
                    if not comando:
                        print(f"Digite seu comando: ", end="", flush=True)
                        continue

                    partes = comando.split()
                    cmd = partes[0].lower()

                    # Lógica de envio (Idêntica à anterior)
                    if not logado:
                        if cmd == "login" and len(partes) >= 2:
                            nome = partes[1]
                            if nome not in PORTAS_CLIENTES:
                                print(f"Erro: '{nome}' não cadastrado.\nDigite seu comando: ", end="", flush=True)
                                continue
                                
                            try:
                                sock.bind((host, PORTAS_CLIENTES[nome]))
                            except OSError:
                                print(f"Erro: Porta em uso.\nDigite seu comando: ", end="", flush=True)
                                continue

                            rdt = RDT(sock, timeout_threshold=timeout_threshold, origem="Cliente", destino="Servidor")
                            seq_envio = rdt.rdt_send(comando.encode(), seq_envio, endereco_servidor)
                            logado = True
                        else:
                            print("Erro: Faça o login primeiro.\nDigite seu comando: ", end="", flush=True)
                    else:
                        seq_envio = rdt.rdt_send(comando.encode(), seq_envio, endereco_servidor)
                        if cmd == "logout":
                            print("Saindo do sistema...")
                            break
                    
                    print("Digite seu comando: ", end="", flush=True)

                # Se apertou Backspace (Apagar)
                elif char == b'\x08': 
                    if len(buffer_teclado) > 0:
                        buffer_teclado = buffer_teclado[:-1]
                        sys.stdout.write('\b \b') # Apaga a letra da tela
                        sys.stdout.flush()
                
                # Se digitou uma letra normal
                else:
                    try:
                        letra = char.decode('utf-8')
                        buffer_teclado += letra
                        sys.stdout.write(letra)
                        sys.stdout.flush()
                    except UnicodeDecodeError:
                        pass # Ignora teclas especiais (setas, F1, etc)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    client()