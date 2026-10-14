import copy
import streamlit as st

# ---------------------------------------------------------------
# DATA AWAL: NESTED DICTIONARY DENGAN KEDALAMAN TIDAK TENTU
# Aturan:
#   - BARANG   : dictionary yang memiliki key "harga" dan "stok"
#   - KATEGORI : dictionary lain yang berisi kategori/barang di dalamnya
# ---------------------------------------------------------------
default_gudang = {
    "Makanan": {
        "Roti & Kue": {
            "Roti Tawar": {"harga": 18000, "stok": 20},
            "Roti Gandum": {"harga": 22000, "stok": 8},
            "Kue Kering": {
                "Nastar": {"harga": 45000, "stok": 12},
                "Kastengel": {"harga": 48000, "stok": 5},
            },
        },
        "Instan": {
            "Mi Instan": {"harga": 3500, "stok": 100},
            "Bubur Instan": {"harga": 6000, "stok": 30},
        },
    },
    "Minuman": {
        "Susu UHT": {"harga": 15000, "stok": 25},
        "Teh Botol": {"harga": 5000, "stok": 60},
        "Kopi": {
            "Kopi Sachet": {"harga": 2500, "stok": 150},
            "Kopi Botol": {"harga": 12000, "stok": 14},
        },
    },
    "Bahan Pokok": {
        "Minyak Goreng": {"harga": 17000, "stok": 15},
        "Telur Ayam 1 Lusin": {"harga": 27000, "stok": 10},
        "Beras": {
            "Premium": {
                "Beras Pandan Wangi 5kg": {"harga": 85000, "stok": 18},
                "Beras Rojolele 5kg": {"harga": 80000, "stok": 9},
            },
            "Medium": {
                "Beras Medium 5kg": {"harga": 65000, "stok": 40},
            },
        },
    },
    "Kantong Plastik": {"harga": 500, "stok": 500},  # barang langsung di root
}


# ---------------------------------------------------------------
# FUNGSI REKURSIF
# Pola umum:
#   1. BASE CASE      : value adalah barang (daun) / jalur sudah habis
#   2. RECURSIVE CASE : value adalah kategori -> panggil fungsi lagi
# ---------------------------------------------------------------
def adalah_barang(isi):
    """True jika isi adalah barang (dict dengan key 'harga' dan 'stok')."""
    return isinstance(isi, dict) and "harga" in isi and "stok" in isi


