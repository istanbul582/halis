# GUMA — tam anlatımlı kurgu

164,2 saniye; 1080 × 1920; 30 fps. Kullanıcının 155,167 saniyelik Ece anlatımı aynı sırada, aynı hızda ve tüm sözcükleriyle korunur. Sonuna 6 saniye kaynaklar ve 3 saniye özgün takip çağrısı eklenir.

Açılış 0–23,04 saniyede stok kullanmaz. Bütçe planı, önceki kitle beyanı, şirketin üretim/satış açıklaması ve kurucunun gazetede yayımlanan sözleri birbirinden ayrılır. 52,32 saniyelik eylem görüntüsü anlatılan genel iş adımlarına karşılık gelir. Kaynaklı şirket/kişi açıklamalarında gerçek tesis veya kişi izlenimi veren stok kullanılmaz. 3D koltuk veya yapay zekâ koltuk görseli kullanılmaz.

## Yerel girdiler

Python 3.12+, Pillow, NumPy ve PATH üzerinde FFmpeg / FFprobe gerekir. Bu sürümün fiili render motoru Pillow + FFmpeg'dir. Three.js, Blender veya Remotion bu videonun görüntüsünü render etmez.

Proje kökünde:

- `film/render_film.py`, `film/finalize.py` ve `film/fonts/`
- `assets/SELECTED_MANIFEST.json`, `assets/EXTRA_PHASES_MANIFEST.json`
- `assets/clips/<manifestteki name>.mp4` — kullanıcının yerel olarak sağladığı 11 sessiz proxy
- `editorial/segments.json`, `editorial/narration.srt`
- Kullanıcının yerel `narration-master.wav` dosyası (155,167 sn), isteğe göre tam `finalmix.wav` dosyası (164,2 sn)

Stoklar ve ham ses kayıtları proje kodundan ayrı yerel girdilerdir. Manifestteki kaynak bağlantısı, tekil stok lisansının ayrıca doğrulandığı anlamına gelmez; kullanıcı bu görüntüleri Pexels'ten aldığını belirtmiştir.

## Çalıştırma

```sh
python film/render_film.py --previews \
  --assets-root /yerel/proje/assets \
  --captions /yerel/proje/editorial/segments.json

python film/render_film.py --render --workers 4 \
  --assets-root /yerel/proje/assets \
  --captions /yerel/proje/editorial/segments.json \
  --audio /yerel/ses/finalmix.wav \
  --voice-master /yerel/ses/narration-master.wav
```

`SCENES` konuşmanın özgün sırasındaki ana bölümleri; `SHOTS` stokların tek yetkili zaman çizelgesini tanımlar. `render/jobs.json` tam kare ızgarasına yuvarlanan fiili kesim listesidir. `output/RENDER_REPORT.json` ses SHA-256'sını, sıfır kesim/hız değişimi bilgisini ve kullanılan stok pencerelerini kaydeder.

Gelecek renderlar RGB tam aralıktan BT.709 sınırlı aralığa gerçek matris dönüşümüyle yazılır. `finalize.py` daha önce üretilmiş etiketsiz BT.601 sınırlı aralık dosyasını dönüştürür; açıkça BT.709 etiketli dosyayı tekrar encode etmez.

Fontlar Manrope, DM Serif Display ve Barlow Condensed'dir. SIL OFL metinleri `fonts/` içindedir. Marka logosu veya markanın özel yazı karakteri kullanılmaz.
