"""Página isolada; HTML/CSS/JS ficam dentro de um iframe do Streamlit."""
import json
from pathlib import Path

import streamlit as st

from services.detalhes import carregar_detalhes


def render_detalhes():
    from views.processos import render_processos

    st.set_page_config(page_title="Detalhes do processo | Enter", layout="wide")
    # Apenas o contêiner desta página; estilos internos vivem no iframe.
    st.markdown("""<style>
    .stApp {background:#22252d;color:#f5f5f7}
    [data-testid="stHeader"] {background:transparent}
    [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] {display:none!important}
    .stMainBlockContainer {max-width:1600px;padding:40px 24px 24px}
    </style>""", unsafe_allow_html=True)
    if st.button("← Voltar aos processos"):
        st.switch_page(st.Page(render_processos, default=True))
    numero = st.query_params.get("processo") or st.session_state.get("processo_detalhe_id")
    detalhes, erros = carregar_detalhes(numero)
    for erro in erros:
        st.warning(erro)
    if not detalhes:
        return
    assets = Path(__file__).resolve().parents[1] / "assets"
    template = (assets / "process-details.html").read_text(encoding="utf-8")
    css = (assets / "process-details.css").read_text(encoding="utf-8")
    js = (assets / "process-details.js").read_text(encoding="utf-8")
    payload = json.dumps(detalhes, ensure_ascii=True).replace("<", "\\u003c")
    html = template.replace("/*DETAIL_CSS*/", css).replace("/*DETAIL_JS*/", js).replace("/*DETAIL_DATA*/", payload)
    st.iframe(html, height="content")
