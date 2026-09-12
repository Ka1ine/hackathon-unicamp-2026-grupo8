from pathlib import Path
from src.monitoring.extractor import CaseProgressionExtractor
from src.monitoring.schemas import CaseProgressionResponse

class MonitoringService:
    def __init__(self, base_data_dir: Path = Path("data/processos_exemplo")):
        self.base_data_dir = base_data_dir
        self.extractor = CaseProgressionExtractor()

    def load_case_files(self, process_id: str) -> str:
        case_dir = self.base_data_dir / process_id / "autos"
        if not case_dir.exists():
            raise FileNotFoundError(f"Pasta de autos para {process_id} não encontrada em {case_dir}")

        combined_text = []
        for file_path in sorted(case_dir.glob("*.*")):
            if file_path.suffix.lower() in [".txt", ".md"]:
                combined_text.append(f"--- Documento: {file_path.name} ---\n" + file_path.read_text(encoding="utf-8"))
        
        return "\n\n".join(combined_text)

    def analyze_case(self, process_id: str) -> CaseProgressionResponse:
        case_text = self.load_case_files(process_id)
        return self.extractor.extract_progression(process_id=process_id, case_text=case_text)
    