# Etkin iş akışı: tam anlatımlı GUMA filmi

Mevcut `/workspace/halis` checkout'unu kullanın; `video-tools/full-reel` doğrudan `/workspace` altında ise o kökü kullanın. Kullanıcı açıkça istemedikçe Git worktree açmayın. Mevcut kullanıcı değişikliklerini koruyun.

Önce `video-tools/full-reel/README.md`, `docs/KAYNAKLAR.md` ve `docs/YAYIN_NOTLARI.md` dosyalarını okuyun. Bu proje toplu video üretimidir; kalıcı web sunucusu gerekmez. `tools/setup.sh` yalıtılmış Python ortamını hazırlar. `ffmpeg` ve `ffprobe` sistemde bulunmalıdır.

Önceki 99 saniyelik V5 kullanıcı tarafından reddedildi. **155,167313 saniyelik orijinal Ece sesinin tamamını, aynı sırada ve hızda koruyun.** Aktif final 164,2 saniyedir. Metni/sesi kısaltmayın; kullanıcının açık talebi olmadan bu kararı değiştirmeyin. Kullanıcının beğenmediği koltuk animasyonunu, AI koltuğu veya 3D fabrikayı geri getirmeyin. İlk bölümdeki hareketli yazı dilini ve anlamına göre seçilen gerçek çalışma görüntülerini esas alın. Kaynaklı şirket ilişkileri ile temsili iş görüntülerinin ayrımı açık kalmalıdır.

Ham ses ve Pexels dosyaları projede dağıtılmaz. Yerel girdiler mevcut değilse hazırmış gibi davranmayın. Eksik sesi yeniden üretmeyin, referans videosunu kullanmayın, kullanıcıdan zaten mevcut dosyayı tekrar istemeden önce yerel varlıkları araştırın. Tüm private medya varsayılan olarak `.gitignore` kapsamındadır.

Gerçek finalde `tools/check_full_narration.py` ses bütünlüğü kontrolünü ve FFmpeg baştan sona çözümleme kontrolünü çalıştırın. Değişen çıktı için süre, kare sayısı, renk, ses ve kaynak satırlarını denetleyin. Anlatımın içinde 50 bin TL'nin plan, 130 binin önceki kitle beyanı olduğu ayrımı korunmalıdır. Şirketin üretim/tedarik açıklaması finansman veya ücretsiz üretim kanıtı değildir.

Önceden kurulan Node/Blender/Remotion alternatifleri `video-tools/free-toolkit` içinde korunur fakat bu finalin üretimi onlara bağlı değildir. Remotion lisansı koşulludur; tüm yazılımları MIT diye sunmayın. GPU yoktur; ComfyUI/FLUX modeli kurulmuş değildir. Rastgele büyük model indirmeyin ve ücretsiz API hazırmış gibi davranmayın.

Kullanıcı, video/kapak/kaynak paketinin `istanbul582/halis` GitHub deposuna yüklenmesine açık izin verdi. Ham medyayı yayımlamayın. GitHub tesliminde gerçek yüklemeyi ve dosya indirme yanıtını doğrulayın. Codex workspace/sandbox/localhost bağlantıları bu kullanıcıda çalışmadı. Ortam taslağı kaydetmek GitHub'a yayımlamak veya ortamı Publish etmek değildir.
