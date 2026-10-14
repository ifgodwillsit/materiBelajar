import copy
import streamlit as st

# ---------------------------------------------------------------
# DATA AWAL: NESTED DICTIONARY (3 level)
# cabang -> data cabang -> inventori -> detail produk
# ---------------------------------------------------------------
default_cabang = {
    "CBG01": {
        "nama": "Minimarket Magelang",
        "kota": "Magelang",
        "inventori": {
            "BRG001": {"nama": "Roti Tawar", "kategori": "Makanan", "harga": 18000, "stok": 20},
            "BRG002": {"nama": "Susu UHT", "kategori": "Minuman", "harga": 15000, "stok": 25},
            "BRG003": {"nama": "Mi Instan", "kategori": "Makanan", "harga": 3500, "stok": 100},
            "BRG004": {"nama": "Minyak Goreng", "kategori": "Bahan Pokok", "harga": 17000, "stok": 15},
        },
    },
    "CBG02": {
        "nama": "Minimarket Yogyakarta",
        "kota": "Yogyakarta",
        "inventori": {
            "BRG001": {"nama": "Roti Tawar", "kategori": "Makanan", "harga": 19000, "stok": 12},
            "BRG003": {"nama": "Mi Instan", "kategori": "Makanan", "harga": 3500, "stok": 80},
            "BRG005": {"nama": "Telur Ayam 1 Lusin", "kategori": "Bahan Pokok", "harga": 27000, "stok": 10},
            "BRG006": {"nama": "Teh Botol", "kategori": "Minuman", "harga": 5000, "stok": 60},
        },
    },
    "CBG03": {
        "nama": "Minimarket Semarang",
        "kota": "Semarang",
        "inventori": {
            "BRG002": {"nama": "Susu UHT", "kategori": "Minuman", "harga": 15500, "stok": 30},
            "BRG004": {"nama": "Minyak Goreng", "kategori": "Bahan Pokok", "harga": 17500, "stok": 8},
            "BRG005": {"nama": "Telur Ayam 1 Lusin", "kategori": "Bahan Pokok", "harga": 28000, "stok": 14},
        },
    },
}

# ---------------------------------------------------------------
# TAMPILAN HALAMAN
# ---------------------------------------------------------------
st.title("🏪 Minimarket Multi-Cabang")
st.markdown("""
Kasus **minimarket dengan beberapa cabang**. Setiap cabang memiliki inventori sendiri
yang disimpan dalam **nested dictionary**.
""")

# ---------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------
if "cabang" not in st.session_state:
    st.session_state["cabang"] = copy.deepcopy(default_cabang)
cabang = st.session_state["cabang"]

if "transaksi" not in st.session_state:
    st.session_state["transaksi"] = []
transaksi = st.session_state["transaksi"]

# ---------------------------------------------------------------
# TAMPILKAN INVENTORI TIAP CABANG
# ---------------------------------------------------------------
st.header("📦 Inventori per Cabang")
tab_list = st.tabs([f"{cid} - {data['kota']}" for cid, data in cabang.items()])
for tab, (cid, data) in zip(tab_list, cabang.items()):
    with tab:
        st.write(f"**{data['nama']}** ({data['kota']})")
        if data["inventori"]:
            st.table(data["inventori"])
        else:
            st.info("Inventori cabang ini masih kosong.")

with st.expander("Lihat struktur nested dictionary (mentah)"):
    st.write(cabang)

# ---------------------------------------------------------------
# TAMBAH TRANSAKSI PER CABANG
# ---------------------------------------------------------------
st.subheader("Tambah Transaksi Penjualan")
col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])

with col_a:
    cabang_id = st.selectbox(
        "Pilih Cabang",
        options=list(cabang.keys()),
        format_func=lambda x: f"{x} - {cabang[x]['kota']}",
    )
with col_b:
    daftar_sku = list(cabang[cabang_id]["inventori"].keys())
    sku_id = st.selectbox("Pilih SKU", options=daftar_sku)
with col_c:
    qty = st.number_input("Qty", min_value=1, value=1, step=1)
with col_d:
    st.write("")
    st.write("")
    tombol = st.button("Tambah")

