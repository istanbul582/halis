# GUMA / Bir markanın başlangıcı — v5

1080×1920, 30 fps, 99 saniye. Ece anlatımı 0–90 sn; kaynaklar 90–96 sn; özgün takip animasyonu 96–99 sn.

Bu kurgu marka videosunun sesini, görüntüsünü veya ekran görüntüsünü kullanmaz. İlk cümle haberde Yavuz Selim Bayraktar'a atfedilen alıntının, kullanıcının sağladığı Ece anlatıcısı tarafından okunmasıdır. İlk karede kişi, yayın ve tarih atfı gösterilir.

## Yerel çalıştırma

Bu klasörün `node_modules` bağlantısı `../runtime/node_modules` dizinini kullanır (`ln -s ../runtime/node_modules node_modules`). Bağımsız kurulumda `npm install --cache /workspace/guma-video/tooling/npm-cache` çalıştırılabilir; paketin sürümleri `package.json` içinde sabitlenmiştir. `npm run stills` temsilî PNG kareleri; `npm run render` tam MP4 üretir. Tarayıcı `/usr/bin/chromium`dur. Gerçek 3D kamera ön render ayarında `chromiumOptions.gl='swangle'` kullanılır. Ana filmin DOM render'ında bu GL zorlama ayarı yoktur; bu ortamda gereksiz yazılım GPU maliyetini önler. Ana filmde önceden render edilmiş 3D görüntüler ve Remotion'un kare saatine bağlı animasyonlar birleştirilir.

`public/mixed_audio.wav` kullanıcının seslendirmesini içerir; ham ses dosyasını GitHub'a yayımlamak gerekmez. İlgili kullanıcı dosyası yerelde bu adla konur. `public/workshop.mp4` ve `public/design.mp4` kullanıcının stoklarından seçilen kısa, temsili planlardır. Dosyaların kendisini yeniden dağıtmak yerine kaynak numarası ve kurgu bilgisi kaydedilir.

## Görsel yaklaşım

Açılışta stok yoktur. Kullanıcının karşısına bir iddia değil, kurucunun açıkça yayımlanmış sözü ve kaynağı çıkar. Özgün mobilya sahnesi temsili olarak kullanılır. Bütçe, önceki kitle ve üretim ilişkisi ayrı kavramlardır; her biri kendi kaynağı ve kapsamıyla etiketlenir. Sayılar başarı veya mali doğrulama gibi sunulmaz.

- 0–14,855: Haberdeki aile ilişkisi, görev ve sektör bilgisi desteği.
- 14,855–21,010: Serinin gerçek başlığı ve yaklaşık 50 bin TL'lik açıklanan bütçe planı.
- 21,010–25,800: Önceden ulaşıldığı söylenen 130 bin kişilik takipçi kitlesi.
- 25,800–31,810: Bütçe, kitle, bilgi ve üretim başlıklarını bağlayan özgün hareketli şema.
- 31,810–46,020: Şirketin açıkladığı Saloni üretimi / GUMA satışı ilişkisi. Gerçek perspektif kameralı, özgün ve temsili 3D yapı açılımı.
- 46,020–59,720: Somut iş adımları; 46,020–48,445 Pexels 6790438, 48,445–49,500 Pexels 5384976; devamında bu video için AI ile oluşturulmuş malzeme etüdü.
- 59,720–90,000: Emek, erişim, izleyici soruları ve tamamlanan kapanış.
- 90,000–99,000: Kaynak kartı ve özgün takip çağrısı.

## Kaynakların sınırı

50 bin TL açıklanan plandır. 130 bin, kurucunun önceki kitleye dair kendi beyanıdır. Saloni ilişkisi şirketin açık metnidir. Aile ilişkisi ve görev bilgisi haberde yer alır. Bu bilgiler bedelsiz üretimi, sermaye aktarımını, ortaklık oranlarını veya aldatmayı kanıtlamaz; kurgu böyle bir sonuca varmaz.

## Görsel kökeni

