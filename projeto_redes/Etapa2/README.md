# AuctionCIn — Etapa 2: Transferência Confiável com RDT 3.0

## Integrantes
- Amanda Lima
- Diego Juan
- Jaubert Gouveia
- Silvanio Assunção

## Descrição
Evolução da Etapa 1 com implementação de transferência confiável sobre UDP seguindo o protocolo **RDT 3.0** (Reliable Data Transfer).

O cliente envia um arquivo ao servidor; o servidor armazena com prefixo `leilao_` e devolve ao cliente. Desta vez toda a comunicação — dados e ACKs, nos dois sentidos — passa pelo canal não confiável simulado.

## Estrutura de arquivos
```
projeto_redes/Etapa2/
├── servidor.py              # servidor UDP com RDT 3.0
├── cliente.py               # cliente UDP com RDT 3.0
├── rdt.py                   # classe RDT: envio/recebimento confiável + simulação de perdas
├── Arquivos/
│   ├── Cliente/             # pasta com os arquivos que o cliente envia
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
python cliente.py
```
O cliente listará os arquivos disponíveis em `Arquivos/Cliente/` e pedirá o nome do arquivo a enviar.

## Resultado esperado

- **Terminal do servidor:** exibe cada pacote recebido, ACKs enviados, perdas simuladas e a devolução do arquivo
- **Terminal do cliente:** exibe cada pacote enviado, timeouts/retransmissões e a confirmação do arquivo devolvido
- **Pasta `Arquivos/Servidor/`:** contém o arquivo recebido com prefixo `leilao_`
- **Pasta `Arquivos/Cliente/`:** contém o arquivo devolvido com prefixo `leilao_`

## Testando com dois tipos de arquivo
```bash
# Crie um arquivo de texto dentro de Arquivos/Cliente/
echo "Este é um arquivo de teste para o leilão." > Arquivos/Cliente/teste.txt

# Execute o cliente e informe o nome quando solicitado
python cliente.py
# > Digite o nome do arquivo que deseja enviar: teste.txt

# Para imagem, copie qualquer .png ou .jpg para Arquivos/Cliente/ e informe o nome
# > Digite o nome do arquivo que deseja enviar: imagem.png
```

## Mecanismos do RDT 3.0 implementados

| Mecanismo | Descrição |
|---|---|
| Alternating bit (seq 0/1) | cada pacote carrega 1 byte de sequência; alterna a cada confirmação |
| Timeout + retransmissão | emissor retransmite se o ACK não chegar dentro do prazo |
| ACK de duplicatas | receptor reconfirma pacotes duplicados e descarta o payload |
| Gerador de perdas | `sendto_com_perda` descarta pacotes com probabilidade `probabilidade_perda` |

## Parâmetros configuráveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `host` | `localhost` | IP do servidor |
| `port` | `5000` | Porta do servidor |
| `BUFFER_SIZE` | `1024` | Tamanho máximo do pacote em bytes |
| `probabilidade_perda` | `0.2` | Chance de um pacote ser descartado (0.0 a 1.0) — argumento do construtor de `RDT` |
| `timeout_threshold` | `2` | Segundos até considerar timeout e retransmitir |


