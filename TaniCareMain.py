
import os
import csv
import pandas as pd
from tabulate import tabulate
from datetime import datetime

# ======================================================
# ASCII logo (TaniCare)
# ======================================================
LOGO = """
╔════════════════════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ███╗   ██╗██╗ ██████╗ █████╗ ██████╗ ███████╗            ║
║  ╚══██╔══╝██╔══██╗████╗  ██║██║██╔════╝██╔══██╗██╔══██╗██╔════╝            ║
║     ██║   ███████║██╔██╗ ██║██║██║     ███████║██████╔╝█████╗              ║
║     ██║   ██╔══██║██║╚██╗██║██║██║     ██╔══██║██╔══██╗██╔══╝              ║
║     ██║   ██║  ██║██║ ╚████║██║╚██████╗██║  ██║██║  ██║███████╗            ║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# ======================================================
# NAMA FILE 
# ======================================================
PENGGUNA_CSV = "pengguna.csv"
STOK_CSV = "stok_pupuk.csv"
KERANJANG_CSV = "keranjang.csv"
TRANS_CSV = "transaksi.csv"
DETAIL_CSV = "detail_transaksi.csv"
RIWAYAT_CSV = "riwayat_pembelian.csv"
KONSULT_CSV = "konsultasi.csv"

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"


# ---------------------------
# HELPERS ringan (inline)
# ---------------------------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def gen_simple_id(prefix, df):
    # buat id berbasis jumlah baris +1: P001, T005, K010...
    try:
        n = len(df) + 1
    except:
        n = 1
    return f"{prefix}{n:03d}"

def now_str():
    return datetime.now().strftime(DATE_FORMAT)

# ======================================================
# AUTH (login/register)
# ======================================================
def login():
    clear()
    print(LOGO)
    print("=================================[ LOGIN ]=================================")
    username = input("Masukkan username: ").strip()
    password = input("Masukkan password: ").strip()

    try:
        users = pd.read_csv(PENGGUNA_CSV)
    except Exception as e:
        print("Error: tidak bisa buka file pengguna.csv. Pastikan file ada dan format benar.")
        print("Detail:", e)
        input("Tekan Enter...")
        return

    # cari user (case-insensitive username)
    matched = None
    for _, row in users.iterrows():
        if str(row['Username']).strip().lower() == username.lower() and str(row['Password']) == password:
            matched = row
            break

    if matched is None:
        print("Username atau password salah!")
        input("Klik Enter untuk melanjutkan...")
        return

    role = str(matched['Role']).strip().lower()
    if role == 'admin':
        print("Selamat datang, Admin!")
        input("Klik Enter untuk melanjutkan...")
        menu_admin(username)
    else:
        print(f"Selamat datang, {matched['Nama Lengkap'] if 'Nama Lengkap' in matched else username}!")
        input("Klik Enter untuk melanjutkan...")
        menu_pembeli(username)

def register_user():
    clear()
    print(LOGO)
    print("=================================[ REGISTER ]================================")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    nama = input("Nama Lengkap: ").strip()
    alamat = input("Alamat: ").strip()
    telp = input("Nomor Telepon: ").strip()
    role = "Pembeli"

    try:
        users = pd.read_csv(PENGGUNA_CSV)
    except Exception as e:
        print("Error buka pengguna.csv:", e)
        input("Enter...")
        return

    if username.lower() in users['Username'].astype(str).str.lower().values:
        print("Username sudah digunakan!")
        input("Enter...")
        return

    users.loc[len(users)] = [username, password, nama, alamat, telp, role]
    users.to_csv(PENGGUNA_CSV, index=False)
    print("Akun berhasil dibuat!")
    input("Enter...")

# ======================================================
# PRODUK (lihat, cari, tambah, hapus, update)
# ======================================================
def tampilkan_produk():
    clear()
    try:
        prod = pd.read_csv(STOK_CSV)
    except Exception as e:
        print("Error buka stok_pupuk.csv:", e)
        input("Enter..."); return

    if prod.empty:
        print("Belum ada produk.")
    else:
        disp = prod.copy().reset_index(drop=True)
        disp.index += 1
        print("==== DAFTAR PRODUK ====")
        print(tabulate(disp[['ID Produk','Nama Produk','Harga','Stok','Status']], headers='keys', tablefmt='fancy_grid'))
    input("Enter...")

def cari_produk():
    clear()
    try:
        prod = pd.read_csv(STOK_CSV)
    except Exception as e:
        print("Error buka stok_pupuk.csv:", e)
        input("Enter..."); return

    if prod.empty:
        print("Belum ada produk.")
        input("Enter..."); return

    q = input("Masukkan ID atau nama (substring): ").strip().lower()
    res = prod[ prod['ID Produk'].astype(str).str.lower().str.contains(q) | prod['Nama Produk'].astype(str).str.lower().str.contains(q) ]
    if res.empty:
        print("Produk tidak ditemukan.")
    else:
        disp = res.copy().reset_index(drop=True); disp.index += 1
        print(tabulate(disp[['ID Produk','Nama Produk','Harga','Stok','Status']], headers='keys', tablefmt='fancy_grid'))
    input("Enter...")

def tambah_produk():
    clear()
    try:
        prod = pd.read_csv(STOK_CSV)
    except Exception as e:
        print("Error buka stok_pupuk.csv:", e)
        input("Enter..."); return

    print("=== TAMBAH PRODUK ===")
    nama = input("Nama produk: ").strip().title()
    try:
        harga = int(input("Harga (angka): ").strip())
        stok = int(input("Stok (angka): ").strip())
    except:
        print("Input tidak valid (harus angka).")
        input("Enter..."); return

    # generate simple ID P###
    pid = gen_simple_id("P", prod)
    status = "Tersedia" if stok > 0 else "Habis"
    prod.loc[len(prod)] = [pid, nama, harga, stok, status]
    prod.to_csv(STOK_CSV, index=False)
    print("Produk berhasil ditambahkan dengan ID", pid)
    input("Enter...")

def hapus_produk(dataframe=None):
    # support both signature styles (kating sometimes passes df)
    clear()
    try:
        prod = pd.read_csv(STOK_CSV)
    except Exception as e:
        print("Error buka stok_pupuk.csv:", e)
        input("Enter..."); return

    if prod.empty:
        print("Belum ada produk.")
        input("Enter..."); return

    disp = prod.copy().reset_index(drop=True); disp.index += 1
    print(tabulate(disp[['ID Produk','Nama Produk','Harga','Stok']], headers='keys', tablefmt='fancy_grid'))
    try:
        idx = int(input("Masukkan index produk yang akan dihapus: ").strip())
    except:
        print("Input tidak valid.")
        input("Enter..."); return
    if idx < 1 or idx > len(prod):
        print("Index salah.")
        input("Enter..."); return
    prod = prod.drop(prod.index[idx-1]).reset_index(drop=True)
    prod.to_csv(STOK_CSV, index=False)
    print("Produk berhasil dihapus.")
    input("Enter...")

def update_produk(dataframe=None):
    clear()
    try:
        prod = pd.read_csv(STOK_CSV)
    except Exception as e:
        print("Error buka stok_pupuk.csv:", e)
        input("Enter..."); return

    if prod.empty:
        print("Belum ada produk.")
        input("Enter..."); return

    disp = prod.copy().reset_index(drop=True); disp.index += 1
    print(tabulate(disp[['ID Produk','Nama Produk','Harga','Stok']], headers='keys', tablefmt='fancy_grid'))
    try:
        idx = int(input("Masukkan index produk yang akan diupdate: ").strip()) - 1
    except:
        print("Input tidak valid.")
        input("Enter..."); return
    if idx < 0 or idx >= len(prod):
        print("Index salah.")
        input("Enter..."); return

    nama = input(f"Nama baru [{prod.at[idx,'Nama Produk']}]: ").strip() or prod.at[idx,'Nama Produk']
    harga_raw = input(f"Harga baru [{prod.at[idx,'Harga']}]: ").strip() or str(prod.at[idx,'Harga'])
    stok_raw = input(f"Stok baru [{prod.at[idx,'Stok']}]: ").strip() or str(prod.at[idx,'Stok'])
    try:
        harga = int(harga_raw); stok = int(stok_raw)
    except:
        print("Input angka salah.")
        input("Enter..."); return
    prod.at[idx,'Nama Produk'] = nama
    prod.at[idx,'Harga'] = harga
    prod.at[idx,'Stok'] = stok
    prod.at[idx,'Status'] = "Tersedia" if stok > 0 else "Habis"
    prod.to_csv(STOK_CSV, index=False)
    print("Produk berhasil diupdate.")
    input("Enter...")

# ======================================================
# KERANJANG, CHECKOUT, TRANSAKSI, DETAIL, RIWAYAT
# ======================================================
def tambah_keranjang(username):
    clear()
    try:
        prod = pd.read_csv(STOK_CSV)
        cart = pd.read_csv(KERANJANG_CSV)
    except Exception as e:
        print("Error buka file CSV:", e)
        input("Enter..."); return

    if prod.empty:
        print("Belum ada produk.")
        input("Enter..."); return

    disp = prod.copy().reset_index(drop=True); disp.index += 1
    print(tabulate(disp[['ID Produk','Nama Produk','Harga','Stok']], headers='keys', tablefmt='fancy_grid'))
    try:
        idx = int(input("Pilih nomor produk: ").strip()) - 1
        jumlah = int(input("Jumlah: ").strip())
    except:
        print("Input invalid.")
        input("Enter..."); return
    if idx < 0 or idx >= len(prod):
        print("Produk tidak valid.")
        input("Enter..."); return
    stok_avail = int(prod.at[idx,'Stok'])
    if jumlah <= 0 or jumlah > stok_avail:
        print("Jumlah tidak tersedia.")
        input("Enter..."); return
    subtotal = jumlah * int(prod.at[idx,'Harga'])
    cart.loc[len(cart)] = [username, prod.at[idx,'ID Produk'], jumlah, subtotal]
    cart.to_csv(KERANJANG_CSV, index=False)
    # update stok (sama seperti kating style)
    prod.at[idx,'Stok'] = stok_avail - jumlah
    prod.at[idx,'Status'] = "Habis" if prod.at[idx,'Stok'] <= 0 else "Tersedia"
    prod.to_csv(STOK_CSV, index=False)
    print("Produk berhasil ditambahkan ke keranjang.")
    input("Enter...")

def lihat_keranjang(username):
    clear()
    try:
        cart = pd.read_csv(KERANJANG_CSV)
    except Exception as e:
        print("Error buka keranjang:", e)
        input("Enter..."); return
    my = cart[cart['Username'] == username]
    if my.empty:
        print("Keranjang kosong.")
    else:
        disp = my.copy().reset_index(drop=True); disp.index += 1
        print(tabulate(disp[['ID Produk','Jumlah','Subtotal']], headers='keys', tablefmt='fancy_grid'))
        print("Total sementara: Rp", int(my['Subtotal'].sum()))
    input("Enter...")

def proses_checkout(username):
    clear()
    try:
        cart = pd.read_csv(KERANJANG_CSV)
    except Exception as e:
        print("Error buka keranjang:", e)
        input("Enter..."); return
    my = cart[cart['Username'] == username]
    if my.empty:
        print("Keranjang kosong.")
        input("Enter..."); return
    total = int(my['Subtotal'].sum())
    print("Total pembayaran: Rp", total)
    try:
        bayar = int(input("Bayar: ").strip())
    except:
        print("Input invalid.")
        input("Enter..."); return
    if bayar < total:
        print("Uang tidak cukup.")
        input("Enter..."); return
    kembalian = bayar - total

    # catat transaksi
    try:
        trans = pd.read_csv(TRANS_CSV)
    except:
        trans = pd.DataFrame(columns=["ID Transaksi","Username","Tanggal Transaksi","Total Pembayaran","Status"])
    tid = gen_simple_id("T", trans)
    trans.loc[len(trans)] = [tid, username, now_str(), total, "Dikemas"]
    trans.to_csv(TRANS_CSV, index=False)

    # detail transaksi
    try:
        detail = pd.read_csv(DETAIL_CSV)
    except:
        detail = pd.DataFrame(columns=["ID Transaksi","ID Produk","Nama Produk","Jumlah","Harga Satuan","Total Harga"])
    try:
        prod = pd.read_csv(STOK_CSV)
    except:
        prod = pd.DataFrame()
    for _, row in my.iterrows():
        pid = row['ID Produk']
        nama_arr = prod[prod['ID Produk'] == pid]['Nama Produk'].values
        nama = nama_arr[0] if len(nama_arr) > 0 else ""
        jumlah = int(row['Jumlah'])
        harga_satuan = int(row['Subtotal']) // jumlah if jumlah > 0 else 0
        total_harga = int(row['Subtotal'])
        detail.loc[len(detail)] = [tid, pid, nama, jumlah, harga_satuan, total_harga]
    detail.to_csv(DETAIL_CSV, index=False)

    # riwayat
    try:
        riwayat = pd.read_csv(RIWAYAT_CSV)
    except:
        riwayat = pd.DataFrame(columns=["ID Riwayat","Username","Tanggal","Total Pengeluaran"])
    rid = gen_simple_id("R", riwayat)
    riwayat.loc[len(riwayat)] = [rid, username, now_str(), total]
    riwayat.to_csv(RIWAYAT_CSV, index=False)

    # kosongkan keranjang user
    cart = cart[cart['Username'] != username]
    cart.to_csv(KERANJANG_CSV, index=False)

    print(f"Transaksi {tid} berhasil dicatat. Kembalian: Rp {kembalian}")
    input("Enter...")

def riwayat_pembeli(username):
    clear()
    try:
        trans = pd.read_csv(TRANS_CSV)
    except Exception as e:
        print("Error buka transaksi:", e)
        input("Enter..."); return
    my = trans[trans['Username'] == username]
    if my.empty:
        print("Belum ada riwayat pembelian.")
    else:
        disp = my.copy().reset_index(drop=True); disp.index += 1
        print(tabulate(disp, headers='keys', tablefmt='fancy_grid'))
    input("Enter...")

# ======================================================
# KONSULTASI (kirim & admin balas)
# ======================================================
def layanan_konsultasi_pembeli(username):
    clear()
    try:
        kons = pd.read_csv(KONSULT_CSV)
    except:
        kons = pd.DataFrame(columns=["ID Pesan","Username Pengirim","Pesan","Balasan","Tanggal"])
    pesan = input("Tulis pesan konsultasi: ").strip()
    kid = gen_simple_id("K", kons)
    kons.loc[len(kons)] = [kid, username, pesan, "", now_str()]
    kons.to_csv(KONSULT_CSV, index=False)
    print("Pesan terkirim.")
    input("Enter...")

def lihat_konsultasi_admin():
    clear()
    try:
        kons = pd.read_csv(KONSULT_CSV)
    except Exception as e:
        print("Error buka konsultasi:", e)
        input("Enter..."); return
    if kons.empty:
        print("Belum ada pesan.")
    else:
        disp = kons.copy().reset_index(drop=True); disp.index += 1
        print(tabulate(disp, headers='keys', tablefmt='fancy_grid'))
    input("Enter...")

def jawab_konsultasi():
    clear()
    try:
        kons = pd.read_csv(KONSULT_CSV)
    except Exception as e:
        print("Error buka konsultasi:", e)
        input("Enter..."); return
    if kons.empty:
        print("Belum ada pesan.")
        input("Enter..."); return
    print(tabulate(kons, headers='keys', tablefmt='fancy_grid'))
    kid = input("Masukkan ID Pesan untuk dibalas: ").strip()
    if kid not in kons['ID Pesan'].astype(str).values:
        print("ID tidak ditemukan.")
        input("Enter..."); return
    idx = kons.index[kons['ID Pesan'].astype(str) == kid][0]
    balasan = input("Tulis balasan: ").strip()
    kons.at[idx, 'Balasan'] = balasan
    kons.to_csv(KONSULT_CSV, index=False)
    print("Balasan tersimpan.")
    input("Enter...")

# ======================================================
# ADMIN: kelola transaksi, laporan, data pengguna, kelola akun
# ======================================================
def kelola_transaksi_admin():
    clear()
    try:
        trans = pd.read_csv(TRANS_CSV)
    except Exception as e:
        print("Error buka transaksi:", e)
        input("Enter..."); return
    if trans.empty:
        print("Belum ada transaksi.")
        input("Enter..."); return
    print(tabulate(trans, headers='keys', tablefmt='fancy_grid'))
    tid = input("Masukkan ID Transaksi untuk update status (atau Enter): ").strip()
    if not tid:
        return
    if tid not in trans['ID Transaksi'].astype(str).values:
        print("Transaksi tidak ditemukan.")
        input("Enter..."); return
    idx = trans.index[trans['ID Transaksi'].astype(str) == tid][0]
    ns = input("Masukkan status baru (Dikemas/Dikirim/Selesai): ").strip()
    trans.at[idx, 'Status'] = ns
    trans.to_csv(TRANS_CSV, index=False)
    print("Status transaksi diupdate.")
    input("Enter...")

def laporan_penjualan():
    clear()
    try:
        detail = pd.read_csv(DETAIL_CSV)
    except Exception as e:
        print("Error buka detail_transaksi:", e)
        input("Enter..."); return
    if detail.empty:
        print("Belum ada penjualan.")
        input("Enter..."); return
    print("1. Laporan per produk")
    print("2. Laporan per periode")
    print("3. Laporan keseluruhan")
    pilihan = input("Pilih: ").strip()
    if pilihan == "1":
        lap = detail.groupby('Nama Produk').agg({'Jumlah':'sum','Total Harga':'sum'}).reset_index()
        lap.index += 1
        print(tabulate(lap, headers='keys', tablefmt='fancy_grid'))
        input("Enter...")
    elif pilihan == "2":
        try:
            trans = pd.read_csv(TRANS_CSV)
            trans['__dt'] = pd.to_datetime(trans['Tanggal Transaksi'], dayfirst=True, errors='coerce')
            start = input("Tanggal mulai (DD-MM-YYYY): ").strip()
            end = input("Tanggal akhir (DD-MM-YYYY): ").strip()
            sd = pd.to_datetime(start, format='%d-%m-%Y')
            ed = pd.to_datetime(end, format='%d-%m-%Y') + pd.Timedelta(days=1)
            merged = pd.merge(detail, trans[['ID Transaksi','__dt']], on='ID Transaksi', how='left')
            filtered = merged[(merged['__dt'] >= sd) & (merged['__dt'] < ed)]
            report = filtered.groupby(filtered['__dt'].dt.date).agg({'Total Harga':'sum'}).reset_index()
            report.index += 1
            print(tabulate(report, headers='keys', tablefmt='fancy_grid'))
        except Exception as e:
            print("Format tanggal salah atau error:", e)
        input("Enter...")
    else:
        total = detail['Total Harga'].sum()
        print("Total pemasukan: Rp", total)
        input("Enter...")

def data_pengguna():
    clear()
    try:
        users = pd.read_csv(PENGGUNA_CSV)
    except Exception as e:
        print("Error buka pengguna:", e)
        input("Enter..."); return
    if users.empty:
        print("Belum ada pengguna.")
    else:
        disp = users.copy().reset_index(drop=True); disp.index += 1
        print(tabulate(disp[['Username','Nama Lengkap','Alamat','Nomor Telepon','Role']], headers='keys', tablefmt='fancy_grid'))
    input("Enter...")

def kelola_akun_kasir():
    clear()
    try:
        users = pd.read_csv(PENGGUNA_CSV)
    except Exception as e:
        print("Error buka pengguna:", e)
        input("Enter..."); return
    disp = users.copy().reset_index(drop=True); disp.index += 1
    print(tabulate(disp[['Username','Nama Lengkap','Role']], headers='keys', tablefmt='fancy_grid'))
    print("1. Tambah akun pembeli")
    print("2. Hapus akun")
    print("3. Kembali")
    p = input("Pilih: ").strip()
    if p == "1":
        username = input("Username baru: ").strip()
        password = input("Password: ").strip()
        nama = input("Nama lengkap: ").strip()
        alamat = input("Alamat: ").strip()
        telp = input("No. telp: ").strip()
        role = "Pembeli"
        if username.lower() in users['Username'].astype(str).str.lower().values:
            print("Username sudah ada.")
            input("Enter..."); return
        users.loc[len(users)] = [username, password, nama, alamat, telp, role]
        users.to_csv(PENGGUNA_CSV, index=False)
        print("Akun pembeli berhasil ditambahkan.")
        input("Enter...")
    elif p == "2":
        try:
            idx = int(input("Index akun yang akan dihapus: ").strip())
        except:
            print("Input invalid."); input("Enter..."); return
        if idx < 1 or idx > len(users):
            print("Index salah."); input("Enter..."); return
        users = users.drop(users.index[idx-1]).reset_index(drop=True)
        users.to_csv(PENGGUNA_CSV, index=False)
        print("Akun dihapus.")
        input("Enter...")
    else:
        return

# ======================================================
# Wrapper menu (admin / pembeli)
# ======================================================
def menu_kasir(username):
    while True:
        clear()
        teks = """
