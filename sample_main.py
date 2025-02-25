import get_distanceData
import connect_LiDAR
import pandas as pd
import threshold_intensity
import matplotlib.pyplot as plt
import plot_data

def main():

    flag_connect, sensor = connect_LiDAR.setup_LiDAR()
    if flag_connect == False:
        print("Error")
        exit()
    fig, ax, scatter_plot = plot_data.set_plt()
    cluster_line_artists = [] 
    overall_marker_artist = None 
    info_text_obj = None

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

if __name__ == "__main__":
    main()