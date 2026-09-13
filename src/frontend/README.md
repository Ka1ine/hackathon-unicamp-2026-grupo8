# Frontend

O frontend Streamlit é a área de trabalho do advogado. Ele apresenta a lista de
processos, histórico, transparência do modelo, configurações e a tela de
detalhes de cada caso.

Na tela de detalhes, o usuário pode consultar os PDFs, a linha do tempo, a
análise estratégica, a fundamentação estatística e o assistente contextual. Ao
abrir um processo, a interface solicita ao backend a atualização do
`policy_data` no JSON consolidado do caso com a agressividade da sessão.

Inicie o sistema completo na raiz do repositório:

```bash
python start.py
```

Depois, acesse http://127.0.0.1:8501 e entre com
`demo@enter.com` / `123456`.

## Organização

- `app.py`: autenticação demonstrativa e navegação.
- `views/`: telas da aplicação.
- `services/`: leitura de dados e comunicação com a API local.
- `assets/`: HTML, CSS e JavaScript da tela de detalhes.
- `components/`: preferências de sessão e elementos reutilizáveis.
- `tests/`: testes de navegação e serviços do frontend.