╔════════════════════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ███╗   ██╗██╗ ██████╗ █████╗ ██████╗ ███████╗            ║
║  ╚══██╔══╝██╔══██╗████╗  ██║██║██╔════╝██╔══██╗██╔══██╗██╔════╝            ║
║     ██║   ███████║██╔██╗ ██║██║██║     ███████║██████╔╝█████╗              ║
║     ██║   ██╔══██║██║╚██╗██║██║██║     ██╔══██║██╔══██╗██╔══╝              ║
║     ██║   ██║  ██║██║ ╚████║██║╚██████╗██║  ██║██║  ██║███████╗            ║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
        print(teks)
        print(f"===================== MENU PEMBELI (User: {username}) =====================")
        print("1. Lihat daftar produk")
        print("2. Cari produk")
        print("3. Tambah ke keranjang")
        print("4. Lihat keranjang")
        print("5. Proses checkout")
        print("6. Riwayat pembelian")
        print("7. Konsultasi pertanian")
        print("8. Logout")
        pilih = input("Pilih menu (1-8): ").strip()
        if pilih == "1": tampilkan_produk()
        elif pilih == "2": cari_produk()
        elif pilih == "3": tambah_keranjang(username)
        elif pilih == "4": lihat_keranjang(username)
        elif pilih == "5": proses_checkout(username)
        elif pilih == "6": riwayat_pembeli(username)
        elif pilih == "7": layanan_konsultasi_pembeli(username)
        elif pilih == "8": break
        else:
            print("Pilihan tidak valid!")
            input("Enter...")

