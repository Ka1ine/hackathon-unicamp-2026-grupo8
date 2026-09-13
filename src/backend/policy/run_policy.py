import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import brier_score_loss, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

CAT_COLS = ["Sub-assunto", "UF"]

FEATURE_COLS = [
    "Comprovante de crédito", "Contrato", "Demonstrativo de evolução da dívida", 
    "Dossiê", "Extrato", "Laudo referenciado", "Sub-assunto", "UF", "Valor da causa",
    "has_comprovante_or_dossie", "has_contrato_extrato", "missing_contrato_extrato", "qtd_subsidios"
]

def calcular_custo_operacional_dinamico(df: pd.DataFrame, base_fixa: float = 350.0, taxa_complexidade: float = 0.02, custo_por_subsidio_faltante: float = 120.0) -> pd.Series:
    """
    Calcula o custo operacional de defesa de forma dinamica e auditavel:
    - Base Fixa: gestao processual, protocolo e saneamento inicial.
    - Complexidade da Causa: percentual sobre o valor da causa (honorarios e risco de sucumbencia).
    - Friccao Operacional: custo interno proporcional aos subsidios faltantes (busca com gerentes/compliance).
    """
    custo_complexidade = df["Valor da causa"] * taxa_complexidade
    qtd_subsidios = df["qtd_subsidios"] if "qtd_subsidios" in df.columns else 0
    subsidios_faltantes = np.maximum(0, 6 - qtd_subsidios)
    custo_busca_documental = subsidios_faltantes * custo_por_subsidio_faltante
    
    return base_fixa + custo_busca_documental + custo_complexidade

def load_and_preprocess_training_data(excel_path: str = "Hackaton_Enter_Base_Candidatos.xlsx") -> pd.DataFrame:
    """Carrega as abas da planilha e prepara o DataFrame de treino."""
    df_res = pd.read_excel(excel_path, sheet_name="Resultados dos processos")
    df_sub = pd.read_excel(excel_path, sheet_name="Subsídios disponibilizados", header=1)
    df_sub = df_sub.rename(columns={"Número do processos": "Número do processo"})
    df = pd.merge(df_res, df_sub, on="Número do processo")

    sub_cols = ["Comprovante de crédito", "Contrato", "Demonstrativo de evolução da dívida", "Dossiê", "Extrato", "Laudo referenciado"]
    for c in sub_cols:
        df[c] = df[c].astype(int)

    df["has_comprovante_or_dossie"] = ((df["Comprovante de crédito"] == 1) | (df["Dossiê"] == 1)).astype(int)
    df["has_contrato_extrato"] = ((df["Contrato"] == 1) & (df["Extrato"] == 1)).astype(int)
    df["missing_contrato_extrato"] = ((df["Contrato"] == 0) & (df["Extrato"] == 0)).astype(int)
    df["qtd_subsidios"] = df[sub_cols].sum(axis=1)

    for col in CAT_COLS:
        df[col] = df[col].astype("category")

    df["target_loss"] = (df["Resultado macro"] == "Não Êxito").astype(int)
    df["target_val"] = df["Valor da condenação/indenização"]
    
    return df

