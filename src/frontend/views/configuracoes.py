"""Preferências que afetam a navegação e a visualização do histórico."""
from datetime import datetime

import streamlit as st

from components.preferencias import aplicar_preferencias_interface, iniciar_preferencias, perfil
from services.historico import ARQUIVO_DADOS, carregar_historico, limpar_cache_historico


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
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button {
            display:flex !important; justify-content:flex-start !important; gap:10px; text-align:left !important;
        }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button > div,
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
        st.button("Configurações", icon=":material/settings:", key="nav_configuracoes", use_container_width=True)
        st.divider()
        if st.button("Sair da conta", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def render_configuracoes():
    st.set_page_config(page_title="Configurações | Enter", layout="wide", initial_sidebar_state="expanded")
    _estilo()
    iniciar_preferencias()
    aplicar_preferencias_interface()
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
        st.subheader("Interface e acessibilidade")
        st.toggle("Usar modo compacto", key="pref_interface_compacta")
        st.toggle(
            "Reduzir animações",
            key="pref_reduzir_animacoes",
            help="Desativa transições e animações visuais da interface.",
        )
        st.caption("As alterações são aplicadas automaticamente em todas as telas.")

    with st.container(border=True):
        st.subheader("Política de Acordos (Machine Learning)")
        st.write(
            "Ajuste o comportamento do motor de decisão. Valores menores tornam o modelo mais **agressivo** (favorecendo a manutenção da defesa e o litígio), "
            "enquanto valores maiores tornam o modelo mais **conservador** (favorecendo a propositura de acordos para mitigar riscos)."
        )

        nivel_slider = st.slider(
            "Nível de Conservadorismo",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get("nivel_slider", 0.50),
            step=0.05,
            help="0.0 = Máxima Agressividade | 0.5 = Balanceado | 1.0 = Máximo Conservadorismo"
        )

        if nivel_slider < 0.35:
            st.info("🛡️ **Estratégia Agressiva:** O modelo focará em teses de defesa fortes e só proporá acordos em casos de risco extremo.")
        elif nivel_slider > 0.65:
            st.warning("🤝 **Estratégia Conservadora:** O modelo priorizará o encerramento rápido dos litígios via acordos para evitar surpresas judiciais.")
        else:
            st.success("⚖️ **Estratégia Balanceada:** O modelo atuará conforme os limiares ótimos de mercado e histórico (Padrão).")

        if st.button("Salvar Preferências de IA"):
            st.session_state["nivel_slider"] = nivel_slider
            st.toast("✅ Preferências de Machine Learning atualizadas com sucesso!")

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
