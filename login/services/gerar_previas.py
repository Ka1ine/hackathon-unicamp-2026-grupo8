"""Gere imagens locais uma vez: python login/services/gerar_previas.py.

Requer pdftoppm (Poppler) no PATH somente para gerar as imagens.
A plataforma continua funcionando com prévia textual quando ele não existe.
"""
import hashlib
from pathlib import Path
import shutil
import subprocess


def gerar_previas():
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise SystemExit("pdftoppm não encontrado. Instale Poppler para gerar prévias visuais; o download e a prévia textual continuam disponíveis.")
    data = Path(__file__).resolve().parents[2] / "data"
    total = 0
    for pasta in ("dados_processo1", "dados_processo2"):
        for pdf in sorted((data / pasta).glob("*.pdf")):
            cache = pdf.parent / ".previews" / hashlib.sha256(pdf.read_bytes()).hexdigest()[:20]
            cache.mkdir(parents=True, exist_ok=True)
            subprocess.run([renderer, "-scale-to", "1400", "-png", str(pdf), str(cache / "render")], check=True, capture_output=True)
            for png in cache.glob("render-*.png"):
                number = int(png.stem.split("-")[-1])
                png.replace(cache / f"page-{number}.png")
                total += 1
    print(f"{total} páginas renderizadas localmente.")


if __name__ == "__main__":
    gerar_previas()
