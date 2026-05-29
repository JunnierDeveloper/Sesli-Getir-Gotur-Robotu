# Sesli ve Akıllı Getir-Götür Ev Robotu Simülasyonu

Bu proje, ev ortamında otonom görevler icra edebilen, sesli komutları algılayıp işleyebilen ve kullanıcıya sesli/görsel geri bildirim sağlayan **2.5D İzometrik Ev Robotu Simülasyonudur**. Python dilinde **Pygame** kütüphanesi kullanılarak sıfırdan geliştirilmiş olup, yapay zeka tabanlı konuşma tanıma ve sentezleme yetenekleriyle donatılmıştır.

---

## 🎓 Akademik Bilgiler

*   **Projeyi Geliştiren Öğrenci:** Nurullah Başar
*   **Proje Danışmanı:** Dr. Öğr. Üyesi HASAN SERDAR
*   **Proje Türü:** Bitirme Projesi / Gelişmiş Robot Simülasyonu Çalışması

---

## 📺 Proje Tanıtım Videosu

Simülasyonun çalışmasını ve sesli komutların nasıl algılandığını aşağıdaki videodan izleyebilirsiniz:

<video src="demo.mp4" width="100%" controls></video>

*Eğer yukarıdaki oynatıcı çalışmazsa, videoyu doğrudan **[buraya tıklayarak tarayıcıda izleyebilir veya indirebilirsiniz](./demo.mp4)**.*

---

## 🚀 Temel Özellikler

*   📐 **2.5D İzometrik Görselleştirme:** Derinlik algısına sahip, özel gölgelendirmeli ve detaylı çizilmiş mobilyalar (yatak, kanepe, tv, mutfak tezgahı, buzdolabı vb.) içeren modern bir ev haritası.
*   🎤 **Sesli Komut Algılama (Speech Recognition):** Google Speech Recognition API entegrasyonu ile Türkçe sesli komutları ("mutfağa git", "kitabı al salona götür") anlık olarak analiz etme ve icra etme.
*   🗣️ **Sesli Geri Bildirim (Text-to-Speech):** `pyttsx3` kütüphanesi aracılığıyla robotun eylemlerini ve durumunu Türkçe olarak seslendirmesi (Örn: *"Mutfağa gidiyorum."*, *"Havlu aldım."*).
*   🧭 **A\* (A-Star) Yol Planlama:** Robotun solid (aşılmaz) engellerin (duvarlar, mobilyalar) etrafından dolaşarak en kısa ve en verimli rotayı çizmesini sağlayan gelişmiş yol bulma algoritması.
*   🔋 **Batarya ve Enerji Yönetimi:** Hareket halindeyken enerji tüketen, robot şarj istasyonuna (`(30,19)` koordinatı) ulaştığında kendini otomatik olarak dolduran dinamik batarya simülasyonu.
*   📊 **Gelişmiş HUD ve Telemetri Paneli:**
    *   Anlık lokasyon (oda ismi) ve durum göstergesi.
    *   Dinamik renk geçişli batarya seviyesi barı.
    *   Fare tekerleğiyle yakınlaştırma/uzaklaştırma (Zoom) ve sol tıkla haritayı kaydırma (Pan) yeteneği.
    *   Detaylı sistem günlüğü (konsol kayıtları) ve interaktif yazılı komut giriş alanı.
*   🎭 **Özel Görevler:** Dans etme modu, tüm evi dolaşarak temizlik yapma veya devriye gezme rutinleri.

---

## 🛠️ Teknik Altyapı ve Matematiksel Modeller

### 1. İzometrik Projeksiyon (2.5D Render)
Haritada bulunan her bir 2D ızgara (grid) hücresi, izometrik düzleme şu matematiksel dönüşüm formülü kullanılarak yansıtılır:

$$x_{pixel} = (x_{grid} - y_{grid}) \cdot \frac{W_{tile}}{2} + O_{x}$$

$$y_{pixel} = (x_{grid} + y_{grid}) \cdot \frac{H_{tile}}{2} + O_{y} - z_{height}$$

*Burada $W_{tile}$ ve $H_{tile}$ hücre boyutlarını, $O_x$ ve $O_y$ ekran kayma (offset) miktarlarını, $z_{height}$ ise objenin yükseklik değerini temsil eder.*

