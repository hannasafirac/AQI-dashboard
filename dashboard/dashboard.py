import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('dashboard/daily_data.csv')
    data['date'] = pd.to_datetime(data['date'])
    return data

data = load_data()

# Sidebar

st.sidebar.title("Filter Data")

# Input tanggal
selected_date = st.sidebar.date_input("Pilih Tanggal", min_value=pd.to_datetime('2013-03-01'), max_value=pd.to_datetime('2017-02-28'), value=pd.to_datetime('2013-03-01'))

# Input station
stations = ['Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan', 'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan', 'Wanliu', 'Wanshouxigong']
selected_station = st.sidebar.selectbox("Pilih Station", stations)

# Filter data
data_1 = data[(data['date'] == pd.to_datetime(selected_date)) & (data['station'] == selected_station)]
data_2 = data[(data['date'] <= pd.to_datetime(selected_date)) & (data['date'] >= pd.to_datetime(selected_date) - pd.Timedelta(days=6)) & (data['station'] == selected_station)]
data_3 = data[data['date'] == pd.to_datetime(selected_date)]

# Mainbar
st.title("Dashboard Air Quality Index (AQI)")

# Subheader 1: Informasi Suhu, AQI, dan Kategori AQI
st.subheader("Informasi Hari Ini")
col1, col2 = st.columns([1, 3])  # Kolom 2 lebih lebar
with col1:
    st.metric("AQI", f"{data_1['AQI'].values[0]:.2f}")  # Dua angka di belakang koma
with col2:
    st.metric("Kategori", data_1['AQI_level'].values[0])

# Subheader 2: Line Plot AQI dan Polutan
st.subheader("Trend 7 Hari Terakhir")
col1, col2 = st.columns(2)
with col1:
    st.write("**Pergerakan AQI**")
    fig, ax = plt.subplots(figsize=(8, 7))  # Ukuran plot AQI
    sns.lineplot(data=data_2, x='date', y='AQI', ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel('Tanggal')
    st.pyplot(fig)

with col2:
    st.write("**Pergerakan Tingkat Polutan**")
    # Menggunakan st.multiselect untuk memilih lebih dari satu polutan
    pollutants = st.multiselect("Pilih Polutan", ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'])
    
    if pollutants:  # Jika ada polutan yang dipilih
        fig, ax = plt.subplots(figsize=(8, 4))  # Ukuran plot polutan
        for pollutant in pollutants:
            sns.lineplot(data=data_2, x='date', y=pollutant, ax=ax, label=pollutant)
        plt.xticks(rotation=45)
        plt.ylabel('Konsentrasi (µg/m³)')
        plt.xlabel('Tanggal')
        plt.legend()  # Menampilkan legenda untuk membedakan polutan
        st.pyplot(fig)
    else:
        st.write("Silakan pilih polutan untuk menampilkan grafik.")

# Subheader 3: Bar Plot Tingkat AQI Tiap Station
st.subheader("Tingkat AQI Tiap Station Hari Ini")
data_3_sorted = data_3.sort_values(by='AQI', ascending=False)
max_aqi_station = data_3_sorted[data_3_sorted['AQI'] == data_3_sorted['AQI'].max()]
fig, ax = plt.subplots(figsize=(10, 6))  # Ukuran plot
# Plot bar biasa dengan warna abu-abu
sns.barplot(data=data_3_sorted, x='AQI', y='station', color='lightgray', errorbar=None, orient='h')
# Plot bar yang memiliki AQI maksimum dengan warna mencolok
sns.barplot(data=max_aqi_station, x='AQI', y='station', color='brown', errorbar=None, orient='h')
plt.xlabel("AQI")
plt.ylabel("Station")
st.pyplot(fig)

# Subheader 4: Peta Persebaran AQI
st.subheader("Persebaran AQI di Seluruh Station")

# Koordinat station
station_coords = {
    'Aotizhongxin': [34.374734, 109.016205],
    'Changping': [40.219646, 116.225091],
    'Dingling': [40.148371, 117.695525],
    'Dongsi': [39.929247, 116.417731],
    'Guanyuan': [29.558719, 112.00761],
    'Gucheng': [37.349035, 115.964682],
    'Huairou': [40.315481, 116.626028],
    'Nongzhanguan': [39.944006, 116.467997],
    'Shunyi': [40.14875, 116.653875],
    'Tiantan': [39.887858, 116.392896],
    'Wanliu': [34.81287, 113.989313],
    'Wanshouxigong': [34.81287, 113.989313]
}

# Warna berdasarkan kategori AQI
aqi_colors = {
    'Good': 'green',
    'Moderate': 'yellow',
    'Unhealthy for Sensitive Groups': 'orange',
    'Unhealthy': 'red',
    'Very Unhealthy': 'purple',
    'Hazardous': 'maroon'
}

aqi_df = pd.DataFrame({
    'Kategori': ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous'],
    'Warna': ['Hijau', 'Kuning', 'Oranye', 'Merah', 'Ungu', 'Marun']
})


st.write('Informasi kategori AQI')
st.dataframe(aqi_df, use_container_width=True)

# Buat peta
m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)  # Lokasi default: Beijing

for station, coords in station_coords.items():
    aqi_level = data_3[data_3['station'] == station]['AQI_level'].values[0]
    folium.Marker(
        location=coords,
        popup=f"{station}: {aqi_level}",
        icon=folium.Icon(color=aqi_colors.get(aqi_level, 'gray'))
    ).add_to(m)

# Tampilkan peta
folium_static(m)
