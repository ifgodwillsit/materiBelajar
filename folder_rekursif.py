import copy
import streamlit as st

# ---------------------------------------------------------------
# DATA AWAL: NESTED DICTIONARY DENGAN KEDALAMAN TIDAK TENTU
# Aturan:
#   - value bertipe dict -> FOLDER (boleh berisi folder/file lain)
#   - value bertipe int  -> FILE (nilainya ukuran dalam KB)
# ---------------------------------------------------------------
default_folder = {
    "Dokumen": {
        "Kuliah": {
            "Struktur Data": {
                "modul.pdf": 2048,
                "tugas1.docx": 350,
                "Praktikum": {
                    "latihan.py": 12,
                    "minimarket_app.py": 8,
                },
            },
            "Basis Data": {
                "modul.pdf": 1800,
                "erd.png": 560,
            },
        },
        "Pribadi": {
            "cv.pdf": 220,
            "Foto": {
                "liburan.jpg": 4096,
                "wisuda.jpg": 3500,
            },
        },
        "laporan.pdf": 900,
    },
    "Unduhan": {
        "installer.exe": 51200,
        "laporan.pdf": 1200,
    },
    "catatan.txt": 4,
}


# ---------------------------------------------------------------
# FUNGSI REKURSIF
# Pola umum:
#   1. BASE CASE      : kondisi berhenti (value bukan dict / jalur habis)
#   2. RECURSIVE CASE : untuk value bertipe dict, panggil fungsi lagi
# ---------------------------------------------------------------
def buat_tree(data, awalan=""):
    """Membuat tampilan pohon folder. Mengembalikan list baris teks."""
    baris = []
    item = list(data.items())
    for i, (nama, isi) in enumerate(item):
        terakhir = i == len(item) - 1
        cabang = "└── " if terakhir else "├── "
        if isinstance(isi, dict):  # recursive case: folder
            baris.append(f"{awalan}{cabang}📁 {nama}")
            baris.extend(buat_tree(isi, awalan + ("    " if terakhir else "│   ")))
        else:  # base case: file
            baris.append(f"{awalan}{cabang}📄 {nama} ({isi} KB)")
    return baris


def total_ukuran(data):
    """Menjumlahkan ukuran seluruh file pada folder dan semua subfolder-nya."""
    total = 0
    for isi in data.values():
        if isinstance(isi, dict):
            total += total_ukuran(isi)  # recursive case
        else:
            total += isi  # base case
    return total


def ukuran_per_folder(data, jalur=()):
    """Mengembalikan dict {jalur_folder (tuple): total ukuran} untuk semua folder."""
    hasil = {jalur: total_ukuran(data)}
    for nama, isi in data.items():
        if isinstance(isi, dict):
            hasil.update(ukuran_per_folder(isi, jalur + (nama,)))
    return hasil


def cari_file(data, nama_dicari, jalur=()):
    """Mencari semua file bernama nama_dicari. Mengembalikan list jalur lengkap."""
    hasil = []
    for nama, isi in data.items():
        if isinstance(isi, dict):
            hasil.extend(cari_file(isi, nama_dicari, jalur + (nama,)))
        elif nama == nama_dicari:
            hasil.append("/".join(jalur + (nama,)))
    return hasil


def kedalaman(data):
    """Kedalaman maksimum (folder root dihitung level 1)."""
    anak_folder = [kedalaman(isi) for isi in data.values() if isinstance(isi, dict)]
    return 1 + max(anak_folder, default=0)


def ambil_nilai(data, jalur, default=None):
    """Mengambil value dari nested dictionary berdasarkan list jalur (rekursif)."""
    if not jalur:  # base case: jalur habis, data saat ini adalah hasilnya
        return data
    if not isinstance(data, dict) or jalur[0] not in data:  # base case: tidak ditemukan
        return default
    return ambil_nilai(data[jalur[0]], jalur[1:], default)  # recursive case


def daftar_folder(data, jalur=()):
    """Mengembalikan list jalur (tuple) dari semua folder, termasuk root ()."""
    hasil = [jalur]
    for nama, isi in data.items():
        if isinstance(isi, dict):
            hasil.extend(daftar_folder(isi, jalur + (nama,)))
    return hasil


def tambah_item(data, jalur, nama, nilai):
    """Menambah file/folder pada folder tujuan (jalur). Return True jika berhasil."""
    if not jalur:  # base case: sudah sampai di folder tujuan
        if nama in data:
            return False
        data[nama] = nilai
        return True
    if jalur[0] not in data or not isinstance(data[jalur[0]], dict):
        return False
    return tambah_item(data[jalur[0]], jalur[1:], nama, nilai)  # recursive case


def nama_jalur(jalur):
    return "/" + "/".join(jalur) if jalur else "/ (root)"


