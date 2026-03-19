<p align="center">
  <h1 align="center">✈ HTTPilot</h1>
  <p align="center">
    <strong>Your HTTP Flight Copilot</strong><br>
    Cliente HTTP leve com interface gráfica, coleções, autenticação e salvamento de requests.<br>
    Construído 100% em Python com Tkinter.
  </p>
  <p align="center">
    <a href="#instalação">Instalação</a> •
    <a href="#funcionalidades">Funcionalidades</a> •
    <a href="#como-usar">Como Usar</a> •
    <a href="#autenticação">Autenticação</a> •
    <a href="#contribuindo">Contribuindo</a> •
    <a href="#licença">Licença</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge" alt="Platform">
    <img src="https://img.shields.io/github/license/winston2016/HTTPilot?style=for-the-badge" alt="License">
    <img src="https://img.shields.io/github/stars/winston2016/HTTPilot?style=for-the-badge&color=yellow" alt="Stars">
  </p>
</p>

---

## 📸 Preview

```
┌─────────────────────────────────────────────────────────────────────┐
│  ✈ HTTPilot                                                        │
├──────────────┬──────────────────────────────────────────────────────┤
│ 📁 Coleções  │  [GET ▾] [https://api.exemplo.com/v1/dados] [▶ Enviar] [💾 Salvar] │
│              │                                                      │
│ 📁 Empresa   │  ┌─ Params ─ Headers ─ Body ─ Auth ──────────┐      │
│  🟡 POST Login│  │ {                                         │      │
│  🟢 GET Users │  │   "usuario": "admin@empresa.com",         │      │
│              │  │   "senha": "********",                     │      │
│ 📁 Testes    │  │   "cliente_id": "12345"                    │      │
│  🟢 GET Health│  │ }                                         │      │
│              │  └─────────────────────────────────────────────┘      │
│              │                                                      │
│              │  Resposta  Status: 200 OK │ 0.342s │ 1.2 KB          │
│              │  ┌─ Body ─ Headers ───────────────────────────┐      │
│              │  │ { "status": "success", "data": [...] }     │      │
│              │  └─────────────────────────────────────────────┘      │
└──────────────┴──────────────────────────────────────────────────────┘
```

> 💡 *Tema escuro Catppuccin Mocha integrado para conforto visual.*

---

## ✨ Funcionalidades

### 🌐 Requisições HTTP Completas
- Métodos suportados: **GET**, **POST**, **PUT**, **PATCH**, **DELETE**, **HEAD**, **OPTIONS**
- Query parameters configuráveis
- Headers customizáveis
- Body com suporte a **JSON**, **Form Data**, **Raw** e **Nenhum**
- Resposta formatada automaticamente (JSON pretty-print)
- Visualização de headers da resposta
- Informações de status, tempo de resposta e tamanho

### 📁 Sistema de Coleções (Pastas e Requests)
- Crie **pastas** para organizar seus requests (ex: `Fornecedor/Company`, `Testes`, `Produção`)
- Salve requests completos com **nome, URL, método, params, headers, body e autenticação**
- **Duplo clique** para carregar um request salvo instantaneamente
- Ícones coloridos por método: 🟢 GET 🟡 POST 🔵 PUT 🟠 PATCH 🔴 DELETE
- Persistência automática em `~/.httpilot/collections.json`
- **Exportar/Importar** coleções via arquivo JSON para compartilhar com a equipe

### 🔐 6 Tipos de Autenticação
- **Basic Auth** — Usuário e senha (Base64)
- **Bearer Token** — JWT / OAuth2
- **API Key** — No header ou query string
- **Digest Auth** — HTTP Digest Authentication
- **HMAC-SHA256** — Assinatura criptográfica do body

### 🛠 Extras
- Copiar resposta para clipboard
- Salvar resposta em arquivo (.json / .txt)
- Tema escuro integrado
- Requests assíncronos (não trava a interface)
- Multiplataforma (Windows, Linux, macOS)

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/winston2016/HTTPilot.git
cd HTTPilot

# 2. Instale as dependências
pip install requests cryptography

# 3. Execute
python httpilot.py
```

### Instalação rápida (uma linha)

```bash
git clone https://github.com/winston2016/HTTPilot.git && cd HTTPilot && pip install requests cryptography && python httpilot.py
```

---

## 📖 Como Usar

### 1. Fazer uma requisição simples

1. Selecione o **método** (GET, POST, etc.)
2. Digite a **URL** da API
3. Configure **Params**, **Headers** e **Body** nas abas
4. Clique em **▶ Enviar**

### 2. Organizar com coleções

1. Clique em **+ Pasta** no menu lateral e dê um nome (ex: `Minha API`)
2. Configure sua requisição normalmente
3. Clique em **💾 Salvar** → escolha a pasta e dê um nome ao request
4. Para carregar: **duplo clique** no request salvo

### 3. Compartilhar coleções

1. Clique em **📤 Exportar** para salvar suas coleções em um arquivo `.json`
2. Envie o arquivo para um colega
3. O colega clica em **📥 Importar** e carrega todas as coleções

### 4. Exemplo prático: API de login

```
Método:  POST
URL:     https://api.empresa.com/v1/auth/login
Headers: Content-Type: application/json
Body (JSON):
{
  "usuario": "admin@empresa.com",
  "senha": "sua_senha",
  "remember": true
}
Auth: Bearer Token → seu_token_aqui
```

---

## 🔐 Autenticação

| Tipo | Descrição | Uso Comum |
|------|-----------|-----------|
| **None** | Sem autenticação | APIs públicas |
| **Basic** | Usuário:Senha em Base64 | APIs legadas, serviços internos |
| **Bearer** | Token no header Authorization | JWT, OAuth2, APIs modernas |
| **API Key** | Chave no header ou query string | Google Maps, OpenAI, etc. |
| **Digest** | Challenge-response HTTP | Servidores Apache, APIs seguras |
| **HMAC-SHA256** | Assinatura criptográfica | Webhooks, APIs financeiras |

---

## 📂 Estrutura do Projeto

```
HTTPilot/
├── httpilot.py          # Aplicação principal
├── README.md            # Este arquivo
├── LICENSE              # Licença MIT
├── requirements.txt     # Dependências
└── .gitignore           # Arquivos ignorados
```

### Dados da aplicação

```
~/.httpilot/
└── collections.json     # Suas coleções salvas (gerado automaticamente)
```

---

## 📋 Requirements.txt

```
requests>=2.28.0
cryptography>=3.4.0
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. Faça um **Fork** do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: minha nova feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um **Pull Request**

### Ideias para contribuir

- [ ] Suporte a variáveis de ambiente (`{{base_url}}`, `{{token}}`)
- [ ] Histórico de requisições
- [ ] Abas múltiplas de requisição
- [ ] Testes automatizados (assertions na resposta)
- [ ] Suporte a WebSocket
- [ ] Geração de código (cURL, Python requests, JavaScript fetch)
- [ ] Tema claro

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ⭐ Apoie o projeto

Se o HTTPilot te ajudou, deixe uma ⭐ no repositório!

```
Se este projeto te ajudou, considere dar uma estrela ⭐
Isso ajuda outros desenvolvedores a encontrar o HTTPilot!
```

---

<p align="center">
  Feito com ☕ e Python por <a href="https://github.com/winston2016">winston2016</a>
</p>
