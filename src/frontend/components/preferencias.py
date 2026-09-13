"""Preferências globais mantidas durante a sessão do usuário."""
from html import escape

import streamlit as st


PADROES = {
    "perfil_nome": "Yasmin Kaline",
    "perfil_empresa": "Banco Unicamp",
    "agressividade": 50,
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


def agressividade():
    """Devolve a preferência decisória atual como percentual seguro."""
    iniciar_preferencias()
    return max(0, min(100, int(st.session_state["agressividade"])))


def salvar_agressividade():
    """Copia o valor transitório do widget para a preferência durável da sessão."""
    st.session_state["agressividade"] = max(
        0,
        min(100, int(st.session_state["_pref_agressividade"])),
    )

