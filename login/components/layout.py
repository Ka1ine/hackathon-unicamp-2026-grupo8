from pathlib import Path
import streamlit as st


def apply_workspace_style():
    css = (Path(__file__).resolve().parents[1] / "assets" / "workspace.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_sidebar(page):
    with st.sidebar:
        st.markdown('''<div class="profile">
          <div class="avatar" role="img" aria-label="Avatar de Yasmin Almeida">
            <svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="18" r="8" fill="currentColor"/>
            <path d="M9 43v-5a15 15 0 0 1 30 0v5" fill="currentColor"/></svg>
          </div><div><strong>Yasmin Almeida</strong><span>Almeida & Associados</span></div>
        </div><div class="nav-caption">ESPAÇO DE TRABALHO</div>''', unsafe_allow_html=True)
        st.page_link(page, label="Processos", icon=":material/folder_open:", use_container_width=True)
        st.markdown('<div class="sidebar-brand">ENTER<span>◧</span></div>', unsafe_allow_html=True)
