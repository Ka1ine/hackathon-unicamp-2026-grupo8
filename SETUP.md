# Setup e Execução

---

## Pré-requisitos

As dependências necessárias para rodar a solução localmente:

* **Python 3.12+**
* **Poppler (`pdftoppm`)**: Necessário no PATH do sistema **apenas** para a geração das imagens de prévia dos PDFs. Caso não seja instalado, a plataforma continua funcionando utilizando apenas a extração de texto bruto dos documentos.
* *Opcional*: Arquivo `.env` na raiz com chaves de API (ex: `OPENAI_API_KEY=sk-...`) preparado para integrações futuras (atualmente a demonstração não realiza chamadas a LLMs externos).

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

## Preparação de Dados (Prévias de PDFs)

A plataforma utiliza os PDFs reais alocados nas pastas `data/0801234-56-2024-8-10-0001` e `data/0654321-09-2024-8-04-0001`. Para gerar a visualização paginada (imagens) na tela de Detalhes do Processo, execute o script de pré-renderização:

```bash
python login/services/gerar_previas.py
```

*(Nota: As imagens geradas serão salvas em cache na pasta `.previews` junto aos originais, associadas por um hash para garantir a integridade em caso de alteração no documento. O PDF original nunca é alterado).*

## Execução da Aplicação (Streamlit)

A interface de usuário e demonstração é baseada em Streamlit. Inicie o servidor frontend executando:

```bash
python -m streamlit run app.py
```

Acesse `http://localhost:8501` se o navegador não abrir automaticamente.

**Credenciais de Demonstração:**

* **Email:** `demo@enter.com`
* **Senha:** `123456`

*(Nota: O login é apenas visual e mockado para demonstração. Ao navegar, os dados dos processos, como nome da parte e valor da causa, são extraídos em tempo real via OCR/texto dos PDFs mapeados).*

## Testes Automatizados

A suíte de testes foi migrada para o `unittest` nativo do Python, garantindo cobertura do login, extração de processos via `pypdf`, filtros de busca, paginação, download de PDFs e fallbacks visuais.

Para rodar a bateria de testes:

```bash
python -m unittest discover -s login/tests
```

## Estrutura do Projeto Atualizada

A arquitetura evoluiu para suportar a visualização modular via Streamlit e iframes integrados:

```text
├── .streamlit/       # configuração visual do tema (config.toml)
├── assets/           # arquivos estáticos, HTML, CSS e JS (usados nos iframes de Detalhes)
├── data/             # diretório de dados (PDFs dos autos), histórico xlsx e cache de prévias
├── services/         # lógica de negócio (extração pypdf, histórico, geração de prévias)
├── views/            # telas da aplicação Streamlit (processos, histórico, detalhes, configurações)
├── tests/            # testes automatizados em unittest (podem estar na pasta login/tests)
├── app.py            # orquestrador e tela de login principal (ponto de entrada Streamlit)
├── .env.example      # template das variáveis de ambiente para futura integração LLM
├── requirements.txt  # bibliotecas e dependências (Streamlit, pypdf, pandas, etc.)
└── README.md         # descrição geral e propósito do desafio
```