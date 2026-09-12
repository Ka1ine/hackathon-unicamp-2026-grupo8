from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

FEATURE_COLS = [
    "UF", "Sub-assunto", "Valor da causa",
    "Contrato", "Extrato", "Comprovante de crédito", "Dossiê",
    "Demonstrativo de evolução da dívida", "Laudo referenciado",
    "qtd_subsidios", "has_contrato_extrato", "missing_contrato_extrato",
    "has_comprovante_or_dossie"
]
CAT_COLS = ["UF", "Sub-assunto"]


def load_and_preprocess_training_data(excel_path: str = "Hackaton_Enter_Base_Candidatos.xlsx") -> pd.DataFrame:
    """Carrega as abas da planilha e prepara o DataFrame de treino."""
    df_res = pd.read_excel(excel_path, sheet_name="Resultados dos processos")
    df_sub = pd.read_excel(excel_path, sheet_name="Subsídios disponibilizados", header=1)
    df_sub = df_sub.rename(columns={"Número do processos": "Número do processo"})
    df = pd.merge(df_res, df_sub, on="Número do processo")

    sub_cols = ["Contrato", "Extrato", "Comprovante de crédito", "Dossiê", "Demonstrativo de evolução da dívida", "Laudo referenciado"]
    for c in sub_cols:
        df[c] = df[c].astype(int)

    df["qtd_subsidios"] = df[sub_cols].sum(axis=1)
    df["has_contrato_extrato"] = ((df["Contrato"] == 1) & (df["Extrato"] == 1)).astype(int)
    df["missing_contrato_extrato"] = ((df["Contrato"] == 0) & (df["Extrato"] == 0)).astype(int)
    df["has_comprovante_or_dossie"] = ((df["Comprovante de crédito"] == 1) | (df["Dossiê"] == 1)).astype(int)

    for col in CAT_COLS:
        df[col] = df[col].astype("category")

    df["target_loss"] = (df["Resultado macro"] == "Não Êxito").astype(int)
    df["target_val"] = df["Valor da condenação/indenização"]
    return df


class SettlementEngine:
    def __init__(self, custo_operacional_defesa: float = 400.0):
        self.custo_operacional_defesa = custo_operacional_defesa
        self.clf = HistGradientBoostingClassifier(
            categorical_features=CAT_COLS, max_iter=200, learning_rate=0.05, max_leaf_nodes=31, random_state=42
        )
        self.reg = HistGradientBoostingRegressor(
            categorical_features=CAT_COLS, max_iter=200, learning_rate=0.05, max_leaf_nodes=31, random_state=42
        )
        self.limiar_otimo = 0.45

    def fit(self, df_train: pd.DataFrame):
        X = df_train[FEATURE_COLS]
        y_clf = df_train["target_loss"]
        y_reg = df_train["target_val"]

        self.clf.fit(X, y_clf)
        mask_condenado = (y_clf == 1)
        self.reg.fit(X[mask_condenado], y_reg[mask_condenado])

        # Otimização do limiar econômico na carteira de treino
        p_loss = self.clf.predict_proba(X)[:, 1]
        custo_status_quo_real = df_train["target_val"] + self.custo_operacional_defesa
        custo_status_quo_total = custo_status_quo_real.sum()
        custo_acordo_mercado = df_train["Valor da causa"] * 0.30
        taxa_aceite_acordo = 0.55

        thresholds = np.linspace(0.10, 0.90, 81)
        curva_custos = []
        for t in thresholds:
            is_acordo = p_loss >= t
            custo_caso = np.where(
                is_acordo,
                taxa_aceite_acordo * custo_acordo_mercado + (1 - taxa_aceite_acordo) * custo_status_quo_real,
                custo_status_quo_real
            )
            custo_total = custo_caso.sum()
            curva_custos.append({"threshold": round(t, 4), "custo_total_M": custo_total / 1e6})

        df_curva = pd.DataFrame(curva_custos)
        ponto_otimo = df_curva.loc[df_curva["custo_total_M"].idxmin()]
        self.limiar_otimo = ponto_otimo["threshold"]
        return self

    def predict(self, df_cases: pd.DataFrame) -> pd.DataFrame:
        df_input = df_cases.copy()
        for col in CAT_COLS:
            df_input[col] = df_input[col].astype("category")

        p_loss = self.clf.predict_proba(df_input[FEATURE_COLS])[:, 1]
        pred_severidade = np.maximum(0, self.reg.predict(df_input[FEATURE_COLS]))

        custo_esperado_defesa = p_loss * pred_severidade + self.custo_operacional_defesa
        teto_acordo = np.minimum(df_input["Valor da causa"] * 0.60, custo_esperado_defesa * 0.75)
        proposta_inicial = np.minimum(teto_acordo * 0.60, df_input["Valor da causa"] * 0.25)

        decisoes = []
        for p in p_loss:
            if p >= 0.80:
                decisoes.append("Acordo Mandatório")
            elif p >= self.limiar_otimo:
                decisoes.append("Acordo Estratégico")
            else:
                decisoes.append("Defesa")

        output = df_input[["Número do processo", "UF", "Sub-assunto", "Valor da causa"]].copy()
        output["qtd_subsidios"] = df_input["qtd_subsidios"]
        output["probabilidade_derrota"] = (p_loss * 100).round(2)
        output["condenacao_prevista"] = pred_severidade.round(2)
        output["custo_esperado_litigio"] = custo_esperado_defesa.round(2)
        output["decisao_sugerida"] = decisoes
        output["valor_proposta_inicial"] = np.where(output["decisao_sugerida"] == "Defesa", 0.0, proposta_inicial.round(2))
        output["valor_teto_acordo"] = np.where(output["decisao_sugerida"] == "Defesa", 0.0, teto_acordo.round(2))
        return output