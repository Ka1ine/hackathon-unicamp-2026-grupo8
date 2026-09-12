from pathlib import Path
from pypdf import PdfReader

def extract_text_from_file(file_path: Path) -> str:
    """Extracts raw text from PDF, TXT, or MD files."""
    if not file_path.exists():
        return ""

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        try:
            reader = PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text)
        except Exception as e:
            print(f"[ERROR] Falha ao ler PDF {file_path}: {e}")
            return ""

    elif extension in [".txt", ".md", ".json", ".csv"]:
        return file_path.read_text(encoding="utf-8", errors="ignore")

    return ""
