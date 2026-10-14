import streamlit as st

# ---------------------------------------------------------------
# DATA: NESTED DICTIONARY DENGAN KEDALAMAN TIDAK TENTU
#   - BARANG   : dictionary yang punya key "harga" dan "stok"
#   - KATEGORI : dictionary lain yang berisi kategori/barang di dalamnya
# ---------------------------------------------------------------
gudang = {
    "Makanan": {
        "Roti Tawar": {"harga": 18000, "stok": 20},
        "Instan": {
            "Mi Instan": {"harga": 3500, "stok": 100},
            "Bubur Instan": {"harga": 6000, "stok": 30},
        },
    },
    "Minuman": {
        "Susu UHT": {"harga": 15000, "stok": 25},
        "Kopi": {
            "Kopi Sachet": {"harga": 2500, "stok": 150},
            "Kopi Botol": {"harga": 12000, "stok": 14},
        },
    },
    "Minyak Goreng": {"harga": 17000, "stok": 15},
}


# ---------------------------------------------------------------
# FUNGSI REKURSIF
#   Base case      : isi adalah barang / jalur sudah habis
#   Recursive case : isi adalah kategori -> panggil fungsi lagi
# ---------------------------------------------------------------
def adalah_barang(isi):
    return "harga" in isi and "stok" in isi


def total_stok(data):
    """Menjumlahkan stok semua barang di semua kedalaman."""
    total = 0
    for isi in data.values():
        if adalah_barang(isi):
            total += isi["stok"]  # base case
        else:
            total += total_stok(isi)  # recursive case
    return total


def total_aset(data):
    """Menjumlahkan harga x stok semua barang di semua kedalaman."""
    total = 0
    for isi in data.values():
        if adalah_barang(isi):
            total += isi["harga"] * isi["stok"]
        else:
            total += total_aset(isi)
    return total


def cari_barang(data, nama_dicari, jalur=""):
    """Mencari barang dengan nama persis nama_dicari. Mengembalikan jalur lengkap atau None."""
    for nama, isi in data.items():
        jalur_saat_ini = f"{jalur}/{nama}" if jalur else nama
        if adalah_barang(isi):
            if nama == nama_dicari:
                return jalur_saat_ini  # base case: ketemu
        else:
            hasil = cari_barang(isi, nama_dicari, jalur_saat_ini)  # recursive case
            if hasil is not None:
                return hasil
    return None  # base case: tidak ketemu


def ambil_nilai(data, jalur, default=None):
    """Mengambil value berdasarkan list jalur."""
    if not jalur:
        return data
    if not isinstance(data, dict) or jalur[0] not in data:
        return default
    return ambil_nilai(data[jalur[0]], jalur[1:], default)


# ---------------------------------------------------------------
# TAMPILAN
# ---------------------------------------------------------------
st.title("📦 Inventori Bertingkat (Rekursif Sederhana)")
st.markdown("Kategori dan sub-kategori barang dengan kedalaman **tidak tentu**.")

with st.expander("Lihat data inventori"):
    st.json(gudang)

st.header("📝 Latihan")

st.subheader("1. Total stok seluruh barang")
st.write(f"Total stok: **{total_stok(gudang)}**")

st.subheader("2. Total nilai aset (harga x stok)")
st.write(f"Total aset: **Rp {total_aset(gudang):,.0f}**")

st.subheader("3. Cari jalur sebuah barang")
nama_cari = st.text_input("Nama barang", value="Kopi Botol")
hasil_cari = cari_barang(gudang, nama_cari)
if hasil_cari:
    st.success(f"Ditemukan di: {hasil_cari}")
else:
    st.error(f"Barang '{nama_cari}' tidak ditemukan!")

st.subheader("4. Ambil stok barang berdasarkan jalur")
jalur_input = st.text_input("Jalur (pisahkan dengan /)", value="Makanan/Instan/Mi Instan")
hasil = ambil_nilai(gudang, jalur_input.split("/"))
if isinstance(hasil, dict) and adalah_barang(hasil):
    st.success(f"Stok: {hasil['stok']}")
else:
    st.error("Jalur tidak ditemukan atau bukan barang!")
