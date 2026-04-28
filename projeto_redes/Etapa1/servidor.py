import socket
import os

def servidor(host='localhost', port=5000):
    
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
        
        # Bloqueia até chegar o primeiro datagrama — que contém o nome do arquivo
        # recvfrom retorna os dados e o endereço (IP, porta) do remetente
        data, addr = sock.recvfrom(BUFFER_SIZE)
        
        # Decodifica os bytes recebidos para obter o nome do arquivo como string
        nome_arquivo = data.decode().strip()
        
        # Ignora pacotes vazios e volta ao início do loop
        if not nome_arquivo:
            continue
        
        # Adiciona o prefixo "leilao_" ao nome original para identificar arquivos processados
        nome_final = f"leilao_{nome_arquivo}"
        
        # Monta o caminho completo onde o arquivo será salvo no disco
        caminho_salvamento = os.path.join(DIRETORIO_STORAGE, nome_final)
        
        print(f"Recebendo: {nome_arquivo} -> Salvando como: {nome_final}")
        
        # Abre (ou cria) o arquivo de destino em modo 'wb' (escrita binária)
        with open(caminho_salvamento, 'wb') as f:
            
            # Loop de recebimento: lê pacotes até encontrar a flag de término "EOF"
            while True:
                # Aguarda o próximo datagrama do cliente
                packet, _ = sock.recvfrom(BUFFER_SIZE)
                
                # Verifica se o pacote recebido é a flag de término "EOF"
                if packet == b"EOF":
                    break
                
                # Caso contrário, escreve o fragmento recebido no arquivo em disco
                f.write(packet)
        
        print(f"Arquivo {nome_final} armazenado. Iniciando devolução...")
        
        # Devolução: relê o arquivo salvo e o envia de volta ao cliente fragmentado
        with open(caminho_salvamento, 'rb') as f:
            
            # Lê o primeiro fragmento do arquivo limitando-se ao tamanho do buffer
            chunk = f.read(BUFFER_SIZE)
            
            while chunk:
                # Envia o fragmento atual de volta para o endereço do cliente (addr)
                sock.sendto(chunk, addr)
                
                # Lê o próximo fragmento de 1024 bytes
                chunk = f.read(BUFFER_SIZE)
            
            # Após enviar todo o arquivo, envia o pacote especial "EOF" sinalizando o fim
            sock.sendto(b"EOF", addr)
        
        print("Devolução concluída.")

if __name__ == "__main__":
    servidor()