import copy
import streamlit as st

# ---------------------------------------------------------------
# DATA AWAL
# ---------------------------------------------------------------
# Tuple untuk mata kuliah (kode, nama, sks)
matkul = (
    ("IF101", "Algoritma Pemrograman", 3),
    ("IF102", "Struktur Data", 3),
    ("IF103", "Basis Data", 3),
    ("IF104", "Pemrograman Web", 2),
    # silahkan tambahkan mata kuliah lainnya
)

# Nested dictionary (4 level):
# prodi -> mahasiswa -> NIM -> nilai -> kode matkul
default_prodi = {
    "TI": {
        "nama": "Teknik Informatika",
        "fakultas": "Teknik",
        "mahasiswa": {
            "2024001": {"nama": "Andi Pratama", "angkatan": 2024,
                        "nilai": {"IF101": 85, "IF102": 78, "IF103": 90}},
            "2024002": {"nama": "Bunga Lestari", "angkatan": 2024,
                        "nilai": {"IF101": 92, "IF102": 88}},
            "2023001": {"nama": "Cahyo Nugroho", "angkatan": 2023,
                        "nilai": {"IF101": 70, "IF102": 65, "IF103": 72, "IF104": 80}},
        },
    },
    "SI": {
        "nama": "Sistem Informasi",
        "fakultas": "Teknik",
        "mahasiswa": {
            "2024101": {"nama": "Dewi Anggraini", "angkatan": 2024,
                        "nilai": {"IF101": 80, "IF103": 85}},
            "2023101": {"nama": "Eko Saputra", "angkatan": 2023,
                        "nilai": {"IF102": 75, "IF103": 68, "IF104": 90}},
        },
    },
    "MI": {
        "nama": "Manajemen Informatika",
        "fakultas": "Vokasi",
        "mahasiswa": {
            "2022201": {"nama": "Fajar Ramadhan", "angkatan": 2022,
                        "nilai": {"IF101": 60, "IF102": 74, "IF104": 82}},
        },
    },
}

# Dictionary bantu dari tuple: kode -> (nama, sks)
info_matkul = {kode: {"nama": nama, "sks": sks} for kode, nama, sks in matkul}


def rata_tertimbang(nilai):
    """Rata-rata nilai tertimbang SKS dari dictionary {kode_matkul: nilai}."""
    total_sks = sum(info_matkul[k]["sks"] for k in nilai)
    if total_sks == 0:
        return 0
    return sum(n * info_matkul[k]["sks"] for k, n in nilai.items()) / total_sks


# ---------------------------------------------------------------
# TAMPILAN HALAMAN
# ---------------------------------------------------------------
st.title("🎓 Sistem Nilai Mahasiswa per Program Studi")
st.markdown("""
Kasus **data akademik** dengan beberapa program studi. Daftar mata kuliah disimpan
dalam **tuple**, sedangkan data mahasiswa dan nilainya dalam **nested dictionary**.
""")

# ---------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------
if "prodi" not in st.session_state:
    st.session_state["prodi"] = copy.deepcopy(default_prodi)
prodi = st.session_state["prodi"]

if "riwayat" not in st.session_state:
    st.session_state["riwayat"] = []
riwayat = st.session_state["riwayat"]

# ---------------------------------------------------------------
# TAMPILKAN DATA MAHASISWA TIAP PRODI
# ---------------------------------------------------------------
st.header("📋 Data Mahasiswa per Prodi")
tab_list = st.tabs([f"{kode} - {data['nama']}" for kode, data in prodi.items()])
for tab, (kode_prodi, data) in zip(tab_list, prodi.items()):
    with tab:
        st.write(f"Fakultas **{data['fakultas']}**")
        if data["mahasiswa"]:
            baris = [
                {
                    "NIM": nim,
                    "Nama": m["nama"],
                    "Angkatan": m["angkatan"],
                    "Jumlah MK": len(m["nilai"]),
                    "Rata-rata (tertimbang SKS)": round(rata_tertimbang(m["nilai"]), 2),
                }
                for nim, m in data["mahasiswa"].items()
            ]
            st.table(baris)
        else:
            st.info("Belum ada mahasiswa pada prodi ini.")

st.caption("**Tuple mata kuliah** (kode, nama, sks).")
with st.expander("Lihat mata kuliah (tuple) dan data mentah (nested dictionary)"):
    st.write("**Tuple matkul:**", matkul)
    st.write("**Data prodi:**", prodi)

# ---------------------------------------------------------------
# INPUT / UBAH NILAI
# ---------------------------------------------------------------
st.subheader("Input Nilai Mahasiswa")
col_a, col_b, col_c, col_d, col_e = st.columns([2, 3, 3, 2, 1])

with col_a:
    prodi_id = st.selectbox("Prodi", options=list(prodi.keys()))
with col_b:
    daftar_nim = list(prodi[prodi_id]["mahasiswa"].keys())
    nim_pilih = st.selectbox(
        "Mahasiswa",
        options=daftar_nim,
        format_func=lambda x: f"{x} - {prodi[prodi_id]['mahasiswa'][x]['nama']}",
    )
with col_c:
    kode_mk = st.selectbox(
        "Mata Kuliah",
        options=[m[0] for m in matkul],
        format_func=lambda x: f"{x} - {info_matkul[x]['nama']}",
    )
with col_d:
    nilai_baru = st.number_input("Nilai", min_value=0, max_value=100, value=75, step=1)
with col_e:
    st.write("")
    st.write("")
    simpan = st.button("Simpan")

