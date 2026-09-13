# Dados da aplicação

```text
data/
├── dados.xlsx
├── example_cases/
│   └── <id-do-processo>/
│       ├── PDFs dos autos e subsídios
│       └── _<id-do-processo-com-hífens>.json
└── cache/                 # resultados de política e monitoramento gerados localmente
```

`dados.xlsx` contém a base histórica usada para treinar o modelo de política.
Cada pasta em `example_cases` contém os documentos e o JSON consolidado de um
processo. O campo `policy_data` desse JSON é atualizado pelo backend quando o
processo é aberto, com a recomendação, valores de negociação, agressividade e
fundamentação estatística vigentes.

Não inclua dados reais, sigilosos ou sensíveis em repositórios públicos.