`hero-ai-polish.png`, tarafımızdan Blender'da yazılan özgün koltuğun AI ile görsel olarak düzenlenmiş tek karesidir. Bu görselin kendisi 3D kamera videosu değildir. `original-material-study.png` bu kurgu için native image generation ile üretilen temsili malzeme kompozisyonudur. Bunlar ücretsiz yerel FLUX / ComfyUI çıktısı olarak sunulmaz. Gerçek 3D planın kaynağı özgün `.blend` / `.glb` sahnesidir; yazılım kamerası ve geometri hareketi ön render edilir. `public/production-camera.mp4`, 540×960 çözünürlükte hesaplanmış 30 perspektif kareden gelir. Hareket FFmpeg `minterpolate` ile ara karelere dönüştürülüp 14,233 sn / 720×1280 / 30 fps olarak hazırlanır; bu, her karenin 1080p olarak yeniden hesaplandığı iddiası değildir. Filmde bu plan 31,810–46,020 sn aralığında gösterilir. Kamera bir yandan diğer yana kayıp yükselirken koltuğun iç parçaları açılır.

Pexels kaynakları kullanıcı beyanı ve yüklediği dosyaların numarasına dayanır; sayfa ve lisansların bağımsız doğrulandığı iddia edilmez. Kendi kendine yeten lisans garantisi verilmez. Manrope ve DM Serif Display fontları SIL OFL ile dağıtılır; lisans dosyaları `public/fonts` içindedir. Remotion'un kendi ticari lisans koşulları ayrıca geçerlidir.


## Çıktı ve yeniden üretim

```sh
npm run stills
npm run render
```

`STILL_FRAMES=1110 node render.mjs --stills` 37. saniyedeki gerçek 3D kamerayı gösterir. `FRAME_RANGE=0,1109 node render.mjs` yalnızca ilk 37 saniyeyi üretir. Tam çıktı `out/GUMA_v5_full.mp4` konumundadır. Bu ortamda Remotion çıktısı yuv420p talebine rağmen full-range yuvj420p olarak işaretlendiği için `finalize-video.sh`, renk aralığını full→limited BT.709 olarak dönüştürür ve standart yuv420p H.264 üretir. Bu geçişte video yeniden kodlanır; AAC stereo ses aynen kopyalanır. `+faststart` metaveri yerleşimi korunur.

Yeniden üretim için gereken yerel medya adları: `public/mixed_audio.wav`, `workshop.mp4`, `design.mp4`, `hero-ai-polish.png`, `original-material-study.png`, `production-camera.mp4` ve `public/fonts/`. İlk üç dosya kullanıcının sesini / ham stoklarını içerdiği için kaynak kodundan ayrı tutulur. Temsili 3D model `furniture.glb`, yapay zekâ görsellerinin `.provenance.json` kayıtları ve font lisansları da korunur.

`python verify_film.py` tam MP4 akışını çözer; süre, kare sayısı, çözünürlük, video/ses biçimi, ses seviyesi ve hızlı web açılışı için MP4 atom sırasını ölçer. Atom sırası gerekirse ses/görüntüyü yeniden kodlamadan düzeltilir. Ölçümler `out/FINAL_VERIFICATION.json` içine yazılır. Bu teknik doğrulama, telif/izin ya da izlenme garantisi değildir.

Renk uyumluluğu ve son kontrol: `npm run finalize` veya `bash finalize-video.sh out/GUMA_v5_full.mp4`. `npm run render` bunu otomatik çalıştırır. Helper önce gerçek giriş piksel/aralık/matris etiketlerini inceler. Bu çıktı yuvj420p / pc / bt470bg olduğu için FFmpeg scale filtresi giriş matrisini otomatik okuyarak BT.709 / tv / yuv420p’ye dönüştürür. Zaten standart sınırlı aralık olan çıktıda dönüşümü atlar; beklenmeyen etiketi tahmin etmek yerine durur. Aday çıktı teknik kontrolden geçmeden özgün dosyanın yerini almaz.
