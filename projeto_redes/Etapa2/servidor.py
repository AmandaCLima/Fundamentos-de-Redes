import socket
import os


# Define o limite máximo de bytes por pacote
BUFFER_SIZE = 1024


def make_ack(seq):
    """Monta um pacote de ACK para a sequência informada.

    Args:
        seq (int): número de sequência a confirmar (0 ou 1).

    Returns:
        bytes: pacote no formato b'ACK' + 1 byte de sequência.
    """
    # Formato simétrico ao que o cliente espera em extrair_ack()
    return b"ACK" + bytes([seq])


def rdt_rcv(sock, seq_esperado):
    """Recebe UM pacote de forma confiável (FSM do receptor RDT 3.0).

        Args:
        sock (socket): socket UDP já criado e associado (bind).
        seq_esperado (int): número de sequência aguardado (0 ou 1).

    Returns:
        tuple: (payload, addr, prox_esperado), onde payload são os bytes úteis,
        addr é o endereço do remetente e prox_esperado é o bit já alternado.
    """
    while True:
        # Bloqueia até chegar um datagrama; retorna os dados e o endereço de quem enviou
        pkt, addr = sock.recvfrom(BUFFER_SIZE)

        # --- parse_pkt: o primeiro byte é a sequência; o restante é o payload ---
        seq = pkt[0]
        payload = pkt[1:]

        if seq == seq_esperado:
            # Pacote esperado: confirma com ACK(seq) e inverte o bit alternado
            sock.sendto(make_ack(seq), addr)
            print(f"[RECEBIDO] pkt seq={seq} ({len(payload)} bytes). Enviado ACK {seq}.")
            return payload, addr, 1 - seq_esperado

        # Pacote duplicado: o ACK anterior provavelmente se perdeu e o emissor
        # retransmitiu. Reenvia o ACK daquele pacote e descarta o payload.
        sock.sendto(make_ack(seq), addr)
        print(f"[DUPLICADO] pkt seq={seq} (esperava {seq_esperado}). Reenviado ACK {seq}, payload descartado.")


def servidor(host="localhost", port=5000, buffer_size=BUFFER_SIZE):
    """Função de Servidor com RDT 3.0.

    Args:
        host (str, optional): Endereço do servidor. Defaults to "localhost".
        port (int, optional): Porta do servidor. Defaults to 5000.
        buffer_size (_type_, optional): Tamanho do buffer de dados. Defaults to BUFFER_SIZE.
    """

    # Caminho da pasta onde o servidor armazena os arquivos recebidos
    DIRETORIO_STORAGE = os.path.join("Arquivos", "Servidor")

    # Cria o diretório de armazenamento caso ainda não exista
    os.makedirs(DIRETORIO_STORAGE, exist_ok=True)

    # Instancia o socket
    # SOCK_DGRAM indica uso do protocolo UDP (Datagramas)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Associa o socket ao endereço e porta do servidor (bind)
    # A partir daqui o SO encaminha os datagramas recebidos nessa porta para este socket
    sock.bind((host, port))

    print(f"Servidor iniciado em {host}:{port}")

    # Loop principal: o servidor fica ativo indefinidamente, atendendo clientes sequencialmente
    while True:
        print("\nPronto para receber novo arquivo...")

        # Número de sequência do bit alternado; reinicia a cada novo arquivo,
        # pois cada cliente começa sua transmissão em 0.
        seq_esperado = 0

        # 1 - Recebe os metadados ("nome|tamanho") de forma confiável.
        metadados_bytes, addr, seq_esperado = rdt_rcv(sock, seq_esperado)
        metadados = metadados_bytes.decode().strip()

        # Ignora pacotes vazios ou que não estejam no padrão "nome|tamanho"
        if not metadados or "|" not in metadados:
            continue

        # Separa o nome e o tamanho do arquivo
        nome_arquivo, tamanho_str = metadados.split("|")
        tamanho_arquivo = int(tamanho_str)

        # Adiciona o prefixo "leilao_" ao nome original para identificar arquivos processados
        nome_final = f"leilao_{nome_arquivo}"

        # Monta o caminho completo onde o arquivo será salvo no disco
        caminho_salvamento = os.path.join(DIRETORIO_STORAGE, nome_final)

        print(f"Recebendo: {nome_arquivo} ({tamanho_arquivo} bytes) -> Salvando como: {nome_final}")

        # 2 - Recebe o conteúdo do arquivo, fragmentado e confiável.
        # Abre (ou cria) o arquivo de destino em modo 'wb' (escrita binária)
        with open(caminho_salvamento, "wb") as f:

            bytes_recebidos = 0

            # Loop de recebimento: lê pacotes até alcançar o tamanho total informado
            while bytes_recebidos < tamanho_arquivo:
                # rdt_rcv só retorna quando o pacote esperado chega (duplicatas
                # são tratadas e descartadas internamente).
                chunk, addr, seq_esperado = rdt_rcv(sock, seq_esperado)

                # Escreve o fragmento recebido no arquivo em disco
                f.write(chunk)

                # Atualiza a contagem de bytes recebidos
                bytes_recebidos += len(chunk)

        print(f"Arquivo {nome_final} armazenado ({bytes_recebidos} bytes).")

        # TODO (próximos passos): devolver o arquivo ao cliente de forma confiável
        # (FSM do emissor RDT 3.0) e implementar o gerador de perdas de pacotes.


if __name__ == "__main__":
    servidor()
