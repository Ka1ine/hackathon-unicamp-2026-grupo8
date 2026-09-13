import json
import pandas as pd
from pathlib import Path
from src.policy.case_extractor import parse_case_folder
from src.policy.policy_schemas import PolicyDecision
from src.policy.run_policy import SettlementEngine, load_and_preprocess_training_data


class PolicyService:
    """Singleton service to train the model once and predict for individual cases."""
    
    _engine = None
    _instance = None

    def __new__(cls, base_data_dir: Path = Path("data")):
        if cls._instance is None:
            cls._instance = super(PolicyService, cls).__new__(cls)
            cls._instance.base_data_dir = base_data_dir
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        """Loads data and trains the HistGradientBoosting models on first boot."""
        train_path = self.base_data_dir / "Hackaton_Enter_Base_Candidatos.xlsx"
        
        if train_path.exists():
            print("[INFO] Inicializando e treinando SettlementEngine...")
            df_train = load_and_preprocess_training_data(str(train_path))
            self._engine = SettlementEngine(custo_operacional_defesa=400.0)
            self._engine.fit(df_train)
            print("[INFO] Modelos treinados com sucesso!")
        else:
            print(f"[ERROR] Base de treino não encontrada em {train_path}")
            self._engine = None

    def evaluate_case(self, process_id: str, force_refresh: bool = False) -> PolicyDecision:
        """Evaluates a single case and caches the decision in a JSON file."""
        cache_dir = self.base_data_dir / "cache"
        cache_dir.mkdir(exist_ok=True, parents=True)
        
        json_file_path = cache_dir / f"{process_id}_policy.json"
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
        result_df = self._engine.predict(df_cases)
        row = result_df.iloc[0]

        policy_decision = PolicyDecision(
            estimated_operacional_cost=float(row["custo_operacional_estimado"]),
            next_recommended_action=row["decisao_sugerida"],
            proposed_value_initial=float(row["valor_sugerido_proposta_inicial"]),
            proposed_value_maximum=float(row["valor_teto_acordo"]),
            risk_level=row["risco"]
        )

        # 3. Save to JSON
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(policy_decision.model_dump_json(indent=4))

        return policy_decision