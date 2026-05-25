import socket
import os

def servidor(host='localhost', port=5000):
    """Função de Servidor para receber um arquivo via UDP e devolvê-lo ao cliente.

    Args:
        host (str, optional): Endereço do servidor. Defaults to 'localhost'.
        port (int, optional): Porta do servidor. Defaults to 5000.
    """
    
    # Define o limite máximo de bytes por pacote
    BUFFER_SIZE = 1024
    
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
        
        # Bloqueia até chegar o primeiro datagrama — que agora contém o nome e o tamanho (ex: "foto.jpg|10245")
        # recvfrom retorna os dados e o endereço (IP, porta) do remetente
        data, addr = sock.recvfrom(BUFFER_SIZE)
        
        # Decodifica os bytes recebidos para obter os metadados como string
        metadados = data.decode().strip()
        
        # Ignora pacotes vazios ou que não estejam no padrão "nome|tamanho"
        if not metadados or '|' not in metadados:
            continue
        
        # Separa o nome e o tamanho do arquivo
        nome_arquivo, tamanho_str = metadados.split('|')
        tamanho_arquivo = int(tamanho_str)
        
        # Adiciona o prefixo "leilao_" ao nome original para identificar arquivos processados
        nome_final = f"leilao_{nome_arquivo}"
        
        # Monta o caminho completo onde o arquivo será salvo no disco
        caminho_salvamento = os.path.join(DIRETORIO_STORAGE, nome_final)
        
        print(f"Recebendo: {nome_arquivo} ({tamanho_arquivo} bytes) -> Salvando como: {nome_final}")
        
        # Abre (ou cria) o arquivo de destino em modo 'wb' (escrita binária)
        with open(caminho_salvamento, 'wb') as f:
            
            bytes_recebidos = 0
            
            # Loop de recebimento: lê pacotes até alcançar o tamanho total do arquivo informado
            while bytes_recebidos < tamanho_arquivo:
                # Aguarda o próximo datagrama do cliente
                packet, _ = sock.recvfrom(BUFFER_SIZE)
                
                # Escreve o fragmento recebido no arquivo em disco
                f.write(packet)
                
                # Atualiza a contagem de bytes recebidos
                bytes_recebidos += len(packet)
        
        print(f"Arquivo {nome_final} armazenado. Iniciando devolução...")
        
        # Obtém o tamanho do arquivo que será devolvido para avisar o cliente
        tamanho_retorno = os.path.getsize(caminho_salvamento)
        
        # Envia os metadados da devolução (nome e tamanho) antes de começar a enviar os bytes
        sock.sendto(f"{nome_final}|{tamanho_retorno}".encode(), addr)
        
        # Devolução: relê o arquivo salvo e o envia de volta ao cliente fragmentado
        with open(caminho_salvamento, 'rb') as f:
            
            # Lê o primeiro fragmento do arquivo limitando-se ao tamanho do buffer
            chunk = f.read(BUFFER_SIZE)
            
            while chunk:
                # Envia o fragmento atual de volta para o endereço do cliente (addr)
                sock.sendto(chunk, addr)
                
                # Lê o próximo fragmento de 1024 bytes
                chunk = f.read(BUFFER_SIZE)
            
          
        
        print("Devolução concluída.")

if __name__ == "__main__":
    servidor()