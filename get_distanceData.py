import connect_LiDAR
import numpy as np
import pandas as pd

def decodeGD_MeasureData(data_dict, sensor, startStep=0, endStep=1080):
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

    df_xy = pd.DataFrame({'x_distance': df["x"], 'y_distance': df["y"], 'Distance': df["Distance"], 'Row Data' : df["Original"]})
    return df_xy

def decodeGE_MeasureData(data_dict, sensor, startStep=0, endStep=1080):
    data = data_dict["Data"]
    substrings = [data[i:i+3] for i in range(0, len(data), 3)]
    df = pd.DataFrame(range(startStep,endStep + 1), columns = ["Step"])
    df['Original_Distance'] = substrings[::2]
    df['Original_intensity'] = substrings[1::2]

    hex30 = 0x30
    df[['Char_1_d', 'Char_2_d', 'Char_3_d']] = pd.DataFrame([[bin(ord(c) - hex30)[2:].zfill(6) for c in row] for row in df['Original_Distance']], index=df.index)
    df['Distance'] = df['Char_1_d'] + df['Char_2_d'] + df['Char_3_d']
    df['Distance'] = [int(x, 2) for x in df['Distance']]

    df[['Char_1_i', 'Char_2_i', 'Char_3_i']] = pd.DataFrame([[bin(ord(c) - hex30)[2:].zfill(6) for c in row] for row in df['Original_intensity']], index=df.index)
    df['Intensity'] = df['Char_1_i'] + df['Char_2_i'] + df['Char_3_i']
    df['Intensity'] = [int(x, 2) for x in df['Intensity']]

    df['Theta_d'] = (2 * np.pi / sensor.ares) * (df['Step'] - sensor.afrt) + (np.pi / 2)
    df['cos_theta_d'] = np.cos(df['Theta_d'])
    df['sin_theta_d'] = np.sin(df['Theta_d'])
    df['x_d'] = df['Distance'] * df['cos_theta_d']
    df['y_d'] = df['Distance'] * df['sin_theta_d']

    df['Theta_i'] = (2 * np.pi / sensor.ares) * (df['Step'] - sensor.afrt) + (np.pi / 2)
    df['cos_theta_i'] = np.cos(df['Theta_i'])
    df['sin_theta_i'] = np.sin(df['Theta_i'])
    df['x_i'] = df['Intensity'] * df['cos_theta_i']
    df['y_i'] = df['Intensity'] * df['sin_theta_i']

    df_xy = pd.DataFrame({'x_distance': df["x_d"], 'y_distance': df["y_d"], 'Distance': df["Distance"], 
                          'x_intensity': df["x_i"], 'y_intensity': df["y_i"], 'Intensity': df['Intensity'],
                          'Row Distance Data' : df["Original_Distance"],'Row Intensity Data' : df["Original_intensity"]})

    return df_xy

def sendGD(sensor, startStep=0, endStep=1080):
    data = sensor.send_d_cmd(cmd="GD",startStep=startStep, endStep=endStep, cluster=0)
    full_data = decodeGD_MeasureData(data, sensor, startStep=startStep, endStep=endStep)
    return full_data

def sendGE(sensor, startStep=0, endStep=1080):
    data = sensor.send_d_cmd(cmd="GE",startStep=startStep, endStep=endStep, cluster=0)
    full_data = decodeGE_MeasureData(data, sensor, startStep=startStep, endStep=endStep)
    return full_data
