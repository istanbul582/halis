import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Pilot} from './Pilot';

const Root: React.FC = () => <Composition id="GumaMaviPilot" component={Pilot} width={1080} height={1920} fps={30} durationInFrames={510}/>;
registerRoot(Root);
