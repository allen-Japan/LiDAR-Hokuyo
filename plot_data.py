import matplotlib.pyplot as plt


def set_plt():
    plt.ion()  # 対話モードを有効にする
    fig, ax = plt.subplots()  # グラフのウィンドウを作成
    scatter_plot = ax.scatter([], [], marker="o", s=0.5)  # 空のプロットを作成
    ax.scatter(0, 0, color='red', s=10)  # 原点を赤い点でプロット
    ax.set_xlim(-15000, 15000)
    ax.set_ylim(-15000, 15000)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Scatter Plot of x and y')
    ax.grid(True)
    return fig, ax, scatter_plot

def update_plot(ax, scatter_plot, x_data, y_data, color_data):
    scatter_plot.set_offsets(list(zip(x_data, y_data)))  # データを更新
    scatter_plot.set_facecolor(color_data)  # 文字色（点の色）を更新
    ax.relim()  # 軸のリミットを再計算
    ax.autoscale_view()  # スケールを更新
    plt.pause(0.01)  # 画面を更新

if __name__ == "__main__":
    import get_distanceData
    import connect_LiDAR
    import pandas as pd
    import threshold_intensity
    from sklearn.cluster import DBSCAN
    import numpy as np

    flag_connect, sensor = connect_LiDAR.setup_LiDAR()
    if flag_connect == False:
        print("Error")
        exit()
    fig, ax, scatter_plot = set_plt()
    while True:
        data = get_distanceData.sendGE(sensor=sensor)
        df_distance = pd.DataFrame({
            "x": data["x_distance"],
            "y": data["y_distance"],
            "Distance": data["Distance"],
            "color": "blue" 
        })
        df_intensity = pd.DataFrame({
            "x": data["x_intensity"],
            "y": data["y_intensity"],
            'Intensity': data['Intensity'],
            "color": "red"
        })

        # df_intensityにDistance情報を追加（インデックスが対応している前提）
        df_intensity["Distance"] = df_distance["Distance"]

        df_intensity = threshold_intensity.apply_threshold(
            df=df_intensity, 
            threshold_intensity=4000, 
            threshold_distance_dead=200
            )
        
        # 閾値が設定されている行で、Intensityが閾値を超えている場合はcolorを緑色に変更
        mask = df_intensity["Threshold"].notnull() & (df_intensity["Intensity"] > df_intensity["Threshold"])
        df_intensity.loc[mask, "color"] = "green"
        df_distance.loc[mask, "color"] = "red" 

        # プロット更新（ここでは散布図の再描画としています）
        # plot_data = pd.concat([df_distance, df_intensity], ignore_index=True)
        plot_data = df_distance
        print(df_intensity)
        update_plot(ax, scatter_plot, plot_data["x"], plot_data["y"], plot_data["color"])

        # Distance側の高反射点（Intensity閾値を超えた点）でクラスタリングを行う
        high_reflectors_distance = df_distance[mask]
        
        # 既存のクラスタリング円を削除
        for patch in list(ax.patches):
            patch.remove()
        
        # DBSCANによるクラスタリングを行い、クラスタが見つかった場合は赤丸を追加
        if not high_reflectors_distance.empty:
            coords = high_reflectors_distance[["x", "y"]].values
            # eps, min_samples は状況に合わせて調整
            clustering = DBSCAN(eps=20, min_samples=1).fit(coords)
            high_reflectors = high_reflectors_distance.copy()  # コピーして操作
            high_reflectors["cluster"] = clustering.labels_
            
            # 各クラスタごとに円を描画（ノイズは除外）
            for cl in high_reflectors["cluster"].unique():
                if cl == -1:
                    continue
                cluster_points = high_reflectors[high_reflectors["cluster"] == cl]
                center_x = cluster_points["x"].mean()
                center_y = cluster_points["y"].mean()
                distances = np.sqrt((cluster_points["x"] - center_x)**2 + (cluster_points["y"] - center_y)**2)
                radius = distances.max() * 1.1  # 余裕を持たせる
                circle = plt.Circle((center_x, center_y), radius, color="red", fill=False, linewidth=2)
                ax.add_patch(circle)
        
        # 明示的に描画更新
        plt.pause(0.001)

        if not plt.fignum_exists(fig.number):  # ウィンドウが閉じられた場合
            break