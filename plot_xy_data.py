import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import numpy as np

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

def clusterling_circle(high_reflectors_distance, cluster_centers, eps=20, min_samples=3):
    coords = high_reflectors_distance[["x", "y"]].values
    # eps, min_samples は状況に合わせて調整
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    high_reflectors = high_reflectors_distance.copy()  # コピーして操作
    high_reflectors["cluster"] = clustering.labels_
    
    # 各クラスタごとに円を描画（ノイズは除外）
    for cl in high_reflectors["cluster"].unique():
        if cl == -1:
            continue
        cluster_points = high_reflectors[high_reflectors["cluster"] == cl]
        center_x = cluster_points["x"].mean()
        center_y = cluster_points["y"].mean()
        cluster_centers.append((center_x, center_y))
    return cluster_centers, high_reflectors

def draw_clustering_circle(high_reflectors, ax):
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


def weight_point(cluster_centers):
    centers_array = np.array(cluster_centers)
    # x座標順にソート（任意の順序でOK）
    sorted_indices = np.argsort(centers_array[:, 0])
    sorted_centers = centers_array[sorted_indices]
    # 直線の中心位置を計算
    overall_center = sorted_centers.mean(axis=0)
    
    # 直線の全長（最も左と右のクラスタ重心間の距離）
    if sorted_centers.shape[0] >= 2:
        line_distance = np.linalg.norm(sorted_centers[-1] - sorted_centers[0])
    else:
        line_distance = 0.0
    
    # 各クラスタ重心から原点までの距離を計算
    center_distances = np.linalg.norm(sorted_centers, axis=1)
    average_center_distance = np.mean(center_distances)
    
    # 直線の回転角度（水平からの角度：最初と最後のクラスタ重心の角度）
    delta = sorted_centers[-1] - sorted_centers[0]
    angle_rad = np.arctan2(delta[1], delta[0])
    angle_deg = np.degrees(angle_rad)

    return line_distance, average_center_distance, angle_deg, sorted_centers, overall_center

def draw_cluster_weight(ax, cluster_line_artists, overall_marker_artist, sorted_centers, overall_center):
    line, = ax.plot(sorted_centers[:, 0], sorted_centers[:, 1],
                    color='green', linestyle='-', linewidth=2)
    cluster_line_artists.append(line)

    overall_marker_artist, = ax.plot(overall_center[0], overall_center[1],
                                    marker='x', color='green', markersize=10, markeredgewidth=3)

    return cluster_line_artists, overall_marker_artist

def update_info_text(ax, info_string, info_text_obj):
    # 既存の情報テキストがあれば削除
    if info_text_obj is not None:
        info_text_obj.remove()
    # ax の座標系 (0～1) で、左上に表示（bbox で背景を半透明に）
    info_text_obj = ax.text(0.02, 0.98, info_string, transform=ax.transAxes,
                            fontsize=10, verticalalignment='top',
                            bbox=dict(facecolor='white', alpha=0.5))
    return info_text_obj

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
    cluster_line_artists = [] 
    overall_marker_artist = None 
    info_text_obj = None  # 情報テキスト用オブジェクト

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

        df_intensity["Distance"] = df_distance["Distance"]

        df_intensity = threshold_intensity.apply_threshold(
            df=df_intensity, 
            threshold_intensity=4000, 
            threshold_distance_dead=200)
        
        # 閾値が設定されている行で、Intensityが閾値を超えている場合はcolorを緑色に変更
        mask = df_intensity["Threshold"].notnull() & (df_intensity["Intensity"] > df_intensity["Threshold"])
        df_intensity.loc[mask, "color"] = "green"
        df_distance.loc[mask, "color"] = "red" 

        # plot_data = pd.concat([df_distance, df_intensity], ignore_index=True)
        plot_data = df_distance
        update_plot(ax, scatter_plot, plot_data["x"], plot_data["y"], plot_data["color"])

        # Distance側の高反射点（Intensity閾値を超えた点）でクラスタリングを行う
        high_reflectors_distance = df_distance.loc[mask].copy()
        high_reflectors_distance.loc[:, "Intensity"] = df_intensity.loc[mask, "Intensity"].values

        # リセット
        for patch in list(ax.patches):
            patch.remove()
        for line in cluster_line_artists:
            line.remove()
        cluster_line_artists = [] 
        if overall_marker_artist is not None:
            overall_marker_artist.remove()
            overall_marker_artist = None
        cluster_centers = []    
        
        # DBSCANによるクラスタリングを行い、クラスタが見つかった場合は赤丸を追加
        if not high_reflectors_distance.empty:
            cluster_centers, high_reflectors = clusterling_circle(
                high_reflectors_distance=high_reflectors_distance, 
                cluster_centers=cluster_centers,
                eps=50, 
                min_samples=5)
            
            draw_clustering_circle(high_reflectors=high_reflectors, ax=ax)

            # 2つ以上のクラスタがある場合、各クラスタ重心を直線で結び、その直線の中心を求める
            if len(cluster_centers) >= 2:
                line_distance, average_center_distance, angle_deg, sorted_centers, overall_center = weight_point(
                    cluster_centers=cluster_centers)
                
                cluster_line_artists, overall_marker_artist= draw_cluster_weight(
                    ax=ax, 
                    cluster_line_artists=cluster_line_artists, 
                    overall_marker_artist=overall_marker_artist, 
                    sorted_centers=sorted_centers, 
                    overall_center=overall_center)
                
                valid_clusters = high_reflectors[high_reflectors["cluster"] != -1].groupby("cluster")
                cluster_info_lines = []
                for cl, group in valid_clusters:
                    avg_intensity = group["Intensity"].mean()
                    cluster_info_lines.append(f"Cluster {cl}: Avg Intensity = {avg_intensity:.2f}")
                clusters_info = "\n".join(cluster_info_lines)
                
                # 情報文字列の作成
                info_string = (
                    f"Line Length: {line_distance:.2f}\n"
                    f"Average Distance to Overall Center: {average_center_distance:.2f}\n"
                    f"Line Rotation Angle: {angle_deg:.2f}°\n"
                    f"Overall Center: (x: {overall_center[0]:.2f}, y: {overall_center[1]:.2f})\n"
                    f"{clusters_info}"
                )
                # 画面上に情報テキストを更新
                info_text_obj = update_info_text(ax, info_string, info_text_obj)
            
        plt.pause(0.001)

        if not plt.fignum_exists(fig.number):  # ウィンドウが閉じられた場合
            break