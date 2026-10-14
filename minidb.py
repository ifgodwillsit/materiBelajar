import operator
import re
import streamlit as st

# ---------------------------------------------------------------
# STRUKTUR DATA: NESTED DICTIONARY
#
# db = {
#     "nama_tabel": {
#         "kolom":   ["nama", "kategori", "harga", "stok"],   # list nama kolom
#         "auto_id": 3,                                       # id berikutnya
#         "baris": {                                          # id -> data baris
#             1: {"nama": "Roti Tawar", "kategori": "Makanan", "harga": 18000, "stok": 20},
#             2: {"nama": "Susu UHT",   "kategori": "Minuman", "harga": 15000, "stok": 25},
#         },
#     },
# }
#
# Mengakses sebuah nilai: db["produk"]["baris"][1]["harga"]
# ---------------------------------------------------------------

OPERATOR = {
    "=": operator.eq, "!=": operator.ne,
    ">=": operator.ge, "<=": operator.le,
    ">": operator.gt, "<": operator.lt,
}

POLA_NILAI = r"""\s*('[^']*'|"[^"]*"|[^,]+)"""

CONTOH_QUERY = """CREATE TABLE produk (nama, kategori, harga, stok);
INSERT INTO produk VALUES ('Roti Tawar', 'Makanan', 18000, 20);
INSERT INTO produk VALUES ('Susu UHT', 'Minuman', 15000, 25);
INSERT INTO produk VALUES ('Mi Instan', 'Makanan', 3500, 100);
INSERT INTO produk VALUES ('Minyak Goreng', 'Bahan Pokok', 17000, 15);
INSERT INTO produk VALUES ('Telur Ayam 1 Lusin', 'Bahan Pokok', 27000, 10);
SELECT * FROM produk WHERE kategori = 'Makanan';
UPDATE produk SET stok = 15 WHERE nama = 'Roti Tawar';
SELECT nama, stok FROM produk WHERE stok < 20"""


# ---------------------------------------------------------------
# FUNGSI BANTU
# ---------------------------------------------------------------
def parse_nilai(teks):
    """Mengubah teks menjadi int, float, atau string (tanda kutip dibuang)."""
    teks = teks.strip()
    if len(teks) >= 2 and teks[0] == teks[-1] and teks[0] in "'\"":
        return teks[1:-1]
    try:
        return int(teks)
    except ValueError:
        pass
    try:
        return float(teks)
    except ValueError:
        return teks


def pisah_nilai(teks):
    """Memisahkan 'a', 'b, c', 10 menjadi list nilai (koma di dalam kutip aman)."""
    return [parse_nilai(x) for x in re.findall(POLA_NILAI, teks)]


def pisah_query(teks):
    """Memisahkan beberapa query yang dibatasi ';' (titik koma dalam kutip aman)."""
    potongan = re.findall(r"""(?:'[^']*'|"[^"]*"|[^;])+""", teks)
    return [p.strip() for p in potongan if p.strip()]


def baca_kondisi(tabel, teks):
    """Membaca klausa WHERE. Return (kondisi, pesan_error)."""
    if teks is None:
        return None, None
    m = re.fullmatch(r"(\w+)\s*(>=|<=|!=|=|>|<)\s*(.+)", teks.strip())
    if not m:
        return None, f"Kondisi WHERE tidak valid: {teks}"
    kolom = m.group(1).lower()
    if kolom not in ["id"] + tabel["kolom"]:
        return None, f"Kolom '{kolom}' tidak ada pada tabel."
    return (kolom, m.group(2), parse_nilai(m.group(3))), None


def cocok(id_baris, baris, kondisi):
    """True jika baris memenuhi kondisi (kondisi None = semua baris cocok)."""
    if kondisi is None:
        return True
    kolom, op, nilai = kondisi
    data = {"id": id_baris, **baris}
    try:
        return OPERATOR[op](data[kolom], nilai)
    except TypeError:  # misalnya membandingkan teks dengan angka
        return False


