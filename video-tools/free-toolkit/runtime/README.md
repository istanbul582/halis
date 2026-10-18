# Ücretsiz hareket, 3D ve kamera araç seti

Bu klasör yalnızca paket listesi değildir: sürümleri kilitli bir Node projesi, tekrar kurulabilir betik ve bu ortamda render edilmiş gerçek 3D kamera testi içerir. Eklenti kurmak, sahnenin anlatımla bağlantısını veya kurgunun kalitesini kendiliğinden düzeltmez; bu altyapı sahne tasarımını uygulamak içindir.

## Kurulum

```bash
cd video-tools/free-toolkit/runtime
bash setup.sh
npm run proof:stills
npm run proof
```

`setup.sh` yönetici yetkisi istemez, küresel paket kurmaz. `npm ci` sürüm kilidini kullanır; tekrar çalıştırılabilir. Node 20 veya üzeri ve sistem Chromium'u gerekir. İstenirse `GUMA_NPM_CACHE` ile yazılabilir önbellek yolu, `CHROMIUM_PATH` ile tarayıcı yolu değiştirilebilir. Varsayılan önbellek bu bulut ortamında yazılabilen `/workspace/guma-video/tooling/npm-cache` dizinidir.

## Gerçekten çalışan parçalar

| Araç | Kullanım | Lisans |
| --- | --- | --- |
| Three.js 0.186.1 | Geometri, malzeme, ışık, gölge ve fiziksel perspektif kamera | MIT |
| React Three Fiber 9.8.2 | 3D sahnenin React içinde kurulması | MIT |
| Drei 10.7.9 | Örnekte yumuşatılmış köşeli gerçek 3D geometri | MIT |
| Motion 14.3.0 | Kamera yolunun kareye bağlı hız eğrisi | MIT |
| Tabler Icons React 3.49.0 | Açık lisanslı vektör ok işareti | MIT |
| React / React DOM 19.3.1 | Sahne bileşenleri | MIT |
| Remotion 4.0.536 | Kareye bağlı kompozisyon ve MP4 dışa aktarımı | Özel lisans; aşağıya bakın |
| @remotion/three 4.0.536 | Remotion ile 3D sahnenin senkron çalışması | Paket MIT; Remotion çekirdeği ayrı lisanslı |

Remotion çekirdeği koşulsuz MIT değildir. Bireysel kullanım ve en fazla üç çalışanı bulunan kâr amaçlı şirketler ücretsiz kullanabilir; daha büyük şirketler için ücretli şirket lisansı gerekir. Güncel koşullar: <https://github.com/remotion-dev/remotion/blob/main/LICENSE.md>. Buraya ücretli API veya ücretli hizmet eklenmedi. Kapsamın dışına çıkan bir kullanımda Remotion yerine Blender + FFmpeg hattı kullanılabilir.

Kurulu paketlerin gerçek sürüm ve lisans alanları `DEPENDENCY_LICENSES.json` içindedir; güncellemek için `npm run audit:licenses` çalıştırılır. Bağımlılıkların kendi lisans dosyaları `node_modules` altında korunur. Daha geniş yazılım/model lisans incelemesi üst dizindeki `audit/` klasöründedir.

## Kamera testinin yaptığı

`src/index.tsx` içinde hiçbir markanın ürün fotoğrafı veya modeli kullanılmadan geometrik parçalardan temsili bir koltuk oluşturulur. Kamera gerçekten 3D uzayda yer değiştirir; öndeki ve arkadaki nesnelerin ilişkisi perspektifle değişir. Bu bir fotoğrafın üstüne uygulanan büyütme efekti değildir.

Kare 0, 29 ve 59 ayrı PNG olarak dışa aktarılır. `npm run proof` komutu ayrıca 720 × 1280, 30 fps, 60 karelik iki saniye H.264 çıktı üretecek şekilde yapılandırılmıştır. Kamera ve yazı animasyonu `useCurrentFrame()` ile hesaplanır; duvar saati, rastgele değer veya CSS zamanlayıcısı kullanılmaz. Aynı kare tekrar istendiğinde aynı kamera konumu hesaplanır.

Doğrulanan çıktı üç farklı PNG karesidir; `PROOF_REPORT.json` dosya özetlerini ve görüntü farkı ölçümünü içerir. İlave 60 kare MP4 testi yazılım sürücüsünde yavaş ilerlediği için ana film renderına CPU bırakmak üzere durduruldu. Bu araç setinin MP4 kamera testini tamamladığı iddia edilmez. Üretim için kısa 3D klipleri düşük çözünürlükte önceden render edip yüksek çözünürlükte metinle birleştirmek daha ekonomiktir.

Bu ortamda `gl: 'swiftshader'` WebGL bağlamı açamadı. Doğrulanmış ayar:

```js
browserExecutable: '/usr/bin/chromium',
chromiumOptions: {gl: 'swangle'}
```

Bu seçenek Chromium'u ANGLE üzerinden SwiftShader yazılım sürücüsüyle çalıştırır. CUDA GPU gerektirmez; CPU ile sahne karmaşıklığı arttıkça render süresi uzar. Chromium/Three.js sürümünden gelen `Clock` ve `PCFSoftShadowMap` kullanım dışı uyarıları renderı durdurmaz. Üretim sahnesine alınmadan önce ışık, malzeme ve kadraj yeniden tasarlanmalıdır; teknik test final görsel kalite örneği değildir.

## Görsel üretimi ve ücretsiz modeller

Blender 4.3.2 bu ortamda ayrıca kurulu olduğundan özgün 3D obje, malzeme, ışık ve kamera üretimi ücretli API olmadan yapılabilir. Three.js ile de yukarıdaki sahne gibi özgün geometri üretilebilir. Bunlar çalışan görsel üretim araçlarıdır.

ComfyUI veya bir yapay zekâ modelinin deposunu indirmek modeli hazır hale getirmez. Model ağırlıklarının lisansı, dosya boyutu, bellek ve GPU gereksinimleri ayrıca değerlendirilmelidir. Bu çalışma kapsamında büyük model ağırlıkları indirilmedi; yerel bir yapay zekâ görsel üreticisinin hazır olduğu iddia edilmez. Yazılımın açık kaynak olması tüm modellerin ticari kullanıma ücretsiz olduğu anlamına gelmez.

## Medya ve kaynaklar

Kamera testindeki geometri ve sahne kodu bu proje için üretildi. Koltuk herhangi bir GUMA/Saloni ürünü olarak sunulmaz; ekranda temsili canlandırma olduğu yazılıdır. Örnek videoların görüntüsü, sesi veya marka logosu bu teste kopyalanmadı. Kaynak etiketi ve alıntıların ekrandaki kullanımı nihai filmin ayrı editoryal katmanında yapılır.

Test edilen bulut ortamı: Node 24.19.0, npm 11.9.0, Chromium 154.0.8037.57, Blender 4.3.2. Paket sürümleri `package-lock.json` ile sabittir. `setup.sh` mevcut çalışma bağımlılıklarına dokunmadan ayrı bir temiz klasörde `npm ci` ile test edildi ve başarıyla tamamlandı. `NPM_AUDIT.json` raporu sıfır bilinen açık bildiriyor; raporun alındığı anda bilinen kayıtları kapsar. `node_modules` ve render çıktıları Git'e eklenmez; teslim edilecek film ayrıca video teslim klasörüne konur.
