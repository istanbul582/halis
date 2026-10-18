#!/usr/bin/env python3
"""Verify the rendered MP4; normalize atom placement without re-encoding if needed."""
import hashlib, json, re, subprocess, sys, time
from pathlib import Path

film = Path(sys.argv[1] if len(sys.argv) > 1 else 'out/GUMA_v5_full.mp4')

def atoms(path):
    result=[]
    with path.open('rb') as f:
        end=path.stat().st_size
        while f.tell()+8<=end:
            offset=f.tell(); header=f.read(8)
            size=int.from_bytes(header[:4],'big'); kind=header[4:].decode('ascii','replace')
            if size==1:size=int.from_bytes(f.read(8),'big')
            elif size==0:size=end-offset
            result.append({'type':kind,'offset':offset,'size':size})
            if size<8:break
            f.seek(offset+size)
    return result

layout=atoms(film); positions={a['type']:a['offset'] for a in layout}
if positions.get('moov',1e99)>positions.get('mdat',-1):
    temp=film.with_name(film.stem+'-faststart-tmp.mp4')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(film),'-map','0','-c','copy','-movflags','+faststart',str(temp)],check=True)
    temp.replace(film)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(film)]))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
checks={
    'resolution':video['width']==1080 and video['height']==1920,
    'video_codec':video['codec_name']=='h264',
    'pixel_format':video.get('pix_fmt')=='yuv420p',
    'fps':video['r_frame_rate']=='30/1',
    'video_frames':int(video['nb_frames'])==2970,
    'duration':abs(float(probe['format']['duration'])-99)<.08,
    'audio_codec':audio['codec_name']=='aac',
    'audio_stereo_48k':audio['channels']==2 and audio['sample_rate']=='48000',
}
subprocess.run(['ffmpeg','-xerror','-v','error','-i',str(film),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
checks['complete_decode']=True
measure=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(film),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
match=re.findall(r'\{\s*"input_i"[\s\S]*?\}',measure.stderr)
loudness=json.loads(match[-1])
checks['loudness_within_0_6_lu']=abs(float(loudness['input_i'])+16)<=.6
checks['true_peak_below_minus_1']=float(loudness['input_tp'])<=-1
layout=atoms(film); positions={a['type']:a['offset'] for a in layout}
checks['faststart_moov_before_mdat']=positions['moov']<positions['mdat']
report={'file':str(film.resolve()),'bytes':film.stat().st_size,'sha256':hashlib.sha256(film.read_bytes()).hexdigest(),'duration':probe['format']['duration'],'video':{k:video.get(k) for k in ['codec_name','width','height','pix_fmt','r_frame_rate','nb_frames']},'audio':{k:audio.get(k) for k in ['codec_name','sample_rate','channels']},'loudness':loudness,'mp4_atoms':layout,'checks':checks,'all_passed':all(checks.values()),'scope':'Media probe, complete FFmpeg decode, atom layout and audio loudness only; not a legal clearance or view prediction.'}
out=film.with_name('FINAL_VERIFICATION.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['all_passed']:sys.exit(1)
