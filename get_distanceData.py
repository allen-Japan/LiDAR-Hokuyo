import connect_LiDAR
import numpy as np
import pandas as pd


def decodeMeasureData(data_dict, sensor, startStep=0, endStep=1080):
    data = data_dict["Data"]
    substrings = [data[i:i+3] for i in range(0, len(data), 3)]
    df = pd.DataFrame(range(startStep,endStep + 1), columns = ["Step"])
    df['Original'] = pd.DataFrame(substrings)

    hex30 = 0x30
    df[['Char_1', 'Char_2', 'Char_3']] = pd.DataFrame([[bin(ord(c) - hex30)[2:].zfill(6) for c in row] for row in df['Original']], index=df.index)
    df['Distance'] = df['Char_1'] + df['Char_2'] + df['Char_3']
    df['Distance'] = [int(x, 2) for x in df['Distance']]

    df['Theta'] = (2 * np.pi / sensor.ares) * (df['Step'] - sensor.afrt) + (np.pi / 2)
    df['cos_theta'] = np.cos(df['Theta'])
    df['sin_theta'] = np.sin(df['Theta'])
    df['x'] = df['Distance'] * df['cos_theta']
    df['y'] = df['Distance'] * df['sin_theta']

    df_xy = pd.DataFrame({'x': df["x"], 'y': df["y"], 'Distance': df["Distance"], 'Row Data' : df["Original"]})
    return df_xy

flag_connect, sensor = connect_LiDAR.setup_LiDAR()
if flag_connect == False:
    print("Error")
    exit()

startStep = 0
endStep=1080

data = sensor.send_d_cmd(startStep=startStep, endStep=endStep)
print(data)
full_data = decodeMeasureData(data, sensor, startStep=startStep, endStep=endStep)
print(full_data)