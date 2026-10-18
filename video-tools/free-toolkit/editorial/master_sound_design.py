from pathlib import Path
import concurrent.futures
import json
import subprocess

ROOT = Path(__file__).resolve().parent
TARGET = 'I=-16:TP=-1.2:LRA=11'


def measure(path):
    result = subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af',f'loudnorm={TARGET}:print_format=json','-f','null','-'], capture_output=True, check=True, text=True)
    data = json.loads(result.stderr[result.stderr.rfind('{'):result.stderr.rfind('}')+1])
    return {k: data[k] for k in ['input_i','input_tp','input_lra','input_thresh']}


premaster = ROOT/'mixed_audio_premaster.wav'
analysis = measure(premaster)
flt = f'loudnorm={TARGET}:measured_I={analysis["input_i"]}:measured_TP={analysis["input_tp"]}:measured_LRA={analysis["input_lra"]}:measured_thresh={analysis["input_thresh"]}:offset=0:linear=true:print_format=json'
result = subprocess.run(['ffmpeg','-y','-hide_banner','-nostats','-i',str(premaster),'-af',flt,'-ar','48000','-c:a','pcm_s24le',str(ROOT/'mixed_audio.wav')], capture_output=True, check=True, text=True)
(ROOT/'mastering.log').write_text(result.stderr)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    master_future = pool.submit(measure, ROOT/'mixed_audio.wav')
    effects_future = pool.submit(measure, ROOT/'sfx_only.wav')
    final, effects = master_future.result(), effects_future.result()

probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(ROOT/'mixed_audio.wav')]))
report = {
    'premaster': analysis, 'mixed_audio': final, 'sfx_only': effects,
    'duration': float(probe['format']['duration']),
    'sample_rate': int(probe['streams'][0]['sample_rate']),
    'channels': probe['streams'][0]['channels'],
    'codec': probe['streams'][0]['codec_name'],
    'decode': 'FFmpeg complete decode passed during loudness verification',
    'target_passed': abs(float(final['input_i'])+16) <= .2 and float(final['input_tp']) <= -1,
    'rights_note': 'Only original procedurally synthesized score/SFX plus user supplied Ece narration; no external music recordings, samples or brand/reference source audio.',
}
(ROOT/'sound_design_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if not report['target_passed']:
    raise SystemExit('Measured loudness/peak target failed')
