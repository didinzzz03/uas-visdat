"""
Analisis multivariat 52 kab/kota terdampak – UAS Visualisasi Data

Input  : data/processed/kabkota_gabungan.csv
Output : data/processed/analisis/
           pca_skor.csv          skor PC1–PC3 + klaster per kab/kota
           pca_loading.csv       kontribusi tiap variabel ke PC
           pca_varians.csv       proporsi varians tiap PC
           klaster_profil.csv    rata-rata (z-score) dan median (asli) per klaster
           heatmap_data.csv      matriks z-score, sudah diurutkan hasil klaster hierarki
           korelasi_spearman.csv korelasi BPS × indikator citra (+ p-value)
           pencilan.csv          kab/kota dengan nilai ekstrem
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

PROC = Path("data/processed")
OUT = PROC / "analisis"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 42

# ---------------------------------------------------------------- 1. Data & variabel
kab = pd.read_csv(PROC / "kabkota_gabungan.csv", dtype={"kode_bps": str})

VAR_BPS = ["p0", "p1", "ipm", "rls", "uhh", "pengeluaran_perkapita", "tpt",
           "pdrb_perkapita", "kepadatan_penduduk"]
VAR_CITRA = ["ntl_penurunan", "ntl_pemulihan", "dndvi_dampak", "dndvi_pemulihan"]
VARS = VAR_BPS + VAR_CITRA          # 13 variabel numerik

X = kab[VARS].copy()
# Transformasi log untuk variabel yang sangat miring
X["pdrb_perkapita"] = np.log(X["pdrb_perkapita"])
X["kepadatan_penduduk"] = np.log(X["kepadatan_penduduk"])
assert X.notna().all().all(), "Masih ada nilai kosong di variabel analisis"

Z = pd.DataFrame(StandardScaler().fit_transform(X), columns=VARS, index=kab.index)

# ---------------------------------------------------------------- 2. PCA
pca = PCA(random_state=SEED).fit(Z)
skor = pca.transform(Z)

varians = pd.DataFrame({
    "pc": [f"PC{i+1}" for i in range(len(VARS))],
    "proporsi": pca.explained_variance_ratio_,
    "kumulatif": np.cumsum(pca.explained_variance_ratio_),
})
varians.to_csv(OUT / "pca_varians.csv", index=False)

loading = pd.DataFrame(pca.components_[:3].T, index=VARS, columns=["PC1", "PC2", "PC3"])
loading.index.name = "variabel"
loading.to_csv(OUT / "pca_loading.csv")

# ---------------------------------------------------------------- 3. K-means
sil = {}
for k in range(2, 7):
    lab = KMeans(n_clusters=k, n_init=50, random_state=SEED).fit_predict(Z)
    sil[k] = silhouette_score(Z, lab)
# Pilih k terbaik di rentang 3–5 agar klaster tetap mudah ditafsirkan
k_best = max(range(3, 6), key=lambda k: sil[k])
km = KMeans(n_clusters=k_best, n_init=50, random_state=SEED).fit(Z)

# Urutkan nomor klaster berdasarkan rata-rata penurunan NTL (klaster 1 = paling terdampak)
urut = (pd.Series(km.labels_).groupby(km.labels_)
        .apply(lambda idx: Z.loc[idx.index, "ntl_penurunan"].mean())
        .sort_values().index)
peta_label = {lama: baru + 1 for baru, lama in enumerate(urut)}
kab["klaster"] = pd.Series(km.labels_).map(peta_label).values

hasil = kab[["kode_bps", "kab_kota", "provinsi", "status", "klaster"]].copy()
for i in range(3):
    hasil[f"PC{i+1}"] = skor[:, i]
hasil.to_csv(OUT / "pca_skor.csv", index=False)

# Profil klaster
prof_z = Z.groupby(kab["klaster"]).mean().round(3)
prof_z.columns = [f"z_{c}" for c in prof_z.columns]
prof_asli = kab.groupby("klaster")[VARS].median().round(3)
prof_asli.columns = [f"median_{c}" for c in prof_asli.columns]
profil = pd.concat([kab.groupby("klaster").size().rename("n"),
                    kab.groupby("klaster")["status"].apply(
                        lambda s: (s == "perlu_atensi_khusus").sum()).rename("n_atensi_khusus"),
                    prof_z, prof_asli], axis=1)
profil.to_csv(OUT / "klaster_profil.csv")

# ---------------------------------------------------------------- 4. Heatmap terklaster
baris = leaves_list(linkage(Z, method="ward"))
kolom = leaves_list(linkage(Z.T, method="ward"))
heat = Z.iloc[baris, kolom].copy()
heat.insert(0, "kab_kota", kab.loc[heat.index, "kab_kota"].values)
heat.insert(1, "klaster", kab.loc[heat.index, "klaster"].values)
heat.to_csv(OUT / "heatmap_data.csv", index=False)

# ---------------------------------------------------------------- 5. Korelasi BPS × citra
rows = []
for b in VAR_BPS:
    for c in VAR_CITRA:
        rho, p = spearmanr(kab[b], kab[c])
        rows.append({"var_bps": b, "var_citra": c, "rho": round(rho, 3), "p_value": round(p, 4)})
korelasi = pd.DataFrame(rows)
korelasi.to_csv(OUT / "korelasi_spearman.csv", index=False)

# ---------------------------------------------------------------- 6. Pencilan
# Jarak dari pusat data di ruang z-score (setara Mahalanobis untuk data terstandar tanpa korelasi)
jarak = np.sqrt((Z ** 2).sum(axis=1))
ambang = jarak.mean() + 2 * jarak.std()
penc = kab.loc[jarak > ambang, ["kab_kota", "provinsi", "klaster"]].copy()
penc["jarak"] = jarak[jarak > ambang].round(2)
penc["variabel_ekstrem"] = [
    ", ".join(f"{v} ({Z.loc[i, v]:+.1f})" for v in Z.columns[Z.loc[i].abs() > 2])
    for i in penc.index
]
penc.sort_values("jarak", ascending=False).to_csv(OUT / "pencilan.csv", index=False)

# ---------------------------------------------------------------- 7. Ringkasan di terminal
atensi = kab["status"] == "perlu_atensi_khusus"
uji = mannwhitneyu(kab.loc[atensi, "ntl_penurunan"], kab.loc[~atensi, "ntl_penurunan"])

print(f"PCA: PC1 {varians.proporsi[0]:.1%}, PC2 {varians.proporsi[1]:.1%}, "
      f"PC3 {varians.proporsi[2]:.1%} (kumulatif {varians.kumulatif[2]:.1%})")
print("Silhouette:", {k: round(v, 3) for k, v in sil.items()}, "→ k =", k_best)
print("Anggota klaster:", kab["klaster"].value_counts().sort_index().to_dict())
print(f"Mann-Whitney penurunan NTL (atensi khusus vs lainnya): p = {uji.pvalue:.4f}")
print("Pencilan:", ", ".join(penc["kab_kota"]) if len(penc) else "tidak ada")
print("Output tersimpan di", OUT)
