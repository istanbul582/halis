"""Re-cut the user's own narrator at complete sentence boundaries.

Source clips are never taken from the brand video or the WhatsApp references.
Per-sentence timing follows the existing reviewed transcript. Short caption
timing is inherited from the earlier, explicitly approximate phrase timings.
"""
from pathlib import Path
import os
import json
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('GUMA_NARRATION_WAV', ROOT / 'USER_NARRATION_WAV_RELINK_REQUIRED.wav'))
DATA = ROOT / 'inputs'
SR = 48000
CROSSFADE = 0.025

SOURCES = {
    'article': {
        'label': 'Yıldırım Gazetesi · 06.10.2025',
        'url': 'https://www.yildirimgazetesi.com/inegollu-mobilyaci-gencler-inanilmazi-basardi',
        'scope': 'Kurucunun açıklaması ve haberde verilen görev; bağımsız mali doğrulama değildir.',
    },
    'first_video': {
        'label': 'GUMA · 1. gün videosu',
        'url': 'https://www.youtube.com/shorts/nnUXsnz3Wi0',
        'scope': 'Açıklanan bütçe planı ve anlatıcının önceki takipçi beyanı; gerçekleşen gider/değerleme değildir.',
    },
    'company_terms': {
        'label': 'gumastore.com · Kullanım Şartları',
        'url': 'https://gumastore.com/pages/kullanim-sartlari',
        'scope': 'Şirketin üretim/satış ilişkisine dair açıklaması; ortaklık paylarını ya da bedelsiz üretimi kanıtlamaz.',
    },
}

PREVIEW = [
    (54.20, 58.68, 'quote', 'article', 'İlk karede konuşanın adıyla açık atıf. Giriş malzeme stoku değil, somut kurucu açıklaması.'),
    (58.84, 63.88, 'role', 'article', 'Alıntıda geçen kişinin haberdeki görevi, iki açık isimle gösterilir.'),
    (63.98, 69.08, 'support_scope', 'article', 'Desteğin açıklanan kapsamı: sektörü tanıma bilgisi. Para aktarımı/bedelsiz üretim simgesi kullanılmaz.'),
    (0.00, 6.18, 'budget_plan', 'first_video', '50 bin TL yalnız plan etiketiyle gösterilir; masaya para düşürülmez.'),
    (35.60, 48.08, 'production', 'company_terms', 'Üretim ve satış rolleri ayrılır. Sahne gerçek GUMA fabrikası gibi sunulmaz.'),
    (147.55, 153.65, 'question', None, 'Görülen üç koşul aynı kadraja bağlanır. Suçlama/itiraf çağrışımı yerine başlangıç sorusu.'),
]

FULL = [
    (54.20, 69.08, 'family_and_context', 'article', 'Kendi sözleriyle başlangıç, haberdeki görev ve bilgi desteğinin kapsamı. Alıntı ilk kareden kişi+haberle ilişkilendirilir.'),
    (0.00, 6.18, 'budget_plan', 'first_video', 'Sonuç/gider gibi değil açıklanan bütçe planı olarak görselleştirilir.'),
    (12.05, 16.84, 'previous_audience', 'first_video', '130 bin, kurucunun daha önce ulaştığını söylediği kitle. GUMA güncel takipçi sayısı değildir.'),
    (16.90, 22.96, 'budget_question', None, 'Yeni bir iddia eklemeden izleyiciye değerlendirme sorusu.'),
    (33.87, 48.08, 'production', 'company_terms', 'Şirketin açıkladığı üretim/satış ilişkisi; açık şirket metni kısa doğru alıntıyla gösterilir.'),
    (90.95, 104.70, 'actual_work', None, 'Üretici, numune, malzeme, tanıtım ve ilk müşteri: birbirine bağlı somut işler.'),
    (104.82, 115.45, 'work_and_access', None, 'Tasarım/pazarlama emeği ve açıklanan erişimler birlikte değerlendirilir.'),
    (122.35, 134.50, 'viewer_questions', None, 'İzleyiciye üç kullanılabilir soru: bütçe neyi karşıladı, hangi imkân vardı, kendisi ne kurmalı?'),
    (147.55, 155.10, 'final_question', None, 'Tamamlanmış final sorusu ve kullanıcının verdiği özgün anlatıcıyla yorum daveti.'),
]

sentences = json.loads((DATA / 'sentences.json').read_text())
phrases = json.loads((DATA / 'segments.json').read_text())
raw = subprocess.run([
    'ffmpeg', '-v', 'error', '-i', str(SOURCE), '-ac', '1', '-ar', str(SR),
    '-f', 'f32le', '-'
], check=True, stdout=subprocess.PIPE).stdout
voice = np.frombuffer(raw, dtype='<f4').copy()


