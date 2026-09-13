"""Página isolada; HTML/CSS/JS ficam dentro de um iframe do Streamlit."""
import json
from pathlib import Path

import streamlit as st

from components.preferencias import agressividade
from services.detalhes import carregar_detalhes
from services.politica import atualizar_politica


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
    nivel_agressividade = agressividade()
    politica_personalizada = st.session_state.get(f"politica_personalizada_{numero}")
    nivel_calculado = st.session_state.get(f"politica_agressividade_{numero}")
    erro_politica = None
    if numero and nivel_calculado != nivel_agressividade:
        if nivel_agressividade == 50:
            politica_personalizada = None
        else:
            politica_personalizada = None
            politica_personalizada, erro_politica = atualizar_politica(numero, nivel_agressividade)
            if politica_personalizada:
                st.session_state[f"politica_personalizada_{numero}"] = politica_personalizada
                st.session_state[f"politica_agressividade_{numero}"] = nivel_agressividade
    detalhes, erros = carregar_detalhes(
        numero,
        politica_personalizada=politica_personalizada,
        aggressiveness=nivel_agressividade,
    )
    for erro in erros:
        st.warning(erro)
    if erro_politica:
        st.warning(f"Agressividade não pôde ser aplicada: {erro_politica}")
    if not detalhes:
        return
    assets = Path(__file__).resolve().parents[1] / "assets"
    template = (assets / "process-details.html").read_text(encoding="utf-8")
    css = (assets / "process-details.css").read_text(encoding="utf-8")
    js = (assets / "process-details.js").read_text(encoding="utf-8")
    payload = json.dumps(detalhes, ensure_ascii=True).replace("<", "\\u003c")
    html = template.replace("/*DETAIL_CSS*/", css).replace("/*DETAIL_JS*/", js).replace("/*DETAIL_DATA*/", payload)
    st.iframe(html, height="content")
