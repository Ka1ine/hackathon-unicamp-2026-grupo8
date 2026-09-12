# Setup e Execução

---

## Pré-requisitos

As dependências necessárias para rodar a solução:

- **Python 3.12+**
- Arquivo `.env` na raiz com `OPENAI_API_KEY=sk-...`

## Instalação

```bash
git clone https://github.com/Ka1ine/hackathon-unicamp-2026-grupo8.git
cd hackathon-unicamp-2026-grupo8

# Ambiente Virtual
python -m venv venv

                                # Ativação ambiente virtual
source venv/bin/activate        #   Linux/macOS

venv\Scripts\activate           #   Windows

pip install -r requirements.txt # Instalação dependencies
```

## Execução

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Dados

Coloque os arquivos de dados fornecidos na pasta `data/`. Consulte [`data/README.md`](./data/README.md) para instruções detalhadas.

## Estrutura do Projeto

```
├── src/          # código-fonte
├── data/         # dados (não versionados — ver .gitignore)
├── docs/         # apresentação e documentação
├── .env.example  # variáveis de ambiente necessárias
├── SETUP.md      # este arquivo
└── README.md     # descrição do desafio
```
