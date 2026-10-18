# Ücretsiz referans analizi ve düzenlenebilir kurgu zaman çizelgesi

Bu klasör iki çalışan üretim aracını içerir. Yeni bir video motoru eklemek yerine, seçilen Kot/Mavi örneğinin kesme ritmini ölçer ve yeni 90 saniyelik anlatımın kesitlerini taşınabilir bir kurgu dosyasına dönüştürür.

## Kurulum

Python 3.12 ile test edildi. İnternet yalnızca ilk kurulumda PyPI paketlerini indirmek için gerekir. Ücretli servis, API anahtarı veya abonelik kullanılmaz.

```bash
bash setup.sh
```

Kurulum bu klasörde `.venv` oluşturur. `requirements.lock.txt` doğrudan ve dolaylı paket sürümlerini sabitler. `requirements.txt` ana araçları listeler. Sistem Python paketleri değiştirilmez; `.venv` Git'e veya teslim paketine eklenmez.

- PySceneDetect 0.6.7.1: sahne değişimi adaylarını ölçmek.
- OpenCV headless 4.12.0.88: videoyu görüntü penceresi açmadan çözmek.
- OpenTimelineIO 0.17.0: medya gömmeden kurgu kararlarını saklamak.
- SciPy 1.17.0 ve NumPy 2.2.6: ses tasarımında filtreleme/DSP ve anlatım kesitlerini örnek düzeyinde hazırlamak. `editorial/make_sound_design.py` içindeki `scipy.signal` aynı ortamdan sağlanır.

## 1. Kot/Mavi referansının gerçek ölçümü

Yerel olarak kullanıcının gönderdiği seçili referansta çalıştırıldı. `results/reference_analysis.json` sürüm, eşik, giriş SHA-256 ve özet ölçüleri içerir. `mavi_candidate_shots_t27.csv` ana aday listesi, `t22` ve `t32` listeleri duyarlılık karşılaştırmasıdır. `mavi_frame_change_metrics.csv` ana geçiş puanlarını içerir.

```bash
.venv/bin/python analyze_reference.py \
  --input '/kendi/yolunuz/Kot-Mavi-referansi.mp4' \
  --output-dir results \
  --threshold 27 \
  --comparison-thresholds 22 32 \
  --min-scene-frames 12 \
  --downscale 3
```

