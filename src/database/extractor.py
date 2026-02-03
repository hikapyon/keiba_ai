import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

class JraVanExtractor:
    def __init__(self):
        # .env ファイルから設定を読み込む
        load_dotenv()
        
        # データベース接続情報を作成
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        
        # PostgreSQLへの接続エンジンを作成
        db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        self.engine = create_engine(db_url)

    def extract(self, start_year=2021, end_year=2023):
        """
        指定された期間のレース結果と馬情報を結合して取得する
        """
        print(f"🔄 データベースから {start_year}年 ～ {end_year}年 のデータを抽出中...")

        # SQLクエリ（命令文）
        # jvd_race_shosai (レース詳細) と jvd_uma_race (馬ごとの結果) を結合します
        query = f"""
        SELECT
            -- レース情報
            r.race_id,
            r.kaisai_nen,       -- 開催年
            r.kaisai_tsukihi,   -- 開催月日
            r.keibajo_code,     -- 競馬場コード
            r.race_bango,       -- レース番号
            r.kyori,            -- 距離
            r.track_code,       -- トラック（芝・ダート）
            r.tenko_code,       -- 天候
            r.baba_jotai_code,  -- 馬場状態
            
            -- 馬の情報
            u.umaban,           -- 馬番
            u.ketto_toroku_bango, -- 血統登録番号（馬ID）
            u.kyoso_ba_meishou, -- 馬名
            u.sex_code,         -- 性別
            u.nengappi,         -- 生年月日（年齢計算用）
            u.futan_weight,     -- 負担重量
            u.kishu_code,       -- 騎手コード
            u.chokyoshi_code,   -- 調教師コード
            u.ba_taiju,         -- 馬体重
            u.zogen_sa,         -- 増減差
            
            -- オッズ・人気
            u.tansho_odds,      -- 単勝オッズ
            u.ninki_bango,      -- 人気順
            
            -- ターゲット（予測したいもの）
            u.kakutei_chakushun -- 確定着順

        FROM jvd_race_shosai AS r
        INNER JOIN jvd_uma_race AS u
            ON r.race_id = u.race_id
        
        WHERE
            -- 指定した期間のデータを取得
            r.kaisai_nen BETWEEN '{start_year}' AND '{end_year}'
            -- 障害レースを除外（必要に応じて）
            AND r.track_code IN ('10', '11', '12', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29')
            -- 完走した馬のみ（中止などを除外）
            AND u.kakutei_chakushun > 0

        ORDER BY r.kaisai_nen, r.kaisai_tsukihi, r.race_id, u.kakutei_chakushun
        """
        
        # SQLを実行してPandasのDataFrameにする
        df = pd.read_sql(query, self.engine)
        
        print(f"✅ 抽出完了: {len(df)} 件のデータを取得しました。")
        return df

if __name__ == "__main__":
    # テスト実行用コード
    extractor = JraVanExtractor()
    df = extractor.extract(2023, 2023) # 2023年だけ試しに取る
    print(df.head())