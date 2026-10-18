# Özgün mobilya üretim sahnesi

Bu klasördeki kanepe, iç ahşap iskelet, malzeme örnekleri, ışıklar ve kamera bu video için kodla üretildi. Hazır model, stok fotoğraf, marka logosu, GUMA/Saloni ürün görseli veya başka videodan kare kullanılmadı.

**Görüntü anlamı:** Mobilya üretimindeki kumaş ve yapısal desteği anlatan temsili canlandırma. Gerçek bir GUMA ürünü, Saloni tesisi veya şirketlerin iç üretim düzenine dair belge değildir. Kullanıldığı sahnede `Temsili 3B canlandırma · Özgün üretim` yazısı gösterilmelidir.

## Dosyalar

- `create_scene.py`: Geometri, prosedürel kadife/meşe malzemesi, beş ışık, gerçek perspektif kamera, alan derinliği ve döşemenin yükseldiği animasyon.
- `original_furniture_reveal.blend`: Düzenlenebilir 10 saniyelik Blender sahnesi.
- `original_furniture_reveal.glb`: Aynı özgün modelin animasyonlu, 281 KB GLB aktarımı. WebGL/Three.js içinde gerçek kamera ile render edilebilir.
- `render_extra.py`: Ayrı kamera açıları ve GLB aktarımı. Workbench denemesi içerir; nihai görsel olarak önerilmez.
- `PROVENANCE.json`: İçerik kökeni.

GLB, prosedürel Blender doku düğümlerini taşımaz. Temel renk, metal ve pürüz değerlerini taşır. WebGL sürümünde kumaş ve ahşap dokusunu yeniden oluşturmak gerekir. Blender alan ışıkları glTF standardına aktarılamadığından WebGL ışıkları ayrıca kurulur.

## Tekrar üretme

```bash
blender -b -t 3 --python create_scene.py
blender -b original_furniture_reveal.blend -t 3 --python render_extra.py -- --glb
env XDG_CACHE_HOME=/workspace/guma-video/toolkit-v5/blender/cache blender -b original_furniture_reveal.blend -t 3 --python render_extra.py -- --angles
```

Blender 4.3.2 kullanıldı. Yazılım ücretsiz ve açık kaynaklıdır: https://www.blender.org/about/license/

Bu ortamda GPU yoktur. Eevee yazılım üzerinden render ederken çok yavaş çalıştığı için yüzlerce karelik Eevee render başlatılmadı. Cycles CPU çalışır; bu sistem paketinde OpenImageDenoise desteği bulunmadığından `use_denoising=False` gerekir. Bu teknik durum ücretsiz yazılımın ücretli bir lisans gerektirdiği anlamına gelmez.

Özgün kod ve sahne proje kullanımı için ücretsizdir. Blender'ın GPL lisansı, özgün render çıktısının kendisini GPL ile yayımlama zorunluluğu getirmez. Üçüncü taraf kaynak yoktur.
