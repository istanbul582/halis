# Video üretim araçları ve yeni GUMA kurgusu

Bu araç seti, görsel seçimini ve kurguyu uygulamak için kurulup test edildi. Yeni film 90 saniyelik anlatım, 6 saniyelik kaynaklar ve 3 saniyelik özgün takip kapanışından oluşur. Başlangıçta stok kullanılmaz. Açılış, gazetede aktarılan kurucu açıklamasını Ece'nin mevcut anlatımıyla verir; kaynak kişinin gerçek sesi veya videosu kullanılmaz.

## Kurulan ücretsiz araçlar

| Araç | Bu projede görevi | Resmî depo |
|---|---|---|
| Three.js, React Three Fiber, Drei | Gerçek 3D sahne, kamera, ışık ve geometri | [Three.js](https://github.com/mrdoob/three.js), [R3F](https://github.com/pmndrs/react-three-fiber), [Drei](https://github.com/pmndrs/drei) |
| Motion | Kare zamanına bağlı hareket eğrileri | [Motion](https://github.com/motiondivision/motion) |
| Tabler | Tutarlı açık lisanslı vektör işaretler | [Tabler Icons](https://github.com/tabler/tabler-icons) |
| Blender 4.3.2 | Özgün mobilya modeli, iç iskelet, malzeme ve kamera hazırlığı | [Blender](https://github.com/blender/blender) |
| PySceneDetect ve OpenCV | Seçilen Kot/Mavi referansında kesme adayı analizi | [PySceneDetect](https://github.com/Breakthrough/PySceneDetect), [OpenCV](https://github.com/opencv/opencv) |
| OpenTimelineIO | Medya gömmeden düzenlenebilir 90 saniyelik kurgu kararları | [OTIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) |
| NumPy ve SciPy | Özgün ses sentezi, filtreleme ve konuşma sırasında müziği kısma | [NumPy](https://github.com/numpy/numpy), [SciPy](https://github.com/scipy/scipy) |

Remotion 4.0.536, kare zamanlaması ve dışa aktarım için ayrıca kullanılır. **Remotion koşulsuz MIT değildir:** bireyler, en fazla üç çalışanı olan kâr amaçlı kuruluşlar ve lisansın saydığı diğer gruplar ücretsiz kullanabilir. [Güncel lisans](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md). Motion+ veya ücretli API eklenmedi.

ComfyUI ve FLUX-schnell lisansları incelendi; bu GPU'suz ortamda büyük model ağırlıkları indirilmedi ve yerel AI üreticisi kurulmuş gibi sunulmaz. Filmdeki iki temsili görsel, Codex'in yerleşik görsel üretimiyle hazırlandı; bu görsellerin ComfyUI veya Blender renderı olduğu iddia edilmez. Birinde bu proje için oluşturulan Blender modeli referans alındı. Köken JSON'ları film varlıklarının yanındadır.

## Doğrulananlar

- Kilit dosyasından temiz Node kurulumu geçti; `npm audit` kontrolünde 0 bilinen açık raporlandı.
- GPU olmadan gerçek perspektif kamerayla üç farklı PNG üretildi: [0](runtime/proof/camera-0.png), [29](runtime/proof/camera-29.png), [59](runtime/proof/camera-59.png). Bunlar teknik testtir; filmin tasarım örneği değildir.
- Chromium 154 için çalışan WebGL seçeneği `gl: 'swangle'`. `swiftshader` seçeneği bu sürümde bağlam açamadı.
- PySceneDetect, referansın 2322 karesini işledi. Eşik 27'de 10 sahne adayı buldu; 22/32 karşılaştırması saklandı. Bu, elle doğrulanmış plan sayısı veya kalite puanı değildir.
- OTIO dosyası yazılıp yeniden okundu: 90,000 saniye, 9 ses kesiti, 8 geçiş. Haricî bir kurgu programına içe aktarma bu ortamda test edilmedi.
- Python paket bağımlılıkları ve gerçek `scipy.signal` filtreleme işlemleri kontrol edildi.

## Yeniden kurulum

Bu dizinden:

```bash
bash runtime/setup.sh
bash analysis-tools/setup.sh
cd runtime
npm run proof:stills
```

Node 20+, Python 3.12, Chromium ve FFmpeg gerekir. Modeli yeniden üretmek için Blender gerekir. Bu bulut ortamında Node 24.19.0, Chromium 154 ve Blender 4.3.2 kullanıldı. Betikler sistem paketlerini veya yönetici ayarlarını değiştirmez. Sürümler `package-lock.json` ve `requirements.lock.txt` içinde kilitlidir. Ayrıntılar: [Node projesi](runtime/README.md), [analiz ve zaman çizelgesi](analysis-tools/README_TR.md).

Mevcut makinede kurulum betiği çalıştırılıp doğrulandı. Tekrarlanabilir kurulum ve başlangıç talimatları, bulut ortamının `install_script` ve `start_skill` taslağına kaydedildi; kopyaları `environment/` içindedir. Kalıcı ortam sürümü için Ortam Ayarları'nda taslağı inceleyip kaydetmek ve ortamı yayımlamak gerekir. Taslak kaydı, ortamın yayımlandığı veya yeni görevde geri yüklemenin test edildiği anlamına gelmez.

## Düzenleme dosyaları

- `film/`: Tam videonun Remotion kompozisyonu, özgün görselleri ve kareye bağlı animasyon kodu.
- `blender/`: Düzenlenebilir özgün model, GLB, sahne betiği ve prosedürel dokular.
- `runtime-generated-bake/`: Üretim sahnesinin 30 gerçek 3D kamera karesini yeniden hesaplayan kaynak. Yeniden hesaplamak için `ln -s ../runtime/node_modules runtime-generated-bake/node_modules`, ardından bu klasörde `node render.mjs`; film klasöründe `bash prepare-camera.sh` çalıştırılır. Var olan bağımlılık bağlantısı tekrar oluşturulmaz.
- `editorial/`: Metin, altyazı, kaynak ilişkileri, ses kesim haritası ve özgün ses tasarımı kodu.
- [Düzenlenebilir OTIO](analysis-tools/results/GUMA_v5_full_90s.otio): ses ve görsel yer tutucuları yeniden bağlanır.
- [Üretim yaklaşımı](URETIM_YAKLASIMI.md): hangi bilginin hangi görselle anlatıldığı.
- [Kaynaklar ve kullanım notları](KAYNAKLAR.md): alıntı, AI, stok, font ve ses kökeni.

Ham kullanıcı anlatımı, ham Pexels klipleri ve dört referans video depoya eklenmez. Film kodunun yeniden render edilmesi için yetkili kullanıcı, 99 saniyelik miksini `film/public/mixed_audio.wav` olarak yerleştirir; kullanıcı stoklarından 6790438 ve 5384976 dosyaları da sırasıyla `film/public/workshop.mp4` ve `film/public/design.mp4` olarak sağlanır. Anlatımı yeniden kesmek isteyenler `GUMA_NARRATION_WAV` değişkeniyle orijinal anlatımı gösterir; cümle/altyazı girdileri `editorial/inputs` içindedir. İnternet bağlantısı yalnız kurulum ve haricî dosya edinimi için gerekir; render yerel varlıklarla yapılır.

Bağımlılık lisansları `audit/`, `runtime/DEPENDENCY_LICENSES.json`, `analysis-tools/licenses/` ve `font-licenses/` içinde saklanır. Yazılım lisansı, üçüncü kişiye ait görüntü, ses, marka veya font kullanım hakkının yerine geçmez.