def rp(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")


def buat_tree(data, awalan=""):
    """Membuat tampilan pohon inventori. Mengembalikan list baris teks."""
    baris = []
    item = list(data.items())
    for i, (nama, isi) in enumerate(item):
        terakhir = i == len(item) - 1
        cabang = "└── " if terakhir else "├── "
        if adalah_barang(isi):  # base case
            baris.append(f"{awalan}{cabang}📦 {nama} ({rp(isi['harga'])}, stok {isi['stok']})")
        else:  # recursive case
            baris.append(f"{awalan}{cabang}📂 {nama}")
            baris.extend(buat_tree(isi, awalan + ("    " if terakhir else "│   ")))
    return baris


def ratakan_barang(data, jalur=()):
    """Mengembalikan list semua barang beserta jalur lengkapnya (flatten)."""
    hasil = []
    for nama, isi in data.items():
        if adalah_barang(isi):
            hasil.append({"jalur": jalur + (nama,), "nama": nama,
                          "harga": isi["harga"], "stok": isi["stok"]})
        else:
            hasil.extend(ratakan_barang(isi, jalur + (nama,)))
    return hasil


def ringkasan_per_kategori(data, jalur=()):
    """
    Mengembalikan dict {jalur_kategori: {"jenis", "stok", "nilai"}} untuk
    setiap kategori. Angka tiap kategori sudah mencakup semua sub-kategorinya.
    """
    hasil = {}
    jenis = stok = nilai = 0
    for nama, isi in data.items():
        if adalah_barang(isi):
            jenis += 1
            stok += isi["stok"]
            nilai += isi["harga"] * isi["stok"]
        else:
            sub = ringkasan_per_kategori(isi, jalur + (nama,))  # recursive case
            anak = sub[jalur + (nama,)]
            jenis += anak["jenis"]
            stok += anak["stok"]
            nilai += anak["nilai"]
            hasil.update(sub)
    return {jalur: {"jenis": jenis, "stok": stok, "nilai": nilai}, **hasil}


def cari_barang(data, kata_kunci, jalur=()):
    """Mencari barang yang namanya mengandung kata_kunci. Return list jalur lengkap."""
    hasil = []
    for nama, isi in data.items():
        if adalah_barang(isi):
            if kata_kunci.lower() in nama.lower():
                hasil.append("/".join(jalur + (nama,)))
        else:
            hasil.extend(cari_barang(isi, kata_kunci, jalur + (nama,)))
    return hasil


def kedalaman(data):
    """Kedalaman maksimum (root = level 1, barang tidak dihitung)."""
    anak = [kedalaman(isi) for isi in data.values() if not adalah_barang(isi)]
    return 1 + max(anak, default=0)


def ambil_nilai(data, jalur, default=None):
    """Mengambil value dari nested dictionary berdasarkan list jalur (rekursif)."""
    if not jalur:  # base case: jalur habis
        return data
    if not isinstance(data, dict) or jalur[0] not in data:  # base case: tidak ada
        return default
    return ambil_nilai(data[jalur[0]], jalur[1:], default)  # recursive case


def daftar_kategori(data, jalur=()):
    """Mengembalikan list jalur (tuple) semua kategori, termasuk root ()."""
    hasil = [jalur]
    for nama, isi in data.items():
        if isinstance(isi, dict) and not adalah_barang(isi):
            hasil.extend(daftar_kategori(isi, jalur + (nama,)))
    return hasil


def tambah_item(data, jalur, nama, isi_baru):
    """Menambah barang/kategori pada kategori tujuan (jalur). Return True jika berhasil."""
    if not jalur:  # base case: sudah di kategori tujuan
        if nama in data:
            return False
        data[nama] = isi_baru
        return True
    if jalur[0] not in data or not isinstance(data[jalur[0]], dict):
        return False
    return tambah_item(data[jalur[0]], jalur[1:], nama, isi_baru)  # recursive case


def kurangi_stok(data, jalur, qty):
    """
    Mengurangi stok barang pada jalur tertentu.
    Return: 'ok', 'tidak_ada', 'bukan_barang', atau 'stok_kurang'.
    """
    if not jalur or jalur[0] not in data:  # base case: jalur tidak valid
        return "tidak_ada"
    isi = data[jalur[0]]
    if len(jalur) == 1:  # base case: sampai di tujuan
        if not adalah_barang(isi):
            return "bukan_barang"
        if isi["stok"] < qty:
            return "stok_kurang"
        isi["stok"] -= qty
        return "ok"
    if not isinstance(isi, dict):
        return "tidak_ada"
    return kurangi_stok(isi, jalur[1:], qty)  # recursive case


def nama_jalur(jalur):
    return "/" + "/".join(jalur) if jalur else "/ (root)"


# ---------------------------------------------------------------
# TAMPILAN HALAMAN
# ---------------------------------------------------------------
st.title("🏬 Inventori Gudang Bertingkat (Rekursif)")
st.markdown("""
Kasus **inventori gudang** dengan kategori dan sub-kategori yang kedalamannya **tidak tentu**.
Dictionary yang punya key `harga` dan `stok` adalah **barang**, selain itu adalah **kategori**.
Semua pemrosesan data menggunakan **fungsi rekursif**.
""")

# ---------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------
if "gudang" not in st.session_state:
    st.session_state["gudang"] = copy.deepcopy(default_gudang)
gudang = st.session_state["gudang"]

if "transaksi" not in st.session_state:
    st.session_state["transaksi"] = []
transaksi = st.session_state["transaksi"]

# ---------------------------------------------------------------
# TAMPILKAN STRUKTUR INVENTORI
# ---------------------------------------------------------------
st.header("📦 Struktur Inventori Saat Ini")
st.code("📦 gudang\n" + "\n".join(buat_tree(gudang)), language=None)
st.caption(f"Kedalaman kategori maksimum: {kedalaman(gudang)} level (root = level 1)")

with st.expander("Lihat nested dictionary (mentah)"):
    st.json(gudang)

if "pesan" in st.session_state:
    st.success(st.session_state.pop("pesan"))

# ---------------------------------------------------------------
# TAMBAH KATEGORI / BARANG
# ---------------------------------------------------------------
st.subheader("Tambah Kategori / Barang")
col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3, 2, 3, 2, 2, 1])
with col_a:
    tujuan = st.selectbox("Kategori tujuan", options=daftar_kategori(gudang),
                          format_func=nama_jalur, key="tujuan_tambah")
with col_b:
    jenis = st.radio("Jenis", ["Barang", "Kategori"], horizontal=True, key="jenis_tambah")
with col_c:
    nama_baru = st.text_input("Nama", key="nama_tambah")
with col_d:
    harga_baru = st.number_input("Harga", min_value=1, value=10000, step=500,
                                 disabled=(jenis == "Kategori"), key="harga_tambah")
with col_e:
    stok_baru = st.number_input("Stok", min_value=0, value=10, step=1,
                                disabled=(jenis == "Kategori"), key="stok_tambah")
with col_f:
    st.write("")
    st.write("")
    tombol_tambah = st.button("Tambah", key="btn_tambah")

if tombol_tambah:
    nama_bersih = nama_baru.strip()
    if not nama_bersih or "/" in nama_bersih:
        st.error("Nama tidak boleh kosong atau mengandung karakter '/'.")
    else:
        isi_baru = ({"harga": int(harga_baru), "stok": int(stok_baru)}
                    if jenis == "Barang" else {})
        if tambah_item(gudang, tujuan, nama_bersih, isi_baru):
            st.session_state["gudang"] = gudang
            st.session_state["pesan"] = f"{jenis} '{nama_bersih}' berhasil ditambahkan ke {nama_jalur(tujuan)}"
            st.rerun()
        else:
            st.error(f"'{nama_bersih}' sudah ada di {nama_jalur(tujuan)}!")

