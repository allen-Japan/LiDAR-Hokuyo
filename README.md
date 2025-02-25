# **LiDAR-Hokuyo**

**LiDAR Data Visualization and Clustering**  
This project collects, analyzes, and visualizes LiDAR sensor data.  
It connects to a LiDAR sensor, retrieves measurement data, applies configurable intensity thresholds to detect high-reflectance points, and performs clustering using DBSCAN.  
The clustering results are visualized using matplotlib, with additional metrics (e.g., line length, rotation angle, cluster average intensity, and FPS) displayed on the screen.

## **Features**

- **Real-time Data Acquisition:** Connect to a LiDAR sensor over the network.  
- **Dynamic Thresholding:** Configure intensity and distance thresholds using an external `params.yaml` file.  
- **Clustering:** Detect high-reflectance points using DBSCAN and compute cluster metrics.  
- **Visualization:** Real-time plotting of LiDAR data and clustering results, with FPS displayed.

## **Requirements**

The required packages are listed in the `requirements.txt` file.  
*Note:* Packages such as `socket` and `time` are part of the Python standard library and are not included.

## **Installation**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/allen-Japan/LiDAR-Hokuyo.git
   cd LiDAR-Hokuyo

2. **Create and activate a virtual environment (optional but recommended):**

    ```bash
   python -m venv venv
   source venv/bin/activate   
   On Windows use: venv/Scripts/activate

3. **pip install -r requirements.txt**

    ```bash
   pip install -r requirements.txt

## **Configuration**
Configure the project parameters in the params.yaml file.  
Adjust the parameters as needed for your sensor and application.

## **Usage
Run the main script:  
    ```bash
    python main.py
The program will attempt to connect to the LiDAR sensor,  
retrieve data, and display the visualization window with clustering results  
and additional metrics (including FPS) updated in real time.

## **Project Structure
main.py: Main entry point of the application.  
plot_xy_data.py: Contains functions for data visualization and plotting.  
threshold_intensity.py: Implements threshold calculations.  
params.yaml: Parameter configuration file.  
requirements.txt: Lists required packages.  
Other modules: Modules such as get_distanceData and connect_LiDAR handle sensor communication.  