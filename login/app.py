"""Tela de login demonstrativa. Execute: python3 -m streamlit run app.py."""

import streamlit as st

from views.processos import render_processos
from views.detalhes import render_detalhes

authenticated = st.session_state.get("authenticated", False)
st.set_page_config(page_title="Processos | Enter" if authenticated else "Entrar | Enter",
                   page_icon="🟨", layout="wide" if authenticated else "centered",
                   initial_sidebar_state="expanded" if authenticated else "collapsed",
                   menu_items={})

if authenticated:
    page = st.navigation([
        st.Page(render_processos, title="Processos", icon=":material/folder_open:", default=True),
        st.Page(render_detalhes, title="Detalhes do processo", url_path="processo"),
    ], position="hidden")
    page.run()
    st.stop()

# Dados fictícios: substitua esta validação por autenticação real ao integrar.
MOCK_USER = {"email": "demo@enter.com", "password": "123456", "name": "Yasmin"}

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #22252d; color: #f5f5f7; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none !important; }
.stMainBlockContainer {
    max-width: 480px; padding: max(36px, calc((100svh - 730px) / 2)) 24px 40px;
}
.brand { display: flex; align-items: center; justify-content: center;
    gap: 8px; margin: 0 0 42px; font: 500 42px/1.1 Arial, sans-serif;
    letter-spacing: 1px; color: #f5f5f7; }
.brand-mark { width: 24px; height: 27px; display: inline-block;
    background: #ffb133; clip-path: polygon(35% 0,100% 0,100% 100%,0 100%,0 60%,35% 60%); }
.intro { text-align: center; margin-bottom: 22px; }
.intro h1 { font-size: 32px; font-weight: 600; padding: 0 0 12px; letter-spacing: -.8px; }
.intro p { color: #b9bbc4; font-size: 15px; margin: 0; line-height: 1.6; }
[data-testid="stForm"] { border: none; padding: 0; }
[data-testid="stTextInput"] label p { color: #e9e9ee; font-size: 14px; }
[data-testid="stTextInput"] [data-baseweb="input"] {
    background: #292d36; border: 1px solid #454954; border-radius: 12px;
}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
    border-color: #ffb133; box-shadow: 0 0 0 2px #ffb13320;
}
[data-testid="stTextInput"] input { color: #f5f5f7; min-height: 50px; }
[data-testid="stTextInput"] input::placeholder { color: #9397a3; }
.stButton button, .stFormSubmitButton button {
    min-height: 52px; border-radius: 12px; font-size: 14px;
    border: 1px solid #454954; background: transparent; color: #f5f5f7;
}
.stFormSubmitButton button[kind="primary"] {
    background: #ffb133; border-color: #ffb133; color: #17191f;
    margin-top: 8px; font-weight: 600;
}
.stFormSubmitButton button[kind="primary"]:hover { background: #ffc15b; border-color: #ffc15b; }
.st-key-forgot button { border: none; min-height: 24px; padding: 0;
    color: #c1c3cd; background: transparent; font-size: 13px; }
.st-key-forgot { display: flex; align-items: flex-end; margin-top: -8px; }
.st-key-forgot button:hover { color: #ffb133; background: transparent; }
.divider { display: flex; align-items: center; gap: 14px;
    color: #9ea2ad; font-size: 13px; margin: 8px 0; }
.divider::before, .divider::after { content: ''; height: 1px; flex: 1; background: #3d414b; }
.demo { text-align: center; color: #969ba8; font-size: 12px; line-height: 1.8; margin-top: 18px; }
.demo strong { color: #d1d4dd; font-weight: 500; }
.corner { position: fixed; right: 38px; bottom: 32px; width: 104px; height: 116px;
    background: #ffb133; opacity: .9; pointer-events: none;
    clip-path: polygon(35% 0,100% 0,100% 100%,0 100%,0 60%,35% 60%); }
@media (max-width: 700px) {
    .corner { display: none; }
    .brand { margin-bottom: 32px; }
    .stMainBlockContainer { padding-top: max(32px, calc((100svh - 710px) / 2)); }
}
</style>
<div class="corner" aria-hidden="true"></div>
""", unsafe_allow_html=True)

st.markdown('<div class="brand" aria-label="Enter">ENTER<span class="brand-mark" aria-hidden="true"></span></div>', unsafe_allow_html=True)

st.markdown('''<div class="intro"><h1>Entrar</h1>
<p>Insira seu email abaixo para entrar na sua conta</p></div>''', unsafe_allow_html=True)

with st.form("login", border=False):
    email = st.text_input("Email", placeholder="meuemail@exemplo.com")
    password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
    submitted = st.form_submit_button("ENTRAR", type="primary", use_container_width=True)

if submitted:
    if not email.strip() or not password:
        st.error("Preencha o email e a senha.")
    elif email.strip().lower() == MOCK_USER["email"] and password == MOCK_USER["password"]:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.error("Email ou senha incorretos.")

with st.container(key="forgot"):
    if st.button("Esqueceu sua senha?"):
        st.info("Nesta demonstração, use demo@enter.com e a senha 123456. Nenhum email é enviado.")
