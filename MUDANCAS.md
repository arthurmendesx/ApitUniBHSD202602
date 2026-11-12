# O que foi feito (branch `multicamadas`)

## 1. Para executar o projeto original
| Problema encontrado | Correção |
|---|---|
| README manda rodar `main:app`, mas o arquivo se chama `App.py` | Rodar com `uvicorn App:app` (e, na nova versão, `app.main:app`) |
| `uvicorn` não estava no `pyproject.toml` | `uv add "uvicorn[standard]"` |
| Não precisa de `uv init` (o `pyproject.toml` já existe) | Basta `uv sync` |

## 2. Refatoração em camadas
O `App.py` (monolito) foi dividido assim:

```
app/
├── main.py                              # cria o FastAPI e registra as rotas
├── core/database.py                     # conexão SQLite + criação da tabela
├── models/registro.py                   # schemas Pydantic (contratos)
├── repositories/registro_repository.py  # SQL (acesso a dados)
├── services/registro_service.py         # regras de negócio (400/404/500)
└── routes/registro_routes.py            # endpoints HTTP (APIRouter)
```

Fluxo: **Rota → Serviço → Repositório → Banco**. Cada camada só conhece a de baixo.

## 3. Melhorias pontuais
- `@app.on_event("startup")` (depreciado) → `lifespan`.
- Conexão injetada via `Depends(get_db)` e sempre fechada no `finally` (antes podia vazar em caso de erro).
- Validação de título em branco agora vale também no `PUT`.
- `.gitignore` para `.venv`, `__pycache__` e `*.db`.

## 4. Como rodar
```bash
pip install uv
uv sync
uv run uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

## 5. Testes realizados (curl)
POST → 201 · POST título vazio → 400 · GET lista → 200 · PUT → 200 · GET por id → 200 · DELETE → 200 · GET removido → 404 · `/docs` → 200.
