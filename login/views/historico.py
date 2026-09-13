"""Visão consolidada dos processos presentes em data/dados.xlsx."""
import unicodedata

import pandas as pd
import streamlit as st

from components.preferencias import aplicar_preferencias_interface, perfil
from services.historico import carregar_historico


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto).casefold())
    return "".join(caractere for caractere in texto if not unicodedata.combining(caractere))


def _moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _aplicar_estilo():
    st.markdown(
        """
        <style>
        .stApp { background: #22252d; color: #f5f5f7; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none !important; }
        .stMainBlockContainer { max-width: 1250px; padding-top: 48px; padding-bottom: 40px; }
        [data-testid="stSidebar"] { background: #1b1e25; border-right: 1px solid #363a45; }
        h1 { font-size: 32px !important; letter-spacing: -.8px; }
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: #292d36; border-color: #414653; border-radius: 10px; min-height: 46px;
        }
        .marca { font-size: 30px; font-weight: 600; letter-spacing: 2px; margin-bottom: 36px; }
        .marca span { color: #ffb133; }
        .perfil { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
        .avatar { width: 44px; height: 44px; border-radius: 12px; background: #ffb133; color: #22252d;
            display: flex; align-items: center; justify-content: center; font-weight: 700; }
        .perfil-nome { font-size: 15px; font-weight: 600; }
        .perfil-empresa { color: #a5aab7; font-size: 13px; margin-top: 3px; }
        [data-testid="stSidebar"] .stButton button { color: #c5c9d2; border: 1px solid transparent;
            background: transparent; justify-content: flex-start; padding: 12px 16px; }
        [data-testid="stSidebar"] .stButton button:hover { color: #ffb133; background: #ffb13312;
            border-color: #ffb13335; }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button {
            display: flex !important; justify-content: flex-start !important; gap: 10px;
            text-align: left !important;
        }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button > div {
            flex: 0 0 auto !important; width: auto !important;
        }
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button {
            color: #ffb133; background: #ffb13318; border-color: #ffb13345;
        }
        .kpi { background: #292d36; border: 1px solid #3b404c; border-radius: 12px; padding: 18px; }
        .kpi-label { color: #a5aab7; font-size: 13px; margin-bottom: 7px; }
        .kpi-value { color: #f5f5f7; font-size: 25px; font-weight: 650; letter-spacing: -.5px; }
        .section-title { margin: 28px 0 10px; font-size: 18px; font-weight: 600; }
        [data-testid="stDataFrame"] { border: 1px solid #3b404c; border-radius: 12px; overflow: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar():
    nome_perfil, empresa_perfil = perfil()
    with st.sidebar:
        st.markdown(
            f"""
            <div class="marca">ENTER<span>■</span></div>
            <div class="perfil"><div class="avatar">YK</div><div>
                <div class="perfil-nome">{nome_perfil}</div>
                <div class="perfil-empresa">{empresa_perfil}</div>
            </div></div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Processos",
            icon=":material/folder_open:",
            key="nav_processos",
            use_container_width=True,
        ):
            from views.processos import render_processos
            st.switch_page(st.Page(render_processos, default=True))
        st.button(
            "Histórico",
            icon=":material/history:",
            key="nav_historico",
            use_container_width=True,
        )
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


def render_historico():
    st.set_page_config(page_title="Histórico | Enter", layout="wide", initial_sidebar_state="expanded")
    _aplicar_estilo()
    aplicar_preferencias_interface()
    _render_sidebar()

    st.title("Histórico")
    st.caption("Acompanhe os resultados consolidados dos processos e a disponibilidade dos subsídios.")

    dados, erros = carregar_historico()
    for erro in erros:
        st.error(erro)
    if dados.empty:
        return

    busca_col, uf_col, resultado_col, assunto_col = st.columns([2.5, 1, 1.3, 1.4])
    with busca_col:
        busca = st.text_input(
            "Buscar por ID do processo ou nome",
            placeholder="Ex.: 1764352-89.2025.8.06.1818",
            key="busca_historico",
            help="A planilha fornecida não contém o nome da parte. A busca por nome ficará disponível quando essa coluna existir na base.",
        )
    with uf_col:
        uf = st.selectbox("UF", ["Todas", *sorted(dados["UF"].dropna().unique())], key="uf_historico")
    with resultado_col:
        resultado = st.selectbox(
            "Resultado macro",
            ["Todos", *sorted(dados["resultado_macro"].dropna().unique())],
            key="resultado_historico",
        )
    with assunto_col:
        sub_assunto = st.selectbox(
            "Sub-assunto",
            ["Todos", *sorted(dados["Sub-assunto"].dropna().unique())],
            key="sub_assunto_historico",
        )

    filtrados = dados.copy()
    if busca.strip():
        termo = _normalizar(busca)
        mascara = filtrados["processo"].map(_normalizar).str.contains(termo, regex=False)
        filtrados = filtrados[mascara]
    if uf != "Todas":
        filtrados = filtrados[filtrados["UF"] == uf]
    if resultado != "Todos":
        filtrados = filtrados[filtrados["resultado_macro"] == resultado]
    if sub_assunto != "Todos":
        filtrados = filtrados[filtrados["Sub-assunto"] == sub_assunto]

    total_processos = len(filtrados)
    taxa_exito = (
        (filtrados["resultado_macro"] == "Êxito").mean() * 100 if total_processos else 0
    )
    indicadores = (
        ("Processos encontrados", f"{total_processos:,}".replace(",", ".")),
        ("Taxa de êxito", f"{taxa_exito:.1f}%".replace(".", ",")),
        ("Valor total da causa", _moeda(filtrados["valor_causa"].sum())),
        ("Condenações/indenizações", _moeda(filtrados["valor_condenacao"].sum())),
    )
    for coluna, (titulo, valor) in zip(st.columns(len(indicadores)), indicadores):
        coluna.markdown(
            f'<div class="kpi"><div class="kpi-label">{titulo}</div><div class="kpi-value">{valor}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Visão geral</div>', unsafe_allow_html=True)
    grafico_resultado, grafico_uf = st.columns(2)
    with grafico_resultado:
        st.caption("Processos por resultado macro")
        por_resultado = filtrados["resultado_macro"].value_counts().rename_axis("Resultado").to_frame("Processos")
        st.bar_chart(por_resultado, color="#ffb133")
    with grafico_uf:
        st.caption("Valor de condenações por UF (10 maiores)")
        por_uf = (
            filtrados.groupby("UF")["valor_condenacao"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .rename("Valor")
        )
        st.bar_chart(por_uf, color="#ffb133")

    st.markdown(f'<div class="section-title">Processos ({total_processos:,})</div>'.replace(",", "."), unsafe_allow_html=True)
    exibir = filtrados[
        [
            "processo", "UF", "Assunto", "Sub-assunto", "resultado_macro",
            "resultado_micro", "valor_causa", "valor_condenacao", "subsidios_disponiveis",
        ]
    ].rename(
        columns={
            "processo": "Processo",
            "resultado_macro": "Resultado macro",
            "resultado_micro": "Resultado micro",
            "valor_causa": "Valor da causa",
            "valor_condenacao": "Valor da condenação/indenização",
            "subsidios_disponiveis": "Subsídios disponíveis",
        }
    )
    st.dataframe(
        exibir,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor da causa": st.column_config.NumberColumn(format="R$ %.2f"),
            "Valor da condenação/indenização": st.column_config.NumberColumn(format="R$ %.2f"),
            "Subsídios disponíveis": st.column_config.NumberColumn(format="%d"),
        },
    )
