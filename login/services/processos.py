"""Leitura dos autos fornecidos, sem valores fixos ou inferência jurídica."""
from pathlib import Path
from decimal import Decimal
import re

from pypdf import PdfReader
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
PASTAS = ("Dados_processo1", "Dados_processo_2")


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


def carregar_processos(raiz=RAIZ):
    processos, erros = [], []
    for pasta in PASTAS:
        diretorio = Path(raiz) / pasta
        arquivos = sorted(diretorio.glob("01_Autos_Processo_*.pdf"))
        if len(arquivos) != 1:
            erros.append(f"{pasta}: esperado um PDF de autos; encontrados {len(arquivos)}.")
            continue
        arquivo = arquivos[0]
        try:
            stat = arquivo.stat()
            processos.append(_ler_pdf(str(arquivo), (stat.st_mtime_ns, stat.st_size)))
        except Exception as exc:
            erros.append(f"Não foi possível ler {arquivo.name}: {exc}")
    return processos, erros