class SettlementEngine:
    def __init__(self, custo_operacional_defesa):
        self.clf = HistGradientBoostingClassifier(
            categorical_features=CAT_COLS, learning_rate=0.05, max_iter=200, max_leaf_nodes=31, random_state=42
        )
        self.custo_operacional_defesa = custo_operacional_defesa
        self.history_stats = {}
        self.limiar_otimo = 0.45
        self.reg = HistGradientBoostingRegressor(
            categorical_features=CAT_COLS, learning_rate=0.05, max_iter=200, max_leaf_nodes=31, random_state=42
        )

    def fit(self, df_train: pd.DataFrame):
        X = df_train[FEATURE_COLS]
        y_clf = df_train["target_loss"]
        y_reg = df_train["target_val"]

        self.history_stats = df_train.groupby("Sub-assunto", observed=False).agg(
            qtd_casos=("target_loss", "count"),
            taxa_derrota=("target_loss", "mean"),
            valor_medio_condenacao=("target_val", lambda x: x[x > 0].mean() if (x > 0).any() else 0.0)
        ).to_dict("index")

        X_tr, X_val, y_tr, y_val = train_test_split(
            X, y_clf, random_state=42, stratify=y_clf, test_size=0.20
        )

        print("\n" + "=" * 60)
        print("VALIDACAO DO MODELO DE CLASSIFICACAO (P(Derrota)):")
        print("=" * 60)

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
        print(classification_report(y_val, val_preds, digits=4, target_names=["Exito (Vitoria)", "Nao Exito (Derrota)"]))
        print("=" * 60 + "\n")

        self.clf.fit(X, y_clf)

        mask_condenado = (y_clf == 1)
        self.reg.fit(X[mask_condenado], y_reg[mask_condenado])

        custo_acordo_mercado = df_train["Valor da causa"] * 0.30
        custo_op_dinamico = calcular_custo_operacional_dinamico(df_train)
        custo_status_quo_real = df_train["target_val"] + custo_op_dinamico
        custo_status_quo_total = custo_status_quo_real.sum()
        p_loss = self.clf.predict_proba(X)[:, 1]
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
            curva_custos.append({"custo_total_M": custo_total / 1e6, "threshold": round(t, 4)})

        df_curva = pd.DataFrame(curva_custos)
        ponto_otimo = df_curva.loc[df_curva["custo_total_M"].idxmin()]
        self.limiar_otimo = ponto_otimo["threshold"]

        print("=" * 65)
        print(f"DESEMPENHO DO CLASSIFICADOR NO LIMIAR OTIMO (Corte: {self.limiar_otimo * 100:.1f}%):")
        print("=" * 65)

        val_preds_otimo = (val_probs >= self.limiar_otimo).astype(int)
        cm_otimo = confusion_matrix(y_val, val_preds_otimo)

        prec_derrota = cm_otimo[1, 1] / (cm_otimo[1, 1] + cm_otimo[0, 1])
        rec_derrota = cm_otimo[1, 1] / (cm_otimo[1, 1] + cm_otimo[1, 0])

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

        delta = (nivel_slider - 0.50) * 0.30

        fator_prop_causa = 0.25 * (1.0 + delta)
        fator_prop_teto = 0.60 * (1.0 + delta/2.0)

        fator_teto_causa = 0.60 * (1.0 - delta)
        fator_teto_custo = 0.75 * (1.0 - delta)

        p_loss = self.clf.predict_proba(df_input[FEATURE_COLS])[:, 1]
        pred_severidade = np.maximum(0, self.reg.predict(df_input[FEATURE_COLS]))

        custo_operacional = calcular_custo_operacional_dinamico(df_input, base_fixa=350.0)
        custo_esperado_defesa = p_loss * pred_severidade + custo_operacional

        teto_acordo = np.minimum(
            custo_esperado_defesa * fator_teto_custo,
            df_input["Valor da causa"] * fator_teto_causa
        )

        proposta_inicial = np.minimum(
            df_input["Valor da causa"] * fator_prop_causa,
            teto_acordo * fator_prop_teto
        )

        decisoes = []
        explicacoes = []
        risco = []
        
        for i, p in enumerate(p_loss):
            if p >= 0.80:
                decisoes.append("Acordo Mandatório")
                risco.append("alto")
            elif p >= self.limiar_otimo:
                decisoes.append("Acordo Estratégico")
                risco.append("médio")
            else:
                decisoes.append("Defesa")
                risco.append("baixo")

            sub_assunto = df_input["Sub-assunto"].iloc[i]
            stats = self.history_stats.get(sub_assunto, {"qtd_casos": 0, "taxa_derrota": 0.0, "valor_medio_condenacao": 0.0})
            
            x_casos = f"{stats['qtd_casos']:,}".replace(",", ".")
            y_historico = stats["taxa_derrota"] * 100
            z_valor = stats["valor_medio_condenacao"]
            w_risco = p * 100
            w_sucesso = (1 - p) * 100
            
            z_formatado = f"{z_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            adv_exito = "apenas " if w_sucesso < 50 else ""
            decisao = decisoes[i]
            
            prop_ini_val = proposta_inicial.iloc[i] if isinstance(proposta_inicial, pd.Series) else proposta_inicial[i]
            teto_val = teto_acordo.iloc[i] if isinstance(teto_acordo, pd.Series) else teto_acordo[i]
            
            prop_ini_fmt = f"{prop_ini_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            teto_fmt = f"{teto_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            base_expl = (f"Analisando {x_casos} casos similares (categoria: {sub_assunto}), "
                         f"identificou-se que {y_historico:.1f}% resultam em condenações, com valor médio de "
                         f"R$ {z_formatado}. Diante de uma taxa de êxito de {adv_exito}{w_sucesso:.1f}% no litígio "
                         f"(o que representa {w_risco:.1f}% de risco), a recomendação sugerida é o {decisao}.")
            
            if decisao == "Defesa":
                justificativa = (" Como a probabilidade de vitória e o risco financeiro estão equilibrados a nosso favor, "
                                 "a melhor estratégia é manter a defesa, evitando gastos desnecessários com o pagamento de acordos.")
            else:
                justificativa = (f" Para mitigar este passivo, sugere-se iniciar a negociação em R$ {prop_ini_fmt}, "
                                 f"limitando-se ao teto de R$ {teto_fmt}. Esta estratégia se mostra uma boa abordagem "
                                 f"pois garante o encerramento da ação por um montante previsível e inferior ao custo médio total esperado caso o litígio prossiga.")
            
            explicacoes.append(base_expl + justificativa)

        output = df_input[["Número do processo", "Sub-assunto", "UF", "Valor da causa", "qtd_subsidios"]].copy()
        
        output["custo_operacional_estimado"] = np.round(custo_operacional, 2)
        output["decisao_sugerida"] = decisoes
        output["explicacao_decisao"] = explicacoes
        output["risco"] = risco
        output["valor_sugerido_proposta_inicial"] = np.where(output["decisao_sugerida"] == "Defesa", 0.0, np.round(proposta_inicial, 2))
        output["valor_teto_acordo"] = np.where(output["decisao_sugerida"] == "Defesa", 0.0, np.round(teto_acordo, 2))
        
        return output