# GUMA: yeni açılış ve kısa tam kurgu

Bu klasördeki sesler, kullanıcının sağladığı **Ece anlatımından** cümle bütünlüğü korunarak kesildi. Marka kaynak videosunun veya WhatsApp stil örneklerinin sesi kullanılmadı. Yeni ses üretimi, ses klonlama ya da ücretli API yapılmadı.

- `GUMA_v5_preview_39s.wav`: 39,255 saniyelik yeni açılışın bağımsız kısa kurgusu.
- `GUMA_v5_full_90s.wav`: 90,000 saniyelik tamamlanmış anlatım.
- Aynı isimli `.json`: kaynak kesimleri, yeni zamanlar, cümleler, kısa altyazılar, sahne amacı ve kaynak adresleri.
- `_captions.json` / `.srt`: render için kısa parçalar. Kelime karaoke zamanları değildir.
- `_metin.txt`: yeni sırayla okunan metin.
- `editorial_validation.json`: süre, format, cümle bütünlüğü ve altyazı sınırı kontrolleri.

## Yeni editoryal tercih

Başlangıçta genel bir mobilya stok görüntüsü yerine kurucunun kendi açıklaması var: “Dayım Haluk Özbek, Guma’nın doğuş hikayesinde önemli bir paya sahip.” Bunu hemen, aynı haberde verilen görev ve desteğin açıklanan kapsamı izliyor. İzleyicinin göreceği somut mesele, marka kurarken para dışında hangi erişimlerin ve işlerin gerektiği.

Alıntı, Ece'nin bu sözleri aktarmasıdır; söz sahibinin gerçek ses kaydı gibi sunulmamalıdır. İlk kareden **“Yavuz Selim Bayraktar · Yıldırım Gazetesi · 06.10.2025”** atfı görünmelidir. Açılış alıntısının ardından metin bilgi desteğinin kapsamını da verdiğinden, cümle aile ilişkisi üzerinden tek başına bırakılmıyor.

90 saniyelik versiyon önceki 155 saniyelik metindeki aynı bilgilerin tekrar sayıldığı bölümü ve genel öğütlerin bir kısmını çıkarır. İlk cümleleri yeniden seslendirmez; yapay bir cümle kurmak için kelime birleştirmez. Kesimler konuşma aralarındadır; 25 ms çapraz geçişler konuşmasız payları yumuşatır.

## Kaynakları görselde doğru kullanma

1. **Haber:** kurucu açıklaması ve haberin verdiği görev. Aile ilişkisi zaten haberde açıklandığından “gizli bağlantı ortaya çıktı” denmemeli.
2. **Birinci gün videosu:** yaklaşık 50 bin TL bir **bütçe planı**; gerçekleşmiş gider veya doğrulanmış marka değeri olarak gösterilmemeli. Tam versiyondaki 130 bin, anlatıcının **önceden ulaştığını söylediği kitle**; GUMA'nın güncel takipçi sayısı değildir.
3. **Şirket kullanım şartları:** Saloni tarafından üretim ve GUMA aracılığıyla satış açıklaması. Ortaklık payı, sermaye aktarımı ya da bedelsiz üretim sonucu çıkarılmaz.

Üretilen stüdyo, mobilya veya üretim görselinde “Temsili 3D canlandırma” etiketi bulunmalı. Sahte resmi belge, fatura veya finans paneli hazırlanmamalı. Kaynak metinleri özgün tipografiyle yeniden dizilebilir; şirketin site tasarımı ve logosu taklit edilmez.

## Teknik sınırlar ve kontrol

Kaynak cümle zamanları, daha önce gözden geçirilmiş Türkçe ASR dökümünden gelir. Kısa altyazı parçalarının cümle içi sınırları önceki `segments.json` dosyasındaki **yaklaşık** zamanları devralır. Bunlar zorlanmış kelime hizalaması değildir; kelime karaoke animasyonunda kesin zaman diye kullanılmaz.

Sesler 48 kHz, mono, 24 bit PCM WAV'dır. 90 saniyelik ses FFmpeg ile tamamen çözüldü; ölçülen ses yüksekliği **−15,89 LUFS**, gerçek tepe **−1,50 dBTP**. Altyazı zamanları ses sınırları içinde ve sıralıdır. Çıktı doğrulaması yeni bir dinleme veya yeni ASR kontrolü yapıldığı anlamına gelmez; kaynak döküm ile kesim haritası karşılaştırılmıştır.

Yeniden üretim: `python build_editorial.py`. Script yalnız yerel kaynak anlatıma ve mevcut cümle/altyazı JSON'larına ihtiyaç duyar; bu kullanıcı kayıtları depoya yüklenmek zorunda değildir.
