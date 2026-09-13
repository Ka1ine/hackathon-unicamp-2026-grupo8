# Instalação e execução

## Visão geral

A aplicação combina uma interface Streamlit para o advogado e uma API FastAPI
para análise de processos, cálculo da política de acordos e assistente
contextual. Os dois serviços são iniciados juntos pelo comando abaixo.

## Pré-requisitos

- Python 3.12 ou superior.
- Arquivos de exemplo em `data/`, incluindo `dados.xlsx` e
  `data/example_cases/<id-do-processo>/`.
- Opcionalmente, um arquivo `.env` na raiz com `OPENAI_API_KEY` para habilitar
  respostas do Assistente do processo. As demais telas funcionam sem essa chave.

## Instalação

```bash
git clone https://github.com/Ka1ine/hackathon-unicamp-2026-grupo8.git
cd hackathon-unicamp-2026-grupo8

python -m venv venv
source venv/bin/activate          # Linux/macOS
# ou: venv\Scripts\activate       # Windows

python -m pip install -r requirements.txt
```

Para usar o assistente, copie `.env.example` para `.env` e preencha a chave:

```env
OPENAI_API_KEY=sk-...
```

## Iniciar tudo

Com o ambiente virtual ativado, execute um único comando na raiz:

```bash
python start.py
```

O comando inicia:

- Interface: http://127.0.0.1:8501
- Documentação da API: http://127.0.0.1:8000/docs

Use `Ctrl+C` no terminal para encerrar os dois serviços.

## Como utilizar

1. Abra a interface e entre com a conta de demonstração:
   `demo@enter.com` / `123456`.
2. Em **Processos**, pesquise ou filtre a carteira e abra um caso.
3. Na tela do caso, consulte documentos, análise, linha do tempo e o
   Assistente do processo.
4. Em **Configurações**, ajuste a **Agressividade**. O percentual permanece
   durante a sessão e, ao abrir um processo, atualiza o `policy_data` do JSON
   consolidado daquele caso.
5. A indicação de solução apresenta risco, recomendação, proposta inicial,
   teto de acordo e a fundamentação estatística da decisão.
6. Use **Histórico** para analisar a base consolidada e **Transparência** para
   entender a política decisória e seus limites.

## Testes

Na raiz do repositório:

```bash
pytest -q
python -m unittest discover -s src/frontend/tests -p 'test_*.py'
```

## Estrutura

```text
├── data/                 # planilha, PDFs e JSONs de exemplo
├── docs/                 # materiais de entrega e apresentação
├── src/
│   ├── backend/          # FastAPI, monitoramento e motor de política
│   └── frontend/         # Streamlit, telas, assets e testes da interface
├── tests/                # testes do backend
├── requirements.txt      # dependências únicas do projeto
├── start.py              # inicialização conjunta da aplicação
└── README.md             # contexto do desafio e visão do produto
```
