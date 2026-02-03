import pandas as pd
import numpy as np

class Simulator:
    def __init__(self):
        pass

    def simulate_tansho(self, df: pd.DataFrame, proba: np.ndarray):
        """
        AIの「自信度（確率）」に基づいて、閾値を変えながらシミュレーションを行う
        """
        print("\n🎰 --- 自信度別の回収率分析 ---")
        
        df = df.copy()
        df['proba'] = proba # AIが出した確率（0.0〜1.0）
        
        # オッズが0のデータはあらかじめ除外
        df = df[df['tansho_odds'] > 0]
        
        # 閾値を 0.5 (50%) から 0.05 刻みで上げていく
        thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        
        print(f"{'閾値':<6} | {'件数':<5} | {'的中率':<6} | {'回収率':<6} | {'収支'}")
        print("-" * 50)
        
        best_roi = 0
        best_th = 0
        
        for th in thresholds:
            # 確率が閾値を超えている馬だけを買う
            bets = df[df['proba'] >= th]
            
            if len(bets) == 0:
                continue
                
            # 1. 投資金額
            cost = len(bets) * 100
            
            # 2. 配当金額
            hits = bets[bets['kakutei_chakujun'] == 1]
            return_amount = (hits['tansho_odds'] / 10).sum() * 100
            
            # 3. 指標
            profit = return_amount - cost
            recovery_rate = return_amount / cost * 100
            hit_rate = len(hits) / len(bets) * 100
            
            print(f"{th:.2f}   | {len(bets):<5} | {hit_rate:.1f}%  | {recovery_rate:.1f}%  | {profit:+,.0f}円")
            
            if recovery_rate > best_roi:
                best_roi = recovery_rate
                best_th = th
                
        print("-" * 50)
        print(f"🏆 最強の閾値: {best_th:.2f} (回収率: {best_roi:.1f}%)")
        
        if best_roi > 100:
            print("🎉 おめでとうございます！プラス収支の条件が見つかりました！")
        else:
            print("🤔 まだ条件が厳しいようです。特徴量の改善が必要です。")