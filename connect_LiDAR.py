import socket
import time

class Sensor:
    def __init__(self, ip_address='192.168.0.10', port=10940):
        # 接続先のIPアドレスとポート番号
        self.host = ip_address
        self.port = port
        self.sensor = None
        self.model = None
        self.dmin = 0
        self.dmax = 30000
        self.ares = 1080
        self.amin = 0
        self.amax = 1080
        self.afrt = 540

    def create_connection(self, max_retries=5):
        attempt = 0
        while attempt < max_retries:
            try:
                # ソケットの作成
                self.sensor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sensor.settimeout(1)  # 1秒でタイムアウト
                # 接続を試みる
                self.sensor.connect((self.host, self.port))
                self.sensor.settimeout(5)
                print("Connected to", self.host)
                return self.sensor  # 接続成功時にソケットを返す
            except socket.error as e:
                attempt += 1
                print(f"Attempt {attempt} failed: {e}. Retrying...")
                time.sleep(1)  # リトライ間隔を待つ
        print(f"Failed to connect to {self.host} after {max_retries} attempts.")
        return None  # 最大リトライ回数を超えた場合、Noneを返す
    
    def update_sensorInfo(self):
        try:
            ppcmd = "PP".encode('utf-8') + b'\r\n'
            self.sensor.sendall(ppcmd)
            data = self.getResponse()
            parsed_info = self.parse_sensor_info(data)
            if "MODL" in parsed_info:
                self.model = str(parsed_info["MODL"])
                print(self.model)
            if "DMIN" in parsed_info:
                self.dmin = int(parsed_info["DMIN"])
            if "DMAX" in parsed_info:
                self.dmax = int(parsed_info["DMAX"])
            if "ARES" in parsed_info:
                self.ares = int(parsed_info["ARES"])
            if "AMIN" in parsed_info:
                self.amin = int(parsed_info["AMIN"])
            if "AMAX" in parsed_info:
                self.amax = int(parsed_info["AMAX"])
            if "AFRT" in parsed_info:
                self.afrt = int(parsed_info["AFRT"])
            return True
        except Exception as e:
            print("Error updating sensor info:", e)
            return False
    
    def send_p_cmd(self, cmd="II"):
        p_cmd = cmd.encode('utf-8') + b'\r\n'
        self.sensor.sendall(p_cmd)
        data = self.getResponse()
        info_dict = self.parse_sensor_info(data)
        return info_dict
    
    def send_d_cmd(self, cmd="GD", startStep=0, endStep=1080, cluster=0, skip=0, limit=0):
        if startStep < self.amin or endStep > self.amax:
            return None
        str_startStep = '{:04d}'.format(startStep)
        str_endStep = '{:04d}'.format(endStep)
        str_cluster = '{:02d}'.format(cluster)
        d_cmd = (cmd + str_startStep + str_endStep + str_cluster).encode("utf-8") + b'\r\n'
        self.sensor.sendall(d_cmd)
        data = self.getResponse()
        data_dict = self.parse_data(data)
        return data_dict
    
    def parse_sensor_info(self, sensor_info):
        info_dict = {}
        lines = sensor_info.splitlines()
        if lines:
            info_dict["Echo"] = lines[0]
        if len(lines) > 1:
            info_dict["Status"] = lines[1][:-1]
        for line in lines[2:]:
            if ':' in line:
                key, rest = line.split(":", 1)
                if ";" in rest:
                    value = rest.split(";", 1)[0]
                else:
                    value = rest
                info_dict[key.strip()] = value.strip()
        return info_dict

    def parse_data(self, data):
        lines = data.split('\n')
        result = {}
        if len(lines) >= 1:
            result["Echo"] = lines[0]
        if len(lines) >= 2:
            result["Status"] = lines[1][:-1]
        if len(lines) >= 3:
            result["Timestamp"] = lines[2][:-1]
        if len(lines) >= 4:
            result["Data"] = "".join([line[:-1] for line in lines[3:] if line != ''])
        return result

    def getResponse(self):
        response = b''
        while True:
            data = self.sensor.recv(1024)
            if not data:
                break
            response += data
            # 終端文字が受信されたらループを抜ける
            if response.endswith(b'\n\n'):
                break
        response = response.decode()
        return response

def setup_LiDAR(ip_address='192.168.0.10', port=10940, max_attempts=5):
    sensor = Sensor(ip_address=ip_address, port=port)
    if sensor.create_connection() is None:
        return False, None

    attempts = 0
    while attempts < max_attempts:
        sensor.update_sensorInfo()
        ii_info = sensor.send_p_cmd(cmd="II")
        if ii_info["LASR"] == "OFF":
            bm_info = sensor.send_p_cmd(cmd="BM")
            if bm_info["Status"] == "00":
                print("Laser activated successfully.")
                return True, sensor
        time.sleep(1)
        attempts += 1
    return False, None


if __name__ == "__main__":
    flag, sensor = setup_LiDAR()
    data = sensor.send_d_cmd()
    print(data)

