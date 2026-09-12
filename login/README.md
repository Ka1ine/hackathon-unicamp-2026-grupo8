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
- Ao entrar, aparece uma confirmação e um perfil mockado; Sair encerra a sessão.
- Recuperação de senha e acesso corporativo mostram avisos de demonstração.
- Nenhum email é enviado e nenhum serviço externo é chamado.

## Integrar ao projeto

`app.py` contém o layout e a lógica; `.streamlit/config.toml` configura o tema.
Copie também a pasta `.streamlit` para a raiz de execução do seu projeto.
Troque o bloco `if st.session_state.get("authenticated", False)` pela sua página
principal. `MOCK_USER` contém os dados fictícios.

Este protótipo não implementa autenticação de produção: a senha está no código.
Ao integrar dados reais, substitua a validação mockada por autenticação segura.
Os seletores CSS internos do Streamlit podem exigir ajustes em futuras versões.

Documentação: https://docs.streamlit.io/develop/api-reference/configuration/config.toml
