# Setup e Execução

---

## Pré-requisitos

As dependências necessárias para rodar a solução:

- **Python 3.12+**
- Arquivo `.env` na raiz com a chave da API: `OPENAI_API_KEY=sk-...`

## Instalação

```bash
git clone https://github.com/Ka1ine/hackathon-unicamp-2026-grupo8.git
cd hackathon-unicamp-2026-grupo8

# Criação do ambiente virtual
python -m venv venv

# Ativação do ambiente virtual
source venv/bin/activate        # Linux/macOS
# ou
venv\Scripts\activate           # Windows

# Instalação das dependências
pip install -r requirements.txt
```

## Execução da API

Inicie o servidor backend (FastAPI):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

A documentação interativa (Swagger UI) estará acessível automaticamente em `http://localhost:8000/docs`.

## Testes Automatizados

O sistema conta com uma suíte de testes baseada no `pytest` para validar a lógica de extração, análise de documentos e scraping em um ambiente isolado.

Para rodar a bateria de testes:

```bash
pytest -v
```

*(Nota: O arquivo `pytest.ini` garante que o framework localize os módulos na pasta `src` corretamente).*

## Dados

Coloque os arquivos de dados fornecidos na pasta `data/`. Consulte [`data/README.md`](https://www.google.com/search?q=./data/README.md) para instruções detalhadas.

## Estrutura do Projeto

```text
├── data/             # diretório de dados (HTML, PDF, TXT) e cache (não versionado)
├── docs/             # documentação adicional e apresentações
├── src/              # código-fonte da aplicação (API, extratores, serviços)
├── tests/            # testes automatizados em pytest
├── .env.example      # template das variáveis de ambiente
├── pytest.ini        # configuração de resolução de caminhos do pytest
├── requirements.txt  # bibliotecas e dependências
├── README.md         # descrição geral e propósito do desafio
└── SETUP.md          # este arquivo de instruções
```
