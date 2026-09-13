"""Inicia a API FastAPI e a interface Streamlit com um único comando."""
from pathlib import Path
import signal
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "src" / "frontend"


def main() -> int:
    processes = [
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT,
        ),
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.address", "127.0.0.1", "--server.port", "8501"],
            cwd=FRONTEND,
        ),
    ]
    print("Aplicação iniciada: http://127.0.0.1:8501")
    print("Documentação da API: http://127.0.0.1:8000/docs")

    def stop(*_args):
        for process in processes:
            if process.poll() is None:
                process.terminate()

    previous_handler = signal.signal(signal.SIGINT, stop)
    try:
        return processes[1].wait()
    finally:
        stop()
        signal.signal(signal.SIGINT, previous_handler)


if __name__ == "__main__":
    raise SystemExit(main())
