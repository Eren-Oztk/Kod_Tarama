<div align="center">

# ⬡ Kod Haritası

**`Disk Tarayıcı · Python · HTML Rapor`**

<br>

[![Live Demo](https://img.shields.io/badge/🌐_Canlı_Demo-GitHub_Pages-1f6feb?style=for-the-badge)](https://eren-oztk.github.io/Kod_Tarama)
[![Language](https://img.shields.io/badge/Python-100%25-3776AB?style=for-the-badge&logo=python)](https://github.com/Eren-Oztk/Kod_Tarama)
[![Platform](https://img.shields.io/badge/Windows-PowerShell%2FCMD-0078D4?style=for-the-badge)](https://github.com/Eren-Oztk/Kod_Tarama)

</div>

---

## Versiyon

`v1.0.0`

## Açıklama

**TR:** Bilgisayardaki tüm disk sürücülerini tarayarak kod dosyalarını bulan, proje klasörlerine göre gruplandıran ve interaktif HTML rapor oluşturan Python aracı.

**EN:** A Python tool that scans all disk drives, groups code files by project folder, and generates an interactive dark-themed HTML report.

---

## Ne Yapar?

`kod_tara.py` çalıştırıldığında Windows'taki tüm disk sürücülerini (C:\, D:\, vb.) otomatik olarak tarar. 30'dan fazla programlama diline ait dosyaları bulur, bunları `requirements.txt`, `package.json`, `.git` gibi proje işaretçilerine göre klasörlere gruplar ve masaüstüne `kod_haritasi.html` adlı bir rapor bırakır.

Rapor açıldığında tüm projelerinizi, dil istatistiklerinizi ve dosya önizlemelerini tek sayfada görebilirsiniz.

## Nasıl Çalışır?

1. Tüm sürücüler `os.walk()` ile taranır; sistem ve geçici klasörler (`node_modules`, `AppData`, vb.) atlanır.
2. Her dizin `requirements.txt`, `package.json`, `Cargo.toml` gibi dosyalara bakılarak "proje klasörü" olarak işaretlenir.
3. Kod dosyaları uzantılarına göre sınıflandırılır ve en yakın üst proje klasörüne atanır.
4. Tüm veriler tek bir bağımsız HTML dosyasına yazılır: arama, dil filtresi ve kod önizleme özellikleriyle gelir.

---

## Desteklenen Diller

| Grup | Diller |
|---|---|
| Python | `.py` |
| Web | `.html`, `.css`, `.scss`, `.js`, `.ts`, `.jsx`, `.tsx`, `.php` |
| Embedded | `.ino`, `.pde`, `.c`, `.h`, `.cpp` |
| Veri / Config | `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.sql` |
| Shell | `.sh`, `.bat`, `.ps1` |
| Diğer | `.rs`, `.go`, `.java`, `.kt`, `.rb`, `.lua`, `.dart`, `.swift` |

---

## Kurulum

Python 3.8+ gereklidir. Dış bağımlılık **yoktur** — yalnızca standart kütüphane kullanılır.

```bash
git clone https://github.com/Eren-Oztk/Kod_Tarama.git
cd Kod_Tarama
python kod_tara.py
```

**Windows için hızlı yol:** `TARA.bat` dosyasına çift tıkla.

### Çıktı

Tarama tamamlandığında masaüstünde `kod_haritasi.html` açılır. Bu dosya tamamen bağımsızdır — tarayıcıda çevrimdışı çalışır.

---

## Bağımlılıklar

Dış bağımlılık yoktur. Yalnızca Python standart kütüphanesi kullanılır:

| Modül | Kullanım |
|---|---|
| `os`, `pathlib` | Dosya sistemi tarama |
| `datetime` | Değiştirilme tarihi |
| `collections` | Dil istatistikleri |
| `webbrowser` | Raporu otomatik açma |

---

## Bilinen Limitasyonlar

- Linux/macOS'ta sürücü tespiti `/` kökünden başlar; performans büyük disklerde düşebilir.
- Proje marker'ı olmayan bağımsız dosyalar "Sahipsiz Dosyalar" bölümüne düşer.
- Her projede en fazla 20 dosya tablo satırı gösterilir (daha fazlası sayı olarak belirtilir).

---

## Lisans

MIT © 2026 Eren Öztürk
