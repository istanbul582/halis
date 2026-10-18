# 99 saniyelik özgün ses tasarımı

`mixed_audio.wav` filmin tamamı için stereo son mikstir: 0–90 saniye Ece anlatımı, 90–96 saniye kaynaklar, 96–99 saniye takip animasyonu. Film render'ında ayrıca ikinci bir anlatım dosyası açılmamalıdır.

`sfx_only.wav` bütün özgün müzik ve efekt katmanlarını içerir; içinde konuşma yoktur. `score_only.wav` yalnız müzik, `transition_effects_only.wav` yalnız geçiş efektleridir. Bunlar son miksin üzerine tekrar eklenmez; alternatif düzenleme içindir.

## Tasarım

- 100 BPM, seyrek C add9 / F majör7 / G6 / C majör dizilimi. Yuvarlak bas ve kısa, yumuşak tuş/pluck sesleri; yoğun davul veya gerilim dronu yok.
- Açılış alıntısı ve görev bilgisinde kısa, hafif tahta vurguları.
- 14,855 / 21,010 / 25,775 / 31,810 / 45,995 / 59,720 / 70,325 / 82,450 saniyedeki anlamlı bölüm değişimlerinde yaklaşık 340 ms hava geçişi. Yükseliş, değişim anında biter; kısa bir vurgu takip eder.
- 90 ve 96 saniyede kaynak/takip animasyonuna hafif armonik işaretler. Sonda 1,2 saniyelik yumuşak sönme.
- Anlatımın RMS zarfı müziği otomatik olarak yaklaşık 10 dB'ye kadar kısar. Anlatımın cümle araları korunur.

## Üretim ve hak kapsamı

Müzik ve efektler bu görev için NumPy/SciPy ile sinüs dalgaları, deterministik rastgele gürültü, zarflar ve filtrelerden üretildi. Hazır kayıt, müzik döngüsü, ses kütüphanesi, örnek videodan müzik, marka kaynak videosundan ses ya da dış ses API'si kullanılmadı. Yeniden üretim kodu `make_sound_design.py` dosyasıdır; ölçümlü mastering kodu `master_sound_design.py` dosyasıdır.

Anlatım kullanıcının sağladığı Ece kaydından gelir; bu kayıtla ilgili mevcut kullanım hakları ayrı kalır. Özgün müzik/efekt üretimi açıklaması, kullanıcının anlatım kaydına veya başka üçüncü taraf varlıklarına yeni bir lisans atamaz.

## Ölçüm

Son miks 48 kHz, stereo, 24 bit PCM WAV'dır. İki geçişli FFmpeg mastering hedefi −16 LUFS ve en fazla −1,2 dBTP'dir. Gerçek son ölçüm, süre ve tam çözme sonucu `sound_design_validation.json` dosyasındadır. `sound_design.json` bölüm olaylarını, üretim yöntemini ve mastering öncesi katman tepe değerlerini içerir.

Teslim edilen son dosya **99,000 saniye, −16,00 LUFS, −4,03 dBTP** ölçüldü ve FFmpeg ile tamamen çözüldü. Ayrı `sfx_only.wav` katmanı mastering öncesinde **−32,95 LUFS, −13,66 dBTP** ölçüldü. İlk denemede bu seyrek katman gereğinden kısık olduğundan ölçüm sonrası 13,06 dB yükseltildi; yukarıdaki değerler bu düzeltme sonrasına aittir.

Bu kontroller tam ses çözümü ve ölçümdür; yeni insan dinleme oturumu yapıldığı iddia edilmez.
