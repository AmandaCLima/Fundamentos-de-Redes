# AuctionCIn — Etapa 1: Transmissão de Arquivos com UDP

## Integrantes
- Amanda Lima
- Diego Juan
- Jaubert Gouveia
- Silvanio Assunção

## Descrição
Implementação de comunicação UDP com envio e devolução de arquivos.
O cliente envia um arquivo ao servidor; o servidor armazena com prefixo
`leilao_` e devolve ao cliente.

## Estrutura de arquivos
```
projeto_redes/
├── servidor.py              # servidor UDP
├── client.py                # cliente UDP
├── Arquivos/
│   ├── Client/              # pasta com os arquivos que o cliente envia
│   └── Servidor/            # criado automaticamente — arquivos salvos pelo servidor
└── README.md
```

## Como executar

### 1. Inicie o servidor (Terminal 1)
```bash
python servidor.py
```
O servidor ficará aguardando conexões na porta 5000.

### 2. Execute o cliente (Terminal 2)
```bash
python client.py
```
O cliente listará os arquivos disponíveis em `Arquivos/Client/` e pedirá o nome do arquivo a enviar.

### Resultado esperado
- **Terminal do servidor**: exibe o recebimento e a devolução do arquivo
- **Terminal do cliente**: exibe o envio e confirma onde o arquivo devolvido foi salvo
- **Pasta `Arquivos/Servidor/`**: contém o arquivo recebido com prefixo `leilao_`
- **Pasta `Arquivos/Client/`**: contém o arquivo devolvido com prefixo `recebido_do_servidor_`

## Testando com dois tipos de arquivo
```bash
# Crie um arquivo de texto dentro de Arquivos/Client/
echo "Este é um arquivo de teste para o leilão." > Arquivos/Client/teste.txt

# Execute o cliente e informe o nome quando solicitado
python client.py
# > Digite o nome do arquivo que deseja enviar: teste.txt

# Para imagem, copie qualquer .png ou .jpg para Arquivos/Client/ e informe o nome
# > Digite o nome do arquivo que deseja enviar: imagem.png
```

## Parâmetros configuráveis
| Parâmetro    | Padrão    | Descrição                        |
|--------------|-----------|----------------------------------|
| `host`       | localhost | IP do servidor                   |
| `port`       | 5000      | Porta do servidor                |
| `BUFFER_SIZE`| 1024      | Tamanho máximo do pacote (bytes) |

## Observações
- Não há confiabilidade nesta etapa (implementada na Etapa 2 com RDT 3.0)
- Os arquivos são transmitidos como bytes brutos (`rb`/`wb`) — funciona para qualquer tipo de arquivo
- O diretório `Arquivos/Servidor/` é criado automaticamente pelo servidor se não existir
