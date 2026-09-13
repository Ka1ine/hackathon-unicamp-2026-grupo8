"""Documentos locais e dados de apresentação do detalhe de um processo."""
import base64
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re

from pypdf import PdfReader

from services.processos import carregar_processos


def carregar_linha_do_tempo(numero, erros):
    """Lê os eventos extraídos dos autos e descarta outras fontes."""
    timeline_vazia = {
        "current_stage": None,
        "next_recommended_action": None,
        "events": [],
    }
    pasta_processo = Path(__file__).resolve().parents[2] / "data" / "example_cases" / str(numero)
    arquivos_json = sorted(pasta_processo.glob("*.json"))
    if not arquivos_json:
        return timeline_vazia

    try:
        conteudo = json.loads(arquivos_json[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        erros.append("Não foi possível ler a linha do tempo deste processo.")
        return timeline_vazia

    timeline = conteudo.get("timeline_data") or {}
    eventos = timeline.get("timeline") or []
    eventos_dos_autos = [
        evento for evento in eventos
        if isinstance(evento, dict) and evento.get("source") == "file"
    ]
    return {
        "current_stage": timeline.get("current_stage"),
        "next_recommended_action": timeline.get("next_recommended_action"),
        "events": eventos_dos_autos,
    }


def carregar_politica(numero, erros):
    """Lê a recomendação estratégica já calculada no JSON consolidado."""
    pasta_processo = Path(__file__).resolve().parents[2] / "data" / "example_cases" / str(numero)
    arquivos_json = sorted(pasta_processo.glob("*.json"))
    if not arquivos_json:
        return None
    try:
        conteudo = json.loads(arquivos_json[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        erros.append("Não foi possível ler a análise estratégica deste processo.")
        return None
    politica = conteudo.get("policy_data")
    return politica if isinstance(politica, dict) else None


def extrair_perfil_autor(texto, nome):
    """Extrai somente características explicitamente declaradas nos autos."""
    perfil = [{"label": "Nome", "value": nome}]
    qualificacao = re.search(
        rf"{re.escape(nome)}.*?\bbrasileir([oa])\b",
        texto,
        re.IGNORECASE,
    )
    if qualificacao:
        perfil.append({
            "label": "Gênero",
            "value": "Feminino" if qualificacao.group(1).casefold() == "a" else "Masculino",
        })
    if re.search(r"\bpessoa idosa\b", texto, re.IGNORECASE):
        perfil.append({"label": "Idade", "value": "Pessoa idosa"})
    localizacao = re.search(
        r"residente e domiciliad[oa].{0,300}?,\s*([^,]+/[A-Z]{2}),\s*CEP",
        texto,
        re.IGNORECASE,
    )
    if localizacao:
        perfil.append({"label": "Localização", "value": localizacao.group(1).strip()})
    if re.search(
        r"(?:subsistência inteiramente custeada|renda mensal proveniente exclusivamente)"
        r".{0,100}?benefício previdenciário",
        texto,
        re.IGNORECASE,
    ):
        perfil.append({"label": "Renda", "value": "Exclusivamente do benefício previdenciário"})
    if re.search(r"aposentad[oa]\s+pelo\s+Regime Geral de Previdência Social", texto, re.IGNORECASE):
        perfil.append({"label": "Tipo de benefício", "value": "Aposentadoria pelo RGPS (INSS)"})
    escolaridade = re.search(r"\bbaixa escolaridade\b", texto, re.IGNORECASE)
    if escolaridade:
        perfil.append({"label": "Instrução", "value": "Baixa escolaridade"})
    return perfil


def resumir_linha_do_tempo(linha_do_tempo):
    """Obtém a data inicial e a ação pendente mais recente dos autos."""
    eventos = linha_do_tempo.get("events") or []
    datas_validas = sorted(
        evento["date"]
        for evento in eventos
        if isinstance(evento.get("date"), str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}", evento["date"])
    )
    eventos_recentes = sorted(
        eventos,
        key=lambda evento: evento.get("date") or "",
        reverse=True,
    )
    acao_pendente = next(
        (
            evento.get("action_required")
            for evento in eventos_recentes
            if isinstance(evento.get("action_required"), str)
            and evento["action_required"].strip()
            and not evento["action_required"].strip().casefold().startswith("aguardar")
        ),
        "Nenhuma ação pendente",
    )
    return {
        "start_date": datas_validas[0] if datas_validas else None,
        "pending_action": acao_pendente,
    }


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
    paginas_autos = PdfReader(autos).pages
    texto = " ".join(" ".join(pagina.extract_text() or "" for pagina in paginas_autos).split())
    banco = re.search(r"em face de\s+(BANCO .+?S\.A\.)", texto, re.I)
    vara = re.search(r"Processo\s+n[º°o.]?\s+[\d.\-]+\s*[-–]\s*(.*?)\s*[-–]\s*Página", texto, re.I)
    linha_do_tempo = carregar_linha_do_tempo(processo["id"], erros)
    resumo_linha_do_tempo = resumir_linha_do_tempo(linha_do_tempo)
    politica = carregar_politica(processo["id"], erros)
    return {
        "id": processo["id"], "name": processo["nome"],
        "amount": float(processo["valor"]),
        "bank": banco.group(1) if banco else "Não informado",
        "court": vara.group(1) if vara else "Não informado",
        "start_date": resumo_linha_do_tempo["start_date"],
        "pending_action": resumo_linha_do_tempo["pending_action"],
        "author_profile": extrair_perfil_autor(texto, processo["nome"]),
        "policy": politica,
        "status": "A avaliar", "documents": documentos,
        "timeline": linha_do_tempo,
    }, erros
