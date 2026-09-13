"""Carregamento da base consolidada usada na tela de histórico."""
from pathlib import Path

import pandas as pd
import streamlit as st


RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_DADOS = RAIZ / "data" / "dados.xlsx"


def carregar_historico():
    """Retorna resultados e cobertura de subsídios por processo."""
    if not ARQUIVO_DADOS.exists():
        return pd.DataFrame(), [f"Arquivo não encontrado: {ARQUIVO_DADOS.name}."]
    estatistica = ARQUIVO_DADOS.stat()
    return _ler_historico(estatistica.st_mtime_ns, estatistica.st_size)


@st.cache_data(show_spinner=False)
def _ler_historico(versao, tamanho):
    """Lê novamente a planilha quando o arquivo de origem for atualizado."""
    try:
        resultados = pd.read_excel(ARQUIVO_DADOS, sheet_name="Resultados dos processos")
        subsidios = pd.read_excel(
            ARQUIVO_DADOS,
            sheet_name="Subsídios disponibilizados",
            header=1,
        )
    except Exception as exc:
        return pd.DataFrame(), [f"Não foi possível ler a base histórica: {exc}"]

    resultados = resultados.rename(
        columns={
            "Número do processo": "processo",
            "Resultado macro": "resultado_macro",
            "Resultado micro": "resultado_micro",
            "Valor da causa": "valor_causa",
            "Valor da condenação/indenização": "valor_condenacao",
        }
    )
    subsidios = subsidios.rename(columns={"Número do processos": "processo"})

    if "processo" not in resultados or "processo" not in subsidios:
        return pd.DataFrame(), ["A planilha não contém a coluna de número do processo esperada."]

    resultados["processo"] = resultados["processo"].astype(str).str.strip()
    subsidios["processo"] = subsidios["processo"].astype(str).str.strip()
    colunas_subsidio = [coluna for coluna in subsidios.columns if coluna != "processo"]
    subsidios["subsidios_disponiveis"] = (
        subsidios[colunas_subsidio]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .sum(axis=1)
        .astype(int)
    )

    dados = resultados.merge(
        subsidios[["processo", "subsidios_disponiveis"]],
        on="processo",
        how="left",
    )
    dados["subsidios_disponiveis"] = dados["subsidios_disponiveis"].fillna(0).astype(int)
    for coluna in ("valor_causa", "valor_condenacao"):
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce").fillna(0.0)

    return dados, []
