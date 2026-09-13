import json
import os
import re
from datetime import datetime
from pathlib import Path

from src.backend.monitoring.subsidio_extractor import SubsidioExtractor
from src.backend.monitoring.subsidio_schemas import (
    CompleteSubsidioAnalysis,
    ComprovanteCreditoDocument,
    ContratoDocument,
    DemonstrativoDividaDocument,
    DossieDocument,
    ExtratoDocument,
    LaudoReferenciadoDocument
)
from src.backend.utils.pdf_utils import extract_text_from_file


class SubsidioService:
    """Service responsible for loading, parsing, and caching supporting legal documents."""

    # Updated to match the actual folder name in the file tree
    def __init__(self, base_data_dir: Path = Path("data/example_cases"), cache_dir: Path = Path("data/cache")):
        self.base_data_dir = base_data_dir
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.extractor = SubsidioExtractor()

    def analyze_process_subsidios(self, process_id: str, force_refresh: bool = False) -> CompleteSubsidioAnalysis:
        cache_file = self.cache_dir / f"{process_id}_subsidios.json"

        if cache_file.exists() and not force_refresh:
            with open(cache_file, "r", encoding="utf-8") as file_handler:
                return CompleteSubsidioAnalysis(**json.load(file_handler))

        process_dir = self.base_data_dir / process_id
        if not process_dir.exists():
            return CompleteSubsidioAnalysis(process_id=process_id)

        analysis = CompleteSubsidioAnalysis(process_id=process_id)

        doc_mappings = [
            (re.compile(r"(?i).*comprovante.*credito.*"), "comprovante_credito", "comprovantes_credito", ComprovanteCreditoDocument),
            (re.compile(r"(?i).*contrato.*"), "contrato", "contratos", ContratoDocument),
            (re.compile(r"(?i).*demonstrativo.*divida.*"), "demonstrativo_divida", "demonstrativos_divida", DemonstrativoDividaDocument),
            (re.compile(r"(?i).*dossie.*"), "dossie", "dossies", DossieDocument),
            (re.compile(r"(?i).*extrato.*"), "extrato", "extratos", ExtratoDocument),
            (re.compile(r"(?i).*laudo.*referenciado.*"), "laudo_referenciado", "laudos_referenciados", LaudoReferenciadoDocument)
        ]

        # Flattened logic: Iterate over the PDFs exactly once
        for target_file in process_dir.glob("*.pdf"):
            for pattern, prefix, list_attr, document_class in doc_mappings:
                if pattern.search(target_file.name):
                    print(f"[DEBUG] Processing {prefix} file: {target_file.name}")

                    timestamp = os.path.getmtime(target_file)
                    added_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                    raw_text = extract_text_from_file(target_file)

                    if raw_text:
                        parsed_result = self.extractor.parse_document(prefix, raw_text)

                        doc_item = document_class(
                            added_date=added_date,
                            extracted_info=parsed_result,
                            file_name=target_file.name
                        )

                        getattr(analysis, list_attr).append(doc_item)

                    # Halt the mapping search for this specific file once a match is found
                    break

        with open(cache_file, "w", encoding="utf-8") as file_handler:
            file_handler.write(analysis.model_dump_json(indent=4))

        return analysis
