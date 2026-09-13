"""Preferências globais mantidas durante a sessão do usuário."""
from html import escape

import streamlit as st


PADROES = {
    "perfil_nome": "Yasmin Kaline",
    "perfil_empresa": "Banco Unicamp",
    "pref_interface_compacta": False,
    "pref_reduzir_animacoes": False,
}


def iniciar_preferencias():
    for chave, valor in PADROES.items():
        st.session_state.setdefault(chave, valor)


def perfil():
    iniciar_preferencias()
    return (
        escape(st.session_state["perfil_nome"].strip() or PADROES["perfil_nome"]),
        escape(st.session_state["perfil_empresa"].strip() or PADROES["perfil_empresa"]),
    )


def aplicar_preferencias_interface():
    iniciar_preferencias()
    estilos = []
    if st.session_state["pref_interface_compacta"]:
        estilos.append(
            """
            .stMainBlockContainer { padding-top: 32px !important; }
            .linha { padding: 10px 18px !important; }
            .kpi { padding: 13px !important; }
            """
        )
    if st.session_state["pref_reduzir_animacoes"]:
        estilos.append(
            """
            *, *::before, *::after {
                animation: none !important;
                transition: none !important;
                scroll-behavior: auto !important;
            }
            """
        )
    if estilos:
        st.markdown(f"<style>{''.join(estilos)}</style>", unsafe_allow_html=True)
