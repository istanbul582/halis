"""Convert legacy untagged BT.601 YUV to explicit limited-range BT.709.
Tagged BT.709 input is copied. This does not merely change metadata.
"""
from pathlib import Path
import argparse,json,subprocess,hashlib

def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
def finalize(src,dst):
 src=Path(src);dst=Path(dst);meta=probe(src);v=next(s for s in meta['streams'] if s['codec_type']=='video')
 already=(v.get('color_space')=='bt709' and v.get('color_range')=='tv' and v.get('color_primaries')=='bt709' and v.get('color_transfer')=='bt709')
 if already:
  args=['-c','copy'];action='copy_explicit_bt709'
 else:
  args=['-vf','scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=tv:out_range=tv,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-threads','4','-crf','18','-preset','veryfast','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','copy'];action='actual_bt601_limited_to_bt709_limited_matrix_conversion'
 subprocess.run(['ffmpeg','-v','error','-i',str(src),'-map','0:v:0','-map','0:a:0?']+args+['-movflags','+faststart','-y',str(dst)],check=True)
 out=probe(dst);vv=next(s for s in out['streams'] if s['codec_type']=='video')
 assert all(vv.get(k)==val for k,val in [('color_space','bt709'),('color_range','tv'),('color_primaries','bt709'),('color_transfer','bt709')]),vv
 report={'input':str(src),'output':str(dst),'action':action,'input_video':v,'output_video':vv,'output_duration':out['format']['duration'],'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}
 dst.with_suffix('.color.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'output':str(dst),'action':action,'bytes':dst.stat().st_size,'sha256':report['sha256']}),flush=True)
 return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');a=ap.parse_args();finalize(a.input,a.output)