def srt_time(seconds):
    ms = int(round(seconds * 1000))
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


def build(name, clips):
    audio = np.zeros(0, dtype=np.float32)
    timeline, adjusted_sentences, adjusted_phrases = [], [], []
    overlap = round(CROSSFADE * SR)
    ramp = np.linspace(0, 1, overlap, dtype=np.float32)
    for index, (start, end, key, source_key, purpose) in enumerate(clips):
        chunk = voice[round(start * SR):round(end * SR)].copy()
        # De-click at cut boundaries, where source pause handles are retained.
        fade = min(round(0.004 * SR), len(chunk) // 2)
        chunk[:fade] *= np.linspace(0, 1, fade)
        chunk[-fade:] *= np.linspace(1, 0, fade)
        dest_start = len(audio) / SR - (CROSSFADE if index else 0)
        if index:
            seam = audio[-overlap:] * (1 - ramp) + chunk[:overlap] * ramp
            audio = np.concatenate([audio[:-overlap], seam, chunk[overlap:]])
        else:
            audio = chunk
        dest_end = len(audio) / SR
        scene = {
            'id': key, 'source_start': start, 'source_end': end,
            'start': round(dest_start, 6), 'end': round(dest_end, 6),
            'source_key': source_key, 'purpose': purpose,
        }
        timeline.append(scene)
        for src_list, dst_list in [(sentences, adjusted_sentences), (phrases, adjusted_phrases)]:
            for line in src_list:
                if line['start'] >= start - 0.001 and line['end'] <= end + 0.001:
                    dst_list.append({
                        'start': round(dest_start + line['start'] - start, 6),
                        'end': round(dest_start + line['end'] - start, 6),
                        'text': line['text'], 'scene_id': key,
                        'source_start': line['start'], 'source_end': line['end'],
                    })
    wav_path = ROOT / f'{name}.wav'
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
        '-i', '-', '-c:a', 'pcm_s24le', str(wav_path)
    ], check=True, input=audio.astype('<f4').tobytes())
    result = {
        'name': name, 'duration': len(audio) / SR, 'sample_rate': SR,
        'channels': 1, 'source': str(SOURCE), 'source_kind': 'user supplied Ece narration only',
        'crossfade_seconds': CROSSFADE,
        'timing_note': 'Sentence boundaries from the reviewed source transcript. Phrase boundaries are approximate, inherited from segments.json; these are not forced-aligned word timestamps.',
        'legal_editorial_notes': [
            'All opening quote words are read by the user supplied Ece narrator; neither the brand source video nor reference audio is copied.',
            'The opening quote must show Yavuz Selim Bayraktar attribution and the article source from the first frame.',
            '50 bin TL is an announced budget plan, not a verified completed spend.',
            '130 bin in the full version is a self-reported previous audience, not current GUMA followers.',
            'The stated family/production relationships were publicly disclosed; do not frame them as hidden or evidence of lying.',
            'No inference of free manufacturing, capital transfer, ownership share or fraud.',
            'Generated furniture/studio scenes must be marked as illustrative rather than actual brand facilities/products.',
        ],
        'sources': SOURCES, 'timeline': timeline,
        'sentences': adjusted_sentences, 'captions': adjusted_phrases,
    }
    (ROOT / f'{name}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    (ROOT / f'{name}_captions.json').write_text(json.dumps(adjusted_phrases, ensure_ascii=False, indent=2))
    (ROOT / f'{name}_sentences.json').write_text(json.dumps(adjusted_sentences, ensure_ascii=False, indent=2))
    transcript = '\n\n'.join(x['text'] for x in adjusted_sentences)
    (ROOT / f'{name}_metin.txt').write_text(transcript + '\n')
    srt = '\n\n'.join(f"{i + 1}\n{srt_time(x['start'])} --> {srt_time(x['end'])}\n{x['text']}" for i, x in enumerate(adjusted_phrases))
    (ROOT / f'{name}.srt').write_text(srt + '\n')
    print(json.dumps({'name': name, 'duration': result['duration'], 'sentences': len(adjusted_sentences), 'phrases': len(adjusted_phrases), 'wav': str(wav_path)}, ensure_ascii=False), flush=True)
    return result


preview = build('GUMA_v5_preview_39s', PREVIEW)
full = build('GUMA_v5_full_90s', FULL)
(ROOT / 'editorial.json').write_text(json.dumps({'preview': preview, 'full': full}, ensure_ascii=False, indent=2))