### 2. A\* Yol Bulma Algoritması
Robotun hareket rotasını bulmak için Manhattan uzaklık sezgiseli (heuristic) kullanan $f(n) = g(n) + h(n)$ formülü esas alınmıştır:

$$h(n) = |x_{hedef} - x_{mevcut}| + |y_{hedef} - y_{mevcut}|$$

Algoritma, engelleri (`SOLID` kümesindeki mobilya ve duvar kodları) hesaba katarak en uygun yolu kuyruk tabanlı `heapq` veri yapısıyla hızlıca hesaplar.

---

## 📁 Proje Klasör Yapısı

```text
Gelismiş Robot Simülasyonu/
│
├── robot_sim.py          # Ana simülasyon ve görselleştirme kodu (Pygame)
├── yedek.py              # Projenin yedek/yedeklenmiş kaynak kod dosyası
├── test.txt              # Test/not dosyası
├── assets/               # Harici görsel ve ses dosyaları için ayrılmış dizin (boş)
└── README.md             # Akademik ve açıklayıcı proje dokümantasyonu
```

---

## 🎮 Örnek Komutlar ve Kullanım Rehberi

Hem sesli modda (Mikrofon aktifken) hem de klavyeden yazarak aşağıdaki komutları kullanabilirsiniz:

| Komut Grubu | Örnek Komut Şablonları | Yapılan Eylem |
| :--- | :--- | :--- |
| **Navigasyon** | *"Mutfağa git"*, *"Salona geç"*, *"Banyoya yürü"* | Belirtilen odaya A\* ile rota çizer ve gider. |
| **Nesne Etkileşimi**| *"Kitabı al"* veya *"Havlu bırak"* | En yakındaki eşyayı envantere alır veya yere bırakır. |
| **Taşıma Zinciri** | *"Kitabı al salona götür"*, *"Kahveyi mutfağa taşı"* | Eşyayı hedeflenen konumdan alır, hedef odaya gidip bırakır. |
| **Rutin Görevler** | *"Devriye gez"*, *"Temizlik yap"* | Tüm odaları sırasıyla gezecek bir görev zinciri başlatır. |
| **Eğlence** | *"Dans et"* | Robot kollarını ve gövdesini sallayarak dans eylemi gerçekleştirir. |
| **Sistem** | *"Durumun ne?"*, *"Dur"*, *"Şarj'a git"* | Anlık durum raporu verir, kuyruğu sıfırlar veya şarj istasyonuna yönlenir. |

*Not: **"Ve"**, **"sonra"**, **"ardından"** gibi bağlaçlarla komutları ardı ardına sıralayarak görev zinciri oluşturabilirsiniz. (Örn: "Kitabı al salona götür sonra mutfağa git ardından dans et")*

---

## ⚙️ Kurulum ve Çalıştırma

Projenin bilgisayarınızda sorunsuz çalışması için gerekli kütüphaneleri yüklemeniz gerekmektedir.

### Gereksinimler

*   **Python 3.8 veya üzeri**
*   **Pygame** (Görsel arayüz ve simülasyon motoru)
*   **SpeechRecognition** (Ses tanıma sistemi için)
*   **pyttsx3** (Sesli geri bildirim sistemi için)
*   **PyAudio** (Mikrofon erişimi için - *SpeechRecognition bağımlılığı*)

### Adım Adım Kurulum

1.  **Gerekli Python Kütüphanelerini Yükleyin:**
    ```bash
    pip install pygame speechrecognition pyttsx3 pyaudio
    ```
    *(Not: Windows sistemlerinde PyAudio yükleme hatası alırsanız, `pip install pipwin` yapıp ardından `pipwin install pyaudio` komutunu deneyebilirsiniz.)*

2.  **Projeyi Çalıştırın:**
    ```bash
    python robot_sim.py
    ```

3.  **Arayüz Kontrolleri:**
    *   `TAB` Tuşu: Sesli Komut Modu (VOICE) ile Yazılı Komut Modu (TEXT) arasında geçiş yapar.
    *   `Fare Tekerleği` / `+` / `-` Tuşları: Haritayı yakınlaştırır veya uzaklaştırır.
    *   `Sol Fare Tık + Sürükleme`: Harita üzerinde gezinmeyi sağlar (Pan özelliği).
    *   `R` Tuşu: Kamerayı varsayılan konumuna ve boyutuna sıfırlar.


