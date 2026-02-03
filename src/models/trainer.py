import pandas as pd
import lightgbm as lgb
from sklearn.metrics import accuracy_score, roc_auc_score

class ModelTrainer:
    def __init__(self):
        self.model = None
        # 特徴量のリスト（カンマ抜けに注意！）
        self.features = [
            'keibajo_code', 'kyori', 'track_code', 'tenko_code',
            'babajotai_code_shiba', 'babajotai_code_dirt',
            'seibetsu_code', 'futan_juryo', 'bataiju', 'zogen_sa',
            'kishu_code',
            
            # --- 既存のエンジニアリング ---
            'bataiju_diff',
            'futan_diff',
            'kishu_course',      # ← ここにカンマが必要です！
            
            # --- ★今回追加した新要素 ---
            'dist_change',       # 距離延長・短縮
            'dist_diff',         # 距離差（数値）
            'course_direction',  # 右回り・左回り
            'course_top3_count'  # このコースでの過去の好走数
        ]

    def train(self, df: pd.DataFrame):
        """
        データを「学習用」と「テスト用」に分けてモデルを育てる
        """
        print("🤖 AIの学習を開始します...")

        # 1. 目的変数を作成
        df['target'] = df['kakutei_chakujun'].apply(lambda x: 1 if x <= 3 else 0)

        # 2. データを分割（時系列スプリット）
        test_year = 2025
        
        train_df = df[df['kaisai_nen'] < test_year]
        test_df = df[df['kaisai_nen'] == test_year]
        
        if len(train_df) == 0 or len(test_df) == 0:
            print("⚠️ データ不足で分割できません。抽出期間を広げてください。")
            return

        # ここで featureリストを使って列を取り出す
        X_train = train_df[self.features]
        y_train = train_df['target']
        X_test = test_df[self.features]
        y_test = test_df['target']

        print(f"   学習データ: {len(X_train)} 件 | テストデータ: {len(X_test)} 件")

        # 3. LightGBMモデルの定義
        self.model = lgb.LGBMClassifier(
            objective='binary',
            metric='auc',
            verbosity=-1,
            random_state=42
        )

        # 4. 学習実行
        self.model.fit(X_train, y_train)
        print("✅ 学習完了！")

        # 5. 予測と評価
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 --- 評価結果 ({test_year}年のデータ) ---")
        print(f"的中率 (Accuracy): {acc:.2%}")
        
        # 重要度ランキング
        importance = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values(by='importance', ascending=False)
        
        print("\n🔍 AIが重視した要素ランキング:")
        print(importance.head(5))

        return self.model