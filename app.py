"""
Dasbor Pemantauan Pemulihan Pascabencana Banjir Bandang Sumatera 2025
Analisis dampak dan pemulihan 674 kecamatan di Aceh, Sumatera Utara, dan Sumatera Barat
UAS Visualisasi Data dan Informasi – Politeknik Statistika STIS
"""
import base64
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ============================================================== Identitas (ISI DI SINI)
IDENTITAS = {
    "nama": "BURHANUDIN ALFADLIL PRASTYO",
    "nim": "222313022",
    "kelas": "3SD2",
    "email": "222313022@stis.ac.id",
}

st.set_page_config(page_title="Pemulihan Pascabencana Banjir Bandang Sumatera 2025", page_icon="🌙",
                   layout="wide", initial_sidebar_state="collapsed")

ROOT = Path(__file__).parent
DATA = ROOT / "data"
LOGO = ROOT / "assets/logo_stis.png"

# ============================================================== Palet (aman buta warna)
TINTA, ABU, GARIS, LATAR = "#1B2A35", "#5C6B75", "#E1E6EA", "#F4F6F8"
UNGU, ORANYE = "#5E3C99", "#E66101"
WARNA_STATUS = {
    "Belum pulih (<80%)": "#E66101",
    "Hampir pulih (80–95%)": "#FDB863",
    "Pulih (95–105%)": "#B2ABD2",
    "Melampaui kondisi awal (>105%)": "#5E3C99",
    "Terlalu gelap untuk diukur": "#CDD3D8",
}
WARNA_KLASTER = {1: "#D55E00", 2: "#E69F00", 3: "#009E73", 4: "#0072B2"}
NAMA_KLASTER = {1: "Pedalaman & kepulauan tertinggal", 2: "Episentrum Aceh",
                3: "Kabupaten menengah Sumut–Sumbar", 4: "Perkotaan"}
LABEL = {
    "p0": "Penduduk miskin (%)", "p1": "Kedalaman kemiskinan (P1)", "ipm": "IPM",
    "rls": "Rata-rata lama sekolah (th)", "uhh": "Umur harapan hidup (th)",
    "pengeluaran_perkapita": "Pengeluaran/kapita (ribu Rp)", "tpt": "Pengangguran terbuka (%)",
    "pdrb_perkapita": "PDRB/kapita ADHB (ribu Rp)", "kepadatan_penduduk": "Kepadatan (jiwa/km²)",
    "ntl_penurunan": "Perubahan cahaya saat bencana", "ntl_pemulihan": "Rasio pemulihan cahaya",
    "dndvi_dampak": "ΔNDVI saat bencana", "dndvi_pemulihan": "ΔNDVI setelah 8 bulan",
}
SUMBER_BPS = "Sumber: BPS, indikator kab/kota 2024 (diolah)."
SUMBER_CITRA = "Sumber: BPS (kode wilayah); BIG (batas kecamatan); NOAA VIIRS, NASA MODIS, CHIRPS via Google Earth Engine (diolah)."
FONT = "Plus Jakarta Sans, Segoe UI, sans-serif"

pio.templates["jejak"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, color=TINTA, size=12),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=8, b=8),
    hoverlabel=dict(font=dict(family=FONT, size=12), bgcolor="white", bordercolor=GARIS),
    legend=dict(font=dict(size=11)),
))
pio.templates.default = "plotly_white+jejak"
KONFIG = {"displaylogo": False, "scrollZoom": True,
          "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage"]}

