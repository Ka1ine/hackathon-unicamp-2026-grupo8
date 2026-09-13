import json

import pandas as pd

from src.backend.policy.policy_schemas import PolicyDecision
from src.backend.policy.policy_service import PolicyService


def test_update_case_policy_persists_the_recalculated_decision(tmp_path):
    process_id = "0000000-00.2024.8.10.0001"
    case_dir = tmp_path / "example_cases" / process_id
    case_dir.mkdir(parents=True)
    master_json = case_dir / f"_{process_id}.json"
    master_json.write_text(json.dumps({"timeline_data": {"events": []}}), encoding="utf-8")
    decision = PolicyDecision(
        estimated_operacional_cost=400.0,
        next_recommended_action="Acordo Estratégico",
        proposed_value_initial=5000.0,
        proposed_value_maximum=10000.0,
        risk_level="médio",
        aggressiveness=80,
        decision_explanation="Fundamentação estatística simulada.",
    )
    service = object.__new__(PolicyService)
    service.base_data_dir = tmp_path
    service.evaluate_case = lambda **_kwargs: decision

    result = service.update_case_policy(process_id, aggressiveness=80)
    persisted = json.loads(master_json.read_text(encoding="utf-8"))

    assert result == decision
    assert persisted["policy_data"] == decision.model_dump()


def test_decision_explanation_uses_similar_cases_statistics():
    service = object.__new__(PolicyService)
    service._training_data = pd.DataFrame(
        {
            "Sub-assunto": ["Golpe", "Golpe", "Genérico"],
            "target_loss": [1, 0, 1],
            "target_val": [12000.0, 0.0, 5000.0],
        }
    )

    explanation = service._decision_explanation(
        {"Sub-assunto": "Golpe"},
        {"probabilidade_derrota": 0.25, "decisao_sugerida": "Acordo Estratégico"},
    )

    assert "2 processos similares da categoria Golpe" in explanation
    assert "50,0% resultaram em condenações" in explanation
    assert "R$ 12.000,00" in explanation
    assert "êxito de 75,0%" in explanation
    assert "risco individual de 25,0%" in explanation
    assert explanation.endswith("Acordo Estratégico.")
