import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {selectComposition, renderMedia, renderStill} from '@remotion/renderer';

const cwd=path.dirname(new URL(import.meta.url).pathname);
const out=path.join(cwd,'out');fs.mkdirSync(out,{recursive:true});
console.log('Bundling Remotion project');
const serveUrl=await bundle({entryPoint:path.join(cwd,'src/index.tsx'),publicDir:path.join(cwd,'public'),onProgress:p=>{if(p===100)console.log('Bundle ready');}});
const browserExecutable='/usr/bin/chromium';
const composition=await selectComposition({serveUrl,id:'GumaMaviPilot',browserExecutable});
console.log('Composition verified',composition.width,composition.height,composition.durationInFrames,composition.fps);
if(process.argv.includes('--stills')){
 for(const frame of [0,60,150,225,285,360,465]){
  await renderStill({serveUrl,composition,browserExecutable,frame,output:path.join(out,`frame-${String(frame).padStart(3,'0')}.png`),imageFormat:'png'});
  console.log('Still',frame);
 }
}else{
 let last=-1;
 await renderMedia({serveUrl,composition,browserExecutable,codec:'h264',outputLocation:path.join(out,'GUMA_MAVI_PILOT_17S_SILENT.mp4'),crf:18,pixelFormat:'yuv420p',concurrency:2,onProgress:p=>{const n=Math.floor(p.progress*10);if(n!==last){console.log(`Rendering ${n*10}%`);last=n;}}});
 console.log('Full render completed');
}
