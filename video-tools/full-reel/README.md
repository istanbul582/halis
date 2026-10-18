# GUMA — tam anlatımlı dikey film

Bu klasör güncel üretim projesidir. Önceki 99 saniyelik deneme kullanıcı tarafından reddedildi. Bu sürümün zaman çizelgesi **164,2 saniye, 4926 kare, 1080×1920 / 30 fps**; özgün Ece kaydının **yaklaşık 155,167 saniyesi** başlangıcından son sözcüğüne kadar korunur. Ses kesilmez, yeniden sıralanmaz veya hızlandırılmaz. Koltuk canlandırması, 3D sahne ve AI koltuk görseli kullanılmaz.

Açılışta hareketli tipografi; kaynaklı şirket açıklamalarında alıntı ve ilişki çizimleri; genel tasarım, üretim ve tanıtım anlatımında bu eylemleri gösteren gerçek stok kesmeleri vardır. Stok görüntüler marka tesisi, çalışanı veya ürünü olarak sunulmaz. Kullanılan asıl sahneler `film/render_film.py` içindeki `SCENES` ve `SHOTS` listeleridir; `editorial/FINAL_TIMELINE.json` bunların paylaşılabilir kaydıdır. Altyazı ve kaynak satırları ayrı yerleşir. Son 6 saniye kaynaklar, son 3 saniye özgün takip kapanışıdır.

## Kurulum

Gerekli sistem araçları Python 3.12+, FFmpeg ve ffprobe'dur. Bu film GPU, Blender, Chromium, Node, Remotion, ücretli servis veya API gerektirmez. Daha önce kurulmuş alternatif araçlar `../free-toolkit/` altında korunur.

```bash
cd video-tools/full-reel
bash tools/setup.sh
tools/.venv/bin/python -m pip check
```

Yeni araçlar: [PyAV](https://github.com/PyAV-Org/PyAV) ile stok karelerini inceleme; [Pillow](https://github.com/python-pillow/Pillow) ve NumPy ile kare tabanlı yazı/çizim üretimi; FFmpeg ile video birleştirme. SciPy, sesin eksiksiz kaldığını denetler. Sürümler `tools/requirements.txt` içinde sabittir; lisans kayıtları `tools/` altındadır. Yazılım lisansı, stok veya ses kullanım hakkı sağlamaz.

## Özel girdiler ve yeniden üretim

Ham kullanıcı sesi, ham stoklar ve kaynak videolar Git'e veya ZIP'e eklenmez. Bunlar kullanıcıya ait yerel girdilerdir. Yalnızca bu girdilerin bilgisayarınızda bulunduğu durumda yeniden render mümkündür; eksik girdiler yerine yeni bir konuşma veya referans videosu konulmamalıdır.

```bash
# Yüklenen orijinal stoklardan seçilmiş 11 sessiz kesiti hazırla.
tools/.venv/bin/python scripts/prepare_media.py \
  --source-dir /private/stock-files --output-dir assets/clips

# Orijinal 155,167313 saniyelik master ile tam ses miksini hazırla.
tools/.venv/bin/python audio/build_audio.py \
  --voice /private/narration-master.wav --output-dir input

# Tam filmi üret. Girdi sesi tek parça olarak kullanılır.
tools/.venv/bin/python film/render_film.py \
  --assets-root assets --captions editorial/segments.json \
  --audio input/finalmix.wav --voice-master /private/narration-master.wav \
  --output-root /tmp/guma-render --render --workers 4

# Her konuşma penceresini orijinal master ile karşılaştır.
tools/.venv/bin/python tools/check_full_narration.py \
  --voice /private/narration-master.wav \
  --film /tmp/guma-render/output/GUMA_V6_TAM_ANLATIM_164s.mp4 \
  --out /tmp/guma-render/FULL_NARRATION_VERIFICATION.json
```

Kullanıcının marka videosu ve WhatsApp örnekleri yalnızca inceleme içindir: son filme görüntü, ekran görüntüsü, ses veya ses taklidi aktarılmaz. Markaların adları standart OFL yazı tipleriyle anılır. Bütçe bir plan olarak, önceki kitle kurucunun beyanı olarak aktarılır; Saloni ilişkisi bedelsiz üretim veya finansman kanıtı olarak yorumlanmaz. Tam kaynaklar ve doğrulamanın sınırları [kaynak notlarında](docs/KAYNAKLAR.md) bulunur.

Teknik doğrulamalar `qa/` altındadır. Ses penceresi karşılaştırması içerik doğruluğu veya hukuki uygunluk denetimi değildir. İnternetten izlenme veya hukuki sorunsuzluk garantisi verilmez.
