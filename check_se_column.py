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

def check_se_columns():
    print("🔍 jvd_se (馬毎レース詳細) の列名を確認します...")
    
    # 列名だけ取得
    query = "SELECT * FROM jvd_se LIMIT 0"
    
    try:
        df = pd.read_sql(query, engine)
        cols = list(df.columns)
        print("\n--- 列名一覧 (jvd_se) ---")
        print(cols)
        
        # 特にエラーになりそうな項目をピックアップ
        print("\n--- 要チェック項目 ---")
        check_list = ['futan', 'weight', 'kinryo', 'taiju', 'zogen', 'sex', 'seibetsu']
        for target in check_list:
            found = [c for c in cols if target in c]
            if found:
                print(f"キーワード '{target}': {found}")

    except Exception as e:
        print("エラー:", e)

if __name__ == "__main__":
    check_se_columns()