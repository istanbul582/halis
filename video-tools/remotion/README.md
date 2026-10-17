# GUMA — Remotion deneme projesi

Kullanıcının seçtiği Kot/Mavi referansının fotoğraf ağırlıklı görsel dili için hazırlanan kısa teknik ve tasarım denemesidir. Referansın görüntüsü, sesi veya marka tasarımı kullanılmaz.

## Kurulum

Node.js, npm, Chromium ve FFmpeg gerekir. Bu Codex ortamında Node 24.19.0, npm 11.9.0, Chromium 154 ve FFmpeg doğrulandı. Remotion ve ilgili paketler `package-lock.json` içinde sabittir.

```sh
npm ci --cache /workspace/npm-cache --no-audit --no-fund
node render.mjs --stills
npm run render
```

`render.mjs` Chromium'u `/usr/bin/chromium` yolundan çalıştırır. Bu proje otomatik bir GitHub Actions iş akışı başlatmaz.

## Yerel medya

Stok görüntülerin bağımsız ham kopyaları bu GitHub projesine eklenmez. Codex ortamında `public/` altında hazırlanmıştır. Yeni bir kurulumda kullanıcı kullanım hakkına sahip olduğu dosyaları şu adlarla yerleştirmelidir:

- `public/material.mp4`: kumaş makrosu; kullanıcı tarafından Pexels / 7677808 kaynağıyla sağlandı.
- `public/room.mp4`: genel koltuk görüntüsü; Pexels / 15887137.
- `public/creator.mp4`: kamera, telefon ve eller; Pexels / 7806870.

Görseller GUMA/Saloni ürününü, tesisini veya çalışanını göstermez. Dosya düzeyinde Pexels lisansı bağımsız doğrulanmamıştır. Anlatıcı kaydı ayrıca kullanıcı tarafından sağlanır; ham ses bu projeye dağıtılmaz. Mevcut `render.mjs` sessiz görüntü çıkarır. Teslim MP4'ünde kullanıcının sağladığı anlatıcının ilk 17 saniyesi kullanılır.

## Kılavuzlar ve lisanslar

- Remotion: https://github.com/remotion-dev/remotion
- Resmî Remotion Agent Skills: https://github.com/remotion-dev/skills
- Kılavuz kurulum komutu: `npx skills add remotion-dev/skills`.
- Bu denemede kılavuz deposunun `1441a11e95db35443bd76bb318386c0d3ca00053` sürümü okunmuştur.
- Remotion'ın özel lisansı vardır. Bireyler, en fazla üç çalışanı olan ticari kuruluşlar ve uygun değerlendirme kullanımları ücretsiz lisans kapsamındadır. Tam koşullar: https://github.com/remotion-dev/remotion/blob/main/LICENSE.md
- Yerel fontlar Google Fonts kaynaklı Manrope, Barlow Condensed ve DM Serif Display'dir; SIL OFL lisansları `public/fonts/` altındadır.

Hareketler kare zamanından üretilir; gerçek zamanlı CSS animasyonu veya rastgele zamanlayıcı kullanılmaz. Aynı kare yeniden üretilebilir. Bu proje otomatik olarak iyi tasarım veya belirli izlenme sayısı sağlamaz; kısa bir stil denemesinin değerlendirilmesine hizmet eder.
