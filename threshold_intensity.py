# 各Distanceに応じたIntensity閾値を計算する関数
def calc_threshold(dist, threshold_intensity=8000, threshold_distance_dead=200):
    if dist < threshold_distance_dead:
        # 200未満は閾値対象外（または任意の値、ここではNoneを返す）
        return None
    elif dist <= 500:
        # 200から500の間は線形に2000から8000に変化
        return 2000 + (dist - threshold_distance_dead) * (threshold_intensity - 2000) / (500 - threshold_distance_dead)
    else:
        # 500以上は固定で8000
        return threshold_intensity
    
def apply_threshold(df, threshold_intensity=8000, threshold_distance_dead=200):
    # 閾値列を追加
    df["Threshold"] = df["Distance"].apply(lambda dist: calc_threshold(
        dist, 
        threshold_intensity=threshold_intensity, 
        threshold_distance_dead=threshold_distance_dead
        ))
    return df