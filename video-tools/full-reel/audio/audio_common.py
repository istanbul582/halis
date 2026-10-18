"""Shared strict input checks for the portable, unchanged narration mix."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

SAMPLE_RATE = 48000
DURATION = 164.2
VOICE_DURATION = 7448033 / 48000
EXPECTED_VOICE_SHA256 = '00688f8d1eddfae678cbb789e3a990af247290c5929cd1080031015bb7f45bb1'
REFERENCE_SOUND_SHA256 = '96518822aace30581bf59c82648e1f2860e66d12a70cd59f4ccb2361457f6e3d'
REFERENCE_MIX_SHA256 = '6ad964b2ca04a644e40165d497d93b5a935a03918e41eb07b8c4b36be97803b5'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def probe_audio(path):
    raw = subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'a:0',
        '-show_entries', 'stream=sample_rate,channels,codec_name:format=duration',
        '-of', 'json', str(path),
    ], text=True)
    return json.loads(raw)


def validate_voice(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError('Private narration master is missing. Supply --voice /private/narration-master.wav.')
    for name in ('ffmpeg', 'ffprobe'):
        if not shutil.which(name):
            raise ValueError(f'{name} is required on PATH')
    digest = sha256(path)
    if digest != EXPECTED_VOICE_SHA256:
        raise ValueError('Wrong narration master SHA-256. The original full normalized WAV is required; no shortened/reordered/re-encoded input is accepted.')
    info = probe_audio(path)
    if not info.get('streams'):
        raise ValueError('Narration has no audio stream')
    stream = info['streams'][0]
    if stream['sample_rate'] != str(SAMPLE_RATE) or stream['channels'] != 1 or stream['codec_name'] != 'pcm_s24le':
        raise ValueError('The original 48 kHz mono PCM24 narration master is required')
    duration = float(info['format']['duration'])
    if abs(duration - VOICE_DURATION) > 0.0001:
        raise ValueError('Narration duration differs from the complete 7,448,033-sample narration master')
    return {'sha256': digest, 'duration_seconds': duration, 'sample_rate': SAMPLE_RATE,
            'channels': 1, 'codec': 'pcm_s24le', 'voice_cut': False,
            'voice_reordered': False, 'voice_speed_changed': False}
