import os
import json
from datetime import datetime
from pathlib import Path
from src.utils.pdf_utils import extract_text_from_file
from src.monitoring.subsidio_extractor import SubsidioExtractor
from src.monitoring.subsidio_schemas import (
    CompleteSubsidioAnalysis, ContratoDocument, ExtratoDocument,
    ComprovanteCreditoDocument, DossieDocument, 
    DemonstrativoDividaDocument, LaudoReferenciadoDocument
)

class SubsidioService:
    def __init__(self, base_data_dir: Path = Path("data/subsidios"), cache_dir: Path = Path("data/monitoramento_cache")):
        self.base_data_dir = base_data_dir
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = SubsidioExtractor()

    def analyze_process_subsidios(self, process_id: str, force_refresh: bool = False) -> CompleteSubsidioAnalysis:
        cache_file = self.cache_dir / f"{process_id}_subsidios.json"

        if cache_file.exists() and not force_refresh:
            with open(cache_file, "r", encoding="utf-8") as f:
                return CompleteSubsidioAnalysis(**json.load(f))

        process_dir = self.base_data_dir / process_id
        if not process_dir.exists():
            return CompleteSubsidioAnalysis(process_id=process_id)

        analysis = CompleteSubsidioAnalysis(process_id=process_id)

        # Mapeamento do prefixo do arquivo para o atributo da lista no modelo principal
        # e para a classe Document que empacota os resultados
        doc_mappings = [
            ("contrato", "contratos", ContratoDocument),
            ("extrato", "extratos", ExtratoDocument),
            ("comprovante_credito", "comprovantes_credito", ComprovanteCreditoDocument),
            ("dossie", "dossies", DossieDocument),
            ("demonstrativo_divida", "demonstrativos_divida", DemonstrativoDividaDocument),
            ("laudo_referenciado", "laudos_referenciados", LaudoReferenciadoDocument)
        ]

        for prefix, list_attr, document_class in doc_mappings:
            # Busca todos os arquivos que começam com o prefixo
            matching_files = list(process_dir.glob(f"{prefix}*.*"))
            
            for target_file in matching_files:
                print(f"[DEBUG] Processing {prefix} file: {target_file.name}")
                
                # Obtém a data de modificação/criação do arquivo
                timestamp = os.path.getmtime(target_file)
                added_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                raw_text = extract_text_from_file(target_file)
                if raw_text:
                    parsed_result = self.extractor.parse_document(prefix, raw_text)
                    
                    # Cria o objeto Document (Ex: ContratoDocument)
                    doc_item = document_class(
                        file_name=target_file.name,
                        added_date=added_date,
                        extracted_info=parsed_result
                    )
                    
                    # Adiciona à lista correspondente no CompleteSubsidioAnalysis
                    getattr(analysis, list_attr).append(doc_item)

        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(analysis.model_dump_json(indent=4))

        return analysis