def menu_admin(username):
    while True:
        clear()
        print(LOGO)
        print(f"===================== MENU ADMIN (Admin: {username}) =====================")
        print("1. Kelola Data Produk")
        print("2. Kelola Transaksi")
        print("3. Laporan & Riwayat Penjualan")
        print("4. Data Pengguna")
        print("5. Kelola Akun Pembeli")
        print("6. Layanan Konsultasi")
        print("7. Logout")
        pilih = input("Pilih menu (1-7): ").strip()
        if pilih == "1": 
            # kelola produk menu
            while True:
                clear(); print("=== KELOLA DATA PRODUK ===")
                print("1. Lihat Produk")
                print("2. Tambah Produk")
                print("3. Ubah Produk")
                print("4. Hapus Produk")
                print("5. Kembali")
                p = input("Pilih: ").strip()
                if p == "1": tampilkan_produk()
                elif p == "2": tambah_produk()
                elif p == "3": update_produk()
                elif p == "4": hapus_produk()
                elif p == "5": break
                else: input("Input salah")
        elif pilih == "2": kelola_transaksi_admin()
        elif pilih == "3": laporan_penjualan()
        elif pilih == "4": data_pengguna()
        elif pilih == "5": kelola_akun_kasir()
        elif pilih == "6":
            while True:
                clear()
                print("=== KONSULTASI ADMIN ===")
                print("1. Lihat Pesan")
                print("2. Balas Pesan")
                print("3. Kembali")
                s = input("Pilih: ").strip()
                if s == "1": lihat_konsultasi_admin()
                elif s == "2": jawab_konsultasi()
                elif s == "3": break
                else: input("Input salah")
        elif pilih == "7": break
        else:
            print("Pilihan tidak valid!")
            input("Enter...")

