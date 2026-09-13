# Detalhes de processo

A página de detalhes apresenta os dados extraídos dos autos, a análise
estratégica, os documentos originais, a linha do tempo e o assistente do
processo.

## Inicialização

Inicie a API e a interface juntas, a partir da raiz do repositório:

```sh
python start.py
```

## Fontes locais

Os PDFs de origem e os JSONs consolidados, usados pela análise, linha do
tempo e recomendação, ficam em `data/example_cases/<id-do-processo>/`.

As prévias opcionais ficam em `.previews/<hash-do-pdf>/page-N.png` ao lado dos
PDFs. Para gerá-las a partir da raiz do repositório:

```sh
python src/frontend/services/gerar_previas.py
```

Esse comando requer `pdftoppm` (Poppler). Sem as imagens, a interface mantém a
prévia textual e o download dos PDFs.

## Assistente do processo

O chat chama `POST /api/v1/monitoring/process/{id}/assistant` no backend. A
API cria o contexto no servidor com os PDFs e o JSON do processo selecionado,
envia-o à OpenAI e devolve a resposta acompanhada das fontes utilizadas. O
histórico permanece apenas enquanto a página está aberta.

## Verificação

```sh
python -m unittest discover -s src/frontend/tests
```