# ---------------------------------------------------------------
# TAMPILAN HALAMAN
# ---------------------------------------------------------------
st.title("🗂️ Simulasi Struktur Folder (Rekursif)")
st.markdown("""
Kasus **struktur folder** dengan kedalaman yang **tidak tentu**. Value bertipe `dict`
adalah folder, sedangkan value bertipe `int` adalah file (ukuran dalam KB).
Semua pemrosesan data menggunakan **fungsi rekursif**.
""")

# ---------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------
if "folder" not in st.session_state:
    st.session_state["folder"] = copy.deepcopy(default_folder)
folder = st.session_state["folder"]

# ---------------------------------------------------------------
# TAMPILKAN STRUKTUR
# ---------------------------------------------------------------
st.header("📁 Struktur Folder Saat Ini")
st.code("📁 root\n" + "\n".join(buat_tree(folder)), language=None)

with st.expander("Lihat nested dictionary (mentah)"):
    st.json(folder)

# ---------------------------------------------------------------
# TAMBAH FILE / FOLDER
# ---------------------------------------------------------------
st.subheader("Tambah File / Folder")
if "pesan" in st.session_state:
    st.success(st.session_state.pop("pesan"))

semua_folder = daftar_folder(folder)
col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 3, 2, 1])
with col_a:
    tujuan = st.selectbox("Folder tujuan", options=semua_folder, format_func=nama_jalur)
with col_b:
    jenis = st.radio("Jenis", ["File", "Folder"], horizontal=True)
with col_c:
    nama_baru = st.text_input("Nama")
with col_d:
    ukuran = st.number_input("Ukuran (KB)", min_value=1, value=100, step=1,
                             disabled=(jenis == "Folder"))
with col_e:
    st.write("")
    st.write("")
    tombol = st.button("Tambah")

if tombol:
    if not nama_baru.strip() or "/" in nama_baru:
        st.error("Nama tidak boleh kosong atau mengandung karakter '/'.")
    else:
        isi_baru = int(ukuran) if jenis == "File" else {}
        if tambah_item(folder, tujuan, nama_baru.strip(), isi_baru):
            st.session_state["folder"] = folder
            st.session_state["pesan"] = f"{jenis} '{nama_baru.strip()}' berhasil ditambahkan ke {nama_jalur(tujuan)}"
            st.rerun()
        else:
            st.error(f"'{nama_baru.strip()}' sudah ada di {nama_jalur(tujuan)}!")

# ---------------------------------------------------------------
# LATIHAN (FUNGSI REKURSIF)
# ---------------------------------------------------------------
st.divider()
st.header("📝 Latihan Fungsi Rekursif")

# --- Soal 1: Menampilkan struktur dalam bentuk pohon ----------------
st.subheader("1. Tampilkan seluruh struktur folder dalam bentuk pohon")
st.caption("Lihat fungsi `buat_tree()`; hasilnya sama dengan tampilan di bagian atas.")
st.code("\n".join(buat_tree(folder)), language=None)

# --- Soal 2: Total ukuran tiap folder -------------------------------
st.subheader("2. Total ukuran seluruh file di setiap folder")
ukuran_folder = ukuran_per_folder(folder)
st.table([
    {"Folder": nama_jalur(j), "Ukuran total (KB)": u}
    for j, u in ukuran_folder.items()
])
st.write(f"Total ukuran seluruh file: **{total_ukuran(folder):,} KB**")

# --- Soal 3: Mencari file di semua kedalaman ------------------------
st.subheader("3. Cari file di semua folder")
nama_cari = st.text_input("Nama file yang dicari", value="laporan.pdf")
if nama_cari:
    ditemukan = cari_file(folder, nama_cari)
    if ditemukan:
        st.success(f"'{nama_cari}' ditemukan di {len(ditemukan)} lokasi:")
        for lokasi in ditemukan:
            st.write(f"- /{lokasi}")
    else:
        st.error(f"File '{nama_cari}' tidak ditemukan!")

# --- Soal 4: Kedalaman maksimum -------------------------------------
st.subheader("4. Kedalaman maksimum struktur folder")
st.write(f"Kedalaman maksimum: **{kedalaman(folder)}** level (root dihitung level 1)")

# --- Soal 5: Mengambil value berdasarkan jalur ----------------------
st.subheader("5. Ambil value berdasarkan jalur")
jalur_input = st.text_input("Jalur (pisahkan dengan /)",
                            value="Dokumen/Kuliah/Struktur Data/modul.pdf")
if jalur_input:
    jalur_list = [p for p in jalur_input.strip("/").split("/") if p]
    hasil = ambil_nilai(folder, jalur_list)
    if hasil is None:
        st.error(f"Jalur '/{'/'.join(jalur_list)}' tidak ditemukan!")
    elif isinstance(hasil, dict):
        st.info(f"Ini adalah folder yang berisi {len(hasil)} item, "
                f"total ukuran {total_ukuran(hasil):,} KB.")
        st.write(list(hasil.keys()))
    else:
        st.success(f"Ini adalah file dengan ukuran {hasil:,} KB.")
