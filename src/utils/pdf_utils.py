from pathlib import Path

from pypdf import PdfReader


def extract_text_from_file(file_path: Path) -> str:
    """Extracts raw text from various file formats including CSV, JSON, MD, PDF, and TXT."""
    # Return early if the target file does not exist
    if not file_path.exists():
        return ""

    extension = file_path.suffix.lower()

    # Handle PDF parsing
    if extension == ".pdf":
        try:
            pages_text = []
            reader = PdfReader(file_path)
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
                    
            return "\n".join(pages_text)
        except Exception as e:
            print(f"[ERROR] Falha ao ler PDF {file_path}: {e}")
            return ""

    # Handle plain text formats
    elif extension in [".csv", ".json", ".md", ".txt"]:
        return file_path.read_text(encoding="utf-8", errors="ignore")

    return ""
