import pandas as pd
import numpy as np
import math

print("Data yüklənir...")
df = pd.read_excel('dummy_muqayise2.xlsx')
df = df.sort_values(by=['vehicle_id', 'timestamp']).reset_index(drop=True)

df['final_speed'] = df['speed2'].clip(upper=120)
df['Ay'] = df['timestamp'].dt.month

QARAJ_LAT = 0.0000
QARAJ_LON = 0.0000

def haversine_array(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi/2.0)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(delta_lambda/2.0)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))

df['dist_to_garage_m'] = haversine_array(df['latitude'], df['longitude'], QARAJ_LAT, QARAJ_LON)

df['next_timestamp'] = df.groupby('vehicle_id')['timestamp'].shift(-1)
df['next_distance'] = df.groupby('vehicle_id')['distance'].shift(-1)
df['next_lat'] = df.groupby('vehicle_id')['latitude'].shift(-1)
df['next_lon'] = df.groupby('vehicle_id')['longitude'].shift(-1)

df['Müddət (saat)'] = (df['next_timestamp'] - df['timestamp']).dt.total_seconds() / 3600.0

df['raw_dist_diff'] = df['next_distance'] - df['distance']
df['Məsafə (km)'] = np.where(
    (df['raw_dist_diff'] < 0) | (df['raw_dist_diff'] > (df['Müddət (saat)'] * 120 + 5)),
    0,
    df['raw_dist_diff']
)

df['hour'] = df['timestamp'].dt.hour

conditions = [
    (df['Müddət (saat)'] > 2.0) & ((df['hour'] >= 23) | (df['hour'] < 7)),
    (df['Müddət (saat)'] > 2.0),
    (df['final_speed'] > 0),
    (df['final_speed'] == 0) & (df['engine_speed'] > 0),
    (df['final_speed'] == 0) & (df['dist_to_garage_m'] <= 100),
    (df['final_speed'] == 0) & (df['dist_to_garage_m'] > 100)
]
choices = ['Gecə Parklaması', 'Siqnal itən ərazi', 'Hərəkətdə', 'Boşda işləmə', 'Qarajda', 'Yolda parklama']
df['status'] = np.select(conditions, choices, default='Bilinməyən')

df['status_block'] = (df['status'] != df['status'].shift(1)).cumsum()
block_duration = df.groupby(['vehicle_id', 'status_block'])['Müddət (saat)'].sum().reset_index(name='block_duration_hr')
df = df.merge(block_duration, on=['vehicle_id', 'status_block'], how='left')
df.loc[(df['status'] == 'Yolda parklama') & (df['block_duration_hr'] <= (5/60.0)), 'status'] = 'Svetofor / Qısa dayanma'

def koordinat_formati(r):
    if r['status'] == 'Siqnal itən ərazi' and pd.notnull(r['next_lat']):
        return f"Qopub: {r['latitude']:.3f}, {r['longitude']:.3f} -> Bərpa: {r['next_lat']:.3f}, {r['next_lon']:.3f}"
    elif r['status'] in ['Yolda parklama', 'Svetofor / Qısa dayanma', 'Gecə Parklaması', 'Boşda işləmə']:
        return f"{r['latitude']:.3f}, {r['longitude']:.3f}"
    else:
        return "-"
df['Məkan_Koordinatı'] = df.apply(koordinat_formati, axis=1)

monthly_days = df.groupby(['vehicle_id', 'Ay'])['timestamp'].apply(lambda x: x.dt.date.nunique()).reset_index(name='days_in_month')
df = df.merge(monthly_days, on=['vehicle_id', 'Ay'], how='left')
df['Maşın_Vəziyyəti'] = np.where(df['days_in_month'] >= 20,
                                 'Analizə Uyğundur',
                                 'Kifayət qədər data yoxdur (Təmirdə/Yeni/GPS xarab)')

df['Müddət (saat)'] = df['Müddət (saat)'].fillna(0)
df['Məsafə (km)'] = df['Məsafə (km)'].fillna(0)

final_cols = ['vehicle_id', 'timestamp', 'Ay', 'final_speed', 'engine_speed', 'distance',
              'status', 'Müddət (saat)', 'Məsafə (km)', 'Məkan_Koordinatı', 'Maşın_Vəziyyəti']
df_final = df[final_cols]

print("Excel faylı yaradılır...")
df_final.to_excel('dummy_muqayise3.xlsx', index=False)
print("Uğurla tamamlandı! dummy_muqayise3.xlsx hazırdır.")
