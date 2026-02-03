from src.database.extractor import JraVanExtractor
from src.features.preprocessor import Preprocessor
from src.models.trainer import ModelTrainer
from src.simulation.simulator import Simulator

def main():
    print("🚀 AIプロジェクトを起動します...")
    
    # 1. データ抽出 (2021-2025)
    extractor = JraVanExtractor()
    raw_data = extractor.extract(start_year=2021, end_year=2025)
    
    if raw_data.empty:
        print("❌ データが取得できませんでした。")
        return

    # 2. 前処理
    preprocessor = Preprocessor()
    processed_data = preprocessor.process(raw_data)
    
    # 3. 学習
    trainer = ModelTrainer()
    model = trainer.train(processed_data)
    
    # --- シミュレーション ---
    
    target_year = 2025
    test_data = processed_data[processed_data['kaisai_nen'] == target_year].copy()
    
    X_test = test_data[trainer.features]
    
    # ★ここを変更！ predict ではなく predict_proba を使う
    # [:, 1] は「クラス1（3着以内）」になる確率を取得するという意味
    proba = model.predict_proba(X_test)[:, 1]
    
    # 4. 回収率シミュレーション
    simulator = Simulator()
    # 確率を渡す
    simulator.simulate_tansho(test_data, proba)

if __name__ == "__main__":
    main()