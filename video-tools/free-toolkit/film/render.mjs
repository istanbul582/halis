import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia} from '@remotion/renderer';
const root=path.dirname(fileURLToPath(import.meta.url)); const out=path.join(root,'out'); fs.mkdirSync(out,{recursive:true});
const browserExecutable='/usr/bin/chromium';
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),publicDir:path.join(root,'public')});
let lastProgressBlock=-1;
const composition=await selectComposition({serveUrl,id:'GumaEvidenceFilm',browserExecutable});
const frames=process.env.STILL_FRAMES?process.env.STILL_FRAMES.split(',').map(Number):[45,216,549,705,1110,1545,1974,2568,2775,2925];
if(process.argv.includes('--stills')) {for(const frame of frames){await renderStill({serveUrl,composition,frame,output:path.join(out,`frame-${String(frame).padStart(4,'0')}.png`),browserExecutable,timeoutInMilliseconds:60000});console.log(`Rendered frame ${frame}`);}}
else {const frameRange=process.env.FRAME_RANGE?process.env.FRAME_RANGE.split(',').map(Number):undefined;await renderMedia({serveUrl,composition,codec:'h264',crf:19,pixelFormat:'yuv420p',outputLocation:path.join(out,frameRange?'GUMA_v5_preview.mp4':'GUMA_v5_full.mp4'),browserExecutable,concurrency:2,timeoutInMilliseconds:120000,frameRange,onProgress:p=>{const block=Math.floor(p.renderedFrames/150);if(block!==lastProgressBlock){lastProgressBlock=block;console.log(`Frames ${p.renderedFrames}/${composition.durationInFrames}`)}}});console.log('Render completed');}
