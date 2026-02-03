import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

class JraVanExtractor:
    def __init__(self):
        # .env ファイルから設定を読み込む
        load_dotenv()
        
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        
        # 接続文字列の作成
        db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        self.engine = create_engine(db_url)

    def extract(self, start_year=2021, end_year=2025):
        """
        jvd_ra（レース情報）と jvd_se（馬ごとの成績）を結合して取得する
        """
        print(f"🔄 データベースから {start_year}年 ～ {end_year}年 のデータを抽出中...")

        # SQLクエリ
        query = f"""
        SELECT
            -- レース情報 (jvd_ra)
            r.kaisai_nen,
            r.kaisai_tsukihi,
            r.keibajo_code,
            
            -- ★ここに追加！レースID作成に必要
            r.kaisai_kai,
            r.kaisai_nichime,
            
            r.race_bango,
            r.kyori,
            r.track_code,
            r.tenko_code,
            r.babajotai_code_shiba,
            r.babajotai_code_dirt,
            
            -- 馬の情報 (jvd_se)
            h.umaban,
            h.ketto_toroku_bango,
            h.bamei,
            h.seibetsu_code,
            h.futan_juryo,
            h.kishu_code,
            h.chokyoshi_code,
            h.bataiju,
            h.zogen_sa,
            h.zogen_fugo,
            
            -- オッズ・結果
            h.tansho_odds,
            h.tansho_ninkijun,
            h.kakutei_chakujun

        FROM jvd_ra AS r
        INNER JOIN jvd_se AS h
            -- 結合キー
            ON r.kaisai_nen = h.kaisai_nen
            AND r.keibajo_code = h.keibajo_code
            AND r.kaisai_kai = h.kaisai_kai
            AND r.kaisai_nichime = h.kaisai_nichime
            AND r.race_bango = h.race_bango
        
        WHERE
            r.kaisai_nen BETWEEN '{start_year}' AND '{end_year}'
            AND h.kakutei_chakujun ~ '^[0-9]+$'
            AND CAST(h.kakutei_chakujun AS INTEGER) > 0

        ORDER BY 
            r.kaisai_nen, 
            r.kaisai_tsukihi, 
            r.race_bango, 
            CAST(h.kakutei_chakujun AS INTEGER)
        """
        
        try:
            df = pd.read_sql(query, self.engine)
            print(f"✅ 抽出完了: {len(df)} 件のデータを取得しました。")
            return df
            
        except Exception as e:
            print("❌ エラーが発生しました。")
            print(e)
            return pd.DataFrame()

if __name__ == "__main__":
    extractor = JraVanExtractor()
    df = extractor.extract(2023, 2023)
    if not df.empty:
        print(df.head())