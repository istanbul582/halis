"""Original editorial score and illustration-synchronised Foley, no sample assets."""
from pathlib import Path
import json,wave,math
import numpy as np
from scipy.signal import butter,sosfilt

import argparse
from audio_common import validate_voice, sha256, REFERENCE_SOUND_SHA256
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--voice',required=True,type=Path)
parser.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent/'build')
args=parser.parse_args()
try:
    voice_info=validate_voice(args.voice)
except ValueError as exc:
    parser.error(str(exc))
OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
VOICE=args.voice
SR=48000;DURATION=164.2;N=int(round(SR*DURATION))
rng=np.random.default_rng(58220261018);t=np.arange(N,dtype=np.float32)/SR
bed=np.zeros((N,2),np.float32);foley=np.zeros_like(bed)

def rms(x):return max(1e-12,float(np.sqrt(np.mean(x*x))))
def normpeak(x,peak):return x*(peak/max(1e-12,float(np.max(np.abs(x)))))
def fade(x,attack=.004,release=.02):
    n=len(x);env=np.ones(n,np.float32);a=min(n//2,max(2,int(attack*SR)));b=min(n//2,max(2,int(release*SR)))
    env[:a]=np.sin(np.linspace(0,np.pi/2,a,dtype=np.float32))**2
    env[-b:]=np.sin(np.linspace(np.pi/2,0,b,dtype=np.float32))**2
    return x*env
def band_noise(duration,low,high):
    nn=max(1,int(duration*SR));noise=rng.standard_normal(nn).astype(np.float32)
    sos=butter(2,[low,high],btype='bandpass',fs=SR,output='sos')
    return sosfilt(sos,noise).astype(np.float32)
def place(bus,x,tm,pan=0):
    a=int(round(tm*SR));b=min(N,a+len(x));off=max(0,-a);a=max(0,a)
    if b<=a:return
    x=x[off:off+b-a]
    # Pan law keeps the mono centre stable; all Foley is original mono synthesis.
    l=math.cos((pan+1)*math.pi/4);r=math.sin((pan+1)*math.pi/4)
    bus[a:b,0]+=x*l;bus[a:b,1]+=x*r

# Warm add9 / major7 chords, soft transient-free pad.
chords=[(0,38,[146.832,220,277.183,329.628]),(30,77,[123.471,185,246.942,293.665]),(69,113,[98,146.832,185,246.942]),(105,145,[110,164.814,246.942,277.183]),(137,164.2,[146.832,220,277.183,329.628])]
for ci,(st,en,notes) in enumerate(chords):
    a=int(st*SR);b=min(N,int(en*SR));lt=np.arange(b-a,dtype=np.float32)/SR;dur=len(lt)/SR
    env=np.ones(len(lt),np.float32);fi=min(7,dur/3);fo=min(7,dur/3)
    m=lt<fi;env[m]=np.sin(lt[m]/fi*np.pi/2)**2;m=lt>dur-fo;env[m]=np.sin((dur-lt[m])/fo*np.pi/2)**2
    for j,f in enumerate(notes):
        phase=float(rng.uniform(0,2*np.pi));amp=[.27,.15,.10,.07][j]
        for ch,sign in [(0,-1),(1,1)]:
            ff=f+sign*.019*(j+1)
            note=np.sin(2*np.pi*ff*lt+phase)+.045*np.sin(2*np.pi*2.005*ff*lt+phase*.3)
            bed[a:b,ch]+=note*env*(.92+.08*np.sin(2*np.pi*.062*lt+ci*.3))*amp

# A light 92 BPM pulse: rounded kick, small brushed ticks and sparse harmonic plucks.
# Narration/quotations and final question get space instead of an uninterrupted loop.
beat=60/92
def rhythm_level(tm):
    if tm<12.18:return .12
    if 48<=tm<69:return .22
    if 83.64<=tm<91.09:return .12
    if 147.69<=tm<155.2:return .08
    if tm>=155.2:return .65
    return 1.0
for k,tm in enumerate(np.arange(.2,DURATION-.6,beat)):
    lev=rhythm_level(float(tm));phase=k%4
    if phase in (0,2):
        dur=.19;tt=np.arange(int(dur*SR),dtype=np.float32)/SR
        # Subtle low kick with a finite pitch glide, not a dramatic bass impact.
        x=np.sin(2*np.pi*(74*tt+13*.035*(1-np.exp(-tt/.035))))*np.exp(-tt/.055)
        place(bed,fade(x,.004,.035)*(.040 if phase==0 else .023)*lev,float(tm))
    if phase in (1,3):
        dur=.075;tt=np.arange(int(dur*SR),dtype=np.float32)/SR
        x=band_noise(dur,2200,6500)*np.exp(-tt/.024)
        place(bed,fade(x,.003,.02)*.035*lev,float(tm),-.25 if phase==1 else .25)
    if k%8 in (0,3,6):
        f=[293.665,329.628,440][(k//3)%3];dur=.34;tt=np.arange(int(dur*SR),dtype=np.float32)/SR
        x=(np.sin(2*np.pi*f*tt)+.10*np.sin(2*np.pi*f*2.002*tt))*np.exp(-tt/.10)
        place(bed,fade(x,.007,.06)*.027*lev,float(tm)+beat*.5,.35 if k%2 else -.35)

# Normalise the original music before applying a measured, voice-driven duck.
bed*=.047/rms(bed[:int(155.2*SR)])

# RMS envelope from the unchanged narration, 10 ms hop; smooth fast attack/slow release.
import subprocess
raw=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-i',str(VOICE),'-f','f32le','-ac','1','-ar',str(SR),'-'])
voice=np.frombuffer(raw,dtype='<f4');hop=480
voice=np.pad(voice,(0,max(0,N-len(voice))))[:N]
frame_rms=np.array([rms(voice[i:i+hop]) for i in range(0,N,hop)],dtype=np.float32)
active=np.clip((frame_rms-.008)/.055,0,1)
smoothed=np.zeros_like(active);state=0.
for i,a in enumerate(active):
    coeff=.48 if a>state else .030
    state+=coeff*(float(a)-state);smoothed[i]=state
env=np.interp(np.arange(N,dtype=np.float32)/hop,np.arange(len(smoothed)),smoothed,left=0,right=0).astype(np.float32)
duck=1-.66*env
bed*=duck[:,None]
# Music ramps in gently, lifting modestly on the source card. Last two seconds fade out.
intro=np.clip(t/1.2,0,1);intro=intro*intro*(3-2*intro)
post=np.clip((t-155.2)/1.6,0,1);post=post*post*(3-2*post)
bed*=((.82+.18*post)*intro)[:,None]
tail=np.clip((DURATION-t)/2,0,1);tail=np.sin(tail*np.pi/2)**2
bed*=tail[:,None]

def paper(duration=.24,peak=.048):
    tt=np.arange(int(duration*SR),dtype=np.float32)/SR
    n=band_noise(duration,370,4700)
    # Uneven broad swish with little fibre-like crackles.
    env=np.sin(np.pi*tt/duration)**1.7*(.72+.28*np.sin(2*np.pi*27*tt+.3)**2)
    x=n*env
    for tm in [duration*.19,duration*.48,duration*.70]:
        i=int(tm*SR);nn=min(int(.012*SR),len(x)-i);x[i:i+nn]+=rng.normal(0,.16,nn)*np.exp(-np.arange(nn)/SR/.003)
    return normpeak(fade(x,.007,.018),peak)
def click(peak=.045,bright=False):
    duration=.072;tt=np.arange(int(duration*SR),dtype=np.float32)/SR
    x=band_noise(duration,900 if bright else 420,5900 if bright else 3300)*np.exp(-tt/.010)
    x+=.15*np.sin(2*np.pi*(1240 if bright else 710)*tt)*np.exp(-tt/.016)
    return normpeak(fade(x,.0015,.018),peak)
def pencil(duration=.33,peak=.038):
    tt=np.arange(int(duration*SR),dtype=np.float32)/SR
    x=band_noise(duration,1100,5200)
    env=(.35+.65*np.sin(2*np.pi*19.3*tt+.2)**2)*np.sin(np.pi*tt/duration)**.7
    return normpeak(fade(x*env,.006,.025),peak)
def swish(duration=.23,peak=.042):
    tt=np.arange(int(duration*SR),dtype=np.float32)/SR
    x=band_noise(duration,700,5900)*np.sin(np.pi*tt/duration)**2
    # High-frequency-only airflow; no siren/pitch riser.
    return normpeak(fade(x,.007,.025),peak)
def soft_impact(peak=.072):
    dur=.21;tt=np.arange(int(dur*SR),dtype=np.float32)/SR
    x=np.sin(2*np.pi*154*tt)*np.exp(-tt/.042)+.11*band_noise(dur,1300,4200)*np.exp(-tt/.015)
    return normpeak(fade(x,.002,.035),peak)
def chime(frequency,peak=.065):
    dur=.55;tt=np.arange(int(dur*SR),dtype=np.float32)/SR
    x=(np.sin(2*np.pi*frequency*tt)+.10*np.sin(2*np.pi*frequency*2.014*tt)+.035*np.sin(2*np.pi*frequency*3.019*tt))*np.exp(-tt/.135)
    return normpeak(fade(x,.007,.09),peak)

events=[
(.2,'paper_reveal'),(3.1,'soft_click'),(6.36,'paper_short'),(8.96,'number_land'),
(12.18,'double_click'),(17.02,'pencil_underline'),(23.04,'paper_flip'),(25.6,'soft_click'),
(27.9,'pencil_graph'),(33.5,'short_swish'),(35.5,'double_click'),(42.5,'pencil_underline'),
(48,'paper_flip'),(54,'quote_click'),(58.15,'paper_short'),(64,'pencil_short'),
(69,'short_swish'),(71,'number_ticks'),(75,'paper_reveal'),(83.64,'soft_click'),
(91.09,'pencil_graph'),(97.5,'soft_click'),(104.96,'paper_short'),(110.5,'pencil_short'),
(115.69,'paper_flip'),(122.51,'quote_click'),(124.73,'quote_click'),(127.02,'pencil_graph'),
(130.9,'soft_click'),(134.77,'paper_short'),(140.48,'quote_click'),(144.34,'pencil_short'),
(147.69,'short_swish'),(153.7,'soft_click'),(155.2,'source_card'),(162.2,'follow_chime')]
event_log=[]
for k,(tm,kind) in enumerate(events):
    pan=[-.14,.10,0,.18,-.10][k%5]
    if kind in ('paper_reveal','paper_flip','paper_short'):
        dur={'paper_reveal':.31,'paper_flip':.25,'paper_short':.17}[kind]
        x=paper(dur,.050 if kind!='paper_short' else .038);place(foley,x,tm-.035,pan)
    elif kind in ('soft_click','quote_click'):
        place(foley,click(.045 if kind=='soft_click' else .035,kind=='quote_click'),tm,pan)
    elif kind=='double_click':
        place(foley,click(.036),tm,-.15);place(foley,click(.030,True),tm+.095,.15)
    elif kind in ('pencil_underline','pencil_graph','pencil_short'):
        dur={'pencil_underline':.34,'pencil_graph':.42,'pencil_short':.23}[kind]
        place(foley,pencil(dur),tm,pan)
        if kind=='pencil_graph':place(foley,click(.019,True),tm+dur-.015,pan)
    elif kind=='short_swish':place(foley,swish(.23),tm-.085,pan)
    elif kind=='number_land':
        place(foley,soft_impact(),tm,0);place(foley,click(.030,True),tm+.06,.1)
    elif kind=='number_ticks':
        for d in [0,.085,.17]:place(foley,click(.029,True),tm+d,-.1+d)
    elif kind=='source_card':place(foley,paper(.34,.045),tm-.07,0)
    elif kind=='follow_chime':
        place(foley,chime(659.255,.060),tm+.07,-.05);place(foley,chime(830.609,.052),tm+.30,.05)
    event_log.append({'time_seconds':tm,'type':kind,'pan':pan,'provenance':'Original deterministic noise/oscillator synthesis in this script; no recordings or samples.'})

# Keep foreground syllables clear; transient Foley receives a milder narration duck.
foley*=(1-.20*env)[:,None]*1.35
# Natural final fade on the effects too, without cutting off the original follow chime.
foley*=np.minimum(1,np.clip((DURATION-t)/.55,0,1))[:,None]
mix=bed+foley
assert np.isfinite(mix).all()
peak=float(np.max(np.abs(mix)));assert peak<.45,peak
def write_wav(path,x):
    pcm=np.round(np.clip(x,-1,1)*32767).astype('<i2')
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(pcm.tobytes())
write_wav(OUT/'music-bed.wav',bed);write_wav(OUT/'foley.wav',foley);write_wav(OUT/'sound-design.wav',mix)
meta={'title':'GUMA v3 original editorial pulse and illustration Foley','duration_seconds':DURATION,'sample_rate':SR,'channels':2,'bpm':92,'seed':58220261018,'music_source':'Original deterministic sine/noise synthesis; no external music, melodies, samples, recordings or platform sounds.','foley_source':'Paper, pencil, mechanical clicks, airflow and soft impacts are synthetic approximations, generated from filtered noise and sine envelopes. No recordings used.','voice_ducking':'Narration RMS envelope; 10 ms analysis, fast attack/slow release, up to approx9dB music duck and2dB Foley duck.','narration_region_music_rms_dBFS':20*math.log10(rms(bed[int(3*SR):int(155.2*SR)])),'narration_region_foley_rms_dBFS':20*math.log10(rms(foley[:int(155.2*SR)])),'sound_design_peak_dBFS':20*math.log10(peak),'voice_modified':False,'sources_card':[155.2,162.2],'follow_animation':[162.2,164.2],'events':event_log}
meta['voice_input']=voice_info
meta['sound_design_sha256']=sha256(OUT/'sound-design.wav')
meta['reference_sound_sha256']=REFERENCE_SOUND_SHA256
meta['matches_reference_sound_bytes']=meta['sound_design_sha256']==REFERENCE_SOUND_SHA256
meta['v6_visual_sources_card']=[155.2,161.2]
meta['v6_visual_follow_animation']=[161.2,164.2]
meta['timing_note']='Original V3 synthesis and effect timing preserved; V6 source card/CTA boundary changed visually only. The 162.2-second chime remains inside the V6 CTA.'
(OUT/'sound-design.metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
(OUT/'sfx-events.json').write_text(json.dumps(event_log,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in meta.items() if k!='events'},ensure_ascii=False,indent=2))
