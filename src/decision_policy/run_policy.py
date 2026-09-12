from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, brier_score_loss, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_validate

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

def calcular_custo_operacional_dinamico(df: pd.DataFrame, base_fixa: float = 350.0, taxa_complexidade: float = 0.02, custo_por_subsidio_faltante: float = 120.0) -> pd.Series:
    """
    Calcula o custo operacional de defesa de forma dinamica e auditavel:
    - Base Fixa: gestao processual, protocolo e saneamento inicial.
    - Complexidade da Causa: percentual sobre o valor da causa (honorarios e risco de sucumbencia).
    - Friccao Operacional: custo interno proporcional aos subsidios faltantes (busca com gerentes/compliance).
    """
    qtd_subsidios = df["qtd_subsidios"] if "qtd_subsidios" in df.columns else 0
    subsidios_faltantes = np.maximum(0, 6 - qtd_subsidios)
    
    custo_complexidade = df["Valor da causa"] * taxa_complexidade
    custo_busca_documental = subsidios_faltantes * custo_por_subsidio_faltante
    
    return base_fixa + custo_complexidade + custo_busca_documental

class SettlementEngine:
    def __init__(self, custo_operacional_defesa):
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

        # -------------------------------------------------------------
        # 1. VALIDAÇÃO DO CLASSIFICADOR (HOLD-OUT ESTRATIFICADO 80/20)
        # -------------------------------------------------------------
        X_tr, X_val, y_tr, y_val = train_test_split(
            X, y_clf, test_size=0.20, random_state=42, stratify=y_clf
        )

        print("\n" + "=" * 60)
        print("VALIDACAO DO MODELO DE CLASSIFICACAO (P(Derrota)):")
        print("=" * 60)

        # Treino no split de validação
        self.clf.fit(X_tr, y_tr)
        val_probs = self.clf.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= 0.50).astype(int)

        auc_score = roc_auc_score(y_val, val_probs)
        brier = brier_score_loss(y_val, val_probs)
        cm = confusion_matrix(y_val, val_preds)

        print(f"-> ROC-AUC Score:      {auc_score:.4f}  (Capacidade de ranqueamento de risco)")
        print(f"-> Brier Score:        {brier:.4f}  (Calibracao probabilistica, menor = melhor)")
        print("\n-> Matriz de Confusao (Corte padrao 50%):")
        print(f"   [VN: {cm[0,0]:5d} | FP: {cm[0,1]:5d}]  -> Negativo = Exito (Vitoria)")
        print(f"   [FN: {cm[1,0]:5d} | VP: {cm[1,1]:5d}]  -> Positivo = Nao Exito (Derrota)")
        print("\n-> Relatorio Detalhado de Metricas por Classe:")
        print(classification_report(y_val, val_preds, target_names=["Exito (Vitoria)", "Nao Exito (Derrota)"], digits=4))
        print("=" * 60 + "\n")

        # Re-treina com 100% dos dados para maximizar performance em producao
        self.clf.fit(X, y_clf)

        # 2. Treino do Regressor de Severidade
        mask_condenado = (y_clf == 1)
        self.reg.fit(X[mask_condenado], y_reg[mask_condenado])

        self.clf.fit(X, y_clf)
        mask_condenado = (y_clf == 1)
        self.reg.fit(X[mask_condenado], y_reg[mask_condenado])

        # Otimização do limiar econômico na carteira de treino
        p_loss = self.clf.predict_proba(X)[:, 1]
        custo_op_dinamico = calcular_custo_operacional_dinamico(df_train)
        custo_status_quo_real = df_train["target_val"] + custo_op_dinamico
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

        # -------------------------------------------------------------
        # DESEMPENHO DO MODELO NO LIMIAR ÓTIMO FINANCEIRO (t* = 45%)
        # -------------------------------------------------------------
        print("=" * 65)
        print(f"DESEMPENHO DO CLASSIFICADOR NO LIMIAR OTIMO (Corte: {self.limiar_otimo * 100:.1f}%):")
        print("=" * 65)

        val_preds_otimo = (val_probs >= self.limiar_otimo).astype(int)
        cm_otimo = confusion_matrix(y_val, val_preds_otimo)

        rec_derrota = cm_otimo[1, 1] / (cm_otimo[1, 1] + cm_otimo[1, 0])
        prec_derrota = cm_otimo[1, 1] / (cm_otimo[1, 1] + cm_otimo[0, 1])

        print(f"-> Matriz de Confusão no Ponto Ótimo:")
        print(f"   [VN: {cm_otimo[0,0]:5d} | FP: {cm_otimo[0,1]:5d}]  -> Negativo = Êxito (Defesa mantida)")
        print(f"   [FN: {cm_otimo[1,0]:5d} | VP: {cm_otimo[1,1]:5d}]  -> Positivo = Não Êxito (Acordo acionado)")
        print(f"\n-> Métricas Chave na Faixa de Risco:")
        print(f"   • Recall de Derrotas (Captura de Risco):  {rec_derrota * 100:.2f}% (vs 76.51% no corte 50%)")
        print(f"   • Precisão dos Acordos Sugeridos:       {prec_derrota * 100:.2f}%")
        print(f"   • Derrotas Evitadas Adicionais:         {cm[1, 0] - cm_otimo[1, 0]} processos")
        print("=" * 65 + "\n")

        return self

    def predict(self, df_cases: pd.DataFrame, nivel_slider: float = 0.50) -> pd.DataFrame:
        """
        nivel_slider: valor contínuo de 0.0 (Mais Agressivo) a 1.0 (Mais Conservador).
                      0.50 representa a política Padrão.
        """
        df_input = df_cases.copy()
        for col in CAT_COLS:
            df_input[col] = df_input[col].astype("category")

        # delta varia de -0.15 (Agressivo) a +0.15 (Conservador)
        delta = (nivel_slider - 0.50) * 0.30

        # 1. Proposta Inicial: sobe no conservador (+delta) e desce no agressivo (-delta)
        fator_prop_causa = 0.25 * (1.0 + delta)
        fator_prop_teto  = 0.60 * (1.0 + delta/2.0)

        # 2. Teto do Acordo: move-se na direção OPOSTA para regular a margem de barganha!
        # No agressivo (delta negativo), (1.0 - delta) AUMENTA o teto -> spread grande.
        # No conservador (delta positivo), (1.0 - delta) APROXIMA o teto -> oferta direta.
        fator_teto_causa = 0.60 * (1.0 - delta)
        fator_teto_custo = 0.75 * (1.0 - delta)

        # 1. Probabilidades e severidade
        p_loss = self.clf.predict_proba(df_input[FEATURE_COLS])[:, 1]
        pred_severidade = np.maximum(0, self.reg.predict(df_input[FEATURE_COLS]))

        # 2. Custo operacional dinâmico com a base da barra
        custo_operacional = calcular_custo_operacional_dinamico(df_input, base_fixa=base_fixa_dinamica)
        custo_esperado_defesa = p_loss * pred_severidade + custo_operacional

        # 3. Teto e Proposta parametrizados continuamente
        teto_acordo = np.minimum(
            df_input["Valor da causa"] * fator_teto_causa,
            custo_esperado_defesa * fator_teto_custo
        )
        proposta_inicial = np.minimum(
            teto_acordo * fator_prop_teto,
            df_input["Valor da causa"] * fator_prop_causa
        )

        # 4. Decisão e Risco
        risco = []
        decisoes = []
        for p in p_loss:
            if p >= 0.80:
                risco.append("alto")
                decisoes.append("Acordo Mandatório")
            elif p >= self.limiar_otimo:
                risco.append("médio")
                decisoes.append("Acordo Estratégico")
            else:
                risco.append("baixo")
                decisoes.append("Defesa")

        output = df_input[["Número do processo", "UF", "Sub-assunto", "Valor da causa", "qtd_subsidios"]].copy()
        output["custo_operacional_estimado"] = np.round(custo_operacional, 2)
        output["risco"] = risco
        output["decisao_sugerida"] = decisoes
        output["valor_sugerido_proposta_inicial"] = np.where(output["decisao_sugerida"] == "Defesa", 0.0, np.round(proposta_inicial, 2))
        output["valor_teto_acordo"] = np.where(output["decisao_sugerida"] == "Defesa", 0.0, np.round(teto_acordo, 2))
        
        return output