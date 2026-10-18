# Ücretsiz üretim araçları: lisans ve uygulanabilirlik denetimi

Denetim tarihi: 18 Ekim 2026. Lisanslar resmî GitHub depolarından normal HTTPS ile okundu; kopyaları ve erişim sonuçları bu klasörde bulunur. Bu rapor kurulum yapıldığını göstermez: kurulum durumu proje paket dosyası ve çalıştırma testiyle ayrıca doğrulanmalıdır.

## Bu video için seçilecek küçük takım

| Araç | İşlevi | Doğrulanan lisans | Karar |
|---|---|---|---|
| [Three.js](https://github.com/mrdoob/three.js) | Gerçek perspektif kamera, ışık, 3B derinlik, malzeme, nesne çevresinde kamera hareketi | [MIT](https://github.com/mrdoob/three.js/blob/dev/LICENSE) | Ana 3B motor |
| [React Three Fiber](https://github.com/pmndrs/react-three-fiber) | Three.js sahnelerini React içinde yönetmek | [MIT](https://github.com/pmndrs/react-three-fiber/blob/master/LICENSE) | React/Remotion ile bağlantı |
| [Drei](https://github.com/pmndrs/drei) | Perspektif kamera, metin, ışık ve sahne yardımcıları | [MIT](https://github.com/pmndrs/drei/blob/master/LICENSE) | Sadece gereken yardımcılar |
| [Motion](https://github.com/motiondivision/motion) | Maske, geçiş, yay hareketi ve 2B katman animasyonları | [MIT](https://github.com/motiondivision/motion/blob/main/LICENSE.md) | Ücretsiz çekirdek; Motion+ satın alınmaz |
| [Tabler Icons](https://github.com/tabler/tabler-icons) | Tek bir çizgi dilinde özgünleştirilebilir SVG ikonlar | [MIT](https://github.com/tabler/tabler-icons/blob/main/LICENSE) | Tek ikon seti yeterli |
| [Blender](https://github.com/blender/blender) | Özgün 3B eşya, malzeme ve çevre üretmek; ışık ve kamera; görüntü katmanları | [GNU GPL v3, bütün olarak](https://github.com/blender/blender/blob/main/README.md#license) | Sistemde zaten var; CPU ile çalışır |
| [FFmpeg](https://ffmpeg.org/) | Kurgu çıktısını birleştirme, renk/ses işleme, MP4 kodlama, teknik kontrol | Kurulu derlemenin lisans bilgisi ayrıca `ffmpeg -L` ile görülür | Sistemde zaten var |

MIT lisansı ücretli API ya da abonelik gerektirmez ve ticari kullanım hakkı verir. Telif/lisans bildirimleri dağıtılan proje içinde korunur. Bu yazılım lisansları, sahnede kullanılan fotoğraf, video, font, 3B model veya marka işaretinin haklarını sağlamaz.

Remotion çıktısında kamera ve animasyonların tamamı aynı kare sayacından yürütülmeli. `useCurrentFrame()`/kareye bağlı dönüşümler kullanılmalı; bağımsız gerçek zamanlı Motion/Three döngüsüyle render yapılmamalı. Aksi hâlde önizleme ile çıktı arasında fark veya donmuş animasyon oluşabilir.

## Yararlı ama bu kurgu için gerekmeyen ikinci seçenekler

| Araç | Lisans | Neden hemen eklenmiyor? |
|---|---|---|
| [PixiJS](https://github.com/pixijs/pixijs) | [MIT](https://github.com/pixijs/pixijs/blob/dev/LICENSE) | Hızlı 2B parçacık/maske için güçlüdür. Ancak bu projede Three.js ve SVG/CSS katmanlarıyla örtüşür; somut bir sahne ihtiyacı doğarsa eklenir. |
| [Lucide](https://github.com/lucide-icons/lucide) | [ISC; bazı Feather kökenli ikonlarda MIT bildirimi de var](https://github.com/lucide-icons/lucide/blob/main/LICENSE) | Tabler ile aynı ihtiyacı karşılar; iki farklı ikon dilini karıştırmaya gerek yok. |
| [Diffusers](https://github.com/huggingface/diffusers) | [Apache-2.0, yalnızca yazılım](https://github.com/huggingface/diffusers/blob/main/LICENSE) | Yapay zekâ modelini çalıştıran yazılımdır. Model ağırlıklarının lisansını veya güçlü donanımı sağlamaz. |

## Yerel yapay zekâ ile görsel üretimi: ücretsiz lisans, donanım sınırı

[ComfyUI](https://github.com/Comfy-Org/ComfyUI) yazılımı [GPL-3.0](https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE) lisanslıdır; ücretsiz ve yerel çalıştırılabilir. Kullanılacak her modelin, LoRA'nın, eklentinin ve giriş görselinin hakları ayrıca değerlendirilir. Ücretsiz masaüstü yazılımı, ücretli bulut/API hizmetinin ücretsiz olduğu anlamına gelmez.

[FLUX.1-schnell model ağırlıkları](https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell) için resmî lisans Apache-2.0 olarak doğrulandı. FLUX deposunun kodu da Apache-2.0 lisanslıdır. FLUX.1-dev, Kontext-dev, Fill-dev ve diğer `dev` modellerinin lisansı aynı değildir; resmî README bunları Non-Commercial License altında listeler. Model adları birbirinin yerine kullanılamaz. Model çıktıları da üçüncü kişilerin marka/telif/kişilik haklarını otomatik olarak çözmez.

Mevcut ortamda 32 GiB cgroup bellek limiti ve yaklaşık 4 CPU kotası var. `nvidia-smi` yok; varsayılan Python'da Torch yok. GPU bulunduğunu gösteren kanıt yok. ComfyUI'nin resmî README'si CPU çalıştırmayı desteklediğini belirtiyor; ancak burada büyük FLUX modellerini indirip CPU üzerinde profesyonel görsel üretim döngüsü kurmak verimli değildir. Büyük model indirilmedi ve ComfyUI kurulmuş gibi sunulmamalı. Bu iş için hemen uygulanabilen yol: mevcut Blender ile özgün 3B görseller + Three.js ile kamera + kullanıcının stoklarının anlamlı detaylarda kullanılması.

## Remotion hakkındaki önemli ayrım

[Remotion'ın lisansı MIT değildir.](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) Şu gruplar ücretsiz lisansa uygundur: bireyler, en fazla 3 çalışanı olan kâr amaçlı kuruluşlar, kâr amacı gütmeyen kuruluşlar ve henüz ticari kullanım yapmayan değerlendirmeler. Uygun kişiler ticari video/görüntü üretebilir. Diğer şirketlerde şirket lisansı gerekir. Remotion'ın kurulmuş olması herkes için sınırsız ücretsiz kullanım anlamına gelmez. Bu projeye eklenen Three/Motion/Tabler kitaplıklarının MIT lisansları bu ayrı koşulu değiştirmez.

## Uygulanabilir sonuç

Yeni bir paket tek başına kurgu kalitesini yükseltmez. Kullanıcının eleştirisi, genel stokla açılması ve görsellerin konuşulan iddiayı taşımamasıyla ilgili. Yeni açılışta her kadrajın ayrı bir görevi olmalı: gerçek alıntıyı göstermek, açıklanan bütçeyi diğer başlangıç koşullarıyla ilişkilendirmek veya üretim-satış ilişkisini anlaşılır yapmak. Özgün 3B nesneler görsel metafor olarak etiketlenmeli; gerçek GUMA ürünü/fabrikası gibi sunulmamalı. İlk saniyelerde rastgele oda veya kumaş stoğu yerine bu anlatı kurulmalı.

## Saklanan kanıtlar

- `fetch-manifest.json`, `fetch-supplement.json`, `fetch-final.json`: URL, HTTP sonucu ve dosya boyutu.
- `*-license.txt`: okunan lisansların kopyaları.
- `*-readme.txt`: resmî proje açıklamaları.
- `runtime.json`: GPU/Torch/Blender/FFmpeg/Node ve bellek kontrolü.
- Hugging Face ve blender.org sayfaları normal erişimde 403 verdi. Erişim engeli aşılmadı. FLUX-schnell lisansı ve Blender lisans bilgisi resmî GitHub deposundan doğrulandı.
