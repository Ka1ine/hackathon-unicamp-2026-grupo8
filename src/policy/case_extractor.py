import os
import re
import glob
from pathlib import Path
from pypdf import PdfReader

TR_TO_UF = {
    '01': 'AC', '02': 'AL', '03': 'AP', '04': 'AM', '05': 'BA',
    '06': 'CE', '07': 'DF', '08': 'ES', '09': 'GO', '10': 'MA',
    '11': 'MT', '12': 'MS', '13': 'MG', '14': 'PA', '15': 'PB',
    '16': 'PR', '17': 'PE', '18': 'PI', '19': 'RJ', '20': 'RN',
    '21': 'RS', '22': 'RO', '23': 'RR', '24': 'SC', '25': 'SE',
    '26': 'SP', '27': 'TO'
}


def extract_text_from_pdf(pdf_path: str, max_pages: int = 5) -> str:
    """Extrai texto das primeiras páginas de um arquivo PDF."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages[:max_pages]:
        text += page.extract_text() or ""
    return text


def parse_case_folder(folder_path: str) -> dict:
    """
    Analisa os PDFs de uma pasta de processo e extrai os dados
    no formato exato da base de dados de treinamento.
    """
    folder = Path(folder_path)
    pdf_files = list(folder.glob("*.pdf"))
    
    if not pdf_files:
        raise ValueError(f"Nenhum PDF encontrado na pasta: {folder_path}")

    # 1. Identificar presença dos 6 Subsídios pelo nome do arquivo
    filenames_lower = [f.name.lower() for f in pdf_files]
    
    has_contrato = int(any("contrato" in f for f in filenames_lower))
    has_extrato = int(any("extrato" in f for f in filenames_lower))
    has_bacen = int(any("comprovante" in f or "bacen" in f for f in filenames_lower))
    has_dossie = int(any("dossie" in f or "veritas" in f for f in filenames_lower))
    has_evolucao = int(any("evolucao" in f or "demonstrativo" in f for f in filenames_lower))
    has_laudo = int(any("laudo" in f for f in filenames_lower))

    # 2. Localizar e ler a Petição Inicial (Autos)
    autos_file = next((f for f in pdf_files if "autos" in f.name.lower()), pdf_files[0])
    autos_text = extract_text_from_pdf(str(autos_file), max_pages=15)

    # A. Número do Processo (Padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO)
    proc_match = re.search(r'(\d{7}[-.]\d{2}[-.]\d{4}[-.]8[-.]\d{2}[-.]\d{4})', autos_text)
    if proc_match:
        raw_proc = proc_match.group(1).replace('-', '.').split('.')
        num_processo = f"{raw_proc[0]}-{raw_proc[1]}.{raw_proc[2]}.8.{raw_proc[4]}.{raw_proc[5]}"
        tr_code = raw_proc[4]
    else:
        tr_match = re.search(r'-8-(\d{2})-', folder.name)
        tr_code = tr_match.group(1) if tr_match else '13'
        num_processo = folder.name

    # B. UF a partir do código do tribunal
    uf = TR_TO_UF.get(tr_code, 'MG')

    # C. Valor da Causa
    valor_causa = 15000.0  # Fallback médio
    causa_match = re.search(r'(?:valor\s+d[ea]\s+causa.*?R\$\s*|d[áa]-se\s+[àa]\s+causa.*?R\$\s*)([\d.,]+)', autos_text, re.IGNORECASE)
    if causa_match:
        raw_val = causa_match.group(1).replace('.', '').replace(',', '.')
        try:
            valor_causa = float(raw_val)
        except ValueError:
            pass

    # D. Sub-assunto (Golpe vs Genérico)
    termos_golpe = ['golpe', 'fraude', 'estelionato', 'terceiro', 'clonagem', 'falso']
    is_golpe = any(term in autos_text.lower() for term in termos_golpe)
    sub_assunto = 'Golpe' if is_golpe else 'Genérico'

    # Monta a linha pronta
    row = {
        'Número do processo': num_processo,
        'UF': uf,
        'Assunto': 'Não reconhece operação',
        'Sub-assunto': sub_assunto,
        'Valor da causa': valor_causa,
        'Contrato': has_contrato,
        'Extrato': has_extrato,
        'Comprovante de crédito': has_bacen,
        'Dossiê': has_dossie,
        'Demonstrativo de evolução da dívida': has_evolucao,
        'Laudo referenciado': has_laudo,
        # Features derivadas
        'qtd_subsidios': sum([has_contrato, has_extrato, has_bacen, has_dossie, has_evolucao, has_laudo]),
        'has_contrato_extrato': int(has_contrato == 1 and has_extrato == 1),
        'missing_contrato_extrato': int(has_contrato == 0 and has_extrato == 0),
        'has_comprovante_or_dossie': int(has_bacen == 1 or has_dossie == 1)
    }
    return row