# ============================================================== CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stRadio, button, input {{ font-family: {FONT}; }}
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
.stApp {{ background: {LATAR}; }}
.block-container {{ padding: 0 1.4rem 0.4rem 1.4rem !important; max-width: 100% !important; }}
[data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stAppViewContainer"] {{ padding-top: 0 !important; }}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{ overflow-x: hidden !important; }}
[data-testid="stMainBlockContainer"] > div > div > div:first-child {{ margin-top: 0 !important; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.45rem; }}
[data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}

.kepala {{ display: flex; align-items: center; gap: 0.9rem; background: {TINTA}; color: white;
          padding: 0.8rem 1.4rem 0.6rem 1.4rem; margin: -1rem -1.4rem 0 -1.4rem; }}

/* --- DESKTOP: bilah navigasi menyatu dengan header --- */
@media (min-width: 769px) {{
.st-key-navbar {{ background: {TINTA}; margin: -1.1rem 0 0.7rem 0; padding: 0 0 0.35rem 0; position: relative;
                  box-shadow: 0 0 0 100vmax {TINTA}; clip-path: inset(0 -100vmax -3px -100vmax); }}
.st-key-navbar::after {{ content: ""; position: absolute; left: -100vmax; right: -100vmax; bottom: -3px; height: 3px;
                         background: {UNGU}; }}
.st-key-navbar button[data-variant="segmented_control"], .st-key-navbar button[data-variant="pills"] {{
    background: rgba(255,255,255,0.06); color: #C9D3DA; border-color: rgba(255,255,255,0.2); }}
.st-key-navbar button[data-variant]:hover {{ color: white; border-color: rgba(255,255,255,0.5); }}
.st-key-navbar button[data-variant][data-selected="true"],
.st-key-navbar button[data-variant][data-selected="true"]:focus,
.st-key-navbar button[data-variant][data-selected="true"]:hover {{ background: white !important; color: {TINTA} !important;
    border-color: white !important; box-shadow: none !important; }}
.st-key-navbar button[data-variant][data-selected="true"] p {{ font-weight: 600; }}
.st-key-navbar button p {{ color: inherit; }}
.st-key-navbar [data-baseweb="select"] > div {{ background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); }}
.st-key-navbar [data-baseweb="select"] div, .st-key-navbar [data-baseweb="select"] svg {{ color: white; fill: white; }}
}}

.kepala {{ position: relative; z-index: 1; }}
@media (min-width: 769px) {{ .kepala {{ box-shadow: 0 1.6rem 0 0 {TINTA}; z-index: 0; }}
                             .st-key-navbar {{ z-index: 2; }} }}
.kepala img {{ height: 40px; width: 40px; object-fit: cover; border-radius: 50%; }}
.kepala .judul {{ flex: 1; min-width: 0; }}
.kepala h1 {{ font-size: 1.2rem; font-weight: 700; margin: 0; padding: 0; color: white; line-height: 1.25; }}
.kepala p {{ font-size: 0.76rem; margin: 0.1rem 0 0 0; color: #C9D3DA; }}
.kepala .id {{ text-align: right; font-size: 0.8rem; line-height: 1.35; color: #C9D3DA; white-space: nowrap; }}
.kepala .id b {{ color: white; font-size: 0.9rem; }}

.kartu {{ background: white; border: 1px solid {GARIS}; border-radius: 10px; padding: 0.45rem 0.8rem; height: 100%; }}
.angka {{ font-size: 1.35rem; font-weight: 700; line-height: 1.1; color: {TINTA}; }}
.angka.oranye {{ color: {ORANYE}; }} .angka.ungu {{ color: {UNGU}; }}
.ket {{ font-size: 0.74rem; color: {ABU}; margin-top: 0.15rem; line-height: 1.3; }}

[data-testid="stMarkdownContainer"] p.panel-judul {{ font-weight: 600; font-size: 0.95rem !important; margin: 0.15rem 0 0.15rem 0 !important; }}
[data-testid="stMarkdownContainer"] p.panel-sub, [data-testid="stMarkdownContainer"] div.panel-sub
    {{ font-size: 0.78rem !important; color: {ABU}; margin: 0 0 0.35rem 0 !important; line-height: 1.4; }}
[data-testid="stMarkdownContainer"] p.sumber {{ font-size: 0.68rem !important; color: #8A979F; margin: -0.25rem 0 0.25rem 0; line-height: 1.3; }}
[data-testid="stMarkdownContainer"] div.temuan {{ font-size: 0.82rem; line-height: 1.45; padding-left: 0.8rem;
    border-left: 3px solid {UNGU}; margin: 0.3rem 0; font-size: 0.78rem !important; line-height: 1.38; }}
.st-key-nav_mobile {{ display: none; }}

.kpi {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.4rem; }}

div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {{ background: white; border: 1px solid {GARIS};
      border-radius: 10px; padding: 4px; }}
div[data-testid="stSegmentedControl"] button {{ font-size: 0.85rem; }}
/* --- MOBILE: menu hamburger, identitas disembunyikan, filter di luar header --- */
@media (max-width: 768px) {{
  .block-container {{ padding-left: 0.8rem !important; padding-right: 0.8rem !important; position: relative; }}
  .kepala {{ gap: 0.6rem; padding: 0.8rem 3.6rem 0.7rem 0.8rem; margin: -1rem -0.8rem 0.3rem -0.8rem;
             border-bottom: 3px solid {UNGU}; }}
  .kepala .id {{ display: none; }}
  .kepala img {{ height: 34px; width: 34px; }}
  .kepala h1 {{ font-size: 1rem; }}
  .kepala p {{ font-size: 0.7rem; }}
  .st-key-nav_desktop {{ display: none !important; }}
  .st-key-nav_mobile {{ display: block; position: absolute; top: 0.85rem; right: 0.8rem; z-index: 1000; width: auto !important; }}
  .st-key-nav_mobile button {{ background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.3); color: white; }}
  .st-key-nav_mobile button p, .st-key-nav_mobile button svg {{ color: white; fill: white; }}
  .st-key-navbar {{ margin: 0 0 0.3rem 0; }}
  .modebar-container {{ display: none !important; }}
}}
</style>
""", unsafe_allow_html=True)


def judul_panel(judul, sub=None):
    html = f'<p class="panel-judul">{judul}</p>'
    if sub:
        html += f'<p class="panel-sub">{sub}</p>'
    st.markdown(html, unsafe_allow_html=True)


def sumber(teks):
    st.markdown(f'<p class="sumber">{teks}</p>', unsafe_allow_html=True)


def rp(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================================== Data
@st.cache_data
def muat():
    kec = pd.read_csv(DATA / "processed/kecamatan_indikator.csv",
                      dtype={"kode_kec": str, "kode_bps": str, "kode_kab_dagri": str})
    kab = pd.read_csv(DATA / "processed/kabkota_gabungan.csv", dtype={"kode_bps": str})
    an = DATA / "processed/analisis"
    skor = pd.read_csv(an / "pca_skor.csv", dtype={"kode_bps": str})
    loading = pd.read_csv(an / "pca_loading.csv")
    varians = pd.read_csv(an / "pca_varians.csv")
    heat = pd.read_csv(an / "heatmap_data.csv")
    profil = pd.read_csv(an / "klaster_profil.csv")
    geo = json.loads((DATA / "geo/kecamatan_terdampak_web.geojson").read_text(encoding="utf-8"))
    p_latar = DATA / "geo/latar_kabkota.geojson"
    latar = json.loads(p_latar.read_text(encoding="utf-8")) if p_latar.exists() else None
    try:
        sumber_tbl = pd.read_excel(DATA / "processed/bps_kabkota_2024.xlsx", sheet_name="sumber")
    except Exception:
        sumber_tbl = pd.DataFrame()

    kab = kab.merge(skor[["kode_bps", "klaster", "PC1", "PC2", "PC3"]], on="kode_bps")
    kab["klaster_nama"] = kab["klaster"].map(NAMA_KLASTER)
    kec = kec.merge(kab[["kode_bps", "klaster"]], on="kode_bps", how="left")
    kec["atensi"] = np.where(kec["status"].eq("perlu_atensi_khusus"), "Perlu atensi khusus", "Normal/mendekati normal")

    pusat = {}
    for ft in geo["features"]:
        g = ft["geometry"]
        cincin = g["coordinates"] if g["type"] == "Polygon" else [r for p in g["coordinates"] for r in p]
        xy = np.array([pt for r in cincin for pt in r])
        pusat[ft["properties"]["KDCPUM"]] = (xy[:, 1].mean(), xy[:, 0].mean())
    kec["lat"] = kec["kode_kec"].map(lambda k: pusat.get(k, (np.nan,) * 2)[0])
    kec["lon"] = kec["kode_kec"].map(lambda k: pusat.get(k, (np.nan,) * 2)[1])
    return kec, kab, loading, varians, heat, profil, geo, latar, sumber_tbl


kec, kab, loading, varians, heat, profil, geo, latar, sumber_tbl = muat()


# ============================================================== Peta (tanpa peta dasar dunia)
def peta(df, warna, tinggi, judul_skala="", fokus=None, **kw):
    hover = {"kab_kota": True, "kode_kec": False}
    fig = px.choropleth(df, geojson=geo, locations="kode_kec", featureidkey="properties.KDCPUM",
                        color=warna, hover_name="kecamatan", hover_data=hover, **kw)
    fig.update_traces(marker_line_width=0.25, marker_line_color="white")
    if latar is not None:
        ids = [f["properties"]["KDPKAB"] for f in latar["features"]]
        dasar = go.Choropleth(geojson=latar, locations=ids, featureidkey="properties.KDPKAB",
                              z=[0] * len(ids), colorscale=[[0, "#E7EBEE"], [1, "#E7EBEE"]], showscale=False,
                              marker_line_color="white", marker_line_width=0.8, hoverinfo="skip")
        fig.add_trace(dasar)
        fig.data = (fig.data[-1],) + fig.data[:-1]
    fig.update_geos(visible=False, projection_type="mercator", bgcolor="rgba(0,0,0,0)",
                    fitbounds="locations")
    if fokus is not None:            # perbesar ke wilayah terpilih
        fig.update_geos(fitbounds=False, lataxis_range=fokus[0], lonaxis_range=fokus[1])
    fig.update_layout(height=tinggi, dragmode="pan",
                      legend=dict(orientation="h", yanchor="bottom", y=0.0, x=0.0, bgcolor="rgba(255,255,255,0.85)",
                                  title_text=""),
                      coloraxis_colorbar=dict(title=judul_skala, thickness=10, len=0.55, x=0.98, y=0.5))
    return fig


def rentang(df):
    if df.empty or len(df) == len(kec):
        return None
    pad = 0.25
    return ([df["lat"].min() - pad, df["lat"].max() + pad], [df["lon"].min() - pad, df["lon"].max() + pad])


# ============================================================== Header
logo_html = ""
if LOGO.exists():
    logo_html = f'<img src="data:image/png;base64,{base64.b64encode(LOGO.read_bytes()).decode()}" alt="Logo Politeknik Statistika STIS">'
st.markdown(f"""
<div class="kepala">
  {logo_html}
  <div class="judul">
    <h1>Pemantauan Pemulihan Pascabencana Banjir Bandang Sumatera 2025</h1>
    <p>Analisis dampak dan pemulihan 674 kecamatan di Provinsi Aceh, Sumatera Utara, dan Sumatera Barat
       berbasis citra satelit dan data Badan Pusat Statistik</p>
  </div>
  <div class="id"><b>{IDENTITAS['nama']}</b><br>{IDENTITAS['nim']} · {IDENTITAS['kelas']} · {IDENTITAS['email']}</div>
</div>
""", unsafe_allow_html=True)

# ============================================================== Navigasi + filter (di dalam header)
navbar = st.container(key="navbar")
c_nav, c_prov, c_kab, c_at = navbar.columns([4.6, 1.7, 1.7, 1.4], vertical_alignment="center")
IKON = {"Ringkasan": ":material/dashboard:", "Peta dampak": ":material/map:",
        "Profil kab/kota": ":material/scatter_plot:", "Hierarki": ":material/account_tree:",
        "Tentang": ":material/info:"}
for k in ("hal", "nav_d", "nav_m"):
    st.session_state.setdefault(k, "Ringkasan")


def pilih_desktop():                 # tab desktop dan menu mobile saling disinkronkan
    if st.session_state.nav_d is None:          # klik ulang tab aktif tidak mengosongkan pilihan
        st.session_state.nav_d = st.session_state.hal
    st.session_state.hal = st.session_state.nav_m = st.session_state.nav_d


def pilih_mobile():
    st.session_state.hal = st.session_state.nav_d = st.session_state.nav_m


with c_nav:
    st.container(key="nav_desktop").segmented_control(
        "Halaman", list(IKON), key="nav_d", on_change=pilih_desktop, label_visibility="collapsed",
        format_func=lambda h: f"{IKON[h]} {h}")
with st.container(key="nav_mobile"):
    with st.popover(":material/menu:", help="Menu halaman"):
        st.radio("Halaman", list(IKON), key="nav_m", on_change=pilih_mobile, label_visibility="collapsed",
                 format_func=lambda h: f"{IKON[h]} {h}")
hal = st.session_state.hal
with c_prov:
    semua_prov = ["Aceh", "Sumatera Utara", "Sumatera Barat"]
    singkat = {"Aceh": "Aceh", "Sumatera Utara": "Sumut", "Sumatera Barat": "Sumbar"}
    prov = st.pills("Provinsi", semua_prov, selection_mode="multi", default=semua_prov, format_func=singkat.get,
                    label_visibility="collapsed") or semua_prov
with c_kab:
    opsi_kab = ["Semua kab/kota"] + sorted(kec.loc[kec["provinsi"].isin(prov), "kab_kota"].unique())
    kab_fokus = st.selectbox("Kab/kota", opsi_kab, label_visibility="collapsed")
with c_at:
    hanya_atensi = st.pills("Prioritas", ["Hanya kab/kota prioritas"], label_visibility="collapsed",
                            help="11 kab/kota yang per Februari 2026 masih berstatus perlu atensi khusus") is not None

m = kec["provinsi"].isin(prov)
if kab_fokus != "Semua kab/kota":
    m &= kec["kab_kota"].eq(kab_fokus)
if hanya_atensi:
    m &= kec["status"].eq("perlu_atensi_khusus")
kf = kec[m]
fokus = rentang(kf)
TINGGI = 400

# ============================================================== Halaman 1: Ringkasan
if hal == "Ringkasan":
    terukur = kf[kf["ntl_terukur"]]
    n_ukur = len(terukur)
    pulih = (terukur["ntl_pemulihan"] >= 0.95).mean() * 100 if n_ukur else np.nan
    belum = int((terukur["ntl_pemulihan"] < 0.80).sum())
    kb = kab[kab["kode_bps"].isin(kf["kode_bps"].unique())]
    med_at = kb.loc[kb["status"].eq("perlu_atensi_khusus"), "ntl_penurunan"].median()
    med_lain = kb.loc[~kb["status"].eq("perlu_atensi_khusus"), "ntl_penurunan"].median()

    def fmt(x, kali=100, d=1, s="%"):
        return "–" if pd.isna(x) else f"{rp(x * kali, d)}{s}"

    kiri, kanan = st.columns([1.05, 1])
    with kiri:
        judul_panel("Status pemulihan cahaya malam per kecamatan",
                    "Cahaya Juli–Agustus 2026 dibanding Juni–Oktober 2025. Seret untuk menggeser, gulir untuk memperbesar.")
        fig = peta(kf, "kategori_pemulihan", TINGGI + 15, fokus=fokus,
                   color_discrete_map=WARNA_STATUS, category_orders={"kategori_pemulihan": list(WARNA_STATUS)},
                   labels={"kategori_pemulihan": "Status", "kab_kota": "Kab/kota"})
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber(SUMBER_CITRA)
    with kanan:
        kartu = [
            (f"{len(kf)}", "", f"kecamatan ditampilkan; {n_ukur} cukup terang untuk diukur dengan cahaya malam"),
            (fmt(pulih, 1, 0), "ungu", "kecamatan terukur sudah pulih atau melampaui kondisi awal (Jul–Agu 2026)"),
            (f"{belum}", "oranye", "kecamatan cahayanya masih di bawah 80% kondisi sebelum bencana"),
            (fmt(med_at), "oranye", f"perubahan cahaya median kab/kota prioritas saat bencana; wilayah lain {fmt(med_lain)}"),
        ]
        st.markdown('<div class="kpi">' + "".join(
            f'<div class="kartu"><div class="angka {k}">{a}</div><div class="ket">{t}</div></div>' for a, k, t in kartu)
            + "</div>", unsafe_allow_html=True)

        judul_panel("Komposisi status per provinsi")
        hit = kf.groupby(["provinsi", "kategori_pemulihan"]).size().reset_index(name="n")
        fig = px.bar(hit, y="provinsi", x="n", color="kategori_pemulihan", orientation="h",
                     color_discrete_map=WARNA_STATUS, category_orders={"kategori_pemulihan": list(WARNA_STATUS),
                                                                       "provinsi": semua_prov},
                     labels={"n": "Jumlah kecamatan", "provinsi": "", "kategori_pemulihan": "Status"})
        fig.update_layout(height=105, showlegend=False, barmode="stack", xaxis_title=None,
                          margin=dict(l=8, r=8, t=4, b=4))
        st.plotly_chart(fig, width="stretch", config=KONFIG)

        judul_panel("Temuan utama · 52 kab/kota terdampak")
        st.markdown("""
<div class="temuan">Dibanding musim yang sama setahun sebelumnya, cahaya malam di 11 kab/kota prioritas turun
<b>8,8%</b> saat bencana, sementara wilayah lain hanya <b>2,1%</b>. Citra satelit sejalan dengan status resmi pemerintah.</div>
<div class="temuan">Kab/kota yang lebih miskin sebelum bencana kehilangan cahaya lebih banyak
(korelasi Spearman <b>−0,43</b> antara persentase penduduk miskin dan perubahan cahaya).</div>
<div class="temuan">Di beberapa kabupaten Aceh, cahaya kini melampaui kondisi awal, lebih mungkin dari huntara,
posko, dan rekonstruksi daripada ekonomi yang sudah pulih.</div>
""", unsafe_allow_html=True)

# ============================================================== Halaman 2: Peta dampak
elif hal == "Peta dampak":
    LAPISAN = {
        "Perubahan cahaya saat bencana": ("ntl_penurunan", "PuOr", (-0.5, 0.5), "%", 100,
                                          "Des 2025–Jan 2026 dibanding Des 2024–Jan 2025 (musim yang sama)"),
        "Rasio pemulihan cahaya": ("ntl_pemulihan", "PuOr", (0.5, 1.5), "×", 1,
                                   "Jul–Agu 2026 dibanding Jun–Okt 2025; 1 = sama dengan kondisi awal"),
        "ΔNDVI saat bencana": ("dndvi_dampak", "BrBG", (-0.06, 0.06), "ΔNDVI", 1,
                               "Vegetasi Des 2025–Jan 2026 dibanding Des 2024–Jan 2025; negatif = vegetasi hilang"),
        "ΔNDVI setelah 8 bulan": ("dndvi_pemulihan", "BrBG", (-0.06, 0.06), "ΔNDVI", 1,
                                  "Vegetasi Jul–Agu 2026 dibanding Jun–Okt 2025"),
        "Hujan 23–28 Nov 2025": ("hujan_total", "Blues", None, "mm", 1, "Akumulasi curah hujan 6 hari pemicu bencana"),
    }
    kiri, kanan = st.columns([1.55, 1])
    with kiri:
        a, b = st.columns([2, 1.3], vertical_alignment="bottom")
        nama = a.selectbox("Indikator", list(LAPISAN), label_visibility="collapsed")
        simbol = b.toggle("Tampilkan cahaya yang hilang", value=False)
        kol, skala, rng, sat, kali, ket = LAPISAN[nama]
        d = kf.assign(nilai=kf[kol] * kali)
        r = None if rng is None else (rng[0] * kali, rng[1] * kali)
        mid = {"hujan_total": None, "ntl_pemulihan": 1}.get(kol, 0)
        arg = dict(color_continuous_scale=skala, labels={"nilai": sat, "kab_kota": "Kab/kota"})
        if r:
            arg["range_color"] = r
        if mid is not None:
            arg["color_continuous_midpoint"] = mid
        fig = peta(d, "nilai", TINGGI + 5, judul_skala=sat, fokus=fokus, **arg)
        if simbol:
            s = kf[kf["cahaya_hilang"] > 0]
            fig.add_trace(go.Scattergeo(lat=s["lat"], lon=s["lon"], mode="markers",
                                        marker=dict(size=s["cahaya_hilang"], sizemode="area",
                                                    sizeref=2 * kec["cahaya_hilang"].max() / 28 ** 2, sizemin=2,
                                                    color="rgba(230,97,1,0.55)", line=dict(color="white", width=0.6)),
                                        text=s["kecamatan"] + ", " + s["kab_kota"],
                                        hovertemplate="<b>%{text}</b><br>Cahaya hilang: %{marker.size:.1f}<extra></extra>",
                                        showlegend=False))
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber(ket + ". Kecamatan tanpa warna terlalu gelap untuk diukur. " + SUMBER_CITRA)

    with kanan:
        judul_panel(f"Kecamatan dengan nilai terendah: {nama.lower()}",
                    "Hanya kecamatan dengan data yang andal")
        d = kf.dropna(subset=[kol])
        if kol.startswith("dndvi"):
            d = d[d["ndvi_andal"]]
        top = d.nsmallest(12, kol) if kol != "hujan_total" else d.nlargest(12, kol)
        top = top.assign(label=top["kecamatan"] + " · " + top["kab_kota"], nilai=top[kol] * kali)
        fig = px.bar(top.iloc[::-1], x="nilai", y="label", orientation="h", color="atensi",
                     color_discrete_map={"Perlu atensi khusus": ORANYE, "Normal/mendekati normal": "#9AA6AE"},
                     labels={"nilai": sat, "label": "", "atensi": ""})
        fig.update_layout(height=TINGGI - 15, legend=dict(orientation="h", y=-0.14, x=0),
                          yaxis=dict(tickfont=dict(size=11), categoryorder="array",
                                     categoryarray=list(top["label"].iloc[::-1])))
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber(("Untuk hujan, ditampilkan 12 kecamatan tertinggi. " if kol == "hujan_total" else "") + SUMBER_CITRA)

# ============================================================== Halaman 3: Profil kab/kota
elif hal == "Profil kab/kota":
    v = varians.set_index("pc")["proporsi"]
    H = 154
    PENDEK = {"p0": "P0", "p1": "P1", "ipm": "IPM", "rls": "RLS", "uhh": "UHH",
              "pengeluaran_perkapita": "Pengeluaran", "tpt": "TPT", "pdrb_perkapita": "PDRB/kap",
              "kepadatan_penduduk": "Kepadatan", "ntl_penurunan": "ΔCahaya", "ntl_pemulihan": "Pulih cahaya",
              "dndvi_dampak": "ΔNDVI", "dndvi_pemulihan": "ΔNDVI 8 bln"}
    a, b = st.columns([1.25, 1])
    with a:
        judul_panel("Peta posisi 52 kab/kota (PCA)",
                    "Klik, atau seret kotak/laso untuk memilih kab/kota. Pilihan disorot di semua grafik.")
        d = kab.assign(kl=kab["klaster"].map(lambda k: f"{k} · {NAMA_KLASTER[k]}"))
        fig = px.scatter(d, x="PC1", y="PC2", color="kl", custom_data=["kab_kota"], hover_name="kab_kota",
                         color_discrete_map={f"{k} · {n}": WARNA_KLASTER[k] for k, n in NAMA_KLASTER.items()},
                         symbol="status", symbol_map={"perlu_atensi_khusus": "diamond",
                                                      "normal_atau_mendekati_normal": "circle"},
                         hover_data={"kl": False, "status": False, "PC1": ":.2f", "PC2": ":.2f"},
                         labels={"PC1": f"PC1 · pembangunan & urbanisasi ({v['PC1']:.0%})",
                                 "PC2": f"PC2 · kemiskinan & kerusakan vegetasi ({v['PC2']:.0%})"})
        fig.update_traces(marker=dict(size=10, line=dict(width=0.8, color="white")))
        for _, r in loading.iterrows():
            fig.add_annotation(x=r["PC1"] * 4.4, y=r["PC2"] * 4.4, ax=0, ay=0, xref="x", yref="y", axref="x",
                               ayref="y", showarrow=True, arrowhead=2, arrowwidth=1, arrowcolor="#A3AEB5")
            fig.add_annotation(x=r["PC1"] * 4.9, y=r["PC2"] * 4.9, showarrow=False, text=PENDEK[r["variabel"]],
                               font=dict(size=9, color=ABU))
        fig.update_layout(height=H, dragmode="lasso", showlegend=False,
                          xaxis=dict(title_font_size=11), yaxis=dict(title_font_size=11))
        ev = st.plotly_chart(fig, width="stretch", key="pca", on_select="rerun",
                             selection_mode=("points", "box", "lasso"),
                             config={"displaylogo": False, "modeBarButtonsToRemove": ["toImage"]})
        sumber("Panah = arah variabel; wajik = kab/kota prioritas. " + SUMBER_BPS + " Indikator citra: VIIRS, MODIS.")
    pilih = [p["customdata"][0] for p in (ev.selection.points if ev and ev.selection else [])]

    with b:
        judul_panel("Peta klaster" if not pilih else f"{len(pilih)} kab/kota dipilih",
                    " · ".join(f'<span style="color:{WARNA_KLASTER[k]}">■</span> {n}' for k, n in NAMA_KLASTER.items()))
        d = kec.copy()
        if pilih:
            d["w"] = np.where(d["kab_kota"].isin(pilih), "Dipilih", "Lainnya")
            fig = peta(d, "w", H, color_discrete_map={"Dipilih": UNGU, "Lainnya": "#D9DEE2"})
        else:
            d["w"] = d["klaster"].astype(int).map(lambda k: f"{k}")
            fig = peta(d, "w", H, color_discrete_map={str(k): c for k, c in WARNA_KLASTER.items()},
                       category_orders={"w": ["1", "2", "3", "4"]})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber(SUMBER_CITRA)

    c, e = st.columns([1.25, 1])
    VAR = ["p0", "p1", "ipm", "rls", "uhh", "pengeluaran_perkapita", "tpt", "pdrb_perkapita",
           "kepadatan_penduduk", "ntl_penurunan", "ntl_pemulihan", "dndvi_dampak", "dndvi_pemulihan"]
    with c:
        judul_panel("Profil 13 variabel", "Satu garis = satu kab/kota. Seret di sumbu untuk menyaring. "
                    "P0 = % miskin, P1 = kedalaman kemiskinan, Δ = perubahan saat bencana.")
        if pilih:
            warna, skala, cr = kab["kab_kota"].isin(pilih).astype(int), [[0, "#DDE2E6"], [1, UNGU]], (0, 1)
        else:
            warna, cr = kab["klaster"], (1, 4)
            skala = [[0, WARNA_KLASTER[1]], [1 / 3, WARNA_KLASTER[2]], [2 / 3, WARNA_KLASTER[3]], [1, WARNA_KLASTER[4]]]
        fig = go.Figure(go.Parcoords(
            line=dict(color=warna, colorscale=skala, cmin=cr[0], cmax=cr[1]),
            labelfont=dict(size=10), tickfont=dict(size=9), rangefont=dict(size=8),
            dimensions=[dict(label=PENDEK[x], values=kab[x]) for x in VAR]))
        fig.update_layout(height=H, margin=dict(l=40, r=40, t=48, b=12))
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber(SUMBER_BPS)
    with e:
        judul_panel("Pola kab/kota × variabel", "z-score, diurutkan dengan klaster hierarki. Kotak hitam = kab/kota dipilih.")
        mat = heat.set_index("kab_kota").drop(columns="klaster")
        mat.columns = [PENDEK[x] for x in mat.columns]
        fig = px.imshow(mat, color_continuous_scale="PuOr_r", zmin=-3, zmax=3, aspect="auto")
        fig.update_layout(height=H, coloraxis_colorbar=dict(thickness=8, len=0.8, title="z"),
                          xaxis=dict(tickfont=dict(size=8), tickangle=-35, title=None),
                          yaxis=dict(tickfont=dict(size=7), title=None))
        for i, n in enumerate(mat.index):
            if n in pilih:
                fig.add_shape(type="rect", x0=-0.5, x1=len(mat.columns) - 0.5, y0=i - 0.5, y1=i + 0.5,
                              line=dict(color="#111", width=1.5))
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber("PDRB/kapita dan kepadatan ditransformasi log. " + SUMBER_BPS)

# ============================================================== Halaman 4: Struktur wilayah
elif hal == "Hierarki":
    PIL = {"ΔNDVI saat bencana": ("dndvi_dampak", "BrBG", 0.06),
           "ΔNDVI setelah 8 bulan": ("dndvi_pemulihan", "BrBG", 0.06),
           "Hujan 23–28 Nov 2025 (mm)": ("hujan_total", "Blues", None)}
    a, b = st.columns([1.2, 3], vertical_alignment="center")
    nama = a.selectbox("Warna", list(PIL), label_visibility="collapsed")
    b.markdown(f'<p class="panel-sub">Provinsi → kab/kota → kecamatan. <b>Ukuran</b> = luas wilayah, '
               f'<b>warna</b> = {nama}. Klik kotak atau irisan untuk masuk ke level berikutnya; '
               f'klik jalur di atas treemap atau pusat sunburst untuk kembali.</p>', unsafe_allow_html=True)
    kol, skala, batas = PIL[nama]
    d = kf.dropna(subset=[kol])
    arg = dict(path=[px.Constant("3 provinsi"), "provinsi", "kab_kota", "kecamatan"], values="luas_km2",
               color=kol, color_continuous_scale=skala,
               hover_data={kol: ":.3f", "luas_km2": ":,.0f"}, labels={kol: nama, "luas_km2": "Luas (km²)"})
    if batas:
        arg.update(range_color=(-batas, batas), color_continuous_midpoint=0)
    kiri, kanan = st.columns([1.5, 1])
    with kiri:
        fig = px.treemap(d, maxdepth=3, **arg)
        fig.update_traces(pathbar_visible=True, root_color=LATAR, marker_line_width=0.5)
        fig.update_layout(height=TINGGI + 2, margin=dict(l=4, r=4, t=28, b=4),
                          coloraxis_colorbar=dict(thickness=10, title=""))
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber("Warna kab/kota dan provinsi = rata-rata tertimbang luas. " + SUMBER_CITRA)
    with kanan:
        fig = px.sunburst(d, maxdepth=3, **arg)
        fig.update_layout(height=TINGGI + 2, margin=dict(l=4, r=4, t=4, b=4), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch", config=KONFIG)
        sumber(SUMBER_CITRA)

# ============================================================== Halaman 5: Tentang data
else:
    TINGGI_KOTAK = TINGGI + 25
    a, b = st.columns(2)
    with a.container(border=True, height=TINGGI_KOTAK):
        judul_panel("Sumber data BPS", "Data utama: indikator kab/kota 2024 untuk 52 kab/kota terdampak")
        if len(sumber_tbl):
            tbl = sumber_tbl.copy()
            tbl.columns = [str(c).strip().lower() for c in tbl.columns]
            kol = [c for c in ["variabel", "judul_tabel", "judul", "provinsi", "tahun_data", "url"] if c in tbl.columns]
            st.dataframe(tbl[kol], width="stretch", hide_index=True, height=225,
                         column_config={"url": st.column_config.LinkColumn("Tautan", display_text="Buka"),
                                        "variabel": "Variabel", "judul_tabel": "Judul tabel", "judul": "Judul tabel",
                                        "provinsi": "Provinsi", "tahun_data": st.column_config.NumberColumn("Tahun", format="%d")})
        judul_panel("Data pendukung")
        st.markdown("""
<div class="panel-sub">
<b>Cahaya malam</b>: NOAA VIIRS DNB bulanan (VCMSLCFG), ±500 m<br>
<b>Vegetasi</b>: NASA MODIS MOD13Q1 NDVI, 250 m<br>
<b>Curah hujan</b>: CHIRPS harian, ±5,5 km<br>
<b>Batas kecamatan</b>: BIG edisi Juli 2026; kode Kemendagri dicocokkan dengan kode BPS
</div>""", unsafe_allow_html=True)
    with b.container(border=True, height=TINGGI_KOTAK):
        judul_panel("Periode pengamatan citra")
        st.markdown("""
<div class="panel-sub">
<b>Sebelum bencana</b>: Juni–Oktober 2025 &nbsp;·&nbsp; <b>Pembanding musiman</b>: Desember 2024–Januari 2025<br>
<b>Saat bencana</b>: Desember 2025–Januari 2026 &nbsp;·&nbsp; <b>Pemulihan</b>: Juli–Agustus 2026
</div>""", unsafe_allow_html=True)
        judul_panel("Keterbatasan")
        st.markdown("""
<div class="temuan">Cahaya malam mengukur aktivitas, bukan kesejahteraan: lampu bisa menyala karena huntara,
posko, atau proyek rekonstruksi.</div>
<div class="temuan">348 kecamatan terlalu gelap (radiance &lt; 0,5 nW/cm²/sr) sehingga rasio cahayanya tidak dihitung.</div>
<div class="temuan">Perubahan cahaya juga dipengaruhi pertumbuhan perkotaan dari tahun ke tahun.</div>
<div class="temuan">MODIS 250 m terlalu kasar untuk longsor kecil; data BPS hanya tersedia di tingkat kab/kota.</div>
""", unsafe_allow_html=True)
        judul_panel("Proyek")
        st.markdown('<div class="panel-sub">UAS Visualisasi Data dan Informasi, Politeknik Statistika STIS, 2026. '
                    'Kode dan data olahan tersedia di repositori GitHub proyek ini.</div>', unsafe_allow_html=True)