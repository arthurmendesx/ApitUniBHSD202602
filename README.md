# Template de API RESTful (FastAPI + SQLite) - Multicamadas + Nginx (Projeto A4)

> 🔀 **Branch `nginx`:** continuação da branch `multicamadas`. Aqui a API passa a ficar **atrás de um proxy reverso Nginx**. O mini tutorial está logo abaixo.

**Integrantes:** _(preencher com o nome de todos os componentes)_

## 🧭 Mini tutorial: Nginx como proxy reverso da API

### Arquitetura

```
Cliente ──► Nginx :8080 ──► Uvicorn/FastAPI :8000 (interno) ──► SQLite
           (rate limit,         (rotas → serviço → repositório)
            headers, logs)
```

O cliente **nunca** acessa o Uvicorn diretamente: a porta 8000 só existe na rede interna; o único ponto de entrada é o Nginx.

### Arquivos adicionados nesta branch

| Arquivo | Função |
|---|---|
| `nginx/nginx.conf` | Configuração do proxy reverso (usada no Docker) |
| `nginx/nginx.local.conf` | Mesma configuração apontando para `127.0.0.1:8000` (sem Docker) |
| `Dockerfile` | Imagem da API (Python 3.12 + uv + Uvicorn com `--proxy-headers`) |
| `docker-compose.yml` | Sobe os serviços `api` (interno) e `nginx` (porta 8080) |
| `app/core/database.py` | Caminho do banco agora vem da variável `DB_PATH` (volume no Docker) |

### O que a configuração do Nginx faz

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;  # rate limiting por IP
limit_req_status 429;

upstream api_backend { server api:8000; }   # mais instâncias aqui = load balancing

