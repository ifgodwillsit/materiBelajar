from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

KOORDINAT = {
    "Borobudur": (-7.6079, 110.2038),
    "Lake Toba": (2.6845, 98.8756),
    "Mandalika": (-8.8927, 116.3024),
    "Labuan Bajo": (-8.4964, 119.8877),
    "Likupang": (1.6810, 125.0760),
    "Bali": (-8.4095, 115.1889),
    "Raja Ampat": (-0.2346, 130.5164),
    "Morotai": (2.3333, 128.4000),
    "Tanjung Kelayang": (-2.5500, 107.7500),
    "Jakarta": (-6.2088, 106.8456),
    "Bromo Tengger Semeru National Park": (-7.9425, 112.9530),
    "Riau Islands": (0.9186, 104.4665),
    "Wakatobi": (-5.3190, 123.5950)
}

st.set_page_config(page_title="Dashboard Wisata", layout="wide")
st.title("Dashboard Destinasi Wisata Indonesia")
st.write("Mengambil data destinasi melalui web scraping dan suhu melalui REST API.")

if st.button("Ambil Data dan Tampilkan Dashboard", type="primary"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    section = None
    for url in ["https://indonesia.travel", "https://www.indonesia.travel/gb/en/home.html"]:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            section = soup.find("section", class_="s-recomendation")
            if section:
                break
        except Exception:
            continue

    data_wisata = []
    seen = set()

    if section:
        items = section.find_all("h3", class_="title-non-active")
        for h3 in items:
            destinasi = h3.get_text(strip=True)
            if destinasi not in seen and destinasi in KOORDINAT:
                seen.add(destinasi)
                span = h3.find_next("span")
                provinsi = span.get_text(strip=True) if span else ""
                lat, lon = KOORDINAT[destinasi]

                api_url = "https://api.open-meteo.com/v1/forecast"
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m",
                    "timezone": "Asia/Jakarta"
                }
                res_api = requests.get(api_url, params=params).json()
                suhu = res_api.get("current", {}).get("temperature_2m", None)

                data_wisata.append({
                    "destinasi": destinasi,
                    "provinsi": provinsi,
                    "latitude": lat,
                    "longitude": lon,
                    "suhu": suhu
                })

                if len(data_wisata) == 13:
                    break

    df = pd.DataFrame(data_wisata, columns=["destinasi", "provinsi", "latitude", "longitude", "suhu"])

    st.subheader("Data Destinasi Wisata")
    st.caption(f"{len(df)} destinasi berhasil diambil.")
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.subheader("Visualisasi")
        col1, col2 = st.columns(2)

        with col1:
            prov_counts = df["provinsi"].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(prov_counts, labels=prov_counts.index, autopct="%1.1f%%", startangle=90)
            ax1.set_title("Persentase Destinasi per Provinsi")
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots()
            ax2.bar(df["destinasi"], df["suhu"])
            ax2.set_title("Suhu Destinasi Wisata")
            ax2.set_xlabel("Destinasi")
            ax2.set_ylabel("Suhu (°C)")
            plt.xticks(rotation=90)
            st.pyplot(fig2)
