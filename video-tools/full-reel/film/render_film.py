"""Original full-voice editorial film. Stocks are illustrative and muted.
All motion is deterministic frame-driven; all quotations remain attributed.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
from functools import lru_cache
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np, math, json, subprocess, hashlib, sys, time, shutil, argparse
SCRIPT_DIR=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description='164.2s full-narration editorial video renderer')
ap.add_argument('--workspace-root',type=Path,default=SCRIPT_DIR.parent)
ap.add_argument('--assets-root',type=Path)
ap.add_argument('--captions',type=Path)
ap.add_argument('--audio',type=Path)
ap.add_argument('--voice-master',type=Path)
ap.add_argument('--output-root',type=Path)
ap.add_argument('--render',action='store_true')
ap.add_argument('--previews',action='store_true')
ap.add_argument('--workers',type=int,default=4)
ap.add_argument('--refresh-sources',action='store_true')
ap.add_argument('--legacy-color',action='store_true',help=argparse.SUPPRESS)
ARGS,_=ap.parse_known_args()
ROOT=ARGS.workspace_root.resolve(); V=ARGS.output_root.resolve() if ARGS.output_root else SCRIPT_DIR
ASSETS_ROOT=ARGS.assets_root.resolve() if ARGS.assets_root else SCRIPT_DIR.parent/'assets'
AUDIO=ARGS.audio.resolve() if ARGS.audio else ROOT/'input/finalmix.wav'
MASTER=ARGS.voice_master.resolve() if ARGS.voice_master else ROOT/'input/narration-master.wav'
CAPTIONS=ARGS.captions.resolve() if ARGS.captions else SCRIPT_DIR.parent/'editorial/segments.json'
if not CAPTIONS.exists(): CAPTIONS=SCRIPT_DIR/'narration_segments.json'
W,H,FPS=1080,1920,30; END=164.2
N='#101b24'; C='#f4efdf'; G='#d8b680'; M='#a5b5b9'; T='#76b0ad'
FONTS=SCRIPT_DIR/'fonts'
SUBS=json.loads(CAPTIONS.read_text())
# Blocks respect the original voice order and every word of the 155.167s master.
SCENES=[
(0,6.36,'budget',None,'AÇIKLANAN BÜTÇE PLANI'),
(6.36,17.02,'audience',None,'ÖNCEKİ KİTLE / KURUCU BEYANI'),
(17.02,23.04,'question',None,'BAŞLANGIÇ KOŞULLARI'),
(23.04,28,'design',None,'TASARLAMAK / DUYURMAK'),
(28,34.01,'channel',None,'ÖNCEDEN KURULAN KANAL'),
(34.01,43.07,'production',None,'ÜRETİM / SATIŞ İLİŞKİSİ'),
(43.07,48.4,'terms',None,'ŞİRKETİN KENDİ İFADESİ'),
(48.4,58.97,'quote',None,'KURUCU AÇIKLAMASI'),
(58.97,64.11,'role',None,'HABERDEKİ GÖREV BİLGİSİ'),
(64.11,69.39,'knowledge',None,'AÇIKLANAN BİLGİ DESTEĞİ'),
(69.39,83.64,'map',None,'BİLGİLERİ BİRLİKTE DÜŞÜN'),
(83.64,91.09,'scope',None,'BİLGİNİN KAPSAMI'),
(91.09,104.96,'process',None,'FİKİRDEN İLK MÜŞTERİYE'),
(104.96,115.69,'work',None,'EMEK / AÇIKLANAN İMKÂNLAR'),
(115.69,134.77,'questions',None,'KENDİ İŞİNİ KURARKEN'),
(134.77,147.69,'prepare',None,'SONUÇ KADAR BAŞLANGIÇ'),
(147.69,155.2,'final',None,'ŞİMDİ SORU SANA'),
(155.2,161.2,'sources',None,'KAYNAKLAR'),
(161.2,164.2,'follow',None,'MERAKI BİRLİKTE SÜRDÜRELİM')]
# Each visible stock window has a literal narration purpose; no looped decorative stock.
SHOT_MANIFEST=json.loads((ASSETS_ROOT/'SELECTED_MANIFEST.json').read_text())+json.loads((ASSETS_ROOT/'EXTRA_PHASES_MANIFEST.json').read_text())
for a in SHOT_MANIFEST:a['source_id']=a.get('source_id',a.get('id'))
SELECTED={a['name']:a for a in SHOT_MANIFEST}
SHOTS=[
 (23.04,25.23,'design_overhead',0),
 (25.23,27.10,'camera_phone',0),
 (28.0,30.70,'content_calendar',0),
 (30.70,33.55,'editing_desk',1.0),
 (91.09,92.70,'workshop_hands',0),
 (92.70,94.30,'workshop_hands',2.3),
 (94.30,95.90,'material_blue',0),
 (95.90,97.45,'camera_phone',2.0),
 (99.41,102.0,'workshop_hands_late',.4),
 (102.0,104.96,'content_calendar_mid',1.0),
 (104.96,107.10,'design_pencil_close',.1),
 (107.10,109.0,'editing_desk',0),
 (110.92,112.8,'design_overhead',2.0),
 (112.8,114.3,'content_calendar_late',0),
 (114.3,115.69,'editing_desk',2.0),
 (115.69,118.2,'content_calendar_mid',1.0),
 (118.2,120.0,'camera_phone',1.0),
 (120.0,122.51,'editing_desk',.5),
 (122.51,124.73,'workshop_hands_early',2.2),
 (124.73,127.02,'design_pencil_close',1.5),
 (127.02,128.8,'content_calendar_late',.3),
 (128.8,130.47,'editing_desk',2.0),
 (140.48,142.2,'content_calendar_late',2.0),
 (142.2,144.34,'editing_desk',1.0),
 (144.34,146.1,'content_calendar_mid',.1),
 (146.1,147.69,'design_pencil_close',2.0)]

def shot_at(t):return next((a for a in SHOTS if a[0]<=t<a[1]),None)
# Affine palette conversion provides a deliberate light editorial chapter without copying source layout.
_A=np.array([[16,27,36,1],[244,239,223,1],[216,182,128,1],[165,181,185,1]],dtype=float)
_B=np.array([[244,239,223],[16,27,36],[155,109,43],[89,112,119]],dtype=float)
_THEME_MATRIX=tuple(np.linalg.solve(_A,_B).T.flatten())
@lru_cache(maxsize=200)
def font(size=50,style='sans',weight='SemiBold'):
 p=FONTS/({'sans':'Manrope.ttf','serif':'DMSerifDisplay-Italic.ttf','roman':'DMSerifDisplay-Regular.ttf','cond':'BarlowCondensed-ExtraBold.ttf'}[style]); f=ImageFont.truetype(str(p),round(size))
 if style=='sans':
  try:f.set_variation_by_name(weight.encode())
  except Exception:pass
 return f
def rgba(c,a=255):return tuple(int(c[i:i+2],16) for i in (1,3,5))+(round(a),)
def ease(v):v=max(0,min(1,v));return 1-(1-v)**3
def p(t,a,b):return ease((t-a)/max(.001,b-a))
def blank(w=W,h=H):return Image.new('RGBA',(w,h))
@lru_cache(maxsize=500)
def sprite(s,z=60,col=C,style='sans',weight='SemiBold',spacing=10):
 f=font(z,style,weight);d=ImageDraw.Draw(blank(10,10));b=d.multiline_textbbox((0,0),s,font=f,spacing=spacing);im=blank(b[2]-b[0]+8,b[3]-b[1]+12);ImageDraw.Draw(im).multiline_text((4-b[0],4-b[1]),s,font=f,fill=col,spacing=spacing);return im
def text(im,s,x,y,z=60,col=C,style='sans',t=9,delay=0,align='left',alpha=1,weight='SemiBold',rise=28):
 k=p(t,delay,delay+.55)
 if k<=0:return
 v=sprite(s,z,col,style,weight)
 if k*alpha<.999:
  v=v.copy();v.putalpha(v.getchannel('A').point(lambda q:round(q*k*alpha)))
 if align=='center':x-=v.width/2
 elif align=='right':x-=v.width
 im.alpha_composite(v,(round(x),round(y+(1-k)*rise)))
def line(im,pts,k=1,col=G,width=3):
 k=max(0,min(1,k));d=ImageDraw.Draw(im);ll=[math.dist(a,b) for a,b in zip(pts,pts[1:])];rem=sum(ll)*k
 for a,b,l in zip(pts,pts[1:],ll):
  if rem<=0:break
  f=min(1,rem/max(.001,l));d.line([a,(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f)],fill=col,width=width);rem-=l

def bez(a,b,c,d,n=80):return [tuple((1-t)**3*x+3*(1-t)**2*t*y+3*(1-t)*t*t*z+t**3*w for x,y,z,w in zip(a,b,c,d)) for t in np.linspace(0,1,n)]
def arrow(im,pts,k=1,col=G,width=3):
 line(im,pts,k,col,width)
 if k>=.99:
  a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);ImageDraw.Draw(im).polygon([b,(b[0]-17*math.cos(ang-.5),b[1]-17*math.sin(ang-.5)),(b[0]-17*math.cos(ang+.5),b[1]-17*math.sin(ang+.5))],fill=col)
@lru_cache(maxsize=4)
def background(kind='navy'):
 yy,xx=np.mgrid[0:H,0:W]; base=np.array([16,27,36],dtype=float) if kind!='cream' else np.array([244,239,223],dtype=float)
 glow=np.exp(-(((xx-450)/650)**2+((yy-800)/900)**2))[:,:,None];a=np.clip(base+glow*(np.array([9,20,25]) if kind!='cream' else np.array([-6,-6,-5])),0,255).astype('uint8');im=Image.fromarray(a).convert('RGBA');return im
@lru_cache(maxsize=1)
def video_scrim():
 a=np.zeros((H,1,4),dtype=np.uint8);a[:,:,:3]=(9,20,28)
 for y in range(H):
  top=180*max(0,1-y/900);bottom=200*max(0,(y-1170)/570);a[y,0,3]=min(235,round(28+top+bottom))
 return Image.fromarray(a).resize((W,H))
def fullphoto(frame):
 if frame is None:return background().copy()
 im=frame.resize((W,H),Image.Resampling.BILINEAR).convert('RGBA');im.alpha_composite(video_scrim());return im

def clip_path(name):
 path=ASSETS_ROOT/'clips'/(name+'.mp4')
 if not path.is_file():raise FileNotFoundError(f'Missing local stock proxy: {path}')
 return path

def source_for(k,t,asset):
 if k in ['budget','audience','channel','question']:
  a='Kaynak: GUMA · 1. gün videosu';b='youtube.com/shorts/nnUXsnz3Wi0';c='Açıklanan plan / kurucunun önceki kitle beyanı'
 elif k in ['production','terms']:
  a='Kaynak: GUMA · Kullanım Şartları';b='gumastore.com/pages/kullanim-sartlari';c='Şirketin kendi üretim ve satış açıklaması'
 elif k in ['quote','role','knowledge']:
  a='Kaynak: Yıldırım Gazetesi · 06.10.2025';b='yildirimgazetesi.com · “İnegöllü mobilyacı gençler…”';c='Kurucunun haberde aktarılan açıklaması / görev bilgisi'
 else:a='Bağlam: GUMA / Yıldırım Gazetesi';b='Tam kaynak bağlantıları videonun sonunda ve açıklamada';c='Anlatıcının değerlendirmesi ve izleyiciye sorular'
 if asset:c='Temsili stok · Pexels '+SELECTED[asset]['source_id']+' · Gerçek marka tesisi/personeli değil'
 return a,b,c

def subtitle(im,t):
 for s in SUBS:
  if s['start']<=t<s['end']:
   ss=s['text'];words=ss.split();lines=[];cur=''
   for word in words:
    test=(cur+' '+word).strip()
    if font(47).getlength(test)>890 and cur:lines.append(cur);cur=word
    else:cur=test
   if cur:lines.append(cur)
   assert len(lines)<=2,(ss,lines)
   val='\n'.join(lines);v=sprite(val,47,C,'sans','SemiBold',10);y=1460-v.height/2
   sh=blank(v.width+38,v.height+30);ImageDraw.Draw(sh).rounded_rectangle((0,0,sh.width,sh.height),12,fill=rgba(N,205));sh.alpha_composite(v,(19,15));im.alpha_composite(sh,(round((W-sh.width)/2),round(y-15)));break

def ornament(im,t):
 d=ImageDraw.Draw(im)
 # Sparse editorial constellation, never a real financial chart.
 for j in range(12):
  x=74+j*84;y=1195+20*math.sin(j*.7+t*.25);r=2 if j%3 else 3;d.ellipse((x-r,y-r,x+r,y+r),fill=rgba(G,55))

def draw_scene(index,q,frame=None):
 st,en,k,asset,chapter=SCENES[index];t=st+q;shot=shot_at(t);asset=shot[2] if shot else None;im=fullphoto(frame) if frame is not None else background().copy();d=ImageDraw.Draw(im)
 if k=='budget':
  text(im,'“Yaklaşık',82,315,68,G,'serif',q+.7)
  text(im,'50 bin',80,435,188,C,'sans',q+.3)
  text(im,'lira sermayeyle',84,665,60,G,'serif',q,.75)
  text(im,'başlayarak…”',84,750,63,C,'serif',q,1.5)
  # Precise measuring sweep becomes a compact budget plan tag.
  d.arc((75,1000,982,1907),194,194+154*p(q,.35,2.8),fill=G,width=3)
  for j in range(31):
   a=math.radians(194+j*5.0);r=454;cx,cy=529,1453
   if j/30<p(q,.3,2.8):d.line((cx+math.cos(a)*r,cy+math.sin(a)*r,cx+math.cos(a)*(r+11),cy+math.sin(a)*(r+11)),fill=rgba(G,110),width=2)
  if q>=3.1:
   text(im,'GUMA',86,1014,74,C,'sans',q,3.1);text(im,'İlk videodaki bütçe planı.',88,1124,32,M,'sans',q,3.6)
   text(im,'Hedef anlatımı; gerçekleşen harcama bilançosu değil.',88,1260,23,M,'sans',q,4.4)
 elif k=='audience':
  a=q
  if a<2.6:
   text(im,'Aynı videoda',84,322,73,C,'serif',a+.5);text(im,'başka bir sayı var.',84,423,73,G,'serif',a,.35)
   text(im,'50 bin',84,740,110,M,'sans',a+.5,alpha=.35)
   arrow(im,bez((435,815),(610,815),(660,770),(886,770)),p(a,.8,2.1),G,3)
  else:
   text(im,'130 bin',83,467,171,C,'sans',a,2.55)
   if a>=3.74:text(im,'Para değil.',89,724,67,M,'serif',a,3.74)
   if a>=4.72:text(im,'Takipçi.',85,824,99,G,'serif',a,4.72)
   # A quantified particle field is explicitly decorative, not 130000 literal accounts.
   for j in range(105):
    an=j*2.39996;r=24*math.sqrt(j);x=685+math.cos(an)*r;y=1120+math.sin(an)*r;z=p(a,4.9+j*.006,5.45+j*.006);rr=3.0*z
    d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=rgba(G,155))
   if a>5.82:
    text(im,'Daha önce ulaştığını',87,1100,33,C,'sans',a,5.82);text(im,'söylediği kitle.',87,1151,33,C,'sans',a,6.1)
    text(im,'GUMA’nın güncel takipçi sayısı olarak sunulmuyor.',87,1275,23,M,'sans',a,7.1)
 elif k=='question':
  text(im,'Başlangıç',85,322,92,C,'serif',q+.5);text(im,'yalnızca bütçe mi?',85,438,78,G,'serif',q,.55)
  yy=1030;line(im,[(86,yy),(980,yy)],p(q,.5,2),rgba(C,180),2)
  for j,(a,b) in enumerate([('50 bin TL','bütçe planı'),('130 bin','önceki kitle beyanı')]):
   text(im,a,88+j*490,yy+45,61,C,'sans',q,.9+j*.3);text(im,b,91+j*490,yy+137,25,M,'sans',q,1.4+j*.3)
 elif k=='design':
  if q<2.19:
   text(im,'Bir ürünü',85,323,74,C,'serif',q+.5);text(im,'tasarlamak.',82,420,108,G,'serif',q,.4)
   line(im,[(89,565),(830,565)],p(q,.4,1.6),G,2)
  else:
   text(im,'O ürünü',85,323,74,C,'serif',q,2.19);text(im,'duyurmak.',82,420,108,G,'serif',q,2.35)
   arrow(im,bez((106,590),(400,590),(644,797),(945,797)),p(q,2.7,4),G,3)
  text(im,'İKİ FARKLI İŞ',86,1210,27,C,'sans',q,1)
 elif k=='channel':
  text(im,'Hazır bir',85,321,86,C,'serif',q+.5);text(im,'anlatma kanalı.',83,428,87,G,'serif',q,.4)
  for j in range(4):
   a=p(q,.6+j*.35,1.2+j*.35);yy=800+j*86;line(im,[(90,yy),(90+780*a,yy)],1,rgba(C,50+30*j),2)
   if j==3:text(im,'Önceki kitle → hikâyeyi duyurma imkânı',91,1155,29,C,'sans',q,2)
 elif k=='production':
  text(im,'Üretim tarafında',84,321,77,C,'serif',q+.5);text(im,'kim var?',84,423,89,G,'serif',q,.45)
  text(im,'Saloni Mobilya',88,755,64,C,'sans',q,1.74);text(im,'ÜRETİM',92,853,27,G,'sans',q,2.3)
  arrow(im,bez((114,918),(113,1079),(815,1064),(841,1163)),p(q,3.0,5.2),G,3)
  text(im,'GUMA',606,1162,75,C,'sans',q,4.1);text(im,'SATIŞ',611,1274,27,G,'sans',q,4.8)
 elif k=='terms':
  # The quote is set as editorial typography, not fabricated official document.
  text(im,'Kullanım şartlarındaki ifade:',86,318,33,M,'sans',q+.5)
  text(im,'“Bünyesinde',80,441,89,C,'serif',q+.4);text(im,'bulunduğu”',80,557,100,G,'serif',q,.55)
  line(im,[(87,714),(946,714)],p(q,.75,2),G,3)
  text(im,'GUMA’nın Saloni Mobilya için',89,1019,35,C,'sans',q,1.7);text(im,'kullandığı kendi tanımı.',89,1076,35,C,'sans',q,2.1)
  text(im,'Bu ifade, ortaklık oranı veya finansman tutarı göstermiyor.',89,1257,23,M,'sans',q,3)
 elif k=='quote':
  text(im,'Bir bilgi daha.',84,318,89,G,'serif',q+.4)
  text(im,'Yavuz Selim Bayraktar',89,445,38,C,'sans',q,.6)
  text(im,'Yıldırım Gazetesi · 06.10.2025',89,514,25,M,'sans',q,1.15)
  if q>=5.93:
   text(im,'“Dayım Haluk Özbek,',84,700,65,C,'serif',q,5.93)
   text(im,'Guma’nın doğuş',84,799,74,G,'serif',q,6.7)
   text(im,'hikayesinde önemli',84,905,72,C,'serif',q,7.6)
   text(im,'bir paya sahip.”',84,1010,76,G,'serif',q,8.4)
  else:
   # A draw-on quotation mark introduces an actual attributed quote.
   text(im,'“',81,680,300,G,'serif',q,1.8)
   text(im,'Kurucunun gazetede',90,1135,36,C,'sans',q,3.1);text(im,'yayımlanan açıklaması.',90,1193,36,C,'sans',q,3.7)
  d.line((86,1345,978,1345),fill=rgba(G,65),width=2)
 elif k=='role':
  text(im,'Haluk Özbek',84,320,91,C,'serif',q+.5);text(im,'Saloni Mobilya',87,490,66,G,'sans',q,.3)
  text(im,'Yönetim Kurulu',87,594,62,C,'sans',q,.8);text(im,'Başkanı',87,681,62,C,'sans',q,1.15)
  text(im,'Haberde bu görevle tanıtılıyor.',90,837,30,M,'sans',q,1.7)
  line(im,bez((95,955),(365,955),(360,1180),(910,1180)),p(q,1.2,3.3),G,3)
  text(im,'“Dayım”',90,1123,77,G,'serif',q,2.1);text(im,'Yavuz Selim Bayraktar’ın ifadesi',91,1261,26,M,'sans',q,2.7)
 elif k=='knowledge':
  text(im,'Açıklanan destek:',84,320,50,C,'sans',q+.5);text(im,'sektörü tanımak.',82,428,91,G,'serif',q,.25)
  text(im,'“Ufuk açıcı bilgileri ile',88,1015,42,C,'serif',q,1.1)
  text(im,'mobilya sektörünü',88,1080,42,C,'serif',q,1.65)
  text(im,'tanımamızı sağladı.”',88,1145,42,G,'serif',q,2.2)
  text(im,'Yavuz Selim Bayraktar · aynı haber',91,1283,25,M,'sans',q,2.8)
 elif k=='map':
  text(im,'Tek rakamın',84,318,82,C,'serif',q+.5);text(im,'yanındaki bilgiler.',83,425,82,G,'serif',q,.35)
  labels=[('50 bin TL','Açıklanan bütçe planı'),('Önceki kitle','Kurucunun kendi beyanı'),('Aile desteği','Sektörü tanıma bilgisi'),('Üretim ilişkisi','Şirketin açıkladığı yapı')]
  times=[2.34,5.55,9.0,11.1]
  for j,((aa,bb),delay) in enumerate(zip(labels,times)):
   yy=640+j*165;kk=p(q,delay,delay+.55)
   d.ellipse((86,yy+15,98,yy+27),fill=rgba(G,255*kk))
   text(im,aa,130,yy,44,C,'sans',q,delay);text(im,bb,132,yy+66,25,M,'sans',q,delay+.2)
   if j<3:line(im,[(92,yy+44),(92,yy+152)],kk,rgba(G,90),2)
 elif k=='scope':
  text(im,'Bu bilgiler',85,320,83,C,'serif',q+.5);text(im,'ne gösterir?',85,428,88,G,'serif',q,.35)
  if q<3:
   text(im,'Ücretsiz üretimin kanıtı değil.',89,1035,47,C,'sans',q,.6)
   line(im,[(92,1130),(963,1130)],p(q,.7,2),rgba(G,200),2)
  else:
   text(im,'Başlangıcı anlamak için',89,1003,46,C,'sans',q,3);text(im,'somut bağlam.',86,1098,70,G,'serif',q,3.5)
  text(im,'İlişkinin mali koşullarına dair bir belge sunulmuyor.',89,1298,23,M,'sans',q,1.6)
 elif k=='process':
  stages=[('Üreticiyi bul',.0),('Numuneyi hazırla',2.0),('Malzemeyi seç',3.8),('Ürünü tanıt',5.5),('İlk müşteriye ulaş',6.9)]
  active=max(i for i,(aa,delay) in enumerate(stages) if q>=delay)
  text(im,'Marka kurmak,',84,320,83,C,'serif',q+.5);text(im,'işleri çözmek.',84,427,89,G,'serif',q,.3)
  if q<8.32:
   text(im,'0'+str(active+1)+' / 05',89,801,30,G,'sans',q,stages[active][1]);text(im,stages[active][0],86,887,62,C,'sans',q,stages[active][1])
  else:
   text(im,'Hangisini,',87,789,81,C,'serif',q,8.32);text(im,'nasıl çözdüler?',87,900,81,G,'serif',q,9)
  for j in range(5):d.rectangle((90+j*181,1205,90+j*181+145,1210),fill=G if j<=active else rgba(C,70))
 elif k=='work':
  text(im,'Tasarım emeği.',84,320,86,C,'serif',q+.5);text(im,'Pazarlama emeği.',84,427,83,G,'serif',q,.7)
  if q>2.6:
   text(im,'Açıklanan ilişkiler.',87,1090,56,C,'sans',q,2.6)
   line(im,[(88,1190),(972,1190)],p(q,2.9,4.2),G,2)
  if q>=5.96:text(im,'Bunlar nasıl bir araya geldi?',88,1288,31,M,'sans',q,5.96)
 elif k=='questions':
  if q<6.82:
   text(im,'“Kaç lirayla',84,323,87,C,'serif',q+.4);text(im,'başladılar?”',84,437,99,G,'serif',q,.3)
   text(im,'Tek başına yeterli bir soru mu?',89,1160,39,C,'sans',q,1.5)
  else:
   steps=[(6.82,'O bütçeyle','hangi işler?'),(9.04,'Hangi imkânlara','erişim?'),(11.33,'Sen ayrıca','neyi kuracaksın?')]
   a=max(j for j,s in enumerate(steps) if q>=s[0]);delay,aa,bb=steps[a]
   text(im,'0'+str(a+1)+' / 03',89,326,29,G,'sans',q,delay);text(im,aa,84,449,78,C,'serif',q,delay);text(im,bb,84,562,85,G,'serif',q,delay+.23)
   for j in range(3):
    d.ellipse((92+j*52,1170,108+j*52,1186),fill=G if j==a else rgba(C,65))
   if q>=15.2:text(im,'Rakam, bu sorularla anlam kazanıyor.',89,1292,30,C,'sans',q,15.2)
 elif k=='prepare':
  if q<5.71:
   text(im,'Sonuca bak.',84,322,91,C,'serif',q+.5);text(im,'Başlangıcı da gör.',84,436,87,G,'serif',q,.5)
   line(im,[(91,1025),(970,1025)],p(q,.5,2),rgba(G,180),3)
   text(im,'İlham → koşulları anlama → kendi hazırlığın',91,1130,31,C,'sans',q,2)
  elif q<9.57:
   text(im,'“Ben de',84,322,104,C,'serif',q,5.71);text(im,'yapabilir miyim?”',84,451,88,G,'serif',q,5.95)
  else:
   text(im,'Kendi yolunda',84,322,83,C,'serif',q,9.57);text(im,'neyi hazırlayacaksın?',84,435,71,G,'serif',q,9.85)
   for j,aa in enumerate(['Bilgi','Erişim','Hazırlık']):text(im,aa,90+j*305,1180,37,C,'sans',q,10.1+j*.35)
 elif k=='final':
  text(im,'Aynı para.',84,323,112,C,'serif',q+.3);text(im,'Aynı başlangıç mı?',84,480,89,G,'serif',q,1.58)
  for j,(yy,xx) in enumerate([(900,145),(1150,370)]):
   line(im,[(130,yy),(960,yy)],p(q,.3+j*.3,1.6+j*.3),rgba(C,140),2)
   x=xx+120*p(q,2,5);d.ellipse((x-8,yy-8,x+8,yy+8),fill=G if j==0 else T)
   text(im,'Aynı tutar' if j==0 else 'Farklı başlangıç koşulları',134,yy+42,29,M,'sans',q,.8+j*.4)
  if q>=6.18:text(im,'Yorumlarda buluşalım.',87,1320,41,C,'sans',q,6.18)
 elif k=='sources':
  text(im,'Kaynaklar',84,309,112,G,'serif',q+.7)
  entries=[('01 / GUMA · ilk gün videosu','Açıklanan bütçe planı ve önceki kitle beyanı','youtube.com/shorts/nnUXsnz3Wi0'),('02 / GUMA · Kullanım Şartları','Şirketin üretim / satış ilişkisine dair metni','gumastore.com/pages/kullanim-sartlari'),('03 / Yıldırım Gazetesi · 06.10.2025','Kurucu açıklaması ve haberdeki görev bilgisi','“İnegöllü mobilyacı gençler inanılmazı başardı”')]
  for j,(aa,bb,cc) in enumerate(entries):
   yy=535+j*248;text(im,aa,89,yy,34,C,'sans',q+.8);text(im,bb,91,yy+72,26,M,'sans',q+.8);text(im,cc,91,yy+119,25,G,'sans',q+.8);line(im,[(91,yy+189),(975,yy+189)],1,rgba(C,50),1)
  text(im,'Temsili stok / Pexels: 5384976 · 5384977 · 6790438\n7806870 · 7679835 · 12625256 · 12911888\nSes: Ece anlatımı. Fontlar: SIL OFL. Grafikler: özgün.\nKaynak videonun sesi veya görüntüsü kullanılmadı.\nTam bağlantılar: açıklama / kaynak paketi.',90,1310,25,M,'sans',q+.8)
 elif k=='follow':
  z=p(q,.05,.8);d.arc((352,593,728,969),-90,-90+359*z,fill=G,width=2)
  line(im,[(480,781),(600,781)],z,G,4);line(im,[(540,721),(540,841)],z,G,4)
  text(im,'Merak et.',540,1098,90,C,'serif',q,.12,'center');text(im,'Sor. Araştır.',540,1220,86,G,'serif',q,.3,'center')
  text(im,'TAKİPTE KAL',540,1397,29,M,'sans',q,.6,'center')
 # Persistent editorial identity, chapter and timeline anchor orientation.
 if k not in ['follow']:
  text(im,'GUMA / başlangıç notları',86,128,28,C,'serif',9)
  text(im,chapter,88,197,21,G,'sans',9)
  line(im,[(87,260),(978,260)],1,rgba(C,38),1)
  if t<155.2:
   subtitle(im,t);aa,bb,cc=source_for(k,t,asset)
   text(im,aa,88,1575,24,C,'sans',9)
   text(im,bb,88,1617,22,M,'sans',9)
   # Limit footer to 2 readable lines; visual attribution persists separately.
   if asset:text(im,'Temsili stok · Pexels '+SELECTED[asset]['source_id']+' · Marka tesisi/personeli değil',88,1663,22,M,'sans',9)
   else:text(im,cc,88,1663,22,M,'sans',9)
   line(im,[(88,1745),(978,1745)],1,rgba(C,36),1);line(im,[(88,1745),(88+890*t/155.167,1745)],1,G,2)
 out=im.convert('RGB')
 if frame is None and k in ['production','terms','map','questions']:
  goldmask=ImageChops.subtract(out.getchannel('R'),out.getchannel('G')).point(lambda v: min(255,max(0,(v-8)*12)))
  ivory=ImageOps.colorize(out.convert('L'),black='#fff9e9',white='#0a1721')
  out=Image.composite(Image.new('RGB',(W,H),'#9b6d2b'),ivory,goldmask)
 return out

def extract(name,t=1):
 path=clip_path(name); dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)]));t=t%max(.1,dur-.1);out=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(path),'-frames:v','1','-vf','scale=720:1280','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1']);return Image.frombytes('RGB',(720,1280),out)
def previews():
 for t in [1.8,11.7,40.7,57.8,61.7,101.3,128.5,151.7]:
  i=next(i for i,s in enumerate(SCENES) if s[0]<=t<s[1]);s=SCENES[i];shot=shot_at(t);fr=extract(shot[2],shot[3]+t-shot[0]) if shot else None;im=draw_scene(i,t-s[0],fr);im.save(V/'preview'/('frame-%05.1f.jpg'%t),quality=92)
 ims=[]
 for path in sorted((V/'preview').glob('frame-*.jpg')):
  im=Image.open(path);im.thumbnail((270,480));ims.append(im)
 sheet=Image.new('RGB',(270*4,480*2),N)
 for j,im in enumerate(ims):sheet.paste(im,((j%4)*270,(j//4)*480))
 sheet.save(V/'preview/contact.jpg',quality=93)
def render_chunk(job):
 idx,st,en,scene_idx,shot=job
 target=V/'render'/f'chunk-{idx:03d}.mp4'
 count=round(en*FPS)-round(st*FPS)
 if count<=0:return {'chunk':idx,'frames':0}
 decoder=None
 if shot:
  a,b,name,offset=shot;path=clip_path(name)
  # No looping; every crop stays within its selected 4–5-second action source.
  seek=offset+st-a
  decoder=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-ss',str(seek),'-i',path,'-an','-vf','scale=720:1280','-r',str(FPS),'-frames:v',str(count),'-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 enc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18']+([] if ARGS.legacy_color else ['-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709'])+['-pix_fmt','yuv420p','-movflags','+faststart','-y',str(target)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 begin=round(st*FPS)
 for f in range(count):
  t=(begin+f)/FPS;frame=None
  if decoder:
   raw=decoder.stdout.read(720*1280*3)
   if len(raw)!=720*1280*3:raise RuntimeError(f'Stock EOF {idx} {name} at {f}/{count}')
   frame=Image.frombytes('RGB',(720,1280),raw)
  im=draw_scene(scene_idx,t-SCENES[scene_idx][0],frame)
  enc.stdin.write(im.tobytes())
 enc.stdin.close();msg=enc.stderr.read().decode();code=enc.wait()
 if decoder:decoder.stdout.close();decoder.wait()
 if code:raise RuntimeError(msg)
 return {'chunk':idx,'frames':count,'start':st,'end':en,'path':str(target),'stock':shot[2] if shot else None}
def render_all(workers=4):
 assert AUDIO.is_file(), f'Missing local full audio input: {AUDIO}'
 assert MASTER.is_file(), f'Missing local voice master: {MASTER}'
 edges=sorted(set([s[0] for s in SCENES]+[END]+[s[0] for s in SHOTS]+[s[1] for s in SHOTS]))
 # Long graphic scenes are independent 4-second chunks. Exact frame grid keeps audio immutable.
 cuts=[]
 for a,b in zip(edges,edges[1:]):
  for v in np.arange(a,b,4):cuts.append(round(v*FPS)/FPS)
 cuts=sorted(set(cuts+[END]));jobs=[]
 for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
  midpoint=(a+b)/2;si=next(i for i,s in enumerate(SCENES) if s[0]<=midpoint<s[1]);jobs.append((j,a,b,si,shot_at(midpoint)))
 (V/'render/jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
 results=[]
 with ProcessPoolExecutor(max_workers=workers) as pool:
  futures={pool.submit(render_chunk,j):j for j in jobs}
  for fu in as_completed(futures):
   r=fu.result();results.append(r);print(json.dumps(r),flush=True)
 results.sort(key=lambda a:a['chunk']);(V/'render/result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 listing=V/'render/concat.txt';listing.write_text(''.join("file '"+q['path']+"'\n" for q in results))
 silent=V/'output/GUMA_V6_FULL_SILENT.mp4'
 subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart','-y',str(silent)],check=True)
 final=V/'output/GUMA_V6_TAM_ANLATIM_164s.mp4'
 raw=V/'output/GUMA_V6_TAM_ANLATIM_164s__raw.mp4'
 audio=AUDIO
 subprocess.run(['ffmpeg','-v','error','-i',str(silent),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(END),'-movflags','+faststart','-y',str(raw)],check=True)
 from finalize import finalize
 color_report=finalize(raw,final)
 master=MASTER;sha=hashlib.sha256(master.read_bytes()).hexdigest()
 report={'timeline_seconds':END,'frame_count':4926,'video_size':[1080,1920],'fps':30,'narration_master':str(master),'narration_sha256':sha,'narration_duration_seconds':155.167,'narration_cuts':0,'narration_speed':1,'narration_original_order':True,'original_sentence_count':39,'caption_segment_count':len(SUBS),'stock_coverage_seconds':round(sum(s[1]-s[0] for s in SHOTS),2),'unique_stock_ids':sorted(set(SELECTED[s[2]]['source_id'] for s in SHOTS)),'unique_proxy_count':len(set(s[2] for s in SHOTS)),'color_action':color_report['action'],'mix':str(audio),'final':str(final),'file_size':final.stat().st_size,'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'stock_windows':SHOTS,'rejected_3d_sofa_included':False,'source_video_frames_or_voice_included':False}
 (V/'output/RENDER_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));shutil.copy(CAPTIONS.with_name('narration.srt'),V/'output/GUMA_V6_altyazi.srt') if CAPTIONS.with_name('narration.srt').exists() else None
 print('FINAL '+str(final),flush=True)
if __name__=='__main__':
 for pth in ['preview','output','render']:(V/pth).mkdir(parents=True,exist_ok=True)
 if '--previews' in sys.argv:previews()
 if ARGS.render:render_all(ARGS.workers)
 if ARGS.refresh_sources:
  jobs=json.loads((V/'render/jobs.json').read_text())
  for job in jobs:
   if job[1]>=155.2 and job[2]<=161.2:print(render_chunk(job),flush=True)
