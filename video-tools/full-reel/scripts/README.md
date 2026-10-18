# Özel stoklardan portre klipleri hazırlama

FFmpeg ve FFprobe gerekir; Python standart kütüphanesi yeterlidir. Özgün stok dosyaları bu depoda bulunmaz. İzinli orijinalleri özel bir dizinde tutun; alt klasörler de taranır. Dosya adı özgün Pexels kimliğiyle başlamalıdır: örneğin `5384976-uhd_4096_2160_30fps.mp4`.

Proje kökünden 11 klibin tamamını hazırlama:

```bash
python scripts/prepare_media.py --source-dir /private/originals
```

Varsayılan çıktı `assets/clips/` klasörüdür. Farklı bir hedef ve tek klip seçmek için:

```bash
python scripts/prepare_media.py --source-dir /private/originals --output-dir /private/proxy-test --only design_overhead --max-seconds 1
```

`--max-seconds` yalnız kısa deneme içindir; üretim hazırlığında kaldırın. Birden fazla ad `--only camera_phone material_blue` şeklinde verilebilir. Mevcut çıktıları yeniden üretmek için `--overwrite` ekleyin.

`media_manifest.json`, asıl dosyadan alınacak **mutlak kaynak başlangıcını**, crop alanını ve tam klip süresini içerir. Eski proxylerin başlangıcına ikinci kez ekleme yapılmaz. 11 klip 7 özgün dosyadan üretilir; eksik veya birden fazla eşleşen girdi varsa işlem başlamadan durur. Eski bilgisayara ait mutlak yollar kullanılmaz ve internetten stok indirilmez.

Her çıktı 720×1280, 30 fps, H.264/yuv420p ve sessizdir. `prepare-report.json` boyut, fps, süre ve SHA-256 sonuçlarını içerir. `Temsili stok` etiketi ve kaynak bilgileri filmde ayrıca gösterilir. Kullanıcının Pexels kaynak beyanı, her tekil dosyanın lisansının bağımsız doğrulandığı anlamına gelmez.