# ---------------------------------------------------------------
# MESIN QUERY
# Mengembalikan tuple (berhasil, pesan, hasil)
#   hasil = list of dict (untuk SELECT / SHOW TABLES) atau None
# ---------------------------------------------------------------
def jalankan_query(db, query):
    q = query.strip()
    flag = re.IGNORECASE | re.DOTALL

    # SHOW TABLES
    if re.fullmatch(r"SHOW\s+TABLES", q, flag):
        hasil = [{"tabel": n, "kolom": ", ".join(t["kolom"]), "jumlah baris": len(t["baris"])}
                 for n, t in db.items()]
        return True, f"{len(hasil)} tabel ditemukan.", hasil

    # CREATE TABLE nama (kolom1, kolom2, ...)
    m = re.fullmatch(r"CREATE\s+TABLE\s+(\w+)\s*\((.+)\)", q, flag)
    if m:
        nama = m.group(1).lower()
        kolom = [k.strip().lower() for k in m.group(2).split(",")]
        if nama in db:
            return False, f"Tabel '{nama}' sudah ada.", None
        if not all(re.fullmatch(r"\w+", k) for k in kolom):
            return False, "Nama kolom hanya boleh huruf, angka, dan underscore.", None
        if len(set(kolom)) != len(kolom):
            return False, "Nama kolom tidak boleh sama.", None
        if "id" in kolom:
            return False, "Kolom 'id' dibuat otomatis, jangan dideklarasikan.", None
        db[nama] = {"kolom": kolom, "auto_id": 1, "baris": {}}
        return True, f"Tabel '{nama}' berhasil dibuat dengan kolom: {', '.join(kolom)}.", None

    # DROP TABLE nama
    m = re.fullmatch(r"DROP\s+TABLE\s+(\w+)", q, flag)
    if m:
        nama = m.group(1).lower()
        if nama not in db:
            return False, f"Tabel '{nama}' tidak ditemukan.", None
        del db[nama]
        return True, f"Tabel '{nama}' berhasil dihapus.", None

    # INSERT INTO nama VALUES (v1, v2, ...)
    m = re.fullmatch(r"INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.+)\)", q, flag)
    if m:
        nama = m.group(1).lower()
        if nama not in db:
            return False, f"Tabel '{nama}' tidak ditemukan.", None
        tabel = db[nama]
        nilai = pisah_nilai(m.group(2))
        if len(nilai) != len(tabel["kolom"]):
            return False, (f"Jumlah nilai ({len(nilai)}) tidak sama dengan jumlah "
                           f"kolom ({len(tabel['kolom'])})."), None
        id_baru = tabel["auto_id"]
        tabel["baris"][id_baru] = dict(zip(tabel["kolom"], nilai))
        tabel["auto_id"] += 1
        return True, f"1 baris ditambahkan ke '{nama}' (id = {id_baru}).", None

    # SELECT kolom FROM nama [WHERE kondisi]
    m = re.fullmatch(r"SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?", q, flag)
    if m:
        nama = m.group(2).lower()
        if nama not in db:
            return False, f"Tabel '{nama}' tidak ditemukan.", None
        tabel = db[nama]
        semua_kolom = ["id"] + tabel["kolom"]
        if m.group(1).strip() == "*":
            kolom_pilih = semua_kolom
        else:
            kolom_pilih = [k.strip().lower() for k in m.group(1).split(",")]
            salah = [k for k in kolom_pilih if k not in semua_kolom]
            if salah:
                return False, f"Kolom tidak ada: {', '.join(salah)}", None
        kondisi, error = baca_kondisi(tabel, m.group(3))
        if error:
            return False, error, None
        hasil = []
        for id_baris, baris in tabel["baris"].items():
            if cocok(id_baris, baris, kondisi):
                data = {"id": id_baris, **baris}
                hasil.append({k: data[k] for k in kolom_pilih})
        return True, f"{len(hasil)} baris ditemukan.", hasil

    # UPDATE nama SET kolom = nilai [WHERE kondisi]
    m = re.fullmatch(r"UPDATE\s+(\w+)\s+SET\s+(\w+)\s*=\s*(.+?)(?:\s+WHERE\s+(.+))?", q, flag)
    if m:
        nama = m.group(1).lower()
        if nama not in db:
            return False, f"Tabel '{nama}' tidak ditemukan.", None
        tabel = db[nama]
        kolom = m.group(2).lower()
        if kolom not in tabel["kolom"]:
            return False, f"Kolom '{kolom}' tidak ada (kolom 'id' tidak bisa diubah).", None
        kondisi, error = baca_kondisi(tabel, m.group(4))
        if error:
            return False, error, None
        nilai_baru = parse_nilai(m.group(3))
        jumlah = 0
        for id_baris, baris in tabel["baris"].items():
            if cocok(id_baris, baris, kondisi):
                baris[kolom] = nilai_baru
                jumlah += 1
        return True, f"{jumlah} baris diperbarui.", None

    # DELETE FROM nama [WHERE kondisi]
    m = re.fullmatch(r"DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?", q, flag)
    if m:
        nama = m.group(1).lower()
        if nama not in db:
            return False, f"Tabel '{nama}' tidak ditemukan.", None
        tabel = db[nama]
        kondisi, error = baca_kondisi(tabel, m.group(2))
        if error:
            return False, error, None
        id_hapus = [i for i, b in tabel["baris"].items() if cocok(i, b, kondisi)]
        for i in id_hapus:
            del tabel["baris"][i]
        return True, f"{len(id_hapus)} baris dihapus.", None

    return False, "Perintah tidak dikenali. Lihat daftar sintaks yang didukung.", None