if tombol:
    if not sku_id:
        st.error("Cabang ini belum memiliki barang!")
    else:
        produk = cabang[cabang_id]["inventori"][sku_id]
        if produk["stok"] >= qty:
            produk["stok"] -= int(qty)
            transaksi.append({
                "cabang": cabang_id,
                "id": sku_id,
                "nama": produk["nama"],
                "qty": int(qty),
                "total": int(qty) * produk["harga"],
            })
            st.session_state["cabang"] = cabang
            st.session_state["transaksi"] = transaksi
            st.success(f"Berhasil: {cabang_id} menjual {sku_id} x {qty}")
        else:
            st.error(f"Stok di {cabang_id} tidak mencukupi! (tersisa {produk['stok']})")

if transaksi:
    with st.expander("Lihat Daftar Transaksi"):
        st.table(transaksi)

# ---------------------------------------------------------------
# LATIHAN (NESTED DICTIONARY)
# ---------------------------------------------------------------
st.divider()
st.header("📝 Latihan Nested Dictionary")

# --- Soal 1: Kategori unik dari seluruh cabang ----------------------
st.subheader("1. Kategori unik di seluruh cabang")
kategori_unik = {
    produk["kategori"]
    for data in cabang.values()
    for produk in data["inventori"].values()
}
st.write("Kategori unik:", sorted(kategori_unik))

# --- Soal 2: Total nilai aset (harga x stok) tiap cabang -------------
st.subheader("2. Total nilai aset tiap cabang")
nilai_aset = {
    cid: sum(p["harga"] * p["stok"] for p in data["inventori"].values())
    for cid, data in cabang.items()
}
for cid, nilai in nilai_aset.items():
    st.write(f"- {cid} ({cabang[cid]['kota']}): **Rp {nilai:,.0f}**")
cabang_terkaya = max(nilai_aset, key=nilai_aset.get)
st.write(f"Cabang dengan aset terbesar: **{cabang_terkaya}** ({cabang[cabang_terkaya]['kota']})")

# --- Soal 3: Total stok Roti Tawar (BRG001) di semua cabang ---------
st.subheader("3. Total stok Roti Tawar di semua cabang")
id_roti = "BRG001"
stok_per_cabang = {
    cid: data["inventori"][id_roti]["stok"]
    for cid, data in cabang.items()
    if id_roti in data["inventori"]
}
st.write("Stok per cabang:", stok_per_cabang)
st.write(f"Total stok seluruh cabang: **{sum(stok_per_cabang.values())}**")
if stok_per_cabang:
    cabang_terbanyak = max(stok_per_cabang, key=stok_per_cabang.get)
    st.write(f"Stok terbanyak ada di cabang: **{cabang_terbanyak}**")

# --- Soal 4: Pencarian key pada nested dictionary -------------------
st.subheader("4. Cari SKU pada cabang tertentu")
c1, c2 = st.columns(2)
cari_cabang = c1.text_input("Kode cabang", value="CBG02")
cari_sku = c2.text_input("Kode SKU", value="BRG005")
if cari_cabang and cari_sku:
    if cari_cabang not in cabang:
        st.error(f"Cabang {cari_cabang} tidak ditemukan!")
    elif cari_sku not in cabang[cari_cabang]["inventori"]:
        st.error(f"SKU {cari_sku} tidak ada di cabang {cari_cabang}!")
    else:
        st.success(f"SKU {cari_sku} ditemukan di cabang {cari_cabang}:")
        st.write(cabang[cari_cabang]["inventori"][cari_sku])

# --- Soal 5: Menambah cabang baru ke nested dictionary --------------
st.subheader("5. Tambah cabang baru")
if "pesan" in st.session_state:
    st.success(st.session_state.pop("pesan"))
with st.form("form_cabang", clear_on_submit=True):
    f1, f2, f3 = st.columns(3)
    new_id = f1.text_input("Kode cabang (mis. CBG04)")
    new_nama = f2.text_input("Nama cabang")
    new_kota = f3.text_input("Kota")
    submit = st.form_submit_button("Simpan Cabang")

if submit:
    if not (new_id and new_nama and new_kota):
        st.error("Semua kolom wajib diisi!")
    elif new_id in cabang:
        st.error(f"Kode cabang {new_id} sudah ada!")
    else:
        cabang[new_id] = {"nama": new_nama, "kota": new_kota, "inventori": {}}
        st.session_state["cabang"] = cabang
        st.session_state["pesan"] = f"Cabang {new_id} berhasil ditambahkan!"
        st.rerun()
