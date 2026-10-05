"""
Membuat lapisan latar peta: batas kab/kota di Aceh, Sumatera Utara, dan Sumatera Barat.

Pemakaian (dari folder utama project):
    pip install geopandas
    python scripts/buat_latar.py "D:/lokasi/BATAS_KECAMATAN_AR_EDISI_JULI_2026.shp"

Output: data/geo/latar_kabkota.geojson (±1–2 MB)
"""
import sys
from pathlib import Path

import geopandas as gpd

sumber = sys.argv[1] if len(sys.argv) > 1 else "BATAS_KECAMATAN_AR_EDISI_JULI_2026.shp"
keluar = Path("data/geo/latar_kabkota.geojson")

g = gpd.read_file(sumber)
g = g[(g["TIPADM"] == 3) & (g["KDPPUM"].isin(["11", "12", "13"]))]
print("Kecamatan di 3 provinsi:", len(g))

kab = g.dissolve(by="KDPKAB", as_index=False)[["KDPKAB", "WADMKK", "WADMPR", "geometry"]]
kab["geometry"] = kab.geometry.force_2d().make_valid().simplify(0.003, preserve_topology=True)
kab.to_file(keluar, driver="GeoJSON")
print("Kab/kota:", len(kab), "→", keluar, f"({keluar.stat().st_size / 1e6:.1f} MB)")
