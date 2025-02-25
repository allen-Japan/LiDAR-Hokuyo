import get_distanceData
import connect_LiDAR
import pandas as pd
import threshold_intensity
import matplotlib.pyplot as plt
import plot_xy_data
import yaml
import time

with open("params.yaml", "r") as f:
    params = yaml.safe_load(f)

eps = params["eps"]
min_samples = params["min_samples"]
threshold_intensity_at500mm = params["threshold_intensity_at500mm"]
threshold_distance_dead = params["threshold_distance_dead"]
ip_address = params['ip_address']
port = params['port']
connection_max_attempts = params['connection_max_attempts']
flag_for_drawing = params["flag_for_drawing"]

def main(ip_address=ip_address, port=port, connection_max_attempts=connection_max_attempts, eps=eps, min_samples=min_samples, 
         threshold_intensity_at500mm=threshold_intensity_at500mm, threshold_distance_dead=threshold_distance_dead):

    flag_connect, sensor = connect_LiDAR.setup_LiDAR(
        ip_address=ip_address, 
        port=port, 
        connection_max_attempts=connection_max_attempts)
    
    if flag_connect == False:
        print("Connection Error")
        exit()
    
    prev_time = time.time() 

    if flag_for_drawing:
        fig, ax, scatter_plot = plot_xy_data.set_plt()
        cluster_line_artists = [] 
        overall_marker_artist = None 
        info_text_obj = None
        fps_text_obj = None

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
            threshold_intensity_at500mm=threshold_intensity_at500mm, 
            threshold_distance_dead=threshold_distance_dead)
        
        mask = df_intensity["Threshold"].notna() & (df_intensity["Intensity"] > df_intensity["Threshold"])
        # Distance側の高反射点（Intensity閾値を超えた点）でクラスタリングを行う
        high_reflectors_distance = df_distance.loc[mask].copy()
        high_reflectors_distance.loc[:, "Intensity"] = df_intensity.loc[mask, "Intensity"].values

        cluster_centers = []
        info_string = "No clusters detected."
        # DBSCANによるクラスタリング
        if not high_reflectors_distance.empty:
            cluster_centers, high_reflectors = plot_xy_data.clusterling_circle(
                high_reflectors_distance=high_reflectors_distance, 
                cluster_centers=cluster_centers,
                eps=eps, 
                min_samples=min_samples)
            
            # 2つ以上のクラスタがある場合、各クラスタ重心を直線で結び、その直線の中心を求める
            if len(cluster_centers) >= 2:
                line_distance, average_center_distance, angle_deg, sorted_centers, overall_center = plot_xy_data.weight_point(
                    cluster_centers=cluster_centers)
                valid_clusters = high_reflectors[high_reflectors["cluster"] != -1].groupby("cluster")
                cluster_info_lines = []
                for cl, group in valid_clusters:
                    avg_intensity = group["Intensity"].mean()
                    cluster_info_lines.append(f"Cluster {cl}: Avg Intensity = {avg_intensity:.2f}")
                clusters_info = "\n".join(cluster_info_lines)
                
                info_string = (
                    f"Line Length: {line_distance:.2f}\n"
                    f"Average Distance to Overall Center: {average_center_distance:.2f}\n"
                    f"Line Rotation Angle: {angle_deg:.2f}°\n"
                    f"Overall Center: (x: {overall_center[0]:.2f}, y: {overall_center[1]:.2f})\n"
                    f"{clusters_info}"
                )
                

        prev_time, fps_string = plot_xy_data.calc_fps(prev_time=prev_time)
        print(fps_string)
        print(info_string)
        """
        ココから描画を行う。
        不要な場合は削除
        flag_for_drawing = True
        """
        if flag_for_drawing:
            fps_text_obj = plot_xy_data.update_fps_text(ax=ax, fps_text_obj=fps_text_obj, fps_string=fps_string)
            df_intensity.loc[mask, "color"] = "green"
            df_distance.loc[mask, "color"] = "red" 
            # plot_data = pd.concat([df_distance, df_intensity], ignore_index=True)
            plot_data = df_distance
            plot_xy_data.update_plot(ax, scatter_plot, plot_data["x"], plot_data["y"], plot_data["color"])

            # リセット
            for patch in list(ax.patches):
                patch.remove()
            for line in cluster_line_artists:
                line.remove()
            cluster_line_artists = [] 
            if overall_marker_artist is not None:
                overall_marker_artist.remove()
                overall_marker_artist = None    
            
            # DBSCANによるクラスタリング
            if not high_reflectors_distance.empty:
                plot_xy_data.draw_clustering_circle(high_reflectors=high_reflectors, ax=ax)

                # 2つ以上のクラスタがある場合、各クラスタ重心を直線で結び、その直線の中心を求める
                if len(cluster_centers) >= 2:
                    cluster_line_artists, overall_marker_artist= plot_xy_data.draw_cluster_weight(
                        ax=ax, 
                        cluster_line_artists=cluster_line_artists, 
                        overall_marker_artist=overall_marker_artist, 
                        sorted_centers=sorted_centers, 
                        overall_center=overall_center)
                    
                    info_text_obj = plot_xy_data.update_info_text(ax, info_string, info_text_obj)
                
            plt.pause(0.001)

            if not plt.fignum_exists(fig.number):
                break

if __name__ == "__main__":
    main()