Ölçüm: `ContentDetector`, varsayılan HSV ağırlıkları, her kare, en kısa aday sahne 12 kare (30 fps'de 0,4 saniye), görüntü boyutunu üçe indirme. Algoritma ani renk/içerik değişimini yakalar; büyük yazı animasyonu, flaş ve hızlı kamera hareketini de kesme sayabilir. Yumuşak geçişleri kaçırabilir. Bu sonuçlar otomatik aday listeleridir; elle doğrulanmış plan sayısı veya estetik kalite puanı değildir. Referansın ritmini değerlendirmek için kullanılır, örneğin görüntülerini yeniden yayınlamak için kullanılmaz.

Seçilen referansta elde edilen gerçek sonuç:

| Eşik | Sahne adayı | Kesme adayı | Medyan sahne süresi |
|---|---:|---:|---:|
| 22 | 11 | 10 | 5,43 sn |
| 27 — ana ölçüm | 10 | 9 | 5,68 sn |
| 32 | 9 | 8 | 7,83 sn |

Her çalışmada 2322 kare kesintisiz kapsandı: video akışı 30 fps ile 77,400 saniye. Kapsayıcı/ses 77,524 saniyedir; son 0,124 saniye farkı çözülmemiş video veya kayıp kare değildir. Ana ölçümde 2,233–26,433 saniyeler tek 24,2 saniyelik aday sahne oluşturur. Dolayısıyla referansın dinamik hissini yalnızca çok sık kesmeyle açıklamak doğru olmaz; aynı sahne içindeki nesne, katman ve kamera hareketleri ayrıca incelenmelidir. Bu analiz izlenme veya beğeni tahmini yapmaz.

Bu betik referanstan **görüntü, ses, kare veya video kesiti dışa aktarmaz**. Yalnızca sayısal CSV/JSON üretir. Ham referans videoyu bu klasöre veya GitHub'a eklemeyin.

## 2. Yeni 90 saniyelik anlatım için OTIO

```bash
.venv/bin/python export_otio.py \
  --input ../editorial/GUMA_v5_full_90s.json \
  --output results/GUMA_v5_full_90s.otio
```

`results/GUMA_v5_full_90s.otio` iki iz içerir:

- A1: kullanıcının mevcut anlatımından seçilen 9 ses kesiti, sekiz adet 25 ms geçiş niyeti.
- V1: aynı kurgu bölümlerine karşılık gelen 9 görsel yer tutucu; amacı ve kaynak ilişkisi metadata içinde.

Ses kaynağı yalnızca `USER_NARRATION_WAV_RELINK_REQUIRED.wav` adlı yer tutucu olarak bağlıdır. Gerçek dosya gömülmez, yerel özgün sesin mutlak yolu taşınmaz. Kendi düzenleyicinizde kullanıcının yetkili olduğu orijinal anlatımı yeniden bağlayın. Görsel yer tutucuları oluşturulan sahnelerle değiştirin.

OTIO, bu dosyada bitmiş animasyonları veya Remotion/Blender efekt düğümlerini taşımaz. Ses kesitleri, kaynak aralıkları, bölüm yerleri, alıntı/kaynak notları ve geçiş niyetini taşır. Açacağınız düzenleyicinin OTIO desteğine/adaptörüne ihtiyaç vardır. Premiere, Resolve veya Kdenlive'a içe aktarma bu ortamda test edilmedi; her programın ses geçişini yorumlama şekli değişebilir.

25 ms örtüşme, 48 kHz ses zamanında tam 1200 örnektir. OTIO kesme noktasının iki yanında 600'er örnek tutularak özgün seçim aralıkları korunur. Bu nedenle 30 fps'ye yuvarlanmış hatalı yaklaşık geçiş yerine örnek doğruluğunda 90 saniyelik ses kurgusu saklanır. Videonun amaçlanan kare hızı 30 fps olarak metadata içinde yazılıdır.

Her dışa aktarmada dosya yeniden okunur. Süre, iz süreleri, kesit/geçiş sayısı, kaynak aralıkları, zaman çizelgesi konumları ve ham ses yolunun bulunmaması otomatik doğrulanır. Sonuç `GUMA_v5_full_90s.validation.json` içindedir. Kaynak JSON'un SHA-256 değeri de saklanır; metin/kesit değişirse yeniden dışa aktarın.

## Lisanslar

- [PySceneDetect — BSD-3-Clause](https://github.com/Breakthrough/PySceneDetect/blob/main/LICENSE). Ana dal lisansı resmî GitHub'dan, kurulu 0.6.7.1 paketinin lisansı ayrıca paketin kendisinden saklandı.
- [OpenTimelineIO 0.17.0 — Apache-2.0](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/v0.17.0/LICENSE.txt).
- [OpenCV 4.12.0 — Apache-2.0](https://github.com/opencv/opencv/blob/4.12.0/LICENSE). Python headless paketinin kendi ve üçüncü taraf bildirimleri de `licenses/` içindedir.
- [SciPy 1.17.0 — BSD-3-Clause](https://github.com/scipy/scipy/blob/v1.17.0/LICENSE.txt). Kurulan ikili paketteki BLAS/LAPACK ve diğer bileşenlerin ek bildirimleri de `licenses/installed-scipy-LICENSE.txt` içinde korunur.

Bu yazılım lisansları ücretsiz ticari kullanıma izin verir; lisans/bildirim koşulları korunmalıdır. Referans videoları, anlatımı, stokları, markaları veya başka varlıkları kullanma hakkı sağlamaz. Üretilen `.otio` dosyası bu medyaların hiçbirini içermez.

`licenses/fetch-*.json` kayıtları lisans URL'lerinin erişim sonucunu gösterir. PySceneDetect'in tahmin edilen `v0.6.7.1`/`v0.6.7` ham dosya URL'leri 404 verdi; başarılı resmî `main` lisansı ile kurulan paketin lisansı kullanıldı. Bu bir erişim kısıtını aşma girişimi değildir.

## Doğrulama dosyaları

- `results/installation_validation.json`: gerçek kurulu sürümler ve `pip check` sonucu.
- `results/reference_analysis.json`: üç eşik çalışması ve tüm karelerin kesintisiz kapsandığı doğrulaması.
- `results/GUMA_v5_full_90s.validation.json`: gerçek OTIO yaz/oku doğrulaması.

Teslime `.venv`, ham referans, ham anlatım veya çıkarılmış referans kareleri eklenmez. Bu klasördeki betikler, sürüm dosyaları, lisans bildirimleri ve yalnızca sayısal analiz/OTIO sonuçları paylaşılır.
