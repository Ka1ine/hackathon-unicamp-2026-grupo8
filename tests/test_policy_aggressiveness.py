import numpy as np
import pandas as pd

from src.backend.policy.run_policy import SettlementEngine


class FixedClassifier:
    def predict_proba(self, features):
        return np.column_stack((np.full(len(features), 0.52), np.full(len(features), 0.48)))


class FixedRegressor:
    def predict(self, features):
        return np.full(len(features), 1000.0)


def test_aggressiveness_changes_the_decision_thresholds():
    engine = SettlementEngine(custo_operacional_defesa=400.0)
    engine.clf = FixedClassifier()
    engine.reg = FixedRegressor()
    engine.limiar_otimo = 0.45
    case = pd.DataFrame([
        {
            "Número do processo": "0000000-00.2024.8.10.0001",
            "Sub-assunto": "Golpe",
            "UF": "MA",
            "Valor da causa": 20000.0,
            "Comprovante de crédito": 1,
            "Contrato": 1,
            "Demonstrativo de evolução da dívida": 1,
            "Dossiê": 1,
            "Extrato": 1,
            "Laudo referenciado": 1,
            "has_comprovante_or_dossie": 1,
            "has_contrato_extrato": 1,
            "missing_contrato_extrato": 0,
            "qtd_subsidios": 6,
        }
    ])

    conservative = engine.predict(case, aggressiveness=0)
    aggressive = engine.predict(case, aggressiveness=100)

    assert conservative.iloc[0]["decisao_sugerida"] == "Acordo Estratégico"
    assert aggressive.iloc[0]["decisao_sugerida"] == "Defesa"
