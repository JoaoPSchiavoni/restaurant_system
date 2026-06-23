# Restaurant System & Dashboard UI 🍽️

Um sistema completo de gerenciamento de pedidos e autenticação para restaurantes, composto por um backend RESTful desenvolvido em **FastAPI** (Python) seguindo conceitos de *Clean Architecture* e um painel web responsivo desenvolvido com **Node.js (Express)**, **HTML5**, **CSS Vanilla** (com temática escura e *glassmorphism*) e **Vanilla JavaScript**.

---

## 🚀 Funcionalidades Principais

- **Autenticação Segura**: Controle de acesso por JWT (JSON Web Tokens) com telas completas de Cadastro (incluindo privilégios de Admin) e Login.
- **Painel de Controle de Pedidos**:
  - Lista lateral dinâmica com status (`PENDING`, `CANCELED`, `FINISHED`), contagem de itens e preços totais.
  - Criação de novos pedidos de forma instantânea.
  - Cancelamento e finalização de pedidos.
- **Itens do Pedido**:
  - Adição de novos itens com modal interativo de escolha de Sabores de Pizza, Tamanhos, Quantidades e preços unitários.
  - Estimativa em tempo real de valores no formulário.
  - Deleção individual de itens de pedidos pendentes.
- **Banco de Dados Relacional**: Persistência completa utilizando **SQLite** e migrações estruturadas via **Alembic**.

---

## 📁 Arquitetura e Estrutura do Projeto

### Backend (Python - FastAPI)
A estrutura segue princípios de separação de responsabilidades (Clean Architecture):
* `src/main.py`: Ponto de entrada e carregamento das rotas da API.
* `src/presentation/routers/`: Definição de endpoints REST para Autenticação (`auth.py`) e Pedidos (`order.py`).
* `src/presentation/schemas.py`: Schemas **Pydantic** para validação estrita de entrada/saída de dados.
* `src/domain/use_cases.py`: Regras de negócio da aplicação (cadastro, login, fluxo de pedidos).
* `src/infrastructure/db/models.py`: Definições das tabelas relacionais do banco utilizando **SQLAlchemy**.
* `src/infrastructure/db/repositories.py`: Abstração de queries e persistência do banco SQLite.
* `alembic/`: Scripts de controle e migração estrutural de banco de dados.

### Frontend & Proxy (Node.js - Express)
* `server.js`: Servidor web Express que hospeda a interface e atua como API Gateway, proxyando requisições do frontend para as rotas FastAPI para evitar problemas de CORS.
* `public/index.html`: Layout semântico do painel administrativo, tela de login/cadastro e modais.
* `public/styles.css`: Estilização premium baseada em HSL, com design responsivo em modo escuro, efeitos translúcidos (*glassmorphism*) e micro-animações.
* `public/app.js`: Gerenciador de estado local, lógica de renderização de listas, interações de modais e chamadas de API.

---

## ⚙️ Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter instalado:
- **Python** (versão 3.11 ou superior) + [Poetry](https://python-poetry.org/)
- **Node.js** (versão 18 ou superior) + **npm**

---

### Passo 1: Instalar Dependências e Reconstruir o Banco

1. **Instale as dependências do Backend (Python)**:
   ```bash
   poetry install
   ```

2. **Execute as Migrações do Banco de Dados**:
   Isso criará o arquivo `banco.db` com as tabelas relacionais (`users`, `orders`, `order_item`):
   ```bash
   poetry run alembic upgrade head
   ```

3. **Instale as dependências do Frontend (Node.js)**:
   ```bash
   npm install
   ```

---

### Passo 2: Inicializar os Servidores

Você precisará de dois terminais abertos para executar ambos os serviços:

#### Terminal 1: Servidor Backend (FastAPI)
Para iniciar a API em segundo plano na porta 8000:
```bash
npm run backend
```
*(Ou execute diretamente: `poetry run uvicorn src.main:app --reload --port 8000`)*

#### Terminal 2: Servidor Frontend (Express)
Para iniciar a interface web na porta 3000:
```bash
npm run dev
```

---

### Passo 3: Utilizar a Aplicação

Abra seu navegador e acesse:
👉 **[http://localhost:3000](http://localhost:3000)**

> 💡 **Nota**: Como o banco SQLite foi inicializado limpo, utilize o formulário da aba **Cadastrar** para criar seu primeiro usuário antes de tentar realizar o login.

---

## 🧪 Suíte de Testes

Os testes unitários e de integração validam as regras de negócio de autenticação, geração de tokens e ciclo de vida de pedidos. Para executá-los:

```bash
poetry run pytest
```
