import json
import os
from datetime import datetime
from pathlib import Path

from src.monitoring.subsidio_extractor import SubsidioExtractor
from src.monitoring.subsidio_schemas import (
    CompleteSubsidioAnalysis,
    ComprovanteCreditoDocument,
    ContratoDocument,
    DemonstrativoDividaDocument,
    DossieDocument,
    ExtratoDocument,
    LaudoReferenciadoDocument
)
from src.utils.pdf_utils import extract_text_from_file


class SubsidioService:
    """Service responsible for loading, parsing, and caching supporting legal documents."""

    def __init__(self, base_data_dir: Path = Path("data/subsidios"), cache_dir: Path = Path("data/monitoramento_cache")):
        """Initializes the service with data directories and the extraction engine."""
        self.base_data_dir = base_data_dir
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.extractor = SubsidioExtractor()

    def analyze_process_subsidios(self, process_id: str, force_refresh: bool = False) -> CompleteSubsidioAnalysis:
        """Analyzes all supporting documents for a specific process ID and returns structured data."""
        cache_file = self.cache_dir / f"{process_id}_subsidios.json"

        # Return cached data if available and refresh is not forced
        if cache_file.exists() and not force_refresh:
            with open(cache_file, "r", encoding="utf-8") as file_handler:
                return CompleteSubsidioAnalysis(**json.load(file_handler))

        # Check if the base directory for this process exists
        process_dir = self.base_data_dir / process_id
        if not process_dir.exists():
            return CompleteSubsidioAnalysis(process_id=process_id)

        # Initialize the consolidated analysis container
        analysis = CompleteSubsidioAnalysis(process_id=process_id)

        # Map file prefixes to their schema properties and document wrapper classes
        doc_mappings = [
            ("comprovante_credito", "comprovantes_credito", ComprovanteCreditoDocument),
            ("contrato", "contratos", ContratoDocument),
            ("demonstrativo_divida", "demonstrativos_divida", DemonstrativoDividaDocument),
            ("dossie", "dossies", DossieDocument),
            ("extrato", "extratos", ExtratoDocument),
            ("laudo_referenciado", "laudos_referenciados", LaudoReferenciadoDocument)
        ]

        # Iterate over each document type and process all matching files
        for prefix, list_attr, document_class in doc_mappings:
            matching_files = list(process_dir.glob(f"{prefix}*.*"))
            
            for target_file in matching_files:
                print(f"[DEBUG] Processing {prefix} file: {target_file.name}")
                
                # Retrieve file metadata (last modified timestamp)
                timestamp = os.path.getmtime(target_file)
                added_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                # Extract plain text from the file
                raw_text = extract_text_from_file(target_file)
                
                if raw_text:
                    # Run LLM extraction based on the document type
                    parsed_result = self.extractor.parse_document(prefix, raw_text)
                    
                    # Wrap the extracted information with its physical metadata
                    doc_item = document_class(
                        added_date=added_date,
                        extracted_info=parsed_result,
                        file_name=target_file.name
                    )
                    
                    # Append the processed document to the appropriate list in the main schema
                    getattr(analysis, list_attr).append(doc_item)

        # Save the finalized analysis back to the cache
        with open(cache_file, "w", encoding="utf-8") as file_handler:
            file_handler.write(analysis.model_dump_json(indent=4))

        return analysis
