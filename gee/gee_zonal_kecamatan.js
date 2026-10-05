// =====================================================================
// UAS Visualisasi Data – Pemulihan Pascabanjir Sumatera (versi ringkas)
// Zonal statistics per kecamatan (674 unit):
//   - NTL VIIRS bulanan (T0, T1, T2)
//   - NDVI MODIS MOD13Q1 (T0, T1, T2)
//   - Curah hujan CHIRPS (pemicu, 23–28 Nov 2025)
// Output: 1 file CSV di Google Drive
// =====================================================================

// ---------- 0. Wilayah & periode ----------
var kec = ee.FeatureCollection('projects/teknologi-big-data-494100/assets/kecamatan_terdampak');
var roi = kec.geometry().bounds();

var P = {
  T0: ['2025-06-01', '2025-11-01'],  // sebelum bencana (Jun–Okt 2025)
  T1: ['2025-12-01', '2026-02-01'],  // dampak (Des 2025–Jan 2026)
  T2: ['2026-07-01', '2026-10-01']   // pemulihan (Jul–Sep 2026)
};
var HUJAN = ['2025-11-23', '2025-11-29'];  // 23–28 Nov 2025 (tanggal akhir eksklusif)

// Gambar kosong (ter-mask) sebagai cadangan jika suatu periode tidak punya citra
function kosong(nama) {
  return ee.Image.constant(0).updateMask(0).rename(nama).toFloat();
}

// ---------- 1. NTL VIIRS bulanan ----------
var viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').filterBounds(roi);
print('VIIRS: bulan terakhir yang tersedia',
      ee.Date(viirs.aggregate_max('system:time_start')).format('YYYY-MM'));

function ntl(periode, kode) {
  var col = viirs.filterDate(periode[0], periode[1]).map(function (img) {
    var rad = img.select('avg_rad').max(0);              // buang radiance negatif (noise)
    return rad.updateMask(img.select('cf_cvg').gt(0));   // hanya piksel dengan observasi bebas awan
  });
  print('Jumlah citra VIIRS ' + kode + ':', col.size());
  var nama = 'ntl_' + kode;
  return ee.Image(ee.Algorithms.If(col.size().gt(0),
                                   col.mean().rename(nama).toFloat(),
                                   kosong(nama)));
}

// ---------- 2. NDVI MODIS (MOD13Q1, 250 m, komposit 16 hari) ----------
var modis = ee.ImageCollection('MODIS/061/MOD13Q1').filterBounds(roi);
print('MODIS: tanggal terakhir yang tersedia',
      ee.Date(modis.aggregate_max('system:time_start')).format('YYYY-MM-dd'));

function ndvi(periode, kode) {
  var col = modis.filterDate(periode[0], periode[1]).map(function (img) {
    var qa = img.select('SummaryQA');                     // 0 = baik, 1 = marginal
    return img.select('NDVI').multiply(0.0001).updateMask(qa.lte(1));
  });
  print('Jumlah citra MODIS ' + kode + ':', col.size());
  var nama = 'ndvi_' + kode;
  return ee.Image(ee.Algorithms.If(col.size().gt(0),
                                   col.median().rename(nama).toFloat(),
                                   kosong(nama)));
}

// ---------- 3. Curah hujan CHIRPS ----------
var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filterDate(HUJAN[0], HUJAN[1]);
print('Jumlah hari CHIRPS (harus 6):', chirps.size());
var hujanTotal = chirps.sum().rename('hujan_total').toFloat();  // mm, akumulasi 6 hari
var hujanMaks  = chirps.max().rename('hujan_maks').toFloat();   // mm, hujan harian tertinggi

// ---------- 4. Gabungkan semua band ----------
// T1ref = musim yang sama setahun sebelum bencana (Des 2024–Jan 2025),
// pembanding untuk T1 agar efek musim hujan tidak terbaca sebagai dampak bencana
var stack = ee.Image.cat([
  ntl(P.T0, 'T0'), ntl(P.T1, 'T1'), ntl(P.T2, 'T2'),
  ntl(['2024-12-01', '2025-02-01'], 'T1ref'),
  ndvi(P.T0, 'T0'), ndvi(P.T1, 'T1'), ndvi(P.T2, 'T2'),
  ndvi(['2024-12-01', '2025-02-01'], 'T1ref'),
  hujanTotal, hujanMaks
]);
print('Band yang dihitung:', stack.bandNames());

// ---------- 5. Zonal statistics per kecamatan ----------
// mean = nilai rata-rata; count = jumlah piksel valid (untuk kontrol kualitas)
var stats = stack.reduceRegions({
  collection: kec,
  reducer: ee.Reducer.mean().combine({reducer2: ee.Reducer.count(), sharedInputs: true}),
  scale: 250,
  tileScale: 4
}).map(function (f) { return f.setGeometry(null); });

print('Contoh hasil (3 kecamatan):', stats.limit(3));

// ---------- 6. Ekspor ke Google Drive ----------
Export.table.toDrive({
  collection: stats,
  description: 'zonal_kecamatan_ntl_ndvi_chirps',
  folder: 'GEE_UAS_Visdat',
  fileNamePrefix: 'zonal_kecamatan_ntl_ndvi_chirps',
  fileFormat: 'CSV'
});

// ---------- 7. Tampilan peta untuk pengecekan visual ----------
var visNTL  = {min: 0, max: 15, palette: ['000000', '3b0f70', 'b73779', 'fc8961', 'fcfdbf']};
var visNDVI = {min: 0.2, max: 0.9, palette: ['8c510a', 'f6e8c3', '5ab4ac', '01665e']};

Map.centerObject(kec, 6);
Map.addLayer(stack.select('ntl_T0').clip(kec), visNTL, 'NTL T0 (sebelum)', false);
Map.addLayer(stack.select('ntl_T1').clip(kec), visNTL, 'NTL T1 (dampak)', false);
Map.addLayer(stack.select('ntl_T2').clip(kec), visNTL, 'NTL T2 (pemulihan)', true);
Map.addLayer(stack.select('ndvi_T0').clip(kec), visNDVI, 'NDVI T0', false);
Map.addLayer(stack.select('ndvi_T1').clip(kec), visNDVI, 'NDVI T1', false);
Map.addLayer(hujanTotal.clip(kec), {min: 100, max: 600, palette: ['ffffcc', '41b6c4', '081d58']},
             'Hujan 23–28 Nov 2025 (mm)', false);
Map.addLayer(ee.Image().paint(kec, 0, 0.5), {palette: ['ffffff']}, 'Batas kecamatan');
