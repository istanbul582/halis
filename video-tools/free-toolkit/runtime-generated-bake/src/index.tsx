import React from 'react';
import {registerRoot,Composition,useCurrentFrame} from 'remotion';
import {Stage} from './Stage';
const Production=()=>{const f=useCurrentFrame();return <Stage w={540} h={960} t={31.81+(f/29)*14.18}/>;};
const Hero=()=>{const f=useCurrentFrame();return <Stage t={(f/29)*14.84}/>;};
const Root=()=> <><Composition id="ProductionCamera" component={Production} width={540} height={960} fps={3} durationInFrames={30}/><Composition id="HeroCamera" component={Hero} width={360} height={640} fps={3} durationInFrames={30}/></>;
registerRoot(Root);
