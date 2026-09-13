# Login Enter — demonstração em Streamlit

Tela inspirada na referência: fundo inteiramente escuro, logo e formulário
centralizados, campos arredondados e botão amarelo. Layout adaptado para celular.

## Executar

Abra o terminal dentro da pasta extraída `enter-login` e execute:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Acesse http://localhost:8501 se o navegador não abrir automaticamente.

Conta fictícia: **demo@enter.com** / **123456**.

## Funcionamento

- O formulário valida os campos e a conta fictícia.
- Ao entrar, a tela Processos abre automaticamente, com menu lateral recolhível e perfil fictício.
- Busca por nome (ignorando acentos) ou número, com ou sem pontuação, e filtros combinados de risco e recomendação.
- Os dois processos são lidos diretamente dos PDFs de autos nas pastas `data/0801234-56-2024-8-10-0001` e `data/0654321-09-2024-8-04-0001`, usando `pypdf`. Número, nome e valor da causa são extraídos do texto, sem cadastro fixo. A planilha não é utilizada.
- Alterações nos PDFs invalidam o cache na próxima interação/reexecução da tela. Arquivos ausentes, ilegíveis ou sem os campos esperados geram aviso; dados não são inventados. PDFs digitalizados sem texto precisam de OCR.
- Risco e recomendação ficam como “A avaliar” até integrar o motor de análise; não são classificações calculadas.
- Recuperação de senha e acesso corporativo mostram avisos de demonstração.
- Nenhum email é enviado e nenhum serviço externo é chamado.

## Integrar ao projeto

`app.py` contém o layout e a lógica; `.streamlit/config.toml` configura o tema.
Copie também a pasta `.streamlit` para a raiz de execução do seu projeto.
`MOCK_USER` contém as credenciais fictícias.

### Organização multipágina

- `app.py`: login, configuração e registro de páginas com `st.navigation`.
- `views/processos.py`: layout fornecido pelo usuário, incluindo CSS, perfil, menu, busca e filtros.
- `services/processos.py`: leitura e extração dos PDFs, cache e erros de carregamento.
- `tests/test_processos.py`: testes de login, extração dos PDFs, busca, filtros e saída.

Os arquivos anteriores `components/layout.py` e `assets/workspace.css` não são mais carregados.

Para adicionar uma tela, crie sua função em `views/`, registre uma `st.Page`
na navegação e acrescente o acesso correspondente no menu lateral.

Na raiz do repositório, também é possível executar `python -m streamlit run login/app.py`.
Para carregar automaticamente o tema em `.streamlit/config.toml`, execute dentro de `login/`.

Este protótipo não implementa autenticação de produção: a senha está no código.
Ao integrar dados reais, substitua a validação mockada por autenticação segura.
Os seletores CSS internos do Streamlit podem exigir ajustes em futuras versões.

Documentação: https://docs.streamlit.io/develop/api-reference/configuration/config.toml
