"""Leitura dos autos fornecidos, sem valores fixos ou inferência jurídica."""
from pathlib import Path
from decimal import Decimal
import json
import re

from pypdf import PdfReader
import streamlit as st

RAIZ = Path(__file__).resolve().parents[3]
PASTA_DADOS = RAIZ / "data"
CASOS_EXEMPLO = (
    "0801234-56.2024.8.10.0001",
    "0654321-09.2024.8.04.0001",
)


def extrair_processo(caminho):
    reader = PdfReader(caminho)
    texto = " ".join(" ".join(page.extract_text() or "" for page in reader.pages).split())
    if not texto:
        raise ValueError("PDF sem texto extraível; é necessário OCR.")
    numero = re.search(r"Processo\s*n[º°o.]?\s*(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", texto, re.I)
    nome = re.search(r"OUTORGANTE:\s*(.+?),\s*brasileir[oa]", texto, re.I)
    valor = re.search(r"D[áa]-se\s+[àa]\s+causa\s+o\s+valor\s+de\s+R\$\s*([\d.]+,\d{2})", texto, re.I)
    faltantes = [campo for campo, resultado in (("número", numero), ("nome da parte", nome), ("valor da causa", valor)) if not resultado]
    if faltantes:
        raise ValueError("Não foi possível identificar: " + ", ".join(faltantes) + ".")
    return {
        "id": numero.group(1),
        "nome": nome.group(1).strip(),
        "valor": Decimal(valor.group(1).replace(".", "").replace(",", ".")),
        "risco": "A avaliar",
        "recomendacao": "A avaliar",
        "fonte": str(caminho),
    }


@st.cache_data(show_spinner=False)
def _ler_pdf(caminho, versao):
    # mtime e tamanho invalidam o cache quando o documento muda.
    return extrair_processo(Path(caminho))


@st.cache_data(show_spinner=False)
def _ler_politica(caminho, versao):
    """Lê risco e recomendação já calculados no JSON consolidado."""
    conteudo = json.loads(Path(caminho).read_text(encoding="utf-8"))
    politica = conteudo.get("policy_data")
    if not isinstance(politica, dict):
        raise ValueError("bloco policy_data ausente ou inválido")
    return politica


def normalizar_risco(valor):
    riscos = {
        "alto": "Alto",
        "medio": "Médio",
        "médio": "Médio",
        "baixo": "Baixo",
    }
    return riscos.get(str(valor or "").strip().casefold(), "A avaliar")


def carregar_processos(raiz=RAIZ):
    processos, erros = [], []
    pasta_dados = Path(raiz) / "data"
    for caso_id in CASOS_EXEMPLO:
        diretorio = pasta_dados / "example_cases" / caso_id
        arquivos = sorted(diretorio.glob("01_Autos_Processo_*.pdf"))
        if len(arquivos) != 1:
            erros.append(f"{caso_id}: esperado um PDF de autos; encontrados {len(arquivos)}.")
            continue
        arquivo = arquivos[0]
        try:
            stat = arquivo.stat()
            processo = dict(_ler_pdf(str(arquivo), (stat.st_mtime_ns, stat.st_size)))
        except Exception as exc:
            erros.append(f"Não foi possível ler {arquivo.name}: {exc}")
            continue

        arquivos_json = sorted(diretorio.glob("*.json"))
        if arquivos_json:
            arquivo_json = arquivos_json[0]
            try:
                stat_json = arquivo_json.stat()
                politica = _ler_politica(
                    str(arquivo_json),
                    (stat_json.st_mtime_ns, stat_json.st_size),
                )
                processo["risco"] = normalizar_risco(politica.get("risk_level"))
                processo["recomendacao"] = (
                    str(politica.get("next_recommended_action") or "").strip()
                    or "A avaliar"
                )
            except Exception as exc:
                erros.append(
                    f"Não foi possível ler a política de {processo['id']}: {exc}."
                )
        processos.append(processo)
    return processos, erros
