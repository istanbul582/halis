import fs from 'node:fs';import path from 'node:path';import {bundle} from '@remotion/bundler';import {renderStill,renderMedia,selectComposition} from '@remotion/renderer';
const root=path.dirname(new URL(import.meta.url).pathname);const start=Date.now();fs.mkdirSync(path.join(root,'out'),{recursive:true});
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),publicDir:path.join(root,'public')});
const common={serveUrl,browserExecutable:'/usr/bin/chromium',chromiumOptions:{gl:'swangle'},timeoutInMilliseconds:60000};
const hero=process.argv.includes('--hero');
const composition=await selectComposition({...common,id:hero?'HeroCamera':'ProductionCamera'});
if(process.argv.includes('--check')){for(const f of [0,29]){await renderStill({...common,composition,frame:f,imageFormat:'png',output:path.join(root,`out/check-${f}.png`)});console.log('CHECK',f,'elapsed sec',Math.round((Date.now()-start)/1000));}}
else {let last=-1;await renderMedia({...common,composition,concurrency:2,codec:'h264',crf:17,pixelFormat:'yuv420p',outputLocation:path.join(root,hero?'out/hero-lowfps.mp4':'out/production-540-lowfps.mp4'),onProgress:p=>{const n=Math.floor(p.progress*10);if(n!==last){console.log('PROGRESS',n*10,'elapsed sec',Math.round((Date.now()-start)/1000));last=n;}}});console.log('COMPLETE',Math.round((Date.now()-start)/1000));}
