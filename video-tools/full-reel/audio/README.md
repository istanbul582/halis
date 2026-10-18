# Tam sesin yeniden üretimi

Bu klasörde ses kaydı, müzik örneği veya stok medya yayımlanmaz. Kod, mevcut videodaki özgün 92 BPM müziği ve gürültü/osilatör tabanlı efektleri yeniden üretir. Kaynak GUMA videosunun sesi kullanılmaz.

Gerekli özel girdi: kullanıcının kaydından hazırlanmış **tam, normalize `narration-master.wav`**. 48 kHz, mono, PCM24; **7.448.033 örnek / 155,167354 saniye**; SHA-256:

```text
00688f8d1eddfae678cbb789e3a990af247290c5929cd1080031015bb7f45bb1
```

Dosya yoksa veya hash eşleşmezse işlem durur. MP3, kısaltılmış dosya veya yeniden kodlanmış WAV kabul edilmez; ses kesilmez, yeniden sıralanmaz ve hızlandırılmaz. Orijinal normalize master özel olarak saklanmalıdır.

Eski ölçüm notlarındaki 155,167313 saniye özgün MP3'ün nominal süresidir. Burada örnek sayısı üzerinden normalize WAV'ın tam süresi kaydedilir; dosyanın içeriği değiştirilmez.

Python 3.11+, FFmpeg/FFprobe ve NumPy/SciPy gerekir. Proje kökünden:

```bash
python -m pip install -r audio/requirements.txt
python audio/build_audio.py --voice /private/narration-master.wav --output-dir /private/audio-build
```

Varsayılan çıktı `audio/build/` klasörüdür. Üretim için `finalmix.wav` kullanılır: **164,2 saniye, 48 kHz stereo PCM24**. Bu süre, anlatımın tamamı ile kaynak ve kapanış alanını içerir. Başlangıçta veya konuşma içinde kesme yapılmaz; yalnız anlatımın doğal sonundan sonra sessizlik eklenir.

Parçaları ayrı üretmek için:

```bash
python audio/make_sound_design.py --voice /private/narration-master.wav --output-dir /private/audio-build
python audio/mix_audio.py --voice /private/narration-master.wav --output-dir /private/audio-build
```

Üretilen dosyalar: `music-bed.wav`, `foley.wav`, `sound-design.wav`, `sfx-events.json`, `finalmix.wav`, ölçüm/log dosyaları. `finalmix.metadata.json` tam çözme, uzunluk, LUFS, true peak ve referans hash karşılaştırmasını içerir.

Referans V3 miks video boyunca değiştirilmeden kullanılır. Referans miks SHA-256:

```text
6ad964b2ca04a644e40165d497d93b5a935a03918e41eb07b8c4b36be97803b5
```

Aynı Python/NumPy/SciPy ve FFmpeg sürümlerinde referans hash karşılaştırması yapılır. Kütüphane/FFmpeg sürümü değişirse sayısal veya WAV üstbilgi farkı oluşabilir; hash eşitliği ayrıca raporlanır, yalnız ölçümlerin tutması “baytları aynı” diye yazılmaz. Giriş sesinin tam hash kontrolü her durumda zorunludur.

Müzik ve efekt zamanlaması referansla aynıdır. V6’da kaynak görüntüsü 155,2–161,2; takip çağrısı 161,2–164,2 saniyedir. 162,2’deki özgün kapanış tınısı takip çağrısının içinde kalır.
