import React, {useLayoutEffect} from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {RoundedBox} from '@react-three/drei';
import * as THREE from 'three';
import {cubicBezier} from 'motion';
import IconArrowUpRight from '@tabler/icons-react/dist/esm/icons/IconArrowUpRight.mjs';

// Camera transforms depend only on the requested video frame. No wall-clock timers.
function CameraRig() {
  const frame = useCurrentFrame();
  const {camera} = useThree();
  const t = interpolate(frame, [0, 59], [0, 1], {extrapolateLeft:'clamp', extrapolateRight:'clamp', easing:cubicBezier(.22,.12,.3,1)});
  useLayoutEffect(() => {
    const c = camera as THREE.PerspectiveCamera;
    c.position.set(6.3 - 4.0 * t, 3.8 - .7 * t, 7.8 - .7 * t);
    c.lookAt(0, 1.2, 0);
    c.fov = 39;
    c.updateProjectionMatrix();
  }, [camera, t]);
  return null;
}

function PaddedBlock({position, args, color='#b97143'}:{position:[number,number,number];args:[number,number,number];color?:string}) {
  return <RoundedBox position={position} args={args} radius={.10} smoothness={3} castShadow receiveShadow>
    <meshStandardMaterial color={color} roughness={.92} />
  </RoundedBox>;
}

function Studio() {
  return <>
    <color attach="background" args={['#111b23']} />
    <ambientLight intensity={.55} />
    <directionalLight position={[3,7,5]} intensity={3.5} color="#ffe4b9" castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-7} shadow-camera-right={7} shadow-camera-top={7} shadow-camera-bottom={-7} />
    <pointLight position={[-4,3,-2]} intensity={25} color="#74b3dc" />
    <CameraRig />
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,0,0]} receiveShadow>
      <planeGeometry args={[200,200]} /><meshStandardMaterial color="#21333c" roughness={.8} />
    </mesh>
    {/* A new, unbranded sofa constructed from geometric primitives. */}
    <group rotation={[0,-.15,0]}>
      <PaddedBlock args={[4.45,.38,1.65]} position={[0,.7,0]} color="#704d38" />
      <PaddedBlock args={[4.1,1.35,.38]} position={[0,1.42,-.7]} />
      <PaddedBlock args={[.45,1,1.8]} position={[-2.05,1.1,0]} />
      <PaddedBlock args={[.45,1,1.8]} position={[2.05,1.1,0]} />
      {[-1,1].map(x=><React.Fragment key={x}>
        <PaddedBlock args={[1.81,.3,1.32]} position={[x*.97,1.03,.05]} color="#c48757" />
        <PaddedBlock args={[1.79,.92,.29]} position={[x*.97,1.6,-.44]} color="#bd7b4c" />
      </React.Fragment>)}
      {[-1.85,1.85].flatMap(x=>[-.57,.57].map(z=><mesh key={`${x}-${z}`} position={[x,.32,z]} castShadow>
        <cylinderGeometry args={[.055,.08,.56,12]} /><meshStandardMaterial color="#b8a782" metalness={.75} roughness={.3} />
      </mesh>))}
    </group>
    <mesh position={[-2.7,.56,1.6]} castShadow>
      <cylinderGeometry args={[.7,.7,.07,64]} /><meshStandardMaterial color="#dbd2bd" roughness={.65} />
    </mesh>
    <mesh position={[-2.7,.28,1.6]} castShadow>
      <cylinderGeometry args={[.12,.2,.55,32]} /><meshStandardMaterial color="#1b2528" roughness={.6} />
    </mesh>
    <mesh position={[0,.005,0]} rotation={[-Math.PI/2,0,0]} receiveShadow>
      <planeGeometry args={[6,4]} /><meshStandardMaterial color="#7e7869" roughness={1} />
    </mesh>
    <mesh position={[-3.8,2.5,-2]} castShadow>
      <boxGeometry args={[.13,5,.13]} /><meshStandardMaterial color="#e7d9bc" roughness={.45} metalness={.4} />
    </mesh>
    <mesh position={[-3.8,4.8,-2]}>
      <sphereGeometry args={[.3,24,24]} /><meshStandardMaterial color="#ffdf9d" emissive="#ffcc73" emissiveIntensity={2}/>
    </mesh>
  </>;
}

const Proof:React.FC = () => {
  const f = useCurrentFrame();
  const titleY = interpolate(f,[0,18],[22,0],{extrapolateRight:'clamp'});
  return <AbsoluteFill style={{background:'#111b23'}}>
    <ThreeCanvas width={720} height={1280} shadows camera={{position:[6.3,3.8,7.8],fov:39,near:.1,far:250}} gl={{antialias:true,alpha:false,preserveDrawingBuffer:true}}><Studio /></ThreeCanvas>
    <AbsoluteFill style={{padding:'80px 55px',fontFamily:'Arial,sans-serif',pointerEvents:'none',color:'#f2eddf',justifyContent:'space-between'}}>
      <div style={{transform:`translateY(${titleY}px)`,opacity:interpolate(f,[0,12],[0,1],{extrapolateRight:'clamp'})}}>
        <div style={{fontSize:17,letterSpacing:4,color:'#d3b675',marginBottom:18,display:'flex',alignItems:'center',gap:12}}>ÖZGÜN 3D · KAMERA TESTİ <IconArrowUpRight size={22}/></div>
        <div style={{fontSize:62,lineHeight:1.05,fontWeight:700}}>Görselin içinde<br/>hareket.</div>
      </div>
      <div style={{fontSize:15,color:'#c0c7c6',lineHeight:1.6}}>
        Temsili canlandırma · Marka ürünü değildir<br/>
        Three.js · React Three Fiber · Remotion<br/>
        Özgün geometri / fiziksel perspektif kamera
      </div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
const Root:React.FC=()=> <Composition id="CameraProof" component={Proof} durationInFrames={60} fps={30} width={720} height={1280} />;
registerRoot(Root);
