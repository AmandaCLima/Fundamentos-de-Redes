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

    # O encode transforma a string em bytes para envio
    sock.sendto(nome_alvo.encode(), endereco_servidor)

    # Abre o arquivo alvo em modo 'rb' 
    with open(caminho_origem, 'rb') as f:
        print("Enviando pacotes...")
        
        # Lê o primeiro fragmento do arquivo limitando-se ao tamanho do buffer 
        chunk = f.read(BUFFER_SIZE)
        
        while chunk:
            # Envia o fragmento de bytes atual para o servidor via UDP
            sock.sendto(chunk, endereco_servidor)
            
            # Lê o próximo fragmento de 1024 bytes
            chunk = f.read(BUFFER_SIZE)
            
        # Após enviar todo o arquivo, envia um pacote especial com a string em bytes "EOF" 
        sock.sendto(b"EOF", endereco_servidor)

    # Devolução do servidor
    
    # Prepara o caminho e o nome do arquivo onde a resposta do servidor será salva
    caminho_retorno = os.path.join(DIRETORIO_CLIENTE, f"recebido_do_servidor_{nome_alvo}")
    
    print("Aguardando devolução do servidor...")
    
    # Abre (ou cria) um arquivo em modo 'wb' 
    with open(caminho_retorno, 'wb') as f:
        
        # Loop infinito aguardando os pacotes que o servidor está mandando de volta
        while True:
            # Retorna os dados do pacote e o endereço de quem enviou (ignorado)
            data, _ = sock.recvfrom(BUFFER_SIZE)
            
            # Verifica se o pacote recebido é a nossa flag de término "EOF"
            if data == b"EOF":
                break 
                
            # Se não for EOF, escreve os bytes recebidos no novo arquivo no disco
            f.write(data)

    # Informa ao usuário onde o arquivo devolvido e validado foi salvo
    print(f"Sucesso! Confira o arquivo em: {caminho_retorno}")
    
    # Fecha o socket, liberando a porta e os recursos do sistema operacional
    sock.close()

if __name__ == "__main__":
    cliente()