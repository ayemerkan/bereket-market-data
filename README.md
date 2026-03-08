# Bereket Market Data 📊

UKON (Ulusal Kırmızı Et Konseyi) web sitesinden haftalık dana ve kuzu kesim fiyatlarını otomatik olarak çeken scraper.

**Bereket Takip** Flutter uygulaması bu verileri kullanmaktadır.

## Nasıl Çalışır?

1. GitHub Actions **6 saatte bir** `scraper.py`'yi çalıştırır
2. Scraper, UKON sitesinden güncel fiyatları çeker
3. Sonuç `data/prices.json` dosyasına kaydedilir
4. Flutter uygulaması bu JSON dosyasını GitHub Pages üzerinden okur

## API Endpoint

```
https://ayemerkan.github.io/bereket-market-data/data/prices.json
```

## Kurulum

### 1. Bu repoyu GitHub'a push edin

```bash
git init
git add .
git commit -m "İlk commit"
git remote add origin https://github.com/ayemerkan/bereket-market-data.git
git branch -M main
git push -u origin main
```

### 2. GitHub Pages'i Aktifleştirin

1. GitHub'da repo sayfasına gidin
2. **Settings** → **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** / **(root)**
5. **Save** butonuna tıklayın

### 3. GitHub Actions İzinlerini Kontrol Edin

1. **Settings** → **Actions** → **General**
2. "Workflow permissions" bölümünde **Read and write permissions** seçin
3. **Save** butonuna tıklayın

### 4. İlk Çalıştırma (Manuel)

1. **Actions** sekmesine gidin
2. "UKON Fiyat Scraper" workflow'unu seçin
3. **Run workflow** butonuna tıklayın

## JSON Formatı

```json
{
  "bulten_tarihi": "12.02.2026",
  "last_update": "2026-03-08T19:00:00Z",
  "source": "UKON",
  "ortalama": { "dana": "606.24", "kuzu": "571.50" },
  "regions": {
    "EGE": { "dana": "607.50", "kuzu": "651.30" },
    "MARMARA": { "dana": "610.00", "kuzu": "698.00" },
    ...
  },
  "history": [ ... ]
}
```

## Lokal Test

```bash
pip install -r requirements.txt
python scraper.py
```