server {
    listen 80;
    server_tokens off;          # esconde a versão do Nginx
    client_max_body_size 1m;    # bloqueia corpos gigantes

    location / {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://api_backend;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- **Ocultação/isolamento:** `proxy_pass` encaminha tudo para o Uvicorn interno.
- **Segurança:** rate limiting (10 req/s por IP, rajada de 20; excedentes recebem `429`), limite de corpo, versão oculta e headers `X-Content-Type-Options`, `X-Frame-Options` e `Referrer-Policy`.
- **Cabeçalhos `X-Forwarded-*`:** o Uvicorn roda com `--proxy-headers`, então a API enxerga o IP e o protocolo reais do cliente (doc do FastAPI *Behind a Proxy*).

### Opção A — Docker Compose (recomendado)

```bash
docker compose up -d --build
```

- API via Nginx: http://localhost:8080/registros
- Swagger: http://localhost:8080/docs
- Health do Nginx: http://localhost:8080/nginx-health
- `http://localhost:8000` **não responde** — a API não é exposta ao host.

Para parar: `docker compose down`.

### Opção B — Sem Docker (Nginx instalado na máquina)

1. Instale o Nginx (`sudo apt install nginx` no Ubuntu/WSL, `brew install nginx` no macOS).
2. Suba a API só na interface local:
   ```bash
   uv sync
   uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers
   ```
3. Copie a configuração e recarregue o Nginx:
   ```bash
   sudo cp nginx/nginx.local.conf /etc/nginx/conf.d/api.conf
   sudo nginx -t && sudo nginx -s reload   # ou: sudo systemctl reload nginx
   ```
4. Acesse http://localhost:8080/docs.

### Testando

```bash
# CRUD passando pelo Nginx
curl -X POST http://localhost:8080/registros -H "Content-Type: application/json" -d '{"titulo":"teste"}'
curl -i http://localhost:8080/registros      # repare em "Server: nginx" e X-Frame-Options

# Rate limiting: 40 requisições seguidas
for i in $(seq 1 40); do curl -s -o /dev/null -w "%{http_code} " http://localhost:8080/registros; done
```

Resultado esperado: ~21 respostas `200` e o restante `429 Too Many Requests`.

### Referências

- [NGINX Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [FastAPI – Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/) / [Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/)
- [NGINX Rate Limiting](https://blog.nginx.org/blog/rate-limiting-nginx)
- Tanenbaum & Van Steen — *Sistemas Distribuídos: Princípios e Paradigmas*

---

> ✅ **Branch `multicamadas`:** o monolito foi refatorado em camadas. Veja **[MUDANCAS.md](MUDANCAS.md)** para o que foi feito e como executar (`uv sync` e `uv run uvicorn app.main:app --reload`).

> 💡 **AVISO IMPORTANTE:** Este repositório contém a estrutura base desenvolvida para o **Projeto A3** em formato **monolítico**. Todo o ciclo de vida da aplicação — conexão com o banco, estruturação de dados e roteamento — está concentrado em um único arquivo (`main.py`). Ao final deste documento, há um guia prático de como evoluir esta base para o **Projeto A4**, adotando uma arquitetura em múltiplas camadas.

Esta é uma API educacional desenvolvida em Python com o framework **FastAPI** e banco de dados relacional **SQLite**. Ela atende aos requisitos iniciais de persistência de dados e documentação automática, servindo como backend para integração com a UC de Usabilidade.

## 🛠 Tecnologias e Pré-requisitos

* **Python 3.8+**
* **uv** (Gerenciador de pacotes e projetos ultrarrápido para Python)
* **FastAPI** (Framework web de alta performance)
* **Uvicorn** (Servidor web ASGI)
* **SQLite** (Banco de dados relacional nativo do Python)

## ⚙️ Como configurar e executar (usando `uv`)

1. Clone este repositório para o seu ambiente local (ou abra no GitHub Codespaces).
2. No terminal, dentro da pasta do projeto, instale o **uv**
```bash
pip install uv
```
3. No terminal, dentro da pasta do projeto, inicialize o ambiente com o **uv** (isso criará o `pyproject.toml` e preparará o ambiente virtual isolado):
   ```bash
   uv init
   ```
4. Adicione as dependências do projeto. O **uv** fará o download e a instalação em frações de segundo:
   ```bash
   uv add fastapi uvicorn
   ```
5. Inicie o servidor local da API utilizando o comando `run` do **uv**:
   ```bash
   uv run uvicorn main:app --reload
   ```
   *(Na primeira execução, o banco de dados será criado automaticamente na mesma pasta).*

6. O servidor estará rodando em: `http://127.0.0.1:8000`

## 📖 Documentação e Testes (Swagger UI)

A API possui documentação interativa gerada automaticamente. Você não precisa de ferramentas externas como Postman ou Insomnia para testar as rotas.

Com o servidor em execução, acesse no navegador:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

## 🚀 Resumo dos Endpoints Disponíveis

A API implementa o CRUD completo. Todos os endpoints estão definidos no arquivo `main.py`:

* **POST `/registros`**: Cria um novo registro no banco (Status `201 Created` ou `400 Bad Request`).
* **GET `/registros`**: Retorna a lista com todos os registros salvos (Status `200 OK`).
* **GET `/registros/{id}`**: Busca os detalhes de um registro específico (Status `200 OK` ou `404 Not Found`).
* **PUT `/registros/{id}`**: Atualiza os dados de um registro existente (Status `200 OK` ou `404 Not Found`).
* **DELETE `/registros/{id}`**: Exclui um registro do banco de dados (Status `200 OK` ou `404 Not Found`).

---

## 🏗️ Guia de Evolução: Do Monolito (A3) para Múltiplas Camadas (A4)

Manter todo o código em um único arquivo (`main.py`) é excelente para o aprendizado inicial e testes rápidos, mas torna a manutenção difícil conforme o sistema cresce. 

Para o **Projeto A4**, o grupo deverá refatorar este monolito em uma **arquitetura de múltiplas camadas**. Siga estes passos para organizar a casa:

1. **Isole o Banco de Dados (`database.py`)**
   * Crie um novo arquivo chamado `database.py`.
   * Mova para ele toda a lógica de conexão com o SQLite (a criação da `engine`, do `cursor` ou a configuração do ORM que estiverem usando) e a função que cria as tabelas iniciais.
   * *Analogia:* Este será o almoxarifado exclusivo do seu sistema.

2. **Separe os Contratos de Dados (`models.py`)**
   * Crie um arquivo `models.py`.
   * Recorte do seu `main.py` todas as classes que herdam de `BaseModel` do Pydantic (como `RegistroCreate`, `RegistroResponse`, etc.) e cole neste novo arquivo.
   * *Analogia:* Este arquivo será o setor de controle de qualidade, ditando o que pode entrar ou sair do sistema.

3. **Limpe as Rotas (`main.py`)**
   * O seu `main.py` agora deve ficar muito mais limpo.
   * Mantenha apenas a inicialização do FastAPI (`app = FastAPI()`) e as funções de rota (os `@app.get`, `@app.post`, etc.).
   * No topo do `main.py`, importe os módulos que você acabou de criar:
     ```python
     from database import conectar_banco, criar_tabelas
     from models import RegistroCreate, RegistroResponse
     ```

Após essa divisão, seu código estará preparado para escalar, integrando facilmente novas funcionalidades de segurança, como um proxy reverso Nginx, de forma totalmente estruturada e profissional.
