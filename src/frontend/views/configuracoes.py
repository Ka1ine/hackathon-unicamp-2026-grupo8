"""Preferências que afetam a navegação e a visualização do histórico."""
from datetime import datetime

import streamlit as st

from components.preferencias import (
    agressividade,
    iniciar_preferencias,
    perfil,
    salvar_agressividade,
)
from services.historico import ARQUIVO_DADOS, carregar_historico, limpar_cache_historico
from services.politica import atualizar_politica


def _atualizar_politica_do_processo_ativo():
    """Recalcula no backend a política do último processo aberto pelo usuário."""
    salvar_agressividade()
    processo_id = st.session_state.get("processo_detalhe_id")
    if not processo_id:
        return

    nivel = agressividade()
    politica, erro = atualizar_politica(processo_id, nivel)
    if politica:
        st.session_state[f"politica_personalizada_{processo_id}"] = politica
        st.session_state[f"politica_agressividade_{processo_id}"] = nivel
        st.session_state["politica_atualizada"] = True
    else:
        st.session_state["politica_erro"] = erro


def _estilo():
    st.markdown(
        """
        <style>
        .stApp { background: #22252d; color: #f5f5f7; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none !important; }
        .stMainBlockContainer { max-width: 980px; padding-top: 48px; padding-bottom: 40px; }
        [data-testid="stSidebar"] { background: #1b1e25; border-right: 1px solid #363a45; }
        h1 { font-size: 32px !important; letter-spacing: -.8px; }
        .marca { font-size: 30px; font-weight: 600; letter-spacing: 2px; margin-bottom: 36px; }
        .marca span { color: #ffb133; }
        .perfil { display:flex; align-items:center; gap:12px; margin-bottom:30px; }
        .avatar { width:44px; height:44px; border-radius:12px; background:#ffb133; color:#22252d;
            display:flex; align-items:center; justify-content:center; font-weight:700; }
        .perfil-nome { font-size:15px; font-weight:600; }
        .perfil-empresa, .muted { color:#a5aab7; font-size:13px; margin-top:3px; }
        [data-testid="stSidebar"] .stButton button { color:#c5c9d2; border:1px solid transparent;
            background:transparent; justify-content:flex-start; padding:12px 16px; }
        [data-testid="stSidebar"] .stButton button:hover { color:#ffb133; background:#ffb13312; border-color:#ffb13335; }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button {
            display:flex !important; justify-content:flex-start !important; gap:10px; text-align:left !important;
        }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button > div {
            flex:0 0 auto !important; width:auto !important;
        }
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button {
            color:#ffb133; background:#ffb13318; border-color:#ffb13345;
        }
        [data-testid="stVerticalBlockBorderWrapper"] { background:#292d36; border-color:#3b404c; }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background:#22252d; border-color:#414653; border-radius:10px; min-height:46px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sidebar():
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
        if st.button("Processos", icon=":material/folder_open:", key="nav_processos", use_container_width=True):
            from views.processos import render_processos
            st.switch_page(st.Page(render_processos, default=True))
        if st.button("Histórico", icon=":material/history:", key="nav_historico", use_container_width=True):
            from views.historico import render_historico
            st.switch_page(st.Page(render_historico, url_path="historico"))
        if st.button("Transparência", icon=":material/visibility:", key="nav_transparencia", use_container_width=True):
            from views.transparencia import render_transparencia
            st.switch_page(st.Page(render_transparencia, url_path="transparencia"))
        st.button("Configurações", icon=":material/settings:", key="nav_configuracoes", use_container_width=True)
        st.divider()
        if st.button("Sair da conta", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def render_configuracoes():
    st.set_page_config(page_title="Configurações | Enter", layout="wide", initial_sidebar_state="expanded")
    _estilo()
    iniciar_preferencias()
    _sidebar()

    st.title("Configurações")
    st.caption("Gerencie seu perfil, a interface e a atualização da base de dados.")

    with st.container(border=True):
        st.subheader("Perfil")
        nome_col, empresa_col = st.columns(2)
        with nome_col:
            st.text_input("Nome exibido", key="perfil_nome")
        with empresa_col:
            st.text_input("Empresa", key="perfil_empresa")
        st.caption("Esses dados aparecem na barra lateral durante esta sessão.")

    with st.container(border=True):
        st.subheader("Modelo decisório")
        st.session_state.setdefault("_pref_agressividade", agressividade())
        st.slider(
            "Agressividade",
            min_value=0,
            max_value=100,
            step=1,
            format="%d%%",
            key="_pref_agressividade",
            on_change=_atualizar_politica_do_processo_ativo,
            help="0% prioriza uma postura mais conservadora; 100% prioriza uma postura mais agressiva.",
        )
        st.caption(
            "A preferência ajusta os limiares de risco e os valores de negociação "
            "antes da recomendação ser calculada. O valor padrão é 50%."
        )
        if st.session_state.pop("politica_atualizada", False):
            st.success("A política e os valores do processo aberto foram atualizados.")
        if erro := st.session_state.pop("politica_erro", None):
            st.warning(f"Não foi possível atualizar a política: {erro}")

    with st.container(border=True):
        st.subheader("Base de dados")
        dados, erros = carregar_historico()
        if erros:
            st.error(erros[0])
        elif ARQUIVO_DADOS.exists():
            atualizado = datetime.fromtimestamp(ARQUIVO_DADOS.stat().st_mtime).strftime("%d/%m/%Y às %H:%M")
            st.markdown(
                f"**Arquivo:** {ARQUIVO_DADOS.name}  \n"
                f"**Registros carregados:** {len(dados):,}".replace(",", ".")
            )
            st.caption(f"Última alteração do arquivo: {atualizado}")
        if st.button("Atualizar dados", icon=":material/refresh:"):
            limpar_cache_historico()
            st.rerun()
