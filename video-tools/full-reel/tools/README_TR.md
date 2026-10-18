# V6: Üretim, görsel seçimi ve tam ses denetimi

V6 filmi **Pillow + NumPy + FFmpeg** ile üretilir: Pillow hareketli yazı ve grafik katmanlarını çizer, NumPy piksel hesaplamalarını yapar, FFmpeg stok karelerini çözer ve H.264 videoyu kodlar. Bu renderer'ın Remotion, Node.js, Blender veya 3D koltuk modeli bağımlılığı yoktur. Önceki sürümlerin araçları ayrı projelere aittir. PyAV gerçek stok kareleri ve metaverilerinin envanterinde, SciPy ise özgün anlatımın finalde eksiksiz kaldığını denetlemek için kullanılır. Ücretli servis, API veya büyük görsel üretim modeli bu araç kurulumu sırasında indirilmedi.

## Kullanılan ücretsiz araçlar

**PyAV 19.0.1**, [resmî GitHub deposu](https://github.com/PyAV-Org/PyAV), BSD-3-Clause. FFmpeg kütüphanelerine Python üzerinden erişir. Bu projede yalnızca video metaverisini okumak ve belirtilen saniyeye en yakın gerçek kareyi çözmek için kullanıldı. **Pillow 13.0.0**, [resmî GitHub deposu](https://github.com/python-pillow/Pillow), MIT-CMU; çözülen kareleri okunabilir temas sayfalarında birleştirir. Resmî, sürüme sabitlenmiş Python yazılım lisanslarının kopyaları ve SHA-256 değerleri `NEW_TOOL_LICENSES.json` dosyasında bulunur.

Pillow gerçek film renderında yazı, grafik ve kare kompozisyonunu da oluşturur. **NumPy 2.3.5**, [resmî GitHub deposu](https://github.com/numpy/numpy), BSD-3-Clause; filmde piksel hesaplamaları ve ses denetiminde dalga biçimleri için kullanılır. **SciPy 1.17.0**, [resmî GitHub deposu](https://github.com/scipy/scipy), BSD-3-Clause; ses korelasyonunu hesaplar. Dört Python bağımlılığının sürümleri `requirements.txt` içinde sabittir. Sistem ayrıca [FFmpeg](https://github.com/FFmpeg/FFmpeg) ve `ffprobe` komutlarını sağlamalıdır; FFmpeg'in lisansı derleme seçeneklerine göre LGPL/GPL'dir ve yürütülebilir dosyası bu pakette dağıtılmaz.

Python 3.12 ile sınanan kurulum bu klasördeki ayrı `.venv` ortamına yapılır; mevcut Node ve Python ortamları değiştirilmez. Kurulum hiçbir videoyu otomatik işlemez. `.venv`, ham kullanıcı sesi/videoları, temas sayfası görselleri ve teknik benchmark MP4'ü herkese açık pakete dahil edilmez. Betikler ve lisans kayıtları paylaşılabilir.

```bash
bash setup.sh
```

Önbellek isteğe bağlıdır; varsayılan kurulum önbelleğe yazmaz. İstenirse bu iş için ayrılan bir yol ve farklı Python yorumlayıcısı belirtilebilir:

```bash
GUMA_V6_PIP_CACHE="$PWD/.cache/pip" GUMA_PYTHON=python3 bash setup.sh
```

Medya envanteri istenirse ayrı çalıştırılır:

```bash
.venv/bin/python media_inventory.py --root /path/to/user-supplied-media --out ./inventory
```

`media_inventory.py`, sayısal stok kimliğiyle başlayan dosyaları seçer. WhatsApp referansları ve markanın kaynak videosu buna dahil edilmez. Kullanıcının mevcut **17 stok videosundan 51 gerçek kare** çözülerek, her stok için üçlü temas sayfası ve toplu `overview.jpg` oluşturuldu. Süre, çözünürlük, kare hızı, ses kanalları ve örneklerin gerçek zamanları `media_inventory.json` dosyasındadır. İşlem 73,463 saniye sürdü. Bu, video kurgu veya otomatik görsel eşleştirme aracı değildir; yönetmenin tüm görüntüleri görerek doğru cümlede doğru planı seçmesini sağlar. Pexels adresleri kullanıcı beyanı ve dosya kimliğine dayanır; yazılım lisansı stok lisansını doğrulamaz.

## Seslendirmeyi eksiksiz koruma denetimi

`check_full_narration.py`, orijinal sesle filmin sesini 8 kHz mono dalga biçimi üzerinden karşılaştırır. Konuşma içeren her 1,5 saniyelik pencerede, en fazla 75 ms küçük kodlayıcı hizası farkıyla eşleşme arar. Müzik eşliğini tolere eder; sesi kesmez, hızlandırmaz veya yeniden yazmaz. Bu kontrol aynı `.venv` içindeki sabit NumPy ve SciPy sürümleriyle çalışır.

```bash
.venv/bin/python check_full_narration.py \
  --voice /path/to/original-narration.wav \
  --film /path/to/final.mp4 \
  --out ./FULL_NARRATION_VERIFICATION.json
```

Pozitif kontrol: 155,167 saniyelik özgün ses ile V3'teki tam anlatım karşılaştırıldı; **103 pencerenin tamamı eşleşti**, en düşük korelasyon 0,98091. Sonucu `VOICE_AUDIT_VALIDATION_V3.json` kaydeder. Aynı araç kısa V5'e karşı da sınanır; kısa film tam sesin sığması koşulunu geçemez. Bu ölçüm içerik doğruluğu veya hukuki uygunluk incelemesi değildir.

## Render performansı

`FFMPEG_RENDER_BENCHMARK.json`, mevcut makinede gerçek bir 10 saniyelik 1080×1920 / 30 fps teknik testinin komutunu ve ölçümünü saklar. Giriş 720×1280 stoktur; iki metin katmanı, hareketli yazı, şeffaf başlık ve ölçekleme uygulanır. H.264 `veryfast`, CRF 19 ve iki iş parçacığıyla **17,53 saniyede** üretildi; bu basit kompozisyon için 17,11 fps demektir. 164 saniyeye doğrusal tahmin yaklaşık 4,8 dakikadır; karmaşık finalin bu sürede biteceği taahhüdü değildir.

Bu kayıt gerçek V6 filminin render süresi veya görsel tasarımı değildir. V6 filmi kendi Pillow/NumPy kare kompozisyonunu FFmpeg'e aktarır; kaynak proje ve final ölçümleri film klasöründedir. Temas sayfası ve ses denetim araçları bu renderer'dan bağımsız olarak çalıştırılabilir.

GPU gerektiren rastgele görsel üretim depoları, otomatik sessizlik kesme araçları ve yeni koltuk animasyonları bu ekin parçası değildir. Tam kullanıcı seslendirmesi korunmalıdır.