# ---------------------------------------------------------------
# TAMPILAN HALAMAN
# ---------------------------------------------------------------
st.title("🗄️ Mini Database dengan Nested Dictionary")
st.markdown("""
Buat **tabel** dan jalankan **query** seperti SQL sederhana. Seluruh data disimpan dalam
**nested dictionary**: `db[tabel]["baris"][id][kolom]`.
""")

if "db" not in st.session_state:
    st.session_state["db"] = {}
db = st.session_state["db"]
st.session_state.setdefault("query", "")


def isi_contoh():
    st.session_state["query"] = CONTOH_QUERY


def reset_database():
    st.session_state["db"] = {}


# ---------------------------------------------------------------
# PETUNJUK SINTAKS
# ---------------------------------------------------------------
with st.expander("📖 Sintaks query yang didukung"):
    st.code("""SHOW TABLES
CREATE TABLE nama_tabel (kolom1, kolom2, kolom3)
DROP TABLE nama_tabel
INSERT INTO nama_tabel VALUES ('teks', 123, 4.5)
SELECT * FROM nama_tabel
SELECT kolom1, kolom2 FROM nama_tabel WHERE kolom3 > 10
UPDATE nama_tabel SET kolom1 = 'baru' WHERE kolom2 = 5
DELETE FROM nama_tabel WHERE kolom3 <= 10""", language="sql")
    st.markdown("""
- Pisahkan beberapa query dengan tanda `;`
- Operator `WHERE`: `=`, `!=`, `>`, `<`, `>=`, `<=` (satu kondisi saja)
- Kolom `id` dibuat otomatis (1, 2, 3, ...) dan boleh dipakai pada `SELECT` dan `WHERE`
- Teks ditulis dengan tanda kutip, angka tanpa kutip
""")

# ---------------------------------------------------------------
# INPUT QUERY
# ---------------------------------------------------------------
st.subheader("Tulis Query")
st.text_area("Query (boleh lebih dari satu, pisahkan dengan ;)", key="query", height=220)

col_a, col_b, col_c = st.columns([1, 1, 3])
jalankan = col_a.button("▶ Jalankan", type="primary")
col_b.button("Isi contoh", on_click=isi_contoh)
col_c.button("Reset database", on_click=reset_database)

# ---------------------------------------------------------------
# EKSEKUSI QUERY (harus sebelum menampilkan isi database)
# ---------------------------------------------------------------
if jalankan:
    daftar_query = pisah_query(st.session_state["query"])
    if not daftar_query:
        st.warning("Query masih kosong.")
    for q in daftar_query:
        berhasil, pesan, hasil = jalankan_query(db, q)
        st.code(q, language="sql")
        if berhasil:
            st.success(pesan)
        else:
            st.error(pesan)
            break  # hentikan jika ada query yang gagal
        if hasil is not None:
            if hasil:
                st.table(hasil)
            else:
                st.info("Tidak ada baris yang cocok.")
    st.session_state["db"] = db

# ---------------------------------------------------------------
# TAMPILKAN ISI DATABASE
# ---------------------------------------------------------------
st.divider()
st.header("🧱 Isi Database")
if not db:
    st.info("Database masih kosong. Coba jalankan `CREATE TABLE ...` atau klik 'Isi contoh'.")
else:
    for nama_tabel, tabel in db.items():
        st.subheader(f"Tabel: {nama_tabel}")
        st.caption(f"Kolom: id (otomatis), {', '.join(tabel['kolom'])} "
                   f"| Jumlah baris: {len(tabel['baris'])}")
        if tabel["baris"]:
            st.table([{"id": i, **b} for i, b in tabel["baris"].items()])
        else:
            st.info("Tabel masih kosong.")
        with st.expander(f"Lihat nested dictionary tabel '{nama_tabel}'"):
            st.json(tabel)

    with st.expander("Lihat seluruh database (nested dictionary)"):
        st.json(db)