if simpan:
    if not nim_pilih:
        st.error("Prodi ini belum memiliki mahasiswa!")
    else:
        mhs = prodi[prodi_id]["mahasiswa"][nim_pilih]
        nilai_lama = mhs["nilai"].get(kode_mk)  # None jika belum ada
        mhs["nilai"][kode_mk] = int(nilai_baru)
        riwayat.append({
            "prodi": prodi_id,
            "nim": nim_pilih,
            "matkul": kode_mk,
            "nilai_lama": nilai_lama if nilai_lama is not None else "-",
            "nilai_baru": int(nilai_baru),
        })
        st.session_state["prodi"] = prodi
        st.session_state["riwayat"] = riwayat
        if nilai_lama is None:
            st.success(f"Nilai baru disimpan: {nim_pilih} - {kode_mk} = {nilai_baru}")
        else:
            st.success(f"Nilai diperbarui: {nim_pilih} - {kode_mk} ({nilai_lama} -> {nilai_baru})")

if riwayat:
    with st.expander("Lihat Riwayat Input Nilai"):
        st.table(riwayat)

# ---------------------------------------------------------------
# LATIHAN (NESTED DICTIONARY)
# ---------------------------------------------------------------
st.divider()
st.header("📝 Latihan Nested Dictionary")

# --- Soal 1: Angkatan unik dari seluruh prodi -----------------------
st.subheader("1. Angkatan unik di seluruh prodi")
angkatan_unik = {
    m["angkatan"]
    for data in prodi.values()
    for m in data["mahasiswa"].values()
}
st.write("Angkatan unik:", sorted(angkatan_unik))

# --- Soal 2: Rata-rata nilai mata kuliah IF102 di semua prodi -------
st.subheader("2. Rata-rata nilai Struktur Data (IF102) di semua prodi")
kode_target = "IF102"
nilai_if102 = [
    m["nilai"][kode_target]
    for data in prodi.values()
    for m in data["mahasiswa"].values()
    if kode_target in m["nilai"]
]
if nilai_if102:
    st.write(f"Nilai IF102 yang terkumpul: {nilai_if102}")
    st.write(f"Rata-rata: **{sum(nilai_if102) / len(nilai_if102):.2f}** "
             f"dari {len(nilai_if102)} mahasiswa")
else:
    st.warning("Belum ada nilai untuk mata kuliah tersebut.")

# --- Soal 3: Mahasiswa terbaik tiap prodi --------------------------
st.subheader("3. Mahasiswa terbaik tiap prodi (rata-rata tertimbang SKS)")
for kode_prodi, data in prodi.items():
    if not data["mahasiswa"]:
        st.write(f"- {kode_prodi}: belum ada mahasiswa")
        continue
    rata_per_mhs = {
        nim: rata_tertimbang(m["nilai"]) for nim, m in data["mahasiswa"].items()
    }
    nim_terbaik = max(rata_per_mhs, key=rata_per_mhs.get)
    nama_terbaik = data["mahasiswa"][nim_terbaik]["nama"]
    st.write(f"- {kode_prodi} ({data['nama']}): **{nama_terbaik}** "
             f"({nim_terbaik}) dengan rata-rata {rata_per_mhs[nim_terbaik]:.2f}")

# --- Soal 4: Pencarian bertingkat prodi -> NIM -> matkul -----------
st.subheader("4. Cari nilai mahasiswa pada prodi tertentu")
c1, c2, c3 = st.columns(3)
cari_prodi = c1.text_input("Kode prodi", value="TI")
cari_nim = c2.text_input("NIM", value="2024001")
cari_mk = c3.text_input("Kode matkul", value="IF103")
if cari_prodi and cari_nim and cari_mk:
    if cari_prodi not in prodi:
        st.error(f"Prodi {cari_prodi} tidak ditemukan!")
    elif cari_nim not in prodi[cari_prodi]["mahasiswa"]:
        st.error(f"NIM {cari_nim} tidak terdaftar di prodi {cari_prodi}!")
    else:
        mhs = prodi[cari_prodi]["mahasiswa"][cari_nim]
        if cari_mk in mhs["nilai"]:
            st.success(f"{mhs['nama']} mendapat nilai {mhs['nilai'][cari_mk]} "
                       f"pada {cari_mk}")
        else:
            st.warning(f"{mhs['nama']} belum memiliki nilai untuk {cari_mk}.")

# --- Soal 5: Menambah mahasiswa baru ke nested dictionary ----------
st.subheader("5. Tambah mahasiswa baru")
if "pesan" in st.session_state:
    st.success(st.session_state.pop("pesan"))

with st.form("form_mahasiswa", clear_on_submit=True):
    f1, f2, f3, f4 = st.columns(4)
    new_prodi = f1.selectbox("Prodi", options=list(prodi.keys()))
    new_nim = f2.text_input("NIM")
    new_nama = f3.text_input("Nama")
    new_angkatan = f4.number_input("Angkatan", min_value=2000, max_value=2100,
                                   value=2025, step=1)
    submit = st.form_submit_button("Simpan Mahasiswa")

if submit:
    nim_sudah_ada = any(new_nim in data["mahasiswa"] for data in prodi.values())
    if not (new_nim and new_nama):
        st.error("NIM dan Nama wajib diisi!")
    elif nim_sudah_ada:
        st.error(f"NIM {new_nim} sudah terdaftar!")
    else:
        prodi[new_prodi]["mahasiswa"][new_nim] = {
            "nama": new_nama,
            "angkatan": int(new_angkatan),
            "nilai": {},
        }
        st.session_state["prodi"] = prodi
        st.session_state["pesan"] = f"Mahasiswa {new_nama} ({new_nim}) berhasil ditambahkan ke {new_prodi}!"
        st.rerun()
