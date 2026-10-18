import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {Film} from './Film';
const Root: React.FC=()=> <Composition id="GumaEvidenceFilm" component={Film} width={1080} height={1920} fps={30} durationInFrames={2970}/>;
registerRoot(Root);
