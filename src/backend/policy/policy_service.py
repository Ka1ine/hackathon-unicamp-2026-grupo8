import json
import pandas as pd
from pathlib import Path
from src.backend.policy.case_extractor import parse_case_folder
from src.backend.policy.policy_schemas import PolicyDecision
from src.backend.policy.run_policy import SettlementEngine, load_and_preprocess_training_data


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class PolicyService:
    """Singleton service to train the model once and predict for individual cases."""
    
    _engine = None
    _instance = None

    def __new__(cls, base_data_dir: Path | None = None):
        if cls._instance is None:
            cls._instance = super(PolicyService, cls).__new__(cls)
            cls._instance.base_data_dir = Path(base_data_dir or DEFAULT_DATA_DIR)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        """Loads data and trains the HistGradientBoosting models on first boot."""
        train_path = next(
            (
                path
                for path in (
                    self.base_data_dir / "Hackaton_Enter_Base_Candidatos.xlsx",
                    self.base_data_dir / "dados.xlsx",
                )
                if path.exists()
            ),
            None,
        )
        
        if train_path:
            print("[INFO] Inicializando e treinando SettlementEngine...")
            df_train = load_and_preprocess_training_data(str(train_path))
            self._training_data = df_train
            self._engine = SettlementEngine(custo_operacional_defesa=400.0)
            self._engine.fit(df_train)
            print("[INFO] Modelos treinados com sucesso!")
        else:
            print(f"[ERROR] Base de treino não encontrada em {self.base_data_dir}")
            self._engine = None
            self._training_data = None

    def _decision_explanation(self, features: dict, row) -> str:
        """Produz uma fundamentação auditável a partir da carteira de treinamento."""
        category = str(features.get("Sub-assunto") or "não classificada")
        training_data = self._training_data
        similar_cases = training_data[
            training_data["Sub-assunto"].astype(str).eq(category)
        ]
        if similar_cases.empty:
            similar_cases = training_data
            category = "comparável"

        total_cases = len(similar_cases)
        convictions = similar_cases[similar_cases["target_loss"] == 1]
        conviction_rate = 100 * len(convictions) / total_cases if total_cases else 0
        average_award = float(convictions["target_val"].mean()) if not convictions.empty else 0.0
        loss_probability = 100 * float(row["probabilidade_derrota"])
        success_rate = 100 - loss_probability
        recommendation = str(row["decisao_sugerida"])
        total_cases_text = f"{total_cases:,}".replace(",", ".")
        average_award_text = f"R$ {average_award:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        conviction_rate_text = f"{conviction_rate:.1f}".replace(".", ",")
        success_rate_text = f"{success_rate:.1f}".replace(".", ",")
        loss_probability_text = f"{loss_probability:.1f}".replace(".", ",")

        return (
            f"Em análise comparativa de {total_cases_text} processos similares da categoria "
            f"{category}, identificou-se que {conviction_rate_text}% resultaram em condenações, "
            f"com valor médio de {average_award_text}. Considerando a taxa estimada de êxito "
            f"de {success_rate_text}% no litígio, equivalente a risco individual de {loss_probability_text}%, "
            f"a recomendação sugerida é {recommendation}."
        )

    def evaluate_case(
        self,
        process_id: str,
        force_refresh: bool = False,
        aggressiveness: int = 50,
    ) -> PolicyDecision:
        """Evaluates a single case and caches the decision in a JSON file."""
        aggressiveness = max(0, min(100, int(aggressiveness)))
        cache_dir = self.base_data_dir / "cache"
        cache_dir.mkdir(exist_ok=True, parents=True)
        
        json_file_path = cache_dir / f"{process_id}_policy_{aggressiveness}_v2.json"
        process_dir = self.base_data_dir / "example_cases" / process_id

        # 1. Check Cache
        if json_file_path.exists() and not force_refresh:
            with open(json_file_path, "r", encoding="utf-8") as f:
                return PolicyDecision(**json.load(f))

        # 2. Extract and Predict
        if not self._engine:
            raise RuntimeError("SettlementEngine não foi inicializado.")
            
        if not process_dir.exists():
            raise FileNotFoundError(f"Pasta do processo não encontrada: {process_dir}")

        # Extract using your existing case_extractor logic
        features_dict = parse_case_folder(str(process_dir))
        df_cases = pd.DataFrame([features_dict])
        
        # Run prediction for this single row
        result_df = self._engine.predict(df_cases, aggressiveness=aggressiveness)
        row = result_df.iloc[0]

        policy_decision = PolicyDecision(
            estimated_operacional_cost=float(row["custo_operacional_estimado"]),
            next_recommended_action=row["decisao_sugerida"],
            proposed_value_initial=float(row["valor_sugerido_proposta_inicial"]),
            proposed_value_maximum=float(row["valor_teto_acordo"]),
            risk_level=row["risco"],
            aggressiveness=aggressiveness,
            decision_explanation=self._decision_explanation(features_dict, row),
        )

        # 3. Save to JSON
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(policy_decision.model_dump_json(indent=4))

        return policy_decision

    def update_case_policy(self, process_id: str, aggressiveness: int = 50) -> PolicyDecision:
        """Recalcula a política e registra o resultado no JSON consolidado do caso."""
        policy_decision = self.evaluate_case(
            process_id=process_id,
            aggressiveness=aggressiveness,
        )
        process_dir = self.base_data_dir / "example_cases" / process_id
        master_json_files = sorted(process_dir.glob("*.json"))
        if not master_json_files:
            raise FileNotFoundError(f"JSON consolidado não encontrado em: {process_dir}")
        master_json_path = master_json_files[0]

        with open(master_json_path, "r", encoding="utf-8") as file:
            case_data = json.load(file)
        case_data["policy_data"] = policy_decision.model_dump()
        with open(master_json_path, "w", encoding="utf-8") as file:
            json.dump(case_data, file, indent=4, ensure_ascii=False)

        return policy_decision
