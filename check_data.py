from src.database.extractor import JraVanExtractor
from src.features.preprocessor import Preprocessor

def check():
    print("🔍 データの中身をチェックします...")
    
    # 1. データを少しだけ抽出
    extractor = JraVanExtractor()
    # 期間を短くして高速化
    raw_data = extractor.extract(start_year=2023, end_year=2023)
    
    # 2. 前処理
    preprocessor = Preprocessor()
    df = preprocessor.process(raw_data)
    
    # 3. オッズと着順のサンプルを表示
    print("\n--- データのサンプル (最初の5行) ---")
    target_cols = ['kaisai_nen', 'race_bango', 'bamei', 'kakutei_chakujun', 'tansho_odds', 'tansho_ninkijun']
    
    # 列が存在するか確認しつつ表示
    cols_to_show = [c for c in target_cols if c in df.columns]
    print(df[cols_to_show].head(5))
    
    print("\n--- オッズの統計情報 ---")
    print(df['tansho_odds'].describe())

if __name__ == "__main__":
    check()