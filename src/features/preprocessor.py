import pandas as pd
import numpy as np

class Preprocessor:
    def __init__(self):
        pass

    def process(self, df: pd.DataFrame):
        """
        生のDataFrameを受け取り、AIが学習できる形に整形する
        """
        print("🍳 データの前処理（特徴量エンジニアリング）を開始します...")
        
        # データのコピー
        df = df.copy()

        # --- 1. 数値の型変換 ---
        numeric_cols = [
            'kaisai_nen', 'futan_juryo', 'bataiju', 'zogen_sa',
            'tansho_odds', 'kakutei_chakujun', 'kyori',
            'kaisai_kai', 'kaisai_nichime', 'race_bango'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- 2. 欠損値処理 ---
        if 'kakutei_chakujun' in df.columns:
            df = df.dropna(subset=['kakutei_chakujun'])
        
        fill_zeros = ['bataiju', 'zogen_sa', 'tansho_odds', 'futan_juryo']
        for col in fill_zeros:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        # --- 3. 時系列順にソート（重要！） ---
        # 過去の成績を計算するために、馬ごとに古い順に並べる必要があります
        # kaisai_tsukihi は "0105" (1月5日) のような文字列なので、年と組み合わせればソート可能
        df = df.sort_values(['ketto_toroku_bango', 'kaisai_nen', 'kaisai_tsukihi'])

        # --- 4. 特徴量エンジニアリング（追加機能） ---
        
        # (A) レースID
        df['race_id'] = (
            df['kaisai_nen'].astype(str) + "_" +
            df['keibajo_code'].astype(str) + "_" +
            df['kaisai_kai'].astype(str) + "_" +
            df['kaisai_nichime'].astype(str) + "_" +
            df['race_bango'].astype(str)
        )

        # (B) 前走との距離変化（延長・短縮）
        # 馬ごとにグループ化して、1つ前の行（前走）の距離を取得
        df['prev_kyori'] = df.groupby('ketto_toroku_bango')['kyori'].shift(1)
        
        # 距離差（今回 - 前回）
        df['dist_diff'] = df['kyori'] - df['prev_kyori']
        df['dist_diff'] = df['dist_diff'].fillna(0) # デビュー戦などは0扱い
        
        # カテゴリ化（延長、短縮、同距離）
        def categorize_dist_change(x):
            if x > 0: return 'extension'   # 延長
            elif x < 0: return 'shortening' # 短縮
            else: return 'same'            # 同距離
        df['dist_change'] = df['dist_diff'].apply(categorize_dist_change).astype('category')

        # (C) コースの回り（右・左・直線）
        # 競馬場コードに基づいてマッピング
        # 01:札幌(右), 02:函館(右), 03:福島(右), 04:新潟(左/直), 05:東京(左)
        # 06:中山(右), 07:中京(左), 08:京都(右), 09:阪神(右), 10:小倉(右)
        def map_course_direction(code):
            code = str(code).zfill(2) # 0埋めして文字列化
            if code in ['01', '02', '03', '06', '08', '09', '10']:
                return 'Right'
            elif code in ['05', '07']:
                return 'Left'
            elif code == '04':
                # 新潟は基本左だが、1000mのみ直線。簡易的に左として扱うか、距離で分ける
                # 今回は簡易的にLeftとする（新潟1000mを厳密にやるなら track_code も見る必要あり）
                return 'Left' 
            return 'Unknown'
            
        df['course_direction'] = df['keibajo_code'].apply(map_course_direction).astype('category')

        # (D) 同競馬場での過去成績（コース適性）
        # 「この競馬場で過去に何回3着以内に入ったか？」
        df['is_top3'] = df['kakutei_chakujun'].apply(lambda x: 1 if x <= 3 else 0)
        
        # 馬と競馬場でグループ化し、過去の累積和を計算（shift(1)することで今回の結果は含めない）
        df['course_top3_count'] = df.groupby(['ketto_toroku_bango', 'keibajo_code'])['is_top3'] \
                                    .transform(lambda x: x.shift(1).cumsum().fillna(0))
                                    
        # (E) 相対データの計算
        grouped = df.groupby('race_id')
        df['bataiju_diff'] = df['bataiju'] - grouped['bataiju'].transform('mean')
        df['futan_diff'] = df['futan_juryo'] - grouped['futan_juryo'].transform('mean')

        # (F) 騎手×コース
        if 'kishu_code' in df.columns and 'keibajo_code' in df.columns:
            df['kishu_course'] = (
                df['kishu_code'].astype(str) + "_" + df['keibajo_code'].astype(str)
            ).astype('category')

        # --- 5. カテゴリ変数の型変換 ---
        category_cols = [
            'keibajo_code', 'track_code', 'tenko_code', 
            'babajotai_code_shiba', 'babajotai_code_dirt', 
            'seibetsu_code', 'kishu_code', 'chokyoshi_code',
            'kishu_course',
            'dist_change',    # 追加
            'course_direction' # 追加
        ]
        
        for col in category_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')

        # --- 6. 必要な列だけ選抜 ---
        use_cols = [
            'kaisai_nen',
            'keibajo_code',
            'kyori',
            'track_code',
            'tenko_code',
            'babajotai_code_shiba',
            'babajotai_code_dirt',
            'seibetsu_code',
            'futan_juryo',
            'bataiju',
            'zogen_sa',
            'kishu_code',
            
            # --- 追加特徴量 ---
            'bataiju_diff',      # 相対馬体重
            'futan_diff',        # 相対斤量
            'kishu_course',      # 騎手×コース
            'dist_change',       # 距離変更区分 (Extension/Shortening/Same)
            'dist_diff',         # 距離差の数値 (+400, -200など)
            'course_direction',  # 回り (Right/Left)
            'course_top3_count', # 同コースでの好走回数
            
            # --- 目的変数 ---
            'tansho_odds',
            'kakutei_chakujun'
        ]
        
        existing_cols = [c for c in use_cols if c in df.columns]
        df_processed = df[existing_cols]
        
        print(f"✨ 特徴量エンジニアリング完了: {len(df_processed)} 件")
        print("   -> 距離変更・回り・コース実績を追加しました")
        
        return df_processed