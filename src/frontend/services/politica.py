"""Consulta a política personalizada calculada pelo backend local."""
from typing import Any

import requests


API_BASE = "http://127.0.0.1:8000"


def calcular_politica(process_id: str, aggressiveness: int) -> tuple[dict[str, Any] | None, str | None]:
    """Retorna a política para a preferência atual, sem impedir a tela em caso de indisponibilidade."""
    try:
        response = requests.get(
            f"{API_BASE}/api/v1/monitoring/process/{process_id}/policy",
            params={"aggressiveness": aggressiveness},
            timeout=2,
        )
        payload = response.json()
        if response.ok and isinstance(payload, dict):
            return payload, None
        return None, str(payload.get("detail") or "Não foi possível recalcular a política.")
    except (requests.RequestException, ValueError):
        return None, "Não foi possível conectar ao serviço de cálculo da política."


def atualizar_politica(process_id: str, aggressiveness: int) -> tuple[dict[str, Any] | None, str | None]:
    """Pede ao backend para recalcular e gravar a política no JSON do processo."""
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/monitoring/process/{process_id}/policy",
            params={"aggressiveness": aggressiveness},
            timeout=10,
        )
        payload = response.json()
        if response.ok and isinstance(payload, dict):
            return payload, None
        return None, str(payload.get("detail") or "Não foi possível atualizar a política.")
    except (requests.RequestException, ValueError):
        return None, "Não foi possível conectar ao serviço de cálculo da política."
