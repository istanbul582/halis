import React, {Suspense, useLayoutEffect, useMemo,useState} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader,useThree} from '@react-three/fiber';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {staticFile,delayRender,continueRender} from 'remotion';
import * as THREE from 'three';
const smooth=(x:number)=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
function textile(wood:boolean){const n=256,d=new Uint8Array(n*n*4);for(let y=0;y<n;y++)for(let x=0;x<n;x++){const i=(y*n+x)*4;const q=wood?(Math.sin(y*.45+Math.sin(x*.028)*3)+Math.sin(y*.12+x*.011))*.17+.66:(Math.sin(x*Math.PI)*.05+Math.sin(y*2.85)*.1+Math.sin(x*27.34+y*6.34)*.08+.77);d[i]=d[i+1]=d[i+2]=Math.min(255,q*255);d[i+3]=255;}const t=new THREE.DataTexture(d,n,n);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(wood?2:15,wood?5:15);t.needsUpdate=true;return t;}
function Asset({t,exploded=false,onReady}:{t:number;exploded?:boolean;onReady:()=>void}) {
 const gltf=useLoader(GLTFLoader,staticFile('furniture.glb'));
 const {scene,gl,camera}=useThree();
 const model=useMemo(()=>{const m=gltf.scene.clone(true); const weave=textile(false),oak=textile(true);m.traverse((o:any)=>{if(o.isCamera||o.isLight){o.visible=false;}if(o.isMesh){o.castShadow=true;o.receiveShadow=true;const name=o.material?.name||'';if(name.includes('velvet'))o.material=new THREE.MeshPhysicalMaterial({color:'#174653',roughness:.72,sheen:1,sheenRoughness:.65,sheenColor:new THREE.Color('#4b7d88'),map:weave,bumpMap:weave,bumpScale:.012});else if(name.includes('oak'))o.material=new THREE.MeshStandardMaterial({color:'#8b5a2b',roughness:.42,map:oak,bumpMap:oak,bumpScale:.009});else if(name.includes('concrete')){o.material=new THREE.MeshStandardMaterial({color:'#0e1a22',roughness:.62,metalness:.12});}else if(name.includes('brass'))o.material=new THREE.MeshStandardMaterial({color:'#bd9454',metalness:.82,roughness:.28});else{o.material=o.material.clone();}o.userData.baseY=o.position.y;}});return m;},[gltf]);
 useLayoutEffect(()=>{const env=new RoomEnvironment();const p=new THREE.PMREMGenerator(gl);const e=p.fromScene(env,.04);scene.environment=e.texture;scene.environmentIntensity=.8;return()=>{e.dispose();p.dispose();env.dispose();}},[gl,scene]);
 useLayoutEffect(()=>{const lift=exploded?smooth((t-31.8)/9):t>45.9&&t<60?smooth((59.7-t)/4):0;model.traverse((o:any)=>{if(o.isMesh&&(o.name.includes('plush')||o.name.includes('pillowed')||o.name.includes('upholstered')||o.name.includes('Seat_seam')||o.name.includes('Seat seam'))){o.position.y=o.userData.baseY+lift*(o.name.includes('base')?.85:1.15);}});},[model,t,exploded]);
 useLayoutEffect(()=>{const c=camera as THREE.PerspectiveCamera;let x=4.2,z=7.2,y=3,targetY=1.35;const u=t;
 if(u<14.85){x=4.4-u*.16;z=7.4+u*.035;y=2.75+Math.sin(u*.13)*.25;}
 else if(u<31.81){x=2.1-(u-14.85)*.055;z=8.8;y=3.6;targetY=1.0;}
 else if(u<46){const a=smooth((u-31.81)/14.2);x=2.7-5.1*a;z=7.8;y=3.0+.9*a;targetY=1.6;}
 else if(u<59.72){const a=(u-46)/13.72;x=-3.2+1.5*a;z=6.4;y=4.6;targetY=1.35;}
 else if(u<70.325){x=-2.0+(u-59.72)*.27;z=8.3;y=2.65;targetY=1.3;}
 else {x=3.5-(u-70.325)*.1;z=7.5;y=3.1;targetY=1.3;}
 c.position.set(x,y,z);c.lookAt(0,targetY,0);c.fov=37;c.updateProjectionMatrix();},[camera,t]);
 useLayoutEffect(()=>{onReady();},[model,onReady]);
 return <primitive object={model}/>;
}
export const Stage:React.FC<{t:number;opacity?:number}>=({t,opacity=1})=>{const [handle]=useState(()=>delayRender('Wait original GLB asset'));return <div style={{position:'absolute',inset:0,opacity}}><ThreeCanvas width={1080} height={1920} shadows camera={{position:[4.4,2.75,7.4],fov:37,near:.1,far:250}} gl={{antialias:true,alpha:false,preserveDrawingBuffer:true}}>
 <color attach="background" args={['#101b24']}/><fog attach="fog" args={['#101b24',10,30]}/><ambientLight intensity={.35}/>
 <directionalLight position={[-3,6,4]} intensity={3} color="#ffdeae" castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-5} shadow-camera-right={5} shadow-camera-top={5} shadow-camera-bottom={-5} shadow-bias={-.0005}/>
 <directionalLight position={[4,2,-3]} intensity={4} color="#7ba9c2"/><spotLight position={[0,5,-2]} angle={.6} penumbra={1} intensity={150} color="#edbd76"/>
 <Suspense fallback={null}><Asset t={t} exploded={t>=31.81&&t<46} onReady={()=>continueRender(handle)}/></Suspense>
 </ThreeCanvas></div>;};
