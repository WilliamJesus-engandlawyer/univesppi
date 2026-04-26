# 📡 Monitor de Ruído — Guia de Instalação (Windows)

> Esse guia foi feito para quem **nunca usou Docker antes**. Siga passo a passo com calma!

---

## 🧰 O que você vai precisar instalar

### Docker Desktop

O Docker é o programa que vai rodar o sistema. Pense nele como uma "caixinha" que contém tudo que o projeto precisa para funcionar, sem precisar instalar mais nada.

**Como instalar:**

1. Acesse: **https://www.docker.com/products/docker-desktop**
2. Clique em **"Download for Windows"**
3. Abra o instalador baixado e clique em **Next** em tudo
4. Quando terminar, **reinicie o computador**
5. Abra o **Docker Desktop** pela área de trabalho

> ✅ Você saberá que está funcionando quando aparecer uma barrinha verde no canto inferior esquerdo do Docker Desktop escrito **"Engine running"**

---

## 📁 Organizando os arquivos do projeto

Crie uma pasta em qualquer lugar do seu computador — por exemplo na Área de Trabalho — e chame de `noise-monitor`.

Coloque todos os arquivos dentro dela exatamente assim:

```
noise-monitor/
├── docker-compose.yaml
├── Dockerfile
├── init.sql
├── .env                ← você vai criar esse (veja abaixo)
├── requirements.txt
├── main.py
├── database.py
└── templates/
    └── index.html
```

> ⚠️ A pasta `templates` precisa estar dentro de `noise-monitor`, e o `index.html` precisa estar dentro de `templates`.

---

## ⚙️ Criando o arquivo `.env`

Esse arquivo guarda as configurações do banco de dados. Você precisa criar ele do zero.

1. Abra o **Bloco de Notas** (pesquise "Bloco de Notas" no menu Iniciar)
2. Cole esse conteúdo:

```
POSTGRES_DB=noisedb
POSTGRES_USER=noiseuser
POSTGRES_PASSWORD=MinhaSenh@2025

RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=60
```

3. Clique em **Arquivo → Salvar como**
4. Navegue até a pasta `noise-monitor`
5. No campo **"Nome do arquivo"** digite: `.env`
6. No campo **"Tipo"** selecione: **Todos os arquivos (\*.\*)**
7. Clique em **Salvar**

> ⚠️ Se salvar como `.env.txt` não vai funcionar! Confira se o nome está exatamente `.env`

---

## 🚀 Rodando o projeto

### Passo 1 — Abra o terminal na pasta do projeto

1. Abra o **Explorador de Arquivos**
2. Navegue até a pasta `noise-monitor`
3. Clique na **barra de endereço** (onde aparece o caminho, tipo `C:\Users\...`)
4. Digite `cmd` e aperte **Enter**

Um terminal preto vai abrir já dentro da pasta certa.

### Passo 2 — Suba o projeto

No terminal, digite exatamente esse comando e aperte **Enter**:

```
docker compose up -d --build
```

> ⏳ Na **primeira vez** vai demorar alguns minutos — ele está baixando e configurando tudo. É normal aparecer várias linhas passando na tela.

Quando o cursor voltar, você pode fechar o terminal. O sistema continuará rodando em segundo plano.

### Passo 3 — Verifique no Docker Desktop

Abra o **Docker Desktop**. Você vai ver algo assim:

```
noise-monitor
  ├── noise_db    ✅ Running
  └── noise_app   ✅ Running
```

Se os dois estiverem com ícone verde e escrito **Running**, está tudo funcionando! 🎉

---

## 🌐 Acessando o dashboard

Abra o navegador e acesse:

```
http://localhost:5000
```

O painel de monitoramento de ruído vai aparecer.

---

## ▶️ Ligar e desligar o sistema

Pelo **Docker Desktop** você não precisa mais abrir terminal nenhum:

| O que fazer | Como fazer no Docker Desktop |
|---|---|
| **Ligar** | Clique no botão ▶️ ao lado de `noise-monitor` |
| **Desligar** | Clique no botão ⏹️ ao lado de `noise-monitor` |
| **Ver erros** | Clique em `noise_app` e depois em **Logs** |

---

## ❓ Problemas comuns

**O Docker Desktop não abre ou dá erro na instalação**
→ Verifique se o Windows está atualizado. O Docker precisa do Windows 10 versão 2004 ou mais recente.

**Aparece erro "port 5000 already in use"**
→ Algum outro programa está usando a porta 5000. Reinicie o computador e tente de novo.

**O `noise_app` aparece como "Restarting" no Docker Desktop**
→ Clique nele, vá em **Logs** e veja a mensagem de erro.

**Salvei o `.env` como `.env.txt` sem querer**
→ Delete o arquivo errado, crie novamente seguindo o passo acima, e depois clique em **Restart** no `noise-monitor` dentro do Docker Desktop.

---

## 📌 Resumo rápido

```
1. Instalar o Docker Desktop
2. Colocar os arquivos na pasta noise-monitor
3. Criar o arquivo .env
4. Abrir cmd na pasta → rodar: docker compose up -d --build
5. Abrir o navegador em: http://localhost:5000
```

---

*Qualquer dúvida é só perguntar! 😊*
