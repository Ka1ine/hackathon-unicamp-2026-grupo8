from html import escape
import unicodedata

import streamlit as st


from services.processos import carregar_processos


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in texto if not unicodedata.combining(c))


def formatar_moeda(valor):
    numero = f"{valor:,.2f}"
    numero = numero.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {numero}"


def render_processos():
    st.set_page_config(
        page_title="Processos | Enter",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .stApp {
            background: #22252d;
            color: #f5f5f7;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stAppDeployButton"],
        [data-testid="stMainMenu"] {
            display: none !important;
        }

        .stMainBlockContainer {
            max-width: 1250px;
            padding-top: 48px;
            padding-bottom: 40px;
        }

        [data-testid="stSidebar"] {
            background: #1b1e25;
            border-right: 1px solid #363a45;
        }

        .marca {
            font-size: 30px;
            font-weight: 600;
            letter-spacing: 2px;
            margin-bottom: 36px;
        }

        .marca span {
            color: #ffb133;
        }

        .perfil {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 30px;
        }

        .avatar {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: #ffb133;
            color: #22252d;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
        }

        .perfil-nome {
            font-size: 15px;
            font-weight: 600;
        }

        .perfil-empresa {
            color: #a5aab7;
            font-size: 13px;
            margin-top: 3px;
        }

        .menu-ativo {
            background: #ffb13318;
            color: #ffb133;
            padding: 14px 16px;
            border: 1px solid #ffb13345;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
        }

        h1 {
            font-size: 32px !important;
            letter-spacing: -0.8px;
        }

        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: #292d36;
            border-color: #414653;
            border-radius: 10px;
            min-height: 46px;
        }

        .lista {
            overflow-x: auto;
        }

        .linha {
            display: grid;
            grid-template-columns: minmax(390px, 2.8fr) 1fr 0.8fr 1.3fr;
            align-items: center;
            gap: 20px;
            min-width: 720px;
            padding: 15px 24px;
            margin-bottom: 8px;
            background: #292d36;
            border: 1px solid #3b404c;
            border-radius: 12px;
        }

        .cabecalho {
            background: transparent;
            border: none;
            padding-top: 8px;
            padding-bottom: 8px;
            color: #a5aab7;
            font-size: 13px;
        }

        .processo-id {
            color: #ffb133;
            font-size: 19px;
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: 4px;
        }

        .processo-nome {
            font-size: 12px;
            font-weight: 400;
            line-height: 1.4;
            color: #a5aab7;
        }

        .valor {
            font-weight: 600;
            white-space: nowrap;
        }

        .risco {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .alto {
            color: #ffaaa5;
            background: #ff736320;
        }

        .medio {
            color: #ffd080;
            background: #ffb13320;
        }

        .baixo {
            color: #8ce1bd;
            background: #43ce9620;
        }

        .pendente { color: #bfc4cf; background: #a5aab720; }

        .recomendacao {
            color: #dedfe5;
            font-size: 14px;
        }

        @media (max-width: 700px) {
            .stMainBlockContainer {
                padding: 32px 18px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="marca">ENTER<span>■</span></div>

            <div class="perfil">
                <div class="avatar">YK</div>
                <div>
                    <div class="perfil-nome">Yasmin Kaline</div>
                    <div class="perfil-empresa">Banco Unicamp</div>
                </div>
            </div>

            <div class="menu-ativo">
                <span>Processos</span>
                <span>›</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        if st.button("Sair da conta", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.title("Processos")
    st.caption(
        "Consulte os processos e acompanhe os riscos "
        "e as recomendações de acordo."
    )

    st.write("")

    with st.container(border=True):
        busca_col, risco_col, recomendacao_col = st.columns([3, 1, 1.5])

        with busca_col:
            busca = st.text_input(
                "Buscar processo",
                placeholder="Buscar por identificação ou nome...",
                key="busca_processos",
            )

        with risco_col:
            risco = st.selectbox(
                "Risco",
                ["Todos", "Alto", "Médio", "Baixo", "A avaliar"],
                key="filtro_risco",
            )

        with recomendacao_col:
            recomendacao = st.selectbox(
                "Recomendação",
                [
                    "Todas",
                    "Propor acordo",
                    "Manter defesa",
                    "Revisar documentos",
                    "A avaliar",
                ],
                key="filtro_recomendacao",
            )

    processos, erros = carregar_processos()
    for erro in erros:
        st.error(erro)

    termo = normalizar(busca.strip())

    filtrados = [
        processo
        for processo in processos
        if (
            (termo in normalizar(f"{processo['id']} {processo['nome']}")
             or (termo.isdigit() and termo in "".join(c for c in processo["id"] if c.isdigit())))
            and (risco == "Todos" or processo["risco"] == risco)
            and (
                recomendacao == "Todas"
                or processo["recomendacao"] == recomendacao
            )
        )
    ]

    st.write("")
    st.subheader(f"Processos ({len(filtrados)})")

    if not filtrados:
        st.info("Nenhum processo encontrado. Tente outra busca ou filtro.")
        return

    classes_risco = {
        "Alto": "alto",
        "Médio": "medio",
        "Baixo": "baixo",
    }

    linhas = []

    for processo in filtrados:
        classe = classes_risco.get(processo["risco"], "pendente")

        linhas.append(
            f"""
            <div class="linha">
                <div>
                    <div class="processo-id">
                        {escape(processo["id"])}
                    </div>
                    <div class="processo-nome">
                        {escape(processo["nome"])}
                    </div>
                </div>

                <div class="valor">
                    {formatar_moeda(processo["valor"])}
                </div>

                <div>
                    <span class="risco {classe}">
                        {escape(processo["risco"])}
                    </span>
                </div>

                <div class="recomendacao">
                    {escape(processo["recomendacao"])}
                </div>
            </div>
            """
        )

    st.markdown(
        '<div class="lista">'
        '<div class="linha cabecalho">'
        "<div>Processo / Nome</div>"
        "<div>Valor</div>"
        "<div>Risco</div>"
        "<div>Recomendação</div>"
        "</div>"
        # Markdown interpreta linhas em branco seguidas de indentação como código.
        # Compactar o HTML mantém toda a lista em um único bloco HTML.
        + "".join(parte.strip() for linha in linhas for parte in linha.splitlines())
        + "</div>",
        unsafe_allow_html=True,
    )
