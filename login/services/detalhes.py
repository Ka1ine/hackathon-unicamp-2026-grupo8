"""Documentos locais e metadados de apresentação, sem análise jurídica ou API."""
import base64
import hashlib
from io import BytesIO
from pathlib import Path
import re

from pypdf import PdfReader

from services.processos import carregar_processos


def nome_documento(nome):
    texto = re.sub(r"^\d+_", "", Path(nome).stem)
    for chave, rotulo in (
        ("Autos_Processo", "Autos do processo"),
        ("Contrato", "Contrato"),
        ("Extrato", "Extrato bancário"),
        ("Comprovante", "Comprovante de crédito"),
        ("Dossie", "Dossiê"),
        ("Demonstrativo", "Evolução da dívida"),
        ("Laudo", "Laudo referenciado"),
    ):
        if texto.startswith(chave):
            return rotulo
    return texto.replace("_", " ")


def ler_documento(arquivo):
    conteudo = arquivo.read_bytes()
    reader = PdfReader(BytesIO(conteudo))
    # Prévias vinculadas ao hash: um PDF alterado nunca reutiliza imagem antiga.
    cache = arquivo.parent / ".previews" / hashlib.sha256(conteudo).hexdigest()[:20]
    previews = []
    for index, page in enumerate(reader.pages, 1):
        imagem = cache / f"page-{index}.png"
        previews.append({
            "image": base64.b64encode(imagem.read_bytes()).decode("ascii") if imagem.exists() else None,
            "text": page.extract_text() or "Prévia não disponível. Baixe o PDF original para consultar esta página.",
        })
    return {
        "id": arquivo.name,
        "name": nome_documento(arquivo.name),
        "filename": arquivo.name,
        "pages": len(reader.pages),
        "bytes": len(conteudo),
        "base64": base64.b64encode(conteudo).decode("ascii"),
        "previews": previews,
    }


def carregar_detalhes(numero):
    processos, erros = carregar_processos()
    processo = next((p for p in processos if p["id"] == numero), None)
    if processo is None:
        return None, erros or ["Selecione um processo na listagem para abrir seus detalhes."]
    autos = Path(processo["fonte"])
    documentos = []
    for arquivo in sorted(autos.parent.glob("*.pdf")):
        try:
            documentos.append(ler_documento(arquivo))
        except Exception:
            erros.append(f"Não foi possível abrir {arquivo.name}.")
    texto = " ".join((PdfReader(autos).pages[0].extract_text() or "").split())
    banco = re.search(r"em face de\s+(BANCO .+?S\.A\.)", texto, re.I)
    vara = re.search(r"Processo\s+n[º°o.]?\s+[\d.\-]+\s*[-–]\s*(.*?)\s*[-–]\s*Página", texto, re.I)
    valor = re.search(r"valor liberado de\s+R\$\s*([\d.]+,\d{2})", texto, re.I)
    parcela = re.search(r"parcelas mensais de\s+R\$\s*([\d.]+,\d{2})", texto, re.I)
    return {
        "id": processo["id"], "name": processo["nome"],
        "amount": float(processo["valor"]),
        "bank": banco.group(1) if banco else "Não informado",
        "court": vara.group(1) if vara else "Não informado",
        "loan": "R$ " + valor.group(1) if valor else "Não informado",
        "installment": "R$ " + parcela.group(1) if parcela else "Não informado",
        "status": "A avaliar", "documents": documentos,
    }, erros
