# AuctionCIn - Sistema de Leilão Multi-Usuário

Projeto da disciplina **Fundamentos de Redes de Computadores (2026.1)**.

## Visão Geral

O **AuctionCIn** é um sistema de leilão multiusuário que permite que vários clientes disputem itens em tempo real através de uma arquitetura cliente-servidor.

O projeto tem como principal objetivo aplicar conceitos fundamentais de redes de computadores, especialmente:

- Comunicação via UDP
- Implementação de confiabilidade em nível de aplicação
- Gerenciamento de múltiplos clientes
- Controle de estado no servidor

O desenvolvimento será dividido em três etapas progressivas, onde cada uma adiciona novas funcionalidades e complexidade ao sistema.

---

## Etapas do Projeto

### Etapa 1: Transmissão de arquivos com UDP
### Etapa 2: Implementação de confiabilidade (RDT 3.0)
### Etapa 3: Sistema completo de leilão multiusuário

---

# Primeira Etapa: Transmissão de Arquivos com UDP

## Objetivo

Implementar a comunicação entre cliente e servidor utilizando sockets UDP em Python, permitindo:

- Envio de um arquivo do cliente para o servidor
- Armazenamento do arquivo no servidor
- Renomeação do arquivo no servidor
- Devolução do arquivo ao cliente

Essa etapa não exige confiabilidade na transmissão.

---

## Requisitos Funcionais

### Cliente

- O cliente deve enviar arquivos reais, não apenas strings

### Servidor

O servidor deve:

- Receber o arquivo
- Armazená-lo localmente
- Renomeá-lo (ex: adicionar prefixo `leilao_`)
- Enviar o arquivo de volta ao cliente

### Cliente (confirmação)

- O cliente deve receber o arquivo renomeado como confirmação

---

## Regras de Transmissão

- O tamanho máximo de cada pacote é de **1024 bytes**
- Arquivos maiores devem ser:
  - Fragmentados no envio
  - Reconstruídos no recebimento
- Arquivos e mensagens são tratados da mesma forma: sequência de bytes

---

## Testes Relizados

Envio de arquivos:

- `.txt`
- `.png`
- `.jpg`

---