# ---------------------------------------------------------------
# TRANSAKSI PENJUALAN
# ---------------------------------------------------------------
st.subheader("Tambah Transaksi Penjualan")
semua_barang = ratakan_barang(gudang)
daftar_jalur_barang = [b["jalur"] for b in semua_barang]

col_g, col_h, col_i = st.columns([5, 2, 1])
with col_g:
    jalur_jual = st.selectbox("Pilih barang", options=daftar_jalur_barang,
                              format_func=lambda j: "/".join(j), key="barang_jual")
with col_h:
    qty = st.number_input("Qty", min_value=1, value=1, step=1, key="qty_jual")
with col_i:
    st.write("")
    st.write("")
    tombol_jual = st.button("Jual", key="btn_jual")

if tombol_jual:
    status = kurangi_stok(gudang, jalur_jual, int(qty))
    if status == "ok":
        harga = ambil_nilai(gudang, list(jalur_jual) + ["harga"])
        transaksi.append({"barang": "/".join(jalur_jual), "qty": int(qty),
                          "total": int(qty) * harga})
        st.session_state["gudang"] = gudang
        st.session_state["transaksi"] = transaksi
        st.session_state["pesan"] = f"Transaksi berhasil: {jalur_jual[-1]} x {qty}"
        st.rerun()
    elif status == "stok_kurang":
        sisa = ambil_nilai(gudang, list(jalur_jual) + ["stok"])
        st.error(f"Stok tidak mencukupi! (tersisa {sisa})")
    else:
        st.error("Barang tidak ditemukan!")

if transaksi:
    with st.expander("Lihat Daftar Transaksi"):
        st.table(transaksi)

# ---------------------------------------------------------------
# LATIHAN (FUNGSI REKURSIF)
# ---------------------------------------------------------------
st.divider()
st.header("📝 Latihan Fungsi Rekursif")

# --- Soal 1: Struktur dalam bentuk pohon -----------------------------
st.subheader("1. Tampilkan seluruh struktur inventori dalam bentuk pohon")
st.caption("Lihat fungsi `buat_tree()`.")
st.code("\n".join(buat_tree(gudang)), language=None)

# --- Soal 2: Ringkasan tiap kategori --------------------------------
st.subheader("2. Ringkasan stok dan nilai aset tiap kategori")
st.caption("Angka tiap kategori mencakup seluruh sub-kategori di dalamnya.")
ringkasan = ringkasan_per_kategori(gudang)
st.table([
    {"Kategori": nama_jalur(j), "Jenis barang": r["jenis"],
     "Total stok": r["stok"], "Nilai aset": rp(r["nilai"])}
    for j, r in ringkasan.items()
])

# --- Soal 3: Barang dengan stok menipis ------------------------------
st.subheader("3. Barang dengan stok menipis")
batas = st.number_input("Batas stok menipis (kurang dari)", min_value=1, value=15, step=1)
menipis = [b for b in ratakan_barang(gudang) if b["stok"] < batas]
if menipis:
    st.warning(f"{len(menipis)} barang memiliki stok kurang dari {batas}:")
    st.table([{"Jalur": "/".join(b["jalur"]), "Stok": b["stok"]}
              for b in sorted(menipis, key=lambda b: b["stok"])])
else:
    st.success("Semua barang stoknya aman.")

# --- Soal 4: Mencari barang di semua kedalaman -----------------------
st.subheader("4. Cari barang di semua kategori")
kata_cari = st.text_input("Kata kunci nama barang", value="kopi", key="cari_kata")
if kata_cari:
    ditemukan = cari_barang(gudang, kata_cari)
    if ditemukan:
        st.success(f"Ditemukan {len(ditemukan)} barang:")
        for lokasi in ditemukan:
            st.write(f"- /{lokasi}")
    else:
        st.error(f"Barang dengan kata kunci '{kata_cari}' tidak ditemukan!")

# --- Soal 5: Mengambil value berdasarkan jalur -----------------------
st.subheader("5. Ambil value berdasarkan jalur")
jalur_input = st.text_input("Jalur (pisahkan dengan /)",
                            value="Makanan/Roti & Kue/Kue Kering/Nastar/harga",
                            key="jalur_ambil")
if jalur_input:
    jalur_list = [p for p in jalur_input.strip("/").split("/") if p]
    hasil = ambil_nilai(gudang, jalur_list)
    if hasil is None:
        st.error(f"Jalur '/{'/'.join(jalur_list)}' tidak ditemukan!")
    elif adalah_barang(hasil):
        st.success(f"Barang dengan harga {rp(hasil['harga'])} dan stok {hasil['stok']}.")
    elif isinstance(hasil, dict):
        r = ringkasan_per_kategori(hasil)[()]
        st.info(f"Kategori berisi {len(hasil)} item (total {r['jenis']} jenis barang, "
                f"stok {r['stok']}, nilai aset {rp(r['nilai'])}).")
        st.write(list(hasil.keys()))
    else:
        st.success(f"Nilainya: {hasil:,}".replace(",", "."))
