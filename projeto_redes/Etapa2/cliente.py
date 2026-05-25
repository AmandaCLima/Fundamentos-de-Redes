import socket
import os


# Define o limite máximo de bytes por pacote
BUFFER_SIZE = 1024


def get_source_file():
    """Pergunta ao usuário qual arquivo enviar e prepara os metadados.

    Returns:
        tuple | None: (tamanho_arquivo, metadados_envio, caminho_origem) ou
        None se o arquivo não existir.
    """
    # Cria o caminho da pasta onde o cliente lê e salva arquivos
    DIRETORIO_CLIENTE = os.path.join("Arquivos", "Client")

    # Lê todos os arquivos presentes na pasta do cliente
    arquivos_disponiveis = os.listdir(DIRETORIO_CLIENTE)
    print(
        f"Arquivos disponíveis em {DIRETORIO_CLIENTE}: {arquivos_disponiveis}")

    # Aguarda o usuário digitar o nome do arquivo que deseja transmitir
    nome_alvo = input("Digite o nome do arquivo que deseja enviar: ")

    # Junta o caminho da pasta com o nome do arquivo escolhido para encontrá-lo no disco
    caminho_origem = os.path.join(DIRETORIO_CLIENTE, nome_alvo)

    # Verifica se o arquivo realmente existe no caminho especificado
    if not os.path.exists(caminho_origem):
        print("Erro: Arquivo não encontrado na pasta Arquivos/Client.")
        return None

    # Obtém o tamanho exato do arquivo em bytes; o servidor usa isso para saber
    # quando parar de receber.
    tamanho_arquivo = os.path.getsize(caminho_origem)

    # Monta os metadados no formato "nome|tamanho" (ex.: "foto.jpg|10245")
    metadados_envio = f"{nome_alvo}|{tamanho_arquivo}"

    return tamanho_arquivo, metadados_envio, caminho_origem


def extrair_ack(resposta):
    """Lê um pacote recebido e devolve o número de sequência confirmado.

    Args:
        resposta (bytes): pacote recebido do servidor.

    Returns:
        int: a sequência confirmada (0 ou 1), ou -1 se não for um ACK válido.
    """
    # ACK válido tem o formato b'ACK' + 1 byte de sequência
    if len(resposta) == 4 and resposta[:3] == b"ACK":
        return resposta[3]
    return -1


def rdt_send(sock, dados, seq, endereco, timeout_threshold):
    """Envia UM pacote de forma confiável (FSM do emissor RDT 3.0).

    Args:
        sock (socket): socket UDP já criado.
        dados (bytes): payload a enviar (metadados ou chunk do arquivo).
        seq (int): número de sequência atual (0 ou 1).
        endereco (tuple): (host, port) do servidor.
        timeout_threshold (float): tempo, em segundos, até considerar timeout.

    Returns:
        int: o próximo número de sequência (bit alternado: 1 - seq).
    """
    # --- make_pkt(seq, data): prefixa 1 byte com o número de sequência ---
    pkt = bytes([seq]) + dados

    # Estado 1: udt_send(sndpkt) + start_timer
    sock.sendto(pkt, endereco)            # udt_send: entrega o pacote ao canal
    sock.settimeout(timeout_threshold)    # start_timer: arma o temporizador
    print(
        f"[ENVIO] pkt seq={seq} enviado ({len(dados)} bytes). Aguardando ACK {seq}...")

    # Estado 2: esperar ACK
    while True:
        try:
            resposta, _ = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            # timeout: udt_send(sndpkt) + start_timer  (retransmissão)
            print(
                f"[TIMEOUT] ACK {seq} não chegou a tempo. Retransmitindo pkt seq={seq}...")
            sock.sendto(pkt, endereco)
            sock.settimeout(timeout_threshold)
            continue

        ack_seq = extrair_ack(resposta)

        if ack_seq == seq:
            # ACK correto e não corrompido: stop_timer e avança o bit alternado
            print(f"[ACK] ack={seq} recebido. Pacote confirmado.")
            sock.settimeout(None)         # stop_timer
            return 1 - seq

        # ACK do pacote anterior (duplicado) ou pacote inesperado: ignora e
        # permanece no estado de espera (o temporizador continua valendo).
        print(
            f"[ACK] resposta inesperada (ack={ack_seq}, esperava {seq}). Ignorando.")


def client(host="localhost", port=5000, buffer_size=BUFFER_SIZE, timeout_threshold=2):
    """Função de Cliente com RDT 3.0.

    Args:
        host (str, optional): Endereço do servidor. Defaults to "localhost".
        port (int, optional): Porta do servidor. Defaults to 5000.
        buffer_size (_type_, optional): Tamanho do buffer de dados. Defaults to BUFFER_SIZE.
        timeout_threshold (int, optional): Limite de tempo para timeout em segundos. Defaults to 2.
    """

    endereco_servidor = (host, port)

    # Instancia o socket
    # SOCK_DGRAM indica uso do protocolo UDP (Datagramas)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Obtém os dados do arquivo a ser enviado
    dados_do_arquivo = get_source_file()

    if not dados_do_arquivo:
        return

    tamanho_arquivo, metadados_envio, caminho_origem = dados_do_arquivo

    # Número de sequência do bit alternado; começa em 0 e alterna a cada pacote
    # confirmado (metadados e todos os chunks compartilham a mesma alternância).
    seq = 0

    # 1) Envia os metadados ("nome|tamanho") de forma confiável.
    print("Enviando metadados do arquivo...")
    seq = rdt_send(sock, metadados_envio.encode(), seq,
                   endereco_servidor, timeout_threshold)

    # 2) Envia o conteúdo do arquivo, fragmentado e confiável.
    with open(caminho_origem, "rb") as f:
        print(f"Enviando arquivo ({tamanho_arquivo} bytes)...")

        # Lê o primeiro fragmento do arquivo limitando-se ao tamanho do buffer
        chunk = f.read(buffer_size)

        while chunk:
            # Cada fragmento é enviado de forma confiável 
            # rdt_send só retorna após o ACK correspondente, devolvendo o próximo número de sequência.
            seq = rdt_send(sock, chunk, seq, endereco_servidor,
                           timeout_threshold)

            # Lê o próximo fragmento
            chunk = f.read(buffer_size)

    print("Arquivo enviado com sucesso (todos os pacotes confirmados).")

    # TODO (próximos passos): receber a devolução do servidor de forma confiável
    # (FSM do receptor RDT 3.0) e fechar o socket.


if __name__ == "__main__":
    client()
