from src.database.extractor import JraVanExtractor

def main():
    print("🚀 AIプロジェクトを起動します...")
    
    # 1. データベースからデータを取得
    extractor = JraVanExtractor()
  
    raw_data = extractor.extract(start_year=2023, end_year=2023)
    
    # 2. 中身をチラ見する
    print("\n--- 取得データのサンプル ---")
    print(raw_data.head())
    
    # 3. データのサイズ確認
    print(f"\nデータ形状: {raw_data.shape}")

if __name__ == "__main__":
    main()