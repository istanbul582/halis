import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {selectComposition, renderStill, renderMedia} from '@remotion/renderer';
const root=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(root,'out');fs.mkdirSync(out,{recursive:true});
const browserExecutable=process.env.CHROMIUM_PATH||'/usr/bin/chromium';
const chromiumOptions={gl:process.env.GUMA_GL||'swangle',disableWebSecurity:false};
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx')});
const composition=await selectComposition({serveUrl,id:'CameraProof',browserExecutable,chromiumOptions});
for(const frame of [0,29,59]) {
  await renderStill({serveUrl,composition,frame,output:path.join(out,`camera-${frame}.png`),imageFormat:'png',browserExecutable,chromiumOptions,timeoutInMilliseconds:60000});
  console.log(`Rendered camera frame ${frame}`);
}
if(!process.argv.includes('--stills')) {
  let last=-1;
  await renderMedia({serveUrl,composition,codec:'h264',crf:20,pixelFormat:'yuv420p',outputLocation:path.join(out,'real-3d-camera-proof.mp4'),browserExecutable,chromiumOptions,concurrency:1,timeoutInMilliseconds:60000,onProgress:p=>{const n=Math.floor(p.progress*10);if(n!==last){console.log(`Camera render ${n*10}%`);last=n;}}});
  console.log('Rendered two-second camera proof');
}
