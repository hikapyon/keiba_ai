import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

def check_columns():
    print("🔍 jvd_ra (レース詳細) の列名を確認します...")
    
    # データは取得せず、列名だけを取得するクエリ
    query = "SELECT * FROM jvd_ra LIMIT 0"
    
    try:
        df = pd.read_sql(query, engine)
        cols = list(df.columns)
        print("\n--- 列名一覧 (jvd_ra) ---")
        print(cols)
        
        # 馬場状態に関係しそうな列を探して表示
        print("\n--- 'baba' がつく列 ---")
        baba_cols = [c for c in cols if 'baba' in c]
        print(baba_cols)

    except Exception as e:
        print("エラー:", e)

if __name__ == "__main__":
    check_columns()