def menu_pembeli(username):
    while True:
        os.system('cls')
        print(f"=== MENU PEMBELI ({username}) ===")
        print("1. Lihat Produk")
        print("2. Tambah ke Keranjang")
        print("3. Lihat Keranjang")
        print("4. Checkout")
        print("5. Layanan Konsultasi")
        print("6. Riwayat Pembelian")
        print("7. Logout")

        p = input("Pilih: ")

        if p == "1":
            tampilkan_produk()
        elif p == "2":
            tambah_keranjang(username)
        elif p == "3":
            lihat_keranjang(username)
        elif p == "4":
            proses_checkout(username)
        elif p == "5":
            layanan_konsultasi_pembeli(username)
        elif p == "6":
            riwayat_pembeli(username)
        elif p == "7":
            break
        else:
            input("Input salah...")


# ======================================================
# ENTRY POINT
# ======================================================
def main():
    while True:
        clear()
        print(LOGO)
        print("══════════════════════ HALAMAN AWAL ══════════════════════")
        print("1. Login")
        print("2. Register")
        print("3. Keluar")
        print("══════════════════════════════════════════════════════════")
        p = input("Pilih: ").strip()
        if p == "1": login()
        elif p == "2": register_user()
        elif p == "3":
            print("Terima kasih sudah menggunakan TaniCare!")
            break
        else:
            input("Pilihan salah. Tekan Enter...")

if __name__ == "__main__":
    main()
