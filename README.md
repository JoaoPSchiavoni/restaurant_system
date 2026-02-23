# Restaurant System API 🍽️

Uma API RESTful escalável para o gerenciamento de restaurantes, desenvolvida com **FastAPI**. Este sistema permite o controle de pedidos, autenticação segura de usuários e persistência de dados utilizando um banco de dados relacional.

## 🚀 Tecnologias Utilizadas

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Banco de Dados:** SQLite (desenvolvimento) / [SQLAlchemy](https://www.sqlalchemy.org/) como ORM
* **Migrações:** [Alembic](https://alembic.sqlalchemy.org/)
* **Autenticação:** JWT (JSON Web Tokens) e Passlib (Bcrypt)
* **Validação de Dados:** Pydantic

## 📁 Arquitetura e Estrutura do Projeto

* `main.py`: Ponto de entrada da aplicação e inicialização do servidor.
* `Models.py`: Modelos declarativos do banco de dados (SQLAlchemy).
* `schemas.py`: Schemas Pydantic para validação de entrada/saída de dados da API.
* `auth_routes.py`: Endpoints de autenticação (Cadastro e Login).
* `order_routes.py`: Endpoints para o CRUD (criação, leitura, atualização e exclusão) de pedidos.
* `dependencies.py`: Funções para injeção de dependência (ex: controle de sessão de DB e validação do usuário atual).
* `tests.py`: Suíte de testes automatizados.
* `alembic/`: Controle de versão estrutural do banco de dados.

## ⚙️ Como executar o projeto localmente

### 1. Clonar o repositório
```bash
git clone [https://github.com/JoaoPSchiavoni/restaurant_system.git](https://github.com/JoaoPSchiavoni/restaurant_system.git)
cd restaurant_system
