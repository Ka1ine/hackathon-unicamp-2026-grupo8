from html import escape
import unicodedata

import streamlit as st


from components.preferencias import aplicar_preferencias_interface, perfil
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

        [data-testid="stSidebar"] .stButton button {
            color: #c5c9d2;
            border: 1px solid transparent;
            background: transparent;
            justify-content: flex-start;
            padding: 12px 16px;
        }

        [data-testid="stSidebar"] .stButton button:hover {
            color: #ffb133;
            background: #ffb13312;
            border-color: #ffb13335;
        }

        div[class*="st-key-nav_processos"] [data-testid="stButton"] button,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button {
            display: flex !important;
            justify-content: flex-start !important;
            gap: 10px;
            text-align: left !important;
        }

        div[class*="st-key-nav_processos"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button > div {
            flex: 0 0 auto !important;
            width: auto !important;
        }

        div[class*="st-key-nav_processos"] [data-testid="stButton"] button {
            color: #ffb133;
            background: #ffb13318;
            border-color: #ffb13345;
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

        .process-card-row {
            margin-bottom: 0;
            transition: background .16s ease;
        }

        div[class*="st-key-process_card_"] {
            position: relative;
            margin-bottom: 8px;
        }

        /* Remove o invólucro intermediário do botão do cálculo de layout.
           Assim, o botão passa a se ancorar no cartão, sem ocultá-lo. */
        div[class*="st-key-process_card_"]
        [data-testid="stElementContainer"]:has(> [data-testid="stButton"]) {
            display: contents;
        }

        div[class*="st-key-process_card_"] [data-testid="stButton"] {
            position: absolute;
            inset: 0;
            z-index: 3;
            height: 100%;
        }

        div[class*="st-key-process_card_"] [data-testid="stButton"] button {
            width: 100%;
            height: 100%;
            min-height: 0;
            opacity: 0;
            cursor: pointer;
        }

        div[class*="st-key-process_card_"]:has(button:hover) .process-card-row,
        div[class*="st-key-process_card_"]:has(button:focus-visible) .process-card-row {
            background: #303540;
            border-color: #ffb13370;
            transform: none !important;
        }

        div[class*="st-key-process_card_"]:has(button:focus-visible) .process-card-row {
            outline: 2px solid #ffb133;
            outline-offset: 3px;
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
    aplicar_preferencias_interface()
    nome_perfil, empresa_perfil = perfil()

    with st.sidebar:
        st.markdown(
            f"""
            <div class="marca">ENTER<span>■</span></div>

            <div class="perfil">
                <div class="avatar">YK</div>
                <div>
                    <div class="perfil-nome">{nome_perfil}</div>
                    <div class="perfil-empresa">{empresa_perfil}</div>
                </div>
            </div>

            """,
            unsafe_allow_html=True,
        )

        st.button(
            "Processos",
            icon=":material/folder_open:",
            key="nav_processos",
            use_container_width=True,
        )
        if st.button(
            "Histórico",
            icon=":material/history:",
            key="nav_historico",
            use_container_width=True,
        ):
            from views.historico import render_historico
            st.switch_page(st.Page(render_historico, url_path="historico"))
        if st.button(
            "Transparência",
            icon=":material/visibility:",
            key="nav_transparencia",
            use_container_width=True,
        ):
            from views.transparencia import render_transparencia
            st.switch_page(st.Page(render_transparencia, url_path="transparencia"))
        if st.button(
            "Configurações",
            icon=":material/settings:",
            key="nav_configuracoes",
            use_container_width=True,
        ):
            from views.configuracoes import render_configuracoes
            st.switch_page(st.Page(render_configuracoes, url_path="configuracoes"))

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
                    "Acordo Mandatório",
                    "Acordo Estratégico",
                    "Defesa",
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

    st.markdown(
        '<div class="lista"><div class="linha cabecalho">'
        '<div>Processo / Nome</div><div>Valor</div><div>Risco</div>'
        '<div>Recomendação</div></div></div>',
        unsafe_allow_html=True,
    )

    for indice, processo in enumerate(filtrados):
        classe = classes_risco.get(processo["risco"], "pendente")
        cartao = f"""
        <div class="lista"><div class="linha process-card-row">
            <div>
                <div class="processo-id">{escape(processo["id"])}</div>
                <div class="processo-nome">{escape(processo["nome"])}</div>
            </div>
            <div class="valor">{formatar_moeda(processo["valor"])}</div>
            <div><span class="risco {classe}">{escape(processo["risco"])}</span></div>
            <div class="recomendacao">{escape(processo["recomendacao"])}</div>
        </div></div>
        """
        with st.container(key=f"process_card_{indice}"):
            st.markdown(
                "".join(parte.strip() for parte in cartao.splitlines()),
                unsafe_allow_html=True,
            )
            if st.button(
                f"Abrir detalhes do processo {processo['id']} de {processo['nome']}",
                key=f"open_process_{indice}",
                use_container_width=True,
            ):
                from views.detalhes import render_detalhes
                st.session_state.processo_detalhe_id = processo["id"]
                st.switch_page(st.Page(render_detalhes, url_path="processo"))
