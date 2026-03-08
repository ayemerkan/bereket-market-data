"""
Bereket Takip - UKON Fiyat Scraper
===================================
UKON (Ulusal Kırmızı Et Konseyi) web sitesinden
haftalık dana ve kuzu kesim fiyatlarını çeker.

GitHub Actions ile 6 saatte bir çalıştırılır.
Sonuç data/prices.json dosyasına kaydedilir.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

UKON_URL = "http://www.ukon.org.tr/fiyatlar"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "prices.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}


def scrape_ukon():
    """UKON sitesinden fiyat verilerini çeker."""
    print(f"🌐 UKON'dan veri çekiliyor: {UKON_URL}")

    response = requests.get(UKON_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"

    print(f"✅ HTTP {response.status_code} - {len(response.content)} byte alındı")

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Bülten tarihini bul
    bulten_tarihi = ""
    for h3 in soup.find_all("h3"):
        match = re.search(r"(\d{2}\.\d{2}\.\d{4})", h3.get_text())
        if match:
            bulten_tarihi = match.group(1)
            print(f"📅 Bülten tarihi: {bulten_tarihi}")
            break

    if not bulten_tarihi:
        # Body'de ara
        body_text = soup.body.get_text() if soup.body else ""
        match = re.search(r"(\d{2}\.\d{2}\.\d{4})", body_text)
        if match:
            bulten_tarihi = match.group(1)
            print(f"📅 Bülten tarihi (body): {bulten_tarihi}")
        else:
            bulten_tarihi = datetime.now().strftime("%d.%m.%Y")
            print(f"⚠️ Tarih bulunamadı, bugünün tarihi kullanılıyor: {bulten_tarihi}")

    # 2. Tablo verilerini çek
    regions = {}
    ortalama = {}

    table = soup.find("table", class_="table-custom")
    if not table:
        print("❌ Fiyat tablosu bulunamadı!")
        return None

    rows = table.find_all("tr")
    print(f"📊 {len(rows)} satır bulundu")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:
            region_name = cells[0].get_text(strip=True)
            dana_raw = cells[1].get_text(strip=True).replace("₺", "").strip()
            kuzu_raw = cells[2].get_text(strip=True).replace("₺", "").strip()

            # "Değişim" satırlarını atla
            if "Değişim" in region_name or "%" in region_name:
                continue

            # Fiyatları parse et (Türkçe format: 607,50 → 607.50)
            try:
                dana_fiyat = float(dana_raw.replace(".", "").replace(",", "."))
                kuzu_fiyat = float(kuzu_raw.replace(".", "").replace(",", "."))
            except ValueError:
                print(f"⚠️ Parse hatası - Bölge: {region_name}, Dana: {dana_raw}, Kuzu: {kuzu_raw}")
                continue

            entry = {
                "dana": f"{dana_fiyat:.2f}",
                "kuzu": f"{kuzu_fiyat:.2f}",
            }

            if "Ortalama" in region_name:
                ortalama = entry
                print(f"  📍 {region_name}: Dana {dana_raw}, Kuzu {kuzu_raw}")
            else:
                # Bölge ismini normalize et
                region_key = normalize_region(region_name)
                regions[region_key] = entry
                print(f"  📍 {region_name} → {region_key}: Dana {dana_raw}, Kuzu {kuzu_raw}")

    if not regions and not ortalama:
        print("❌ Hiç veri parse edilemedi!")
        return None

    # 3. JSON çıktısını oluştur
    result = {
        "bulten_tarihi": bulten_tarihi,
        "last_update": datetime.utcnow().isoformat() + "Z",
        "source": "UKON",
        "ortalama": ortalama,
        "regions": regions,
    }

    print(f"\n✅ Toplam {len(regions)} bölge + ortalama verisi başarıyla çekildi")
    return result


def normalize_region(name):
    """Bölge ismini Flutter uygulamasındaki formatla eşleşecek şekilde normalize eder."""
    name = name.strip()
    mapping = {
        "Ege Bölgesi": "EGE",
        "Akdeniz Bölgesi": "AKDENİZ",
        "Marmara Bölgesi": "MARMARA",
        "İç Anadolu Bölgesi": "İÇ ANADOLU",
        "Doğu Anadolu Bölgesi": "DOĞU ANADOLU",
        "Güneydoğu Anadolu Bölgesi": "GÜNEYDOĞU ANADOLU",
        "G.Doğu Anadolu Bölgesi": "GÜNEYDOĞU ANADOLU",
        "Karadeniz Bölgesi": "KARADENİZ",
    }

    for key, value in mapping.items():
        if key.lower() in name.lower() or name.lower() in key.lower():
            return value

    # Eşleşme bulunamazsa büyük harfle döndür
    return name.upper()


def save_json(data):
    """JSON dosyasını kaydeder."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Veri kaydedildi: {OUTPUT_FILE}")


def load_existing():
    """Mevcut JSON dosyasını yükler (history için)."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    print("=" * 50)
    print("🚀 Bereket Takip - UKON Scraper")
    print(f"⏰ {datetime.now().isoformat()}")
    print("=" * 50)

    data = scrape_ukon()

    if data is None:
        print("\n❌ Scraping başarısız! Mevcut veri korunuyor.")
        return

    # Mevcut veriyi yükle ve history'e ekle
    existing = load_existing()
    if existing and "history" in existing:
        history = existing["history"]
    else:
        history = []

    # Son 90 günlük veriyi tut (günde ~4 kayıt × 90 gün = ~360 kayıt)
    history.append({
        "date": data["last_update"],
        "bulten_tarihi": data["bulten_tarihi"],
        "ortalama": data["ortalama"],
    })

    # Maksimum 360 kayıt tut
    if len(history) > 360:
        history = history[-360:]

    data["history"] = history

    save_json(data)

    print("\n✅ Scraping başarıyla tamamlandı!")
    print(f"📊 Dana (Ortalama): {data['ortalama'].get('dana', 'N/A')} TL/KG")
    print(f"📊 Kuzu (Ortalama): {data['ortalama'].get('kuzu', 'N/A')} TL/KG")


if __name__ == "__main__":
    main()
