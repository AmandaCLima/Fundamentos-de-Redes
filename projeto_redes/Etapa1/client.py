import socket
import os

# Define a função principal do cliente, assumindo localhost e porta 5000 como padrão
def cliente(host='localhost', port=5000):
    
    # Define o limite máximo de bytes por pacote 
    BUFFER_SIZE = 1024
    
    endereco_servidor = (host, port)
    
    # Cria o caminho da pasta onde o cliente lê e salva arquivos, 
    DIRETORIO_CLIENTE = os.path.join("Arquivos", "Client")

    # Instancia o socket 
    # SOCK_DGRAM indica uso do protocolo UDP (Datagramas)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Lê todos os arquivos presentes na pasta do cliente
    arquivos_disponiveis = os.listdir(DIRETORIO_CLIENTE)
    print(f"Arquivos disponíveis em {DIRETORIO_CLIENTE}: {arquivos_disponiveis}")
    
    # Aguarda o usuário digitar o nome do arquivo que deseja transmitir
    nome_alvo = input("Digite o nome do arquivo que deseja enviar: ")
    
    # Junta o caminho da pasta com o nome do arquivo escolhido para encontrar o arquivo no disco
    caminho_origem = os.path.join(DIRETORIO_CLIENTE, nome_alvo)

    # Verifica se o arquivo realmente existe no caminho especificado 
    if not os.path.exists(caminho_origem):
        print("Erro: Arquivo não encontrado na pasta Arquivos/Client.")
        return 

    # Obtém o tamanho exato do arquivo em bytes para o novo protocolo
    tamanho_arquivo = os.path.getsize(caminho_origem)

    # O encode transforma a string (agora com nome e tamanho) em bytes para envio
    metadados_envio = f"{nome_alvo}|{tamanho_arquivo}"
    sock.sendto(metadados_envio.encode(), endereco_servidor)

    # Abre o arquivo alvo em modo 'rb' 
    with open(caminho_origem, 'rb') as f:
        print(f"Enviando pacotes ({tamanho_arquivo} bytes)...")
        
        # Lê o primeiro fragmento do arquivo limitando-se ao tamanho do buffer 
        chunk = f.read(BUFFER_SIZE)
        
        while chunk:
            # Envia o fragmento de bytes atual para o servidor via UDP
            sock.sendto(chunk, endereco_servidor)
            
            # Lê o próximo fragmento de 1024 bytes
            chunk = f.read(BUFFER_SIZE)
            
    # Devolução do servidor 
    
    print("Aguardando devolução do servidor...")
    
    # O primeiro pacote recebido do servidor agora contém os metadados da devolução
    dados_meta, _ = sock.recvfrom(BUFFER_SIZE)
    nome_retorno, tamanho_retorno_str = dados_meta.decode().split('|')
    tamanho_retorno = int(tamanho_retorno_str)
    
    caminho_retorno = os.path.join(DIRETORIO_CLIENTE, nome_retorno)
    
    # Abre (ou cria) um arquivo em modo 'wb' 
    with open(caminho_retorno, 'wb') as f:
        
        bytes_recebidos = 0
        
        # Loop aguardando os pacotes baseado no tamanho exato que o servidor informou
        while bytes_recebidos < tamanho_retorno:
            # Retorna os dados do pacote e o endereço de quem enviou (ignorado)
            data, _ = sock.recvfrom(BUFFER_SIZE)
            
            # Escreve os bytes recebidos no novo arquivo no disco
            f.write(data)
            
            # Atualiza o contador de bytes recebidos
            bytes_recebidos += len(data)

    # Informa ao usuário onde o arquivo devolvido e validado foi salvo
    print(f"Sucesso! {bytes_recebidos} bytes recebidos. Confira o arquivo em: {caminho_retorno}")
    
    # Fecha o socket, liberando a porta e os recursos do sistema operacional
    sock.close()

if __name__ == "__main__":
    cliente()