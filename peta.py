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

FALLBACK_HTML = """
<section class="s-recomendation">
    <div><h3 class="title-non-active">Borobudur</h3><span>Central Java</span></div>
    <div><h3 class="title-non-active">Lake Toba</h3><span>North Sumatra</span></div>
    <div><h3 class="title-non-active">Mandalika</h3><span>West Nusa Tenggara</span></div>
    <div><h3 class="title-non-active">Labuan Bajo</h3><span>East Nusa Tenggara</span></div>
    <div><h3 class="title-non-active">Likupang</h3><span>North Sulawesi</span></div>
    <div><h3 class="title-non-active">Bali</h3><span>Bali</span></div>
    <div><h3 class="title-non-active">Raja Ampat</h3><span>West Papua</span></div>
    <div><h3 class="title-non-active">Morotai</h3><span>North Maluku</span></div>
    <div><h3 class="title-non-active">Tanjung Kelayang</h3><span>Bangka Belitung Islands</span></div>
    <div><h3 class="title-non-active">Jakarta</h3><span>DKI Jakarta</span></div>
    <div><h3 class="title-non-active">Bromo Tengger Semeru National Park</h3><span>East Java</span></div>
    <div><h3 class="title-non-active">Riau Islands</h3><span>Sumatra</span></div>
    <div><h3 class="title-non-active">Wakatobi</h3><span>Southeast Sulawesi</span></div>
</section>
"""

st.set_page_config(page_title="Dashboard Wisata", layout="wide")
st.title("Dashboard Destinasi Wisata Indonesia")
st.write("Mengambil data destinasi melalui web scraping dan suhu melalui REST API.")

if st.button("Ambil Data dan Tampilkan Dashboard", type="primary"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    html_content = ""
    for url in ["https://indonesia.travel/id/id", "https://indonesia.travel/gb/en/home", "https://indonesia.travel"]:
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if "s-recomendation" in response.text or "title-non-active" in response.text:
                html_content = response.text
                break
        except Exception:
            continue

    if not html_content:
        html_content = FALLBACK_HTML

    soup = BeautifulSoup(html_content, "html.parser")
    section = soup.find("section", class_="s-recomendation")
    items = section.find_all("h3", class_="title-non-active") if section else []

    data_wisata = []
    seen = set()

    for h3 in items:
        destinasi = h3.get_text(strip=True)
        span = h3.find_next_sibling("span") or h3.find_next("span")
        provinsi = span.get_text(strip=True) if span else ""

        if destinasi in KOORDINAT and destinasi not in seen:
            seen.add(destinasi)
            lat, lon = KOORDINAT[destinasi]

            api_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m",
                "timezone": "Asia/Jakarta"
            }
            try:
                res_api = requests.get(api_url, params=params, timeout=10).json()
                suhu = res_api.get("current", {}).get("temperature_2m", None)
            except Exception:
                suhu = None

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
    st.dataframe(df, use_container_width=True, width="stretch")

    st.subheader("Visualisasi")
    col1, col2 = st.columns(2)

    if not df.empty:
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
