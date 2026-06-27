# AuctionCIn — Etapa 3: Sistema de Leilão Multi-Usuário

## Integrantes
- Amanda Lima
- Diego Juan
- Jaubert Gouveia
- Silvanio Assunção

## Descrição
Implementação final do sistema de leilões online **AuctionCIn**, com suporte a múltiplos clientes simultâneos. O cliente interage via linha de comando e o servidor gerencia o estado do leilão em tempo real. Toda a comunicação mantém a transferência confiável sobre UDP com **RDT 3.0** das etapas anteriores.

## Estrutura de arquivos
```
projeto_redes/Etapa 3/
├── Servidor.py              # servidor UDP — gerencia leilão e clientes conectados
├── Cliente.py               # cliente UDP — interface de linha de comando
├── rdt.py                   # classe RDT: envio/recebimento confiável + simulação de perdas
├── Arquivos/
│   ├── Cliente/             # arquivos recebidos pelo vencedor do leilão
│   └── Servidor/            # itens disponíveis para leilão (ex: Carro.txt, Notebook.txt)
└── README.md
```

## Como executar

### 1. Inicie o servidor (Terminal 1)
```bash
python Servidor.py
```
O servidor ficará aguardando conexões na porta 5000.

### 2. Execute os clientes (Terminais 2, 3, ...)
```bash
python Cliente.py
```
Abra ao menos dois terminais de cliente. Cada cliente possui uma porta única associada ao seu nome.

## Comandos disponíveis

| Funcionalidade       | Comando                    |
|----------------------|----------------------------|
| Conectar ao sistema  | `login <nome_do_usuario>`  |
| Dar um lance         | `bid <id_item> <valor>`    |
| Ver itens e preços   | `list`                     |
| Ver quem está ganhando | `status`                 |
| Sair do sistema      | `logout`                   |

## Usuários cadastrados

| Nome    | Porta |
|---------|-------|
| Diego   | 5001  |
| Amanda  | 5002  |
| Silvano | 5003  |
| Jaubert | 5004  |

## Parâmetros configuráveis

| Parâmetro           | Padrão | Descrição                                         |
|---------------------|--------|---------------------------------------------------|
| `host`              | `127.0.0.1` | IP do servidor                               |
| `port_servidor`     | `5000` | Porta do servidor                                 |
| `BUFFER_SIZE`       | `1024` | Tamanho máximo do pacote em bytes                 |
| `timeout_threshold` | `2`    | Segundos até considerar timeout e retransmitir    |
