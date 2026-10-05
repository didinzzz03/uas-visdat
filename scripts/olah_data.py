"""
Pengolahan data UAS Visualisasi Data – Pemulihan Pascabanjir Sumatera (versi ringkas)

Input  : data/raw/zonal_kecamatan_ntl_ndvi_chirps.csv  (ekspor GEE, 674 kecamatan)
         data/processed/bps_kabkota_2024.xlsx           (9 indikator BPS, 52 kab/kota)
Output : data/processed/kecamatan_indikator.csv          (674 baris)
         data/processed/kabkota_gabungan.csv             (52 baris)
"""
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("data/raw")
PROC = Path("data/processed")
PROC.mkdir(parents=True, exist_ok=True)

AMBANG_NTL = 0.5      # nW/cm²/sr: di bawah ini kecamatan dianggap terlalu gelap untuk dihitung rasionya
AMBANG_PIKSEL = 50    # piksel MODIS 250 m (~3 km²): di bawah ini NDVI dianggap kurang andal
AMBANG_TURUN = -0.20  # penurunan NTL ≥20% (dibanding musim yang sama tahun sebelumnya) dianggap "turun besar"

# Catatan metode: dampak dihitung terhadap T1ref (Des 2024–Jan 2025), yaitu musim yang sama
# setahun sebelum bencana, agar efek musim hujan (awan, atmosfer) tidak terbaca sebagai dampak.
# Pemulihan dihitung terhadap T0 (Jun–Okt 2025), musim yang sepadan dengan T2 (Jul–Agu 2026).

# ---------------------------------------------------------------- 1. Baca data
g = pd.read_csv(RAW / "zonal_kecamatan_ntl_ndvi_chirps.csv",
                dtype={"KODE_BPS": str, "KDCPUM": str, "KDPKAB": str, "KDPPUM": str})
g = g.drop(columns=["system:index", ".geo"], errors="ignore")
g = g.rename(columns={
    "KDCPUM": "kode_kec", "KDPKAB": "kode_kab_dagri", "KDPPUM": "kode_prov",
    "KODE_BPS": "kode_bps", "LUASWH": "luas_km2", "STATUS": "status",
    "WADMKC": "kecamatan", "WADMKK": "kab_kota", "WADMPR": "provinsi",
})
for p in ["T0", "T1ref", "T1", "T2"]:
    g = g.rename(columns={f"ntl_{p}_mean": f"ntl_{p}", f"ndvi_{p}_mean": f"ndvi_{p}"})
g = g.rename(columns={"hujan_total_mean": "hujan_total", "hujan_maks_mean": "hujan_maks"})

bps = pd.read_excel(PROC / "bps_kabkota_2024.xlsx", sheet_name="data", dtype={"kode_bps": str})

# ---------------------------------------------------------------- 2. Indikator per kecamatan
k = g.copy()

# NTL: rasio hanya dihitung jika kondisi awal cukup terang
k["ntl_terukur"] = (k["ntl_T0"] >= AMBANG_NTL) & (k["ntl_T1ref"] >= AMBANG_NTL)
k["ntl_penurunan"] = np.where(k["ntl_terukur"], (k["ntl_T1"] - k["ntl_T1ref"]) / k["ntl_T1ref"], np.nan)
k["ntl_pemulihan"] = np.where(k["ntl_terukur"], k["ntl_T2"] / k["ntl_T0"], np.nan)

# Cahaya yang hilang (nilai absolut, untuk simbol proporsional): radiance rata-rata × luas
k["cahaya_hilang"] = ((k["ntl_T1ref"] - k["ntl_T1"]) * k["luas_km2"]).clip(lower=0)

# NDVI: selisih terhadap kondisi awal
k["ndvi_andal"] = (k["ndvi_T0_count"] >= AMBANG_PIKSEL) & k["ndvi_T0"].notna()
k["dndvi_dampak"] = k["ndvi_T1"] - k["ndvi_T1ref"]
k["dndvi_pemulihan"] = k["ndvi_T2"] - k["ndvi_T0"]

# Kategori pemulihan NTL untuk peta
def kategori(r):
    if pd.isna(r):
        return "Terlalu gelap untuk diukur"
    if r < 0.8:
        return "Belum pulih (<80%)"
    if r < 0.95:
        return "Hampir pulih (80–95%)"
    if r <= 1.05:
        return "Pulih (95–105%)"
    return "Melampaui kondisi awal (>105%)"
k["kategori_pemulihan"] = k["ntl_pemulihan"].map(kategori)

kolom_kec = ["kode_kec", "kecamatan", "kode_bps", "kode_kab_dagri", "kab_kota", "kode_prov",
             "provinsi", "status", "luas_km2",
             "hujan_total", "hujan_maks",
             "ntl_T0", "ntl_T1ref", "ntl_T1", "ntl_T2", "ntl_terukur", "ntl_penurunan", "ntl_pemulihan",
             "kategori_pemulihan", "cahaya_hilang",
             "ndvi_T0", "ndvi_T1ref", "ndvi_T1", "ndvi_T2", "ndvi_andal", "dndvi_dampak", "dndvi_pemulihan",
             "ntl_T0_count", "ndvi_T0_count"]
k[kolom_kec].to_csv(PROC / "kecamatan_indikator.csv", index=False)

# ---------------------------------------------------------------- 3. Agregasi ke kab/kota
def agregat(df):
    a = df["luas_km2"]
    s0, s2 = (df["ntl_T0"] * a).sum(), (df["ntl_T2"] * a).sum()
    ok = df[df["ntl_T1ref"].notna()]          # kecamatan dengan data pembanding musiman
    s1, s1r = (ok["ntl_T1"] * ok["luas_km2"]).sum(), (ok["ntl_T1ref"] * ok["luas_km2"]).sum()
    nd = df[df["ndvi_T0"].notna() & df["ndvi_T1ref"].notna() & df["ndvi_T1"].notna()]
    terukur = df[df["ntl_terukur"]]
    return pd.Series({
        "n_kecamatan": len(df),
        "luas_km2": a.sum(),
        "hujan_total": np.average(df["hujan_total"], weights=a),
        # NTL: dari total cahaya kab/kota (lebih stabil daripada rata-rata rasio)
        "ntl_penurunan": (s1 - s1r) / s1r,
        "ntl_pemulihan": s2 / s0,
        "pct_kec_turun_besar": (terukur["ntl_penurunan"] <= AMBANG_TURUN).mean() * 100
                               if len(terukur) else np.nan,
        # NDVI: rata-rata tertimbang luas
        "dndvi_dampak": np.average(nd["dndvi_dampak"], weights=nd["luas_km2"]),
        "dndvi_pemulihan": np.average(nd["dndvi_pemulihan"], weights=nd["luas_km2"]),
    })

kab_rs = k.groupby(["kode_bps", "status"]).apply(agregat, include_groups=False).reset_index()
kab = bps.merge(kab_rs, on="kode_bps", how="inner", validate="one_to_one")
assert len(kab) == 52, f"Jumlah kab/kota setelah penggabungan: {len(kab)}"
kab.to_csv(PROC / "kabkota_gabungan.csv", index=False)

print("Kecamatan:", len(k), "| NTL terukur:", int(k["ntl_terukur"].sum()),
      "| NDVI andal:", int(k["ndvi_andal"].sum()))
print("Kab/kota tergabung:", len(kab))
