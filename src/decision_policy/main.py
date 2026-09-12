import glob
from pathlib import Path
import pandas as pd

# Importações relativas dentro da pasta decision_policy
from case_extractor import parse_case_folder
from run_policy import load_and_preprocess_training_data, SettlementEngine


# =====================================================================
# MAPEAMENTO DINÂMICO DE CAMINHOS BASEADO NA NOVA ESTRUTURA
# =====================================================================
# __file__ está em: repo_root/src/decision_policy/main.py
# .parent é 'decision_policy', .parent.parent é 'src', .parent.parent.parent é a raiz do repo
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"

EXCEL_TRAIN_PATH = DATA_DIR / "Hackaton_Enter_Base_Candidatos.xlsx"
CASES_DIR = DATA_DIR / "processos_exemplo"
OUTPUT_CSV_PATH = DATA_DIR / "resultado_novos_casos.csv"


def main():
    print("=" * 80)
    print("ORQUESTRADOR: PIPELINE END-TO-END DE ACORDOS (ENTER AI)")
    print("=" * 80)

    # 1. Validação e Carregamento da Base de Treino
    if not EXCEL_TRAIN_PATH.exists():
        raise FileNotFoundError(f"Planilha não encontrada em: {EXCEL_TRAIN_PATH}")

    print(f"\n[Passo 1/3] Treinando modelos com a base: {EXCEL_TRAIN_PATH.name}...")
    df_train = load_and_preprocess_training_data(str(EXCEL_TRAIN_PATH))

    engine = SettlementEngine(custo_operacional_defesa=400.0)
    engine.fit(df_train)
    print(f"-> Modelos treinados com sucesso! Limiar ótimo da carteira: {engine.limiar_otimo * 100:.1f}%")

    # 2. Localização das Pastas dos Processos (PDFs)
    print(f"\n[Passo 2/3] Buscando pastas de processos em: {CASES_DIR}...")
    
    # Busca tanto subpastas dentro de processos_exemplo quanto pastas Caso_*
    case_folders = sorted([p for p in CASES_DIR.iterdir() if p.is_dir()])
    
    # Fallback: caso as pastas dos casos ainda estejam na raiz do repo ou em data/
    if not case_folders:
        case_folders = sorted(list(DATA_DIR.glob("Caso_*")) + list(REPO_ROOT.glob("Caso_*")))

    if not case_folders:
        print(f"ATENÇÃO: Nenhuma pasta de processo encontrada em {CASES_DIR} ou na raiz.")
        return

    print(f"-> Encontradas {len(case_folders)} pastas de casos. Extraindo dados dos PDFs...")
    records = []
    for folder in case_folders:
        print(f"   Processando: {folder.name}")
        extracted_data = parse_case_folder(str(folder))
        records.append(extracted_data)

    df_cases = pd.DataFrame(records)
    print(f"-> Extração concluída! Total de casos prontos: {len(df_cases)}")

    # 3. Inferência e Decisão
    print("\n[Passo 3/3] Aplicando política de acordos aos novos casos...")
    resultados = engine.predict(df_cases)

    cols_display = [
        "Número do processo", "UF", "Sub-assunto", "Valor da causa",
        "qtd_subsidios", "probabilidade_derrota", "decisao_sugerida",
        "valor_proposta_inicial", "valor_teto_acordo"
    ]

    print("\n" + "=" * 80)
    print("RESULTADO FINAL DA ANÁLISE DOS CASOS:")
    print("=" * 80)
    print(resultados[cols_display].to_string(index=False))

    # Salva o CSV na mesma pasta do script
    resultados.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\nResultados salvos com sucesso em: {OUTPUT_CSV_PATH}\n")


if __name__ == "__main__":
    main()