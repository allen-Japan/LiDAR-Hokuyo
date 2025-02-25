import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import numpy as np
import time

def update_fps_text(ax,fps_text_obj, fps_string):
    # 既存のfpsテキストがあれば削除
    if fps_text_obj is not None:
        fps_text_obj.remove()
    # 右下にFPS情報を表示
    fps_text_obj = ax.text(0.98, 0.02, fps_string, transform=ax.transAxes,
                           fontsize=10, horizontalalignment='right', verticalalignment='bottom',
                           bbox=dict(facecolor='white', alpha=0.5))
    return fps_text_obj

def calc_fps(prev_time):
    current_time = time.time()
    delta = current_time - prev_time
    fps = 1.0 / delta if delta > 0 else 0.0
    prev_time = current_time
    fps_string = f"FPS: {fps:.2f}"
    return prev_time, fps_string